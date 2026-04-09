# reports_feature/views.py
# Author: Student 5 – Reports Module
# -------------------------------------------------------
# Week 1: App created, stub views defined, libraries installed
# Week 2: Full implementation – dashboard, preview, PDF + Excel export
# Week 3: Bug fixes – field names, template paths, related_name, edge cases
# -------------------------------------------------------

import io
from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import FileResponse, HttpResponse
from django.shortcuts import render

try:
    from teams_feature.models import Team
except ImportError:
    Team = None

try:
    from organisation_feature.models import Department
except ImportError:
    Department = None

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

User = get_user_model()


# ──────────────────────────────────────────────────────
# Query helpers
# ──────────────────────────────────────────────────────

def _teams_by_department():
    """Report 1 – count of teams per department, A→Z.
    Uses 'teams' as the related_name on Team.department FK.
    Department field is 'department_name', not 'name'.
    """
    if Department is None or Team is None:
        return []
    return (
        Department.objects
        .annotate(team_count=Count('teams'))
        .values('department_name', 'team_count')
        .order_by('department_name')
    )


def _teams_without_managers():
    """Report 2 – Teams with no manager assigned.
    Returns queryset of Team objects where manager is NULL.
    """
    if Team is None:
        return []
    return Team.objects.filter(manager__isnull=True).select_related('department')


def _summary_stats():
    """Report 3 – headline numbers across the whole application."""
    return {
        'total_teams':            Team.objects.count() if Team else 0,
        'total_departments':      Department.objects.count() if Department else 0,
        'total_users':            User.objects.count(),
        'teams_without_managers': Team.objects.filter(manager__isnull=True).count() if Team else 0,
    }


# ──────────────────────────────────────────────────────
# Views
# ──────────────────────────────────────────────────────

@login_required
def reports_dashboard(request):
    """Renders the reports home page with three report-type cards."""
    report_types = [
        {
            'id':          'teams_by_department',
            'title':       'Teams by Department',
            'description': 'Shows how many engineering teams exist in each department.',
            'icon':        'bi-diagram-3',
        },
        {
            'id':          'teams_without_managers',
            'title':       'Teams Without Managers',
            'description': 'Lists every team that currently has no assigned manager.',
            'icon':        'bi-person-x',
        },
        {
            'id':          'summary',
            'title':       'Summary Statistics',
            'description': 'High-level totals: teams, departments, users, unmanaged teams.',
            'icon':        'bi-bar-chart-line',
        },
    ]
    return render(request, 'reports/reports_dashboard.html', {'report_types': report_types})


@login_required
def report_preview(request, report_type):
    """HTML table preview of the chosen report with PDF/Excel download buttons."""
    context = {'report_type': report_type}

    if report_type == 'teams_by_department':
        context['title']   = 'Teams by Department'
        context['headers'] = ['Department', 'Number of Teams']
        context['rows']    = list(_teams_by_department())

    elif report_type == 'teams_without_managers':
        context['title']   = 'Teams Without Managers'
        context['headers'] = ['Team Name', 'Department']
        context['rows'] = [
            {
                'name':       t.team_name,
                'department': t.department.department_name if t.department else 'N/A',
            }
            for t in _teams_without_managers()
        ]

    elif report_type == 'summary':
        context['title']   = 'Summary Statistics'
        context['headers'] = ['Metric', 'Value']
        stats = _summary_stats()
        context['rows'] = [
            {'label': 'Total Teams',              'value': stats['total_teams']},
            {'label': 'Total Departments',        'value': stats['total_departments']},
            {'label': 'Total Registered Users',   'value': stats['total_users']},
            {'label': 'Teams Without Managers',   'value': stats['teams_without_managers']},
        ]

    else:
        context['error'] = f'Unknown report type: {report_type}'

    return render(request, 'reports/report_preview.html', context)


@login_required
def generate_report(request):
    """POST-only view. Returns PDF or Excel file as a download."""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    report_type = request.POST.get('report_type', '')
    fmt         = request.POST.get('format', 'pdf')

    if fmt == 'pdf':
        return _build_pdf(report_type)
    elif fmt == 'excel':
        return _build_excel(report_type)
    else:
        return HttpResponse('Unsupported format', status=400)


# ──────────────────────────────────────────────────────
# PDF builder
# ──────────────────────────────────────────────────────

