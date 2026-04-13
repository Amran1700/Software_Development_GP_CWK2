""" Name: Ehsaan Zakriya
 ID: W2115831 """
from django.shortcuts import render, get_object_or_404
from .models import Department, TeamType
from teams_feature.models import Team, UpstreamDependency, DownstreamDependency


def org_chart(request):
    """
    Displays the organisation chart view.
    Queries all departments and prefetches their related teams
    so they can be displayed hierarchically in the template.
    """
    departments = Department.objects.prefetch_related('teams').all()
    return render(request, 'organisation_feature/org_chart.html', {
        'departments': departments,
    })


def department_list(request):
    """
    Displays a searchable, filterable list of all departments.
    Accepts GET parameter 'q' for search and 'filter' for category filtering.
    Filters by department name or specialisation if a query is provided.
    Filters by department name if a filter chip is selected.
    3+ Teams filter shows departments with 3 or more teams.
    """
    query = request.GET.get('q', '')
    active_filter = request.GET.get('filter', '')
    departments = Department.objects.all()

    if query:
        departments = departments.filter(
            department_name__icontains=query
        ) | departments.filter(
            specialisation__icontains=query
        )

    if active_filter == '3teams':
        departments = [d for d in departments if d.teams.count() >= 3]
    elif active_filter:
        departments = departments.filter(department_name__icontains=active_filter)

    return render(request, 'organisation_feature/department_list.html', {
        'departments': departments,
        'query': query,
        'active_filter': active_filter,
    })


def department_detail(request, department_id):
    """
    Displays the detail page for a single department.
    Retrieves the department by ID, returns 404 if not found.
    Passes teams, team types, and dependency data to the template.
    """
    # Get department or return 404 if not found
    department = get_object_or_404(Department, id=department_id)
    # Get all teams belonging to this department
    teams = Team.objects.filter(department=department)
    # Get all team types for the team types section
    team_types = TeamType.objects.all()
    # Build dependency data for each team in this department
    team_dependencies = []
    for team in teams:
        upstream = UpstreamDependency.objects.filter(team=team)
        downstream = DownstreamDependency.objects.filter(team=team)
        team_dependencies.append({
            'team': team,
            'upstream': upstream,
            'downstream': downstream,
        })

    return render(request, 'organisation_feature/department_detail.html', {
        'department': department,
        'teams': teams,
        'team_types': team_types,
        'team_dependencies': team_dependencies,
    })