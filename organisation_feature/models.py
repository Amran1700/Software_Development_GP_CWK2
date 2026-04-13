"""Name: Ehsaan Zakriya 
ID: W2115831 """

from django.db import models


# Stores the category/type of a team, such as Frontend or Backend
class TeamType(models.Model):
    """
    Represents a category or type that a team can belong to.
    Examples: Frontend, Backend, DevOps, Data.
    Used to classify teams across all departments.
    """

    # Name of the team type
    type_name = models.CharField(max_length=100)

    # Optional longer description of the team type
    description = models.TextField(blank=True)

    # Return the team type name when the object is displayed
    def __str__(self):
        return self.type_name

    # Sort team types alphabetically by name by default
    class Meta:
        ordering = ['type_name']


# Stores each department in the organisation
class Department(models.Model):
    """
    Represents a department within the Sky Engineering organisation.
    Each department contains multiple teams and has a specialisation area.
    Links to teams via the Team model in teams_feature (FK on Team side).
    """

    # Full department name
    department_name = models.CharField(max_length=150)

    # Optional area of expertise for the department
    specialisation = models.CharField(max_length=200, blank=True)

    # Optional longer description of the department
    description = models.TextField(blank=True)

    # Return the department name when the object is displayed
    def __str__(self):
        return self.department_name

    # Sort departments alphabetically by name by default
    class Meta:
        ordering = ['department_name']