""" Marc Ferandes w2081572 """
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Team, Skill
from organisation_feature.models import Department


@login_required
def team_list(request):
    """
    Displays a paginated list of all active teams with search and filter functionality.

    Supports three GET parameters for filtering:
        - q: filters teams by name (case-insensitive, partial match)
        - department: filters teams by department name
        - skill: filters teams by skill name via the TeamSkill junction table

    Passes the following context to team_list.html:
        - teams: paginated queryset of filtered active teams
        - query, department, skill: current filter values for repopulating the form
        - departments: all departments for the filter dropdown
        - skills: all skills for the skill filter
        - total_teams: total count of all active teams (unfiltered, for the stat counter)
        - total_members: total member count across all active teams (for the stat counter)
        - page_obj: pagination object for rendering page controls in the template
    """

    # Base queryset — only active teams, with related fields loaded in one query
    teams = Team.objects.filter(is_active=True).select_related('department', 'manager', 'team_type')

    # Read search and filter values from GET params — default to empty string if not provided
    query = request.GET.get('q', '')
    department = request.GET.get('department', '')
    skill = request.GET.get('skill', '')

    # Apply filters only if the user has provided a value
    if query:
        # icontains = case-insensitive partial match e.g. "prop" matches "Propulsion Systems"
        teams = teams.filter(team_name__icontains=query)
    if department:
        teams = teams.filter(department__department_name__icontains=department)
    if skill:
        # Filters across the TeamSkill junction table to match by skill name
        teams = teams.filter(team_skills__skill__skill_name__icontains=skill)

    # distinct() prevents duplicate rows when filtering across related tables (e.g. multiple skills)
    teams = teams.distinct()

    # Stats for the header counters — always based on ALL active teams, not the filtered set
    total_teams = Team.objects.filter(is_active=True).count()
    total_members = sum(
        t.members.count()
        for t in Team.objects.filter(is_active=True).prefetch_related('members')
    )

    # Pagination — show 10 teams per page
    paginator = Paginator(teams, 10)
    page_number = request.GET.get('page')  # get current page number from URL e.g. ?page=2
    page_obj = paginator.get_page(page_number)  # get_page handles invalid/missing page numbers safely

    # All departments for the filter dropdown
    departments = Department.objects.all().order_by('department_name')
    skills = Skill.objects.all()

    return render(request, 'teams_feature/team_list.html', {
        'teams': page_obj,          # paginated teams (replaces full queryset)
        'page_obj': page_obj,       # pagination object for rendering page controls
        'query': query,
        'department': department,
        'skill': skill,
        'skills': skills,
        'departments': departments,
        'total_teams': total_teams,
        'total_members': total_members,
    })


@login_required
def team_detail(request, team_id):
    """
    Displays the full detail page for a single team.

    Retrieves the team by its primary key (team_id from the URL).
    Returns a 404 page if the team does not exist.

    Uses select_related to load department, manager, and team_type in a single
    database query rather than triggering separate queries for each field.

    Passes the following context to team_detail.html:
        - team: the Team object
        - members: all TeamMember objects linked to this team
        - skills: all TeamSkill objects with related Skill names
        - repos: all active TeamRepository objects for this team
        - upstream: all UpstreamDependency objects (teams this team depends on)
        - downstream: all DownstreamDependency objects (teams that depend on this team)
    """

    # get_object_or_404 returns the team if it exists, otherwise returns a 404 response
    team = get_object_or_404(
        Team.objects.select_related('department', 'manager', 'team_type'),
        pk=team_id
    )

    # Fetch all related data — each uses select_related or filter to minimise queries
    members = team.members.all()
    skills = team.team_skills.select_related('skill').all()  # loads skill name in same query
    repos = team.repositories.filter(is_active=True)         # only show active repos
    upstream = team.upstream_dependencies.select_related('upstream_team').all()
    downstream = team.downstream_dependencies.select_related('downstream_team').all()

    return render(request, 'teams_feature/team_detail.html', {
        'team': team,
        'members': members,
        'skills': skills,
        'repos': repos,
        'upstream': upstream,
        'downstream': downstream,
    })