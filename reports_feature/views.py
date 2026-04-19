# reports_feature/views.py
# Author: Student 5 – Sadana Suresh (w21162895)
# Module: 5COSC021W – Software Development Group Project CWK2
# Description: Views and report data builders for the Reports module.
#              Handles dashboard, preview, and file download (PDF/Excel) for 3 report types.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import io
from datetime import datetime
from io import BytesIO

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# openpyxl import for Excel generation
import openpyxl

# Import models from teammate apps – try/except ensures app runs standalone if models not yet available
from organisation_feature.models import Department
from teams_feature.models import Team


# ── REPORT DATA BUILDERS ──────────────────────────────────────────────────────
# Each builder function returns a dictionary with title, description, stats, columns and rows.
# This separates database query logic from view logic, keeping views clean and maintainable.

def get_teams_report_data():
    """
    Builds data for the Teams Summary Report.
    Returns department breakdown with team counts, plus headline statistics.
    Queries Department and Team models from teammate apps.
    """
    # Count totals for the stats cards
    total_teams = Team.objects.count()
    total_depts = Department.objects.count()
    teams_without_managers = Team.objects.filter(manager__isnull=True).count()

    # Build department rows using annotate to count teams per department
    # 'teams' is the related_name on the Team.department ForeignKey
    dept_rows = []
    for dept in Department.objects.annotate(team_count=Count('teams')).order_by('-team_count'):
        dept_rows.append([dept.department_name, str(dept.team_count)])

    # Stats cards shown at top of the preview page
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
    """
    Builds data for the All Teams Report.
    Returns every team with manager name, department, size and active status.
    Uses select_related to load department and manager in a single query (avoids N+1).
    """
    rows = []
    for team in Team.objects.select_related('department', 'manager').order_by('department__department_name', 'team_name'):
        # Use em dash if no manager assigned
        manager_name = team.manager.username if team.manager else '—'
        rows.append([
            team.team_name,
            manager_name,
            team.department.department_name if team.department else '—',
            str(team.team_size) if team.team_size else '0',
            'Active' if team.is_active else 'Inactive',
        ])

    # Stats cards shown at top of the preview page
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
    """
    Builds data for the Teams Without Managers report.
    Returns all teams where manager is NULL, with their department shown.
    Uses select_related to avoid N+1 queries on department lookup.
    This satisfies the brief requirement: 'teams without managers'.
    """
    rows = []
    for team in Team.objects.filter(manager__isnull=True).select_related('department').order_by('team_name'):
        rows.append([
            team.team_name,
            team.department.department_name if team.department else '—',
        ])

    # Stats cards shown at top of the preview page
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
    """
    Router function that maps a report_type slug to the correct builder function.
    Returns an empty dict if the report_type is not recognised.
    Adding a new report type only requires adding one entry to this dictionary.
    """
    builders = {
        'teams':      get_teams_report_data,
        'all-teams':  get_all_teams_data,
        'no-manager': get_no_manager_data,
    }
    builder = builders.get(report_type)
    return builder() if builder else {}


# ── PDF GENERATOR ─────────────────────────────────────────────────────────────

def generate_pdf(title, description, columns, rows, stats):
    """
    Builds and returns a PDF file as a BytesIO buffer using ReportLab.
    Includes a title block, stats summary table, and main data table.
    Called from the download_report view when format is 'pdf'.
    """
    # Create in-memory buffer – no file written to disk
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    # Colour constants – defined once so changing brand colours only requires editing here
    styles = getSampleStyleSheet()
    brand_blue = colors.HexColor('#2d3a5e')
    accent_blue = colors.HexColor('#4277D6')
    light_grey = colors.HexColor('#f8f9fc')

    # Custom paragraph styles for title, subtitle and metadata
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

    # Title block – report name, description and generation timestamp
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(description, subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')} — Sky Engineering", meta_style))
    elements.append(Spacer(1, 0.3*cm))

    # Stats summary table – label row on top, value row below
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

    # Main data table – first row is column headers, remaining rows are data
    if columns and rows:
        table_data = [columns] + rows
        col_width = (A4[0] - 3*cm) / len(columns)
        main_table = Table(table_data, colWidths=[col_width] * len(columns), repeatRows=1)
        main_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND',    (0, 0), (-1, 0), accent_blue),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 10),
            ('TOPPADDING',    (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            # Data rows styling
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 9),
            ('TEXTCOLOR',     (0, 1), (-1, -1), colors.HexColor('#495057')),
            ('TOPPADDING',    (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            # Alternating row background for readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_grey]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(main_table)

    # Build the PDF into the buffer and reset to start for reading
    doc.build(elements)
    buffer.seek(0)
    return buffer


# ── EXCEL GENERATOR ───────────────────────────────────────────────────────────

def generate_excel(title, columns, rows):
    """
    Builds and returns a real .xlsx file as a BytesIO buffer using openpyxl.
    Writes column headers and all data rows into a single worksheet.
    Called from the download_report view when format is 'excel'.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title[:31]  # Excel worksheet tab names are capped at 31 characters

    ws.append(columns)  # First row is the header
    for row in rows:    # Remaining rows are data
        ws.append(row)

    # Save to in-memory buffer – no file written to disk
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


# ── VIEWS ─────────────────────────────────────────────────────────────────────

@login_required
def reports_dashboard(request):
    """
    Renders the Reports Dashboard page showing all available report type cards.
    Protected by @login_required – unauthenticated users are redirected to login.
    """
    report_types = [
        {'name': 'Teams Summary Report',    'slug': 'teams'},
        {'name': 'All Teams Report',        'slug': 'all-teams'},
        {'name': 'Teams Without Managers',  'slug': 'no-manager'},
    ]
    return render(request, 'reports_feature/reports_dashboard.html', {'report_types': report_types})


@login_required
def report_preview(request, report_type):
    """
    Renders the HTML preview page for a given report type.
    Passes stats, column headers and row data to the template.
    If report_type is not recognised, meta will be empty and template shows no data.
    Protected by @login_required.
    """
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
    """
    Handles file download requests for a given report type and format.
    Supported formats: 'pdf' (via ReportLab) and 'excel' (via openpyxl, real .xlsx).
    Returns 400 if report_type is not recognised or format is not supported.
    Protected by @login_required.
    """
    meta = get_report_meta(report_type)

    # Return 400 if report type not recognised – prevents silent empty downloads
    if not meta:
        return HttpResponse('Unknown report type', status=400)

    columns     = meta.get('columns', [])
    rows        = meta.get('rows',    [])
    title       = meta.get('title',   report_type)
    description = meta.get('description', '')
    stats       = meta.get('stats',   [])

    if file_format == 'excel':
        # Generate a real .xlsx file using openpyxl
        buffer = generate_excel(title, columns, rows)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        return response

    elif file_format == 'pdf':
        # Generate PDF using ReportLab and return as file download
        buffer = generate_pdf(title, description, columns, rows, stats)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
        return response

    # Return 400 for any unsupported format (e.g. csv, xml)
    return HttpResponse('Invalid format', status=400)
