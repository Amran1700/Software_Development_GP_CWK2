""" Marc Ferandes w2081572 """
from django.contrib import admin

from .models import (
    TeamType, Skill, Role, Team, TeamMember,
    TeamRepository, TeamSkill, UserRole,
    UpstreamDependency, DownstreamDependency
)

@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'category')
    search_fields = ('skill_name',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'category', 'is_active')


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1


class TeamSkillInline(admin.TabularInline):
    model = TeamSkill
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'department', 'manager', 'team_size', 'is_active')
    search_fields = ('team_name', 'department__dept_name')
    list_filter = ('is_active', 'department', 'team_type')
    inlines = [TeamMemberInline, TeamSkillInline]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role', 'team')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('team',)


@admin.register(TeamRepository)
class TeamRepositoryAdmin(admin.ModelAdmin):
    list_display = ('repo_name', 'repo_url', 'repo_type', 'team', 'is_active')
    list_filter = ('team', 'is_active')


@admin.register(UpstreamDependency)
class UpstreamDependencyAdmin(admin.ModelAdmin):
    list_display = ('team', 'upstream_team', 'description')


@admin.register(DownstreamDependency)
class DownstreamDependencyAdmin(admin.ModelAdmin):
    list_display = ('team', 'downstream_team', 'description')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'is_active')
# Register your models here.
