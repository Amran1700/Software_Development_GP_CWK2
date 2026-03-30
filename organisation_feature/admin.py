from django.contrib import admin
from .models import Department, TeamType

# Register your models here.

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    #admin config for departmen model
    list_display = ['department_name', 'specialisation']
    search_fields= ['department_name', 'specialisation']

@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    #Admin config for teamType model
    list_display = ['type_name', 'description']
    search_fields = ['type_name']
    

