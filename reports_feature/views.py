# reports_feature/views.py
# Author: Sadana Suresh w21162895
# This file has all the views and report builder functions for the Reports module.
# PDF generation uses ReportLab, Excel uses openpyxl, both write to memory buffers.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import io
from datetime import datetime
from io import BytesIO

# ReportLab for PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# openpyxl for Excel
import openpyxl

# try/except so the app still runs if teammate models aren't connected yet
from organisation_feature.models import Department
from teams_feature.models import Team


# --- REPORT BUILDERS ---
# Each function builds the data for one report type and returns a dict.
# Keeping these separate from the views means if a query changes I only edit one place.

def get_teams_report_data():
    # Teams Summary: department breakdown with team counts
    total_teams = Team.objects.count()
    total_depts = Department.objects.count()
    teams_without_managers = Team.objects.filter(manager__isnull=True).count()

    # Count('teams') uses the related_name set on Team.department ForeignKey in Student 1's model
    dept_rows = []
    for dept in Department.objects.annotate(team_count=Count('teams')).order_by('-team_count'):
        dept_rows.append([dept.department_name, str(dept.team_count)])

    stats = [
        {'label': 'Total Teams',            'value': str(total_teams)},
        {'label': 'Total Departments',      'value': str(total_depts)},
        {'label': 'Teams Without Managers', 'value': str(teams_without_managers)},
    ]

    return {
        'title':       'Teams Report',
        'description': 'Sky Engineering team registry summary and department metrics.',
        'stats':       stats,
        'columns':     ['Department', 'Number of Teams'],
        'rows':        dept_rows,
    }


def get_all_teams_data():
    # All Teams: full list with manager, department, size and status
    # select_related loads department and manager in one query instead of hitting the DB per row
    rows = []
    for team in Team.objects.select_related('department', 'manager').order_by('department__department_name', 'team_name'):
        manager_name = team.manager.username if team.manager else 'None'
        rows.append([
            team.team_name,
            manager_name,
            team.department.department_name if team.department else 'None',
            str(team.team_size) if team.team_size else '0',
            'Active' if team.is_active else 'Inactive',
        ])

    stats = [
        {'label': 'Total Teams',   'value': str(Team.objects.count())},
        {'label': 'Departments',   'value': str(Department.objects.count())},
        {'label': 'No Manager',    'value': str(Team.objects.filter(manager__isnull=True).count())},
        {'label': 'Active Teams',  'value': str(Team.objects.filter(is_active=True).count())},
    ]

    return {
        'title':       'All Teams',
        'description': 'Full list of all engineering teams, their managers and departments.',
        'stats':       stats,
        'columns':     ['Team Name', 'Manager', 'Department', 'Team Size', 'Status'],
        'rows':        rows,
    }


def get_no_manager_data():
    # Teams Without Managers: filters where manager is null
    # This is the dedicated report the brief requires, not just a count
    rows = []
    for team in Team.objects.filter(manager__isnull=True).select_related('department').order_by('team_name'):
        rows.append([
            team.team_name,
            team.department.department_name if team.department else 'None',
        ])

    stats = [
        {'label': 'Teams Without Managers', 'value': str(len(rows))},
        {'label': 'Total Teams',            'value': str(Team.objects.count())},
    ]

    return {
        'title':       'Teams Without Managers',
        'description': 'Engineering teams currently without an assigned manager.',
        'stats':       stats,
        'columns':     ['Team Name', 'Department'],
        'rows':        rows,
    }


def get_report_meta(report_type):
    # Maps the URL slug to the right builder function.
    # Adding a new report only needs one new entry here, nothing else changes.
    builders = {
        'teams':      get_teams_report_data,
        'all-teams':  get_all_teams_data,
        'no-manager': get_no_manager_data,
    }
    builder = builders.get(report_type)
    return builder() if builder else {}


# --- PDF GENERATOR ---

