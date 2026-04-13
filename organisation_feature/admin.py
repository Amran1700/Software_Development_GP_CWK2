"""Name: Ehsaan Zakriya 
ID: W2115831 """

from django.contrib import admin
from .models import Department, TeamType


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Department model.
    Displays department name and specialisation in the list view.
    Allows searching by department name and specialisation.
    """
    list_display = ['department_name', 'specialisation']
    search_fields = ['department_name', 'specialisation']
    list_filter = ['specialisation']


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TeamType model.
    Displays type name and description in the list view.
    Allows searching by type name.
    """
    list_display = ['type_name', 'description']
    search_fields = ['type_name']