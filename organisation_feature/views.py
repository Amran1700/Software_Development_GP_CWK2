from django.shortcuts import render, get_object_or_404
from .models import Department, TeamType
from teams_feature.models import Team


def org_chart(request):
    """Displays the organisation chart showing all departments and their teams."""
    departments = Department.objects.prefetch_related('teams').all()
    return render(request, 'organisation_feature/org_chart.html', {
        'departments': departments,
    })


def department_list(request):
    """Displays a list of all departments with optional search."""
    query = request.GET.get('q', '')
    if query:
        departments = Department.objects.filter(
            department_name__icontains=query
        ) | Department.objects.filter(
            specialisation__icontains=query
        )
    else:
        departments = Department.objects.all()
    return render(request, 'organisation_feature/department_list.html', {
        'departments': departments,
        'query': query,
    })


def department_detail(request, department_id):
    """Displays the detail page for a single department."""
    department = get_object_or_404(Department, id=department_id)
    teams = Team.objects.filter(department=department)
    team_types = TeamType.objects.all()
    return render(request, 'organisation_feature/department_detail.html', {
        'department': department,
        'teams': teams,
        'team_types': team_types,
    })