def generate_pdf(title, description, columns, rows, stats):
    # Builds a PDF in memory using ReportLab and returns a BytesIO buffer.
    # No files written to disk.
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    # brand colours defined once so they're easy to update
    brand_blue  = colors.HexColor('#2d3a5e')
    accent_blue = colors.HexColor('#4277D6')
    light_grey  = colors.HexColor('#f8f9fc')

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        textColor=brand_blue,
        fontSize=22,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#6c757d'),
        fontSize=10,
        spaceAfter=4,
    )
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        textColor=colors.HexColor('#6c757d'),
        fontSize=8,
        spaceAfter=16,
    )

    elements = []

    # title, description and timestamp at the top
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(description, subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')} - Sky Engineering", meta_style))
    elements.append(Spacer(1, 0.3*cm))

    # stats table: labels on top row, values on bottom row
    if stats:
        stat_data = [[s['label'] for s in stats], [s['value'] for s in stats]]
        stat_col_width = (A4[0] - 3*cm) / len(stats)
        stat_table = Table(stat_data, colWidths=[stat_col_width] * len(stats))
        stat_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), light_grey),
            ('BACKGROUND',    (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR',     (0, 1), (-1, 1), brand_blue),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica'),
            ('FONTNAME',      (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 8),
            ('FONTSIZE',      (0, 1), (-1, 1), 18),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ]))
        elements.append(stat_table)
        elements.append(Spacer(1, 0.5*cm))

    # main data table - first row is headers, rest is data
    if columns and rows:
        table_data = [columns] + rows
        col_width = (A4[0] - 3*cm) / len(columns)
        main_table = Table(table_data, colWidths=[col_width] * len(columns), repeatRows=1)
        main_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), accent_blue),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 10),
            ('TOPPADDING',    (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 9),
            ('TEXTCOLOR',     (0, 1), (-1, -1), colors.HexColor('#495057')),
            ('TOPPADDING',    (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            # alternating row shading makes it easier to read
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_grey]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(main_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# --- EXCEL GENERATOR ---

def generate_excel(title, columns, rows):
    # Builds a real .xlsx file in memory using openpyxl.
    # Fixed from earlier version that was writing CSV bytes with the wrong content type.
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title[:31]  # Excel tab names max out at 31 chars

    ws.append(columns)  # header row
    for row in rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


# --- VIEWS ---

@login_required
def reports_dashboard(request):
    # Shows the dashboard with three report cards
    report_types = [
        {'name': 'Teams Summary Report',   'slug': 'teams'},
        {'name': 'All Teams Report',       'slug': 'all-teams'},
        {'name': 'Teams Without Managers', 'slug': 'no-manager'},
    ]
    return render(request, 'reports_feature/reports_dashboard.html', {'report_types': report_types})


@login_required
def report_preview(request, report_type):
    # Loads the HTML preview for a given report type.
    # If the report_type slug isn't in the router, meta is empty and the template shows no data.
    meta = get_report_meta(report_type)
    context = {
        'report_type':        report_type,
        'report_title':       meta.get('title',       'Report'),
        'report_description': meta.get('description', ''),
        'stats':              meta.get('stats',        []),
        'columns':            meta.get('columns',      []),
        'rows':               meta.get('rows',         []),
    }
    return render(request, 'reports_feature/report_preview.html', context)


@login_required
def download_report(request, report_type, file_format):
    # Handles PDF and Excel downloads. Returns 400 for unknown types or formats.
    meta = get_report_meta(report_type)

    if not meta:
        # unknown report type - don't want silent empty downloads
        return HttpResponse('Unknown report type', status=400)

    columns     = meta.get('columns', [])
    rows        = meta.get('rows',    [])
    title       = meta.get('title',   report_type)
    description = meta.get('description', '')
    stats       = meta.get('stats',   [])

    if file_format == 'excel':
        buffer = generate_excel(title, columns, rows)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        return response

    elif file_format == 'pdf':
        buffer = generate_pdf(title, description, columns, rows, stats)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
        return response

    # anything other than pdf or excel gets a 400
    return HttpResponse('Invalid format', status=400)