def _build_pdf(report_type):
    """Builds and returns a PDF FileResponse for the given report_type."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=16, spaceAfter=4,
        textColor=colors.HexColor('#1a3a5c'),
    )
    SUB = ParagraphStyle(
        'SUB', parent=styles['Normal'],
        fontSize=9, spaceAfter=14, textColor=colors.grey,
    )
    NAVY = colors.HexColor('#1a3a5c')
    ALT  = colors.HexColor('#f0f4f8')

    elems = [
        Paragraph('Sky Engineering Teams Portal', H1),
        Paragraph(f'Generated: {date.today().strftime("%d %B %Y")}', SUB),
        Spacer(1, 0.3*cm),
    ]

    if report_type == 'teams_by_department':
        elems.append(Paragraph('Report: Teams by Department', H1))
        data = [['Department', 'Number of Teams']]
        rows = list(_teams_by_department())
        if rows:
            data += [[r['department_name'], str(r['team_count'])] for r in rows]
        else:
            data.append(['No data available', ''])
        filename = 'teams_by_department.pdf'

    elif report_type == 'teams_without_managers':
        elems.append(Paragraph('Report: Teams Without Managers', H1))
        data  = [['Team Name', 'Department']]
        teams = list(_teams_without_managers())
        if teams:
            data += [
                [t.team_name, t.department.department_name if t.department else 'N/A']
                for t in teams
            ]
        else:
            data.append(['All teams have managers assigned', ''])
        filename = 'teams_without_managers.pdf'

    elif report_type == 'summary':
        elems.append(Paragraph('Report: Summary Statistics', H1))
        stats = _summary_stats()
        data = [
            ['Metric', 'Value'],
            ['Total Teams',            str(stats['total_teams'])],
            ['Total Departments',      str(stats['total_departments'])],
            ['Total Registered Users', str(stats['total_users'])],
            ['Teams Without Managers', str(stats['teams_without_managers'])],
        ]
        filename = 'summary_report.pdf'

    else:
        return HttpResponse('Unknown report type', status=400)

    tbl = Table(data, colWidths=[10*cm, 5*cm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1,  0), NAVY),
        ('TEXTCOLOR',      (0, 0), (-1,  0), colors.white),
        ('FONTNAME',       (0, 0), (-1,  0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1,  0), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ALT]),
        ('GRID',           (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('FONTNAME',       (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',       (0, 1), (-1, -1), 10),
        ('TOPPADDING',     (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 6),
        ('LEFTPADDING',    (0, 0), (-1, -1), 8),
    ]))
    elems.append(tbl)
    doc.build(elems)

    buffer.seek(0)
    resp = FileResponse(buffer, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


# ──────────────────────────────────────────────────────
# Excel builder
# ──────────────────────────────────────────────────────

def _build_excel(report_type):
    """Builds and returns an Excel FileResponse for the given report_type."""
    wb = openpyxl.Workbook()
    ws = wb.active

    hdr_font  = Font(bold=True, color='FFFFFF', size=11)
    hdr_fill  = PatternFill('solid', start_color='1A3A5C', end_color='1A3A5C')
    hdr_align = Alignment(horizontal='center', vertical='center')
    alt_fill  = PatternFill('solid', start_color='F0F4F8', end_color='F0F4F8')
    thin      = Side(style='thin', color='CCCCCC')
    bdr       = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws['A1'] = 'Sky Engineering Teams Portal'
    ws['A1'].font = Font(bold=True, size=13, color='1A3A5C')
    ws['A2'] = f'Generated: {date.today().strftime("%d %B %Y")}'
    ws['A2'].font = Font(italic=True, color='888888', size=10)
    ws.append([])
    ws.append([])

    def write_headers(cols):
        """Write a styled header row."""
        ws.append(cols)
        r = ws.max_row
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=r, column=c)
            cell.font      = hdr_font
            cell.fill      = hdr_fill
            cell.alignment = hdr_align
            cell.border    = bdr

    def write_row(values, idx):
        """Write a data row with alternating fill."""
        ws.append(values)
        r = ws.max_row
        for c in range(1, len(values) + 1):
            cell = ws.cell(row=r, column=c)
            if idx % 2 == 1:
                cell.fill = alt_fill
            cell.border = bdr

    if report_type == 'teams_by_department':
        ws.title = 'Teams by Dept'
        write_headers(['Department', 'Number of Teams'])
        rows = list(_teams_by_department())
        if rows:
            for i, r in enumerate(rows):
                write_row([r['department_name'], r['team_count']], i)
        else:
            write_row(['No data available', 0], 0)
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20
        filename = 'teams_by_department.xlsx'

    elif report_type == 'teams_without_managers':
        ws.title = 'No Manager Teams'
        write_headers(['Team Name', 'Department'])
        teams = list(_teams_without_managers())
        if teams:
            for i, t in enumerate(teams):
                write_row([t.team_name, t.department.department_name if t.department else 'N/A'], i)
        else:
            write_row(['All teams have managers assigned', ''], 0)
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 30
        filename = 'teams_without_managers.xlsx'

    elif report_type == 'summary':
        ws.title = 'Summary'
        write_headers(['Metric', 'Value'])
        stats = _summary_stats()
        for i, (label, val) in enumerate([
            ('Total Teams',            stats['total_teams']),
            ('Total Departments',      stats['total_departments']),
            ('Total Registered Users', stats['total_users']),
            ('Teams Without Managers', stats['teams_without_managers']),
        ]):
            write_row([label, val], i)
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20
        filename = 'summary_report.xlsx'

    else:
        return HttpResponse('Unknown report type', status=400)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    resp = FileResponse(
        out,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp