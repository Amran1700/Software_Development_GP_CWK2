from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Team, Skill
from organisation_feature.models import Department
 
 
@login_required
def team_list(request):
    teams = Team.objects.filter(is_active=True).select_related('department', 'manager', 'team_type')
 
    # Search and filter via GET params
    query = request.GET.get('q', '')
    department = request.GET.get('department', '')
    skill = request.GET.get('skill', '')
 
    if query:
        teams = teams.filter(team_name__icontains=query)
    if department:
        teams = teams.filter(department__department_name__icontains=department)
    if skill:
        teams = teams.filter(team_skills__skill__skill_name__icontains=skill)
 
    teams = teams.distinct()
 
    # Stats for the header
    total_teams = Team.objects.filter(is_active=True).count()
    total_members = sum(t.members.count() for t in Team.objects.filter(is_active=True).prefetch_related('members'))
 
    # All departments for the filter dropdown
    departments = Department.objects.all().order_by('department_name')
    skills = Skill.objects.all()
 
    return render(request, 'teams/team_list.html', {
        'teams': teams,
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
    team = get_object_or_404(
        Team.objects.select_related('department', 'manager', 'team_type'),
        pk=team_id
    )
    members = team.members.all()
    skills = team.team_skills.select_related('skill').all()
    repos = team.repositories.filter(is_active=True)
    upstream = team.upstream_dependencies.select_related('upstream_team').all()
    downstream = team.downstream_dependencies.select_related('downstream_team').all()
 
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'skills': skills,
        'repos': repos,
        'upstream': upstream,
        'downstream': downstream,
    })