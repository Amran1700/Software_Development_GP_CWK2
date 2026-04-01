from django.db import models


class TeamType(models.Model):
    """
    Represents a category or type that a team can belong to.
    Examples: Frontend, Backend, DevOps, Data.
    Used to classify teams across all departments.
    """

    type_name = models.CharField(max_length=100)  # Name of the team type
    description = models.TextField(blank=True)  # Optional description

    def __str__(self):
        return self.type_name

    class Meta:
        ordering = ['type_name']  # Order alphabetically by type name


class Department(models.Model):
    """
    Represents a department within the Sky Engineering organisation.
    Each department contains multiple teams and has a specialisation area.
    Links to teams via the Team model in teams_feature (FK on Team side).
    """

    department_name = models.CharField(max_length=150)  # Full department name
    specialisation = models.CharField(max_length=200, blank=True)  # Area of expertise
    description = models.TextField(blank=True)  # Detailed description of department

    def __str__(self):
        return self.department_name

    class Meta:
        ordering = ['department_name']  # Order alphabetically by department name