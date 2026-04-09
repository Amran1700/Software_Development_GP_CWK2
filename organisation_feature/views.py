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
    Displays a searchable list of all departments.
    Accepts a GET parameter 'q' for search queries.
    Filters by department name or specialisation if a query is provided.
    """
    query = request.GET.get('q', '')  # Get search query from URL params

    if query:
        # Filter departments by name or specialisation (case insensitive)
        departments = Department.objects.filter(
            department_name__icontains=query
        ) | Department.objects.filter(
            specialisation__icontains=query
        )
    else:
        # Return all departments if no search query
        departments = Department.objects.all()

    return render(request, 'organisation_feature/department_list.html', {
        'departments': departments,
        'query': query,
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