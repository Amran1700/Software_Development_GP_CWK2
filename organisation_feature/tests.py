from django.test import TestCase, Client
from django.urls import reverse
from .models import Department, TeamType
from teams_feature.models import Team


class OrgChartTests(TestCase):
    """Tests for the organisation chart view (TC1, TC2, TC3)."""

    def setUp(self):
        """Set up test data for org chart tests."""
        self.client = Client()
        self.dept = Department.objects.create(
            department_name='Engineering',
            specialisation='Backend Development',
            description='Infrastructure and backend services'
        )

    def test_org_chart_loads(self):
        """TC1 - Org chart page loads successfully."""
        response = self.client.get(reverse('org_chart'))
        self.assertEqual(response.status_code, 200)

    def test_org_chart_title(self):
        """TC1 - Org chart page contains correct title."""
        response = self.client.get(reverse('org_chart'))
        self.assertContains(response, 'Organisation Structure')

    def test_org_chart_shows_departments(self):
        """TC1 - Org chart shows department cards."""
        response = self.client.get(reverse('org_chart'))
        self.assertContains(response, 'Engineering')


class DepartmentListTests(TestCase):
    """Tests for the department list view (TC4, TC5, TC6)."""

    def setUp(self):
        """Set up test departments for list view tests."""
        self.client = Client()
        Department.objects.create(department_name='Engineering', specialisation='Backend Development')
        Department.objects.create(department_name='Design', specialisation='UX/UI')
        Department.objects.create(department_name='Product', specialisation='Product Management')
        Department.objects.create(department_name='Marketing', specialisation='Digital Marketing')

    def test_department_list_loads(self):
        """TC4 - Department list page loads successfully."""
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)

    def test_department_list_shows_all(self):
        """TC4 - All 4 departments are shown."""
        response = self.client.get(reverse('department_list'))
        self.assertContains(response, 'Engineering')
        self.assertContains(response, 'Design')
        self.assertContains(response, 'Product')
        self.assertContains(response, 'Marketing')

    def test_department_search_by_name(self):
        """TC5 - Search by department name returns correct result."""
        response = self.client.get(reverse('department_list'), {'q': 'Engineering'})
        self.assertContains(response, 'Engineering')
        self.assertNotContains(response, 'Digital Marketing')

    def test_department_search_by_specialisation(self):
        """TC5 - Search by specialisation returns correct result."""
        response = self.client.get(reverse('department_list'), {'q': 'UX/UI'})
        self.assertContains(response, 'Design')

    def test_department_search_no_results(self):
        """TC5 - Search with no match shows empty state."""
        response = self.client.get(reverse('department_list'), {'q': 'xyz999'})
        self.assertContains(response, 'No departments found')

    def test_department_filter_by_name(self):
        """TC6 - Filter chip by department name works."""
        response = self.client.get(reverse('department_list'), {'filter': 'Engineering'})
        self.assertContains(response, 'Engineering')
        self.assertNotContains(response, 'Digital Marketing')

    def test_department_filter_all(self):
        """TC6 - No filter shows all departments."""
        response = self.client.get(reverse('department_list'))
        self.assertContains(response, 'Engineering')
        self.assertContains(response, 'Marketing')


class DepartmentDetailTests(TestCase):
    """Tests for the department detail view (TC7, TC8, TC9)."""

    def setUp(self):
        """Set up test department and teams for detail view tests."""
        self.client = Client()
        self.dept = Department.objects.create(
            department_name='Engineering',
            specialisation='Backend Development',
            description='Infrastructure and backend services'
        )

    def test_department_detail_loads(self):
        """TC7 - Department detail page loads successfully."""
        response = self.client.get(reverse('department_detail', args=[self.dept.id]))
        self.assertEqual(response.status_code, 200)

    def test_department_detail_shows_name(self):
        """TC7 - Department detail shows correct department name."""
        response = self.client.get(reverse('department_detail', args=[self.dept.id]))
        self.assertContains(response, 'Engineering')

    def test_department_detail_404(self):
        """TC7 - Non-existent department returns 404."""
        response = self.client.get(reverse('department_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_department_detail_shows_specialisation(self):
        """TC9 - Department detail shows specialisation."""
        response = self.client.get(reverse('department_detail', args=[self.dept.id]))
        self.assertContains(response, 'Backend Development')