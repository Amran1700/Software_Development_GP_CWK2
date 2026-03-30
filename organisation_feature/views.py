from django.shortcuts import render
from .models import Department, TeamType


def org_chart(request):
    """Displays the organisation chart showing all departments and their teams."""
    departments = Department.objects.all()
    return render(request, 'organisation_feature/org_chart.html', {'departments': departments})


def department_list(request):
    """Displays a list of all departments with optional search."""
    query = request.GET.get('q', '')
    if query:
        departments = Department.objects.filter(
            department_name__icontains=query
        ) | Department.objects.filter(
            specialisation__icontains=query
        )
    else:
        departments = Department.objects.all()
    return render(request, 'organisation_feature/department_list.html', {
        'departments': departments,
        'query': query,
    })

def department_detail(request, department_id):
    """Displays the detail page for a single department."""
    department = Department.objects.get(id=department_id)
    team_types = TeamType.objects.all()
    return render(request, 'organisation_feature/department_detail.html', {
        'department': department,
        'team_types': team_types,
    })
