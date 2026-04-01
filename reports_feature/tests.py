# reports_feature/tests.py
# Author: Student 5 – Reports Module
# Week 3: Full test suite – TC01 to TC16
# Run with: python manage.py test reports_feature

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from organisation_feature.models import Department
from teams_feature.models import Team

User = get_user_model()


class ReportsBaseTest(TestCase):
    """Creates a logged-in user, two departments, and sample teams."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.dept_alpha = Department.objects.create(department_name='Alpha Engineering')
        self.dept_beta  = Department.objects.create(department_name='Beta Systems')

        self.team_managed = Team.objects.create(
            team_name='Phoenix Team',
            department=self.dept_alpha,
            manager=self.user,
        )

        self.team_no_mgr = Team.objects.create(
            team_name='Orphan Team',
            department=self.dept_beta,
            manager=None,
        )


# TC01
class TC01_DashboardLoadsForLoggedInUser(ReportsBaseTest):
    """TC01 – Dashboard returns HTTP 200 for authenticated user."""

    def test_dashboard_loads(self):
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)


# TC02
class TC02_DashboardRedirectsAnonymous(ReportsBaseTest):
    """TC02 – Unauthenticated user is redirected away from dashboard."""

    def test_dashboard_redirects_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('reports:dashboard'))
        self.assertNotEqual(response.status_code, 200)


# TC03
class TC03_DashboardShowsAllThreeCards(ReportsBaseTest):
    """TC03 – Dashboard page contains all three report card titles."""

    def test_dashboard_contains_report_cards(self):
        response = self.client.get(reverse('reports:dashboard'))
        self.assertContains(response, 'Teams by Department')
        self.assertContains(response, 'Teams Without Managers')
        self.assertContains(response, 'Summary Statistics')


# TC04
class TC04_PreviewTeamsByDept(ReportsBaseTest):
    """TC04 – Teams by Department preview loads and shows department name."""

    def test_preview_teams_by_dept(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams_by_department'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teams by Department')
        self.assertContains(response, 'Alpha Engineering')


# TC05
class TC05_PreviewTeamsWithoutManagers(ReportsBaseTest):
    """TC05 – Teams Without Managers preview loads and shows unmanaged team."""

    def test_preview_no_managers(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams_without_managers'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orphan Team')


# TC06
class TC06_PreviewSummary(ReportsBaseTest):
    """TC06 – Summary Statistics preview loads and shows metric rows."""

    def test_preview_summary(self):
        response = self.client.get(
            reverse('reports:preview', args=['summary'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Teams')
        self.assertContains(response, 'Total Departments')


# TC07
class TC07_PreviewUnknownTypeShowsError(ReportsBaseTest):
    """TC07 – An unrecognised report_type renders an error message, not a crash."""

    def test_preview_unknown_type_shows_error(self):
        response = self.client.get(
            reverse('reports:preview', args=['nonsense_report'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unknown report type')


# TC08
class TC08_PreviewEmptyData(TestCase):
    """TC08 – Preview with no teams/departments shows 'No data found' message."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser', password='pass')
        self.client.login(username='emptyuser', password='pass')

    def test_preview_empty_teams_by_dept(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams_by_department'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data found')


# TC09
class TC09_PDFTeamsByDept(ReportsBaseTest):
    """TC09 – PDF download for Teams by Department returns correct content-type."""

    def test_generate_pdf_teams_by_dept(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'teams_by_department',
            'format': 'pdf',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('teams_by_department.pdf', response['Content-Disposition'])


# TC10
class TC10_ExcelTeamsByDept(ReportsBaseTest):
    """TC10 – Excel download for Teams by Department returns correct content-type."""

    def test_generate_excel_teams_by_dept(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'teams_by_department',
            'format': 'excel',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])
        self.assertIn('teams_by_department.xlsx', response['Content-Disposition'])


# TC11
class TC11_PDFNoManagers(ReportsBaseTest):
    """TC11 – PDF download for Teams Without Managers returns correct content-type."""

    def test_generate_pdf_no_managers(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'teams_without_managers',
            'format': 'pdf',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC12
class TC12_ExcelNoManagers(ReportsBaseTest):
    """TC12 – Excel download for Teams Without Managers returns correct content-type."""

    def test_generate_excel_no_managers(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'teams_without_managers',
            'format': 'excel',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])


# TC13
class TC13_PDFSummary(ReportsBaseTest):
    """TC13 – PDF download for Summary Statistics returns correct content-type."""

    def test_generate_pdf_summary(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'summary',
            'format': 'pdf',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('summary_report.pdf', response['Content-Disposition'])


# TC14
class TC14_ExcelSummary(ReportsBaseTest):
    """TC14 – Excel download for Summary Statistics returns correct content-type."""

    def test_generate_excel_summary(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'summary',
            'format': 'excel',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])
        self.assertIn('summary_report.xlsx', response['Content-Disposition'])


# TC15
class TC15_GETRequestNotAllowed(ReportsBaseTest):
    """TC15 – GET to generate endpoint returns 405 Method Not Allowed."""

    def test_get_request_not_allowed(self):
        response = self.client.get(reverse('reports:generate'))
        self.assertEqual(response.status_code, 405)


# TC16
class TC16_AllTeamsHaveManagers(TestCase):
    """TC16 – Teams Without Managers report shows friendly message when all teams are managed."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='mgr_user', password='pass')
        self.client.login(username='mgr_user', password='pass')

        dept = Department.objects.create(department_name='Fully Staffed Dept')
        Team.objects.create(
            team_name='Well Managed Team',
            department=dept,
            manager=self.user,
        )

    def test_no_manager_report_empty_state(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams_without_managers'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data found')
