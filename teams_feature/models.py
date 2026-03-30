from django.db import models
from django.contrib.auth.models import User
from organisation_feature.models import Department

class TeamType(models.Model):
    type_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.type_name


class Skill(models.Model):
    skill_name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.skill_name


class Role(models.Model):
    role_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.role_name


class Team(models.Model):
    team_name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, 
        related_name='teams'
    )
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='managed_teams'
    )
    team_type = models.ForeignKey(
        TeamType, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='teams'
    )
    description = models.TextField(blank=True)
    purpose = models.TextField(blank=True)
    team_size = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.team_name


class TeamMember(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    role = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, 
        related_name='members'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TeamRepository(models.Model):
    repo_name = models.CharField(max_length=100)
    repo_url = models.URLField()
    repo_type = models.CharField(max_length=50, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, 
        related_name='repositories'
    )

    def __str__(self):
        return self.repo_name


# M:M Junction — Team <-> Skill
class TeamSkill(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='team_skills')
    proficiency_level = models.CharField(
        max_length=20, 
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        default='intermediate'
    )

    class Meta:
        unique_together = ('team', 'skill')  # Compound PK

    def __str__(self):
        return f"{self.team.team_name} — {self.skill.skill_name}"


# M:M Junction — User <-> Role
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='roles_assigned'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} — {self.role.role_name}"


# M:M Self-Referencing — Upstream Dependencies
class UpstreamDependency(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, 
        related_name='upstream_dependencies'
    )
    upstream_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, 
        related_name='downstream_dependents'
    )
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('team', 'upstream_team')

    def __str__(self):
        return f"{self.team.team_name} depends on {self.upstream_team.team_name}"


# M:M Self-Referencing — Downstream Dependencies
class DownstreamDependency(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, 
        related_name='down
        stream_dependencies'
    )
    downstream_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, 
        related_name='upstream_dependents'
    )
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('team', 'downstream_team')

    def __str__(self):
        return f"{self.downstream_team.team_name} depends on {self.team.team_name}"

# Create your models here.
