# reports_feature/tests.py
# Author: Student 5 – Sadana Suresh (w21162895)
# Module: 5COSC021W – Software Development Group Project CWK2
# Description: Full test suite for the Reports module – TC01 to TC22.
#              Covers dashboard, preview, PDF/Excel download, authentication,
#              edge cases, and negative/invalid input scenarios.
#              Run with: python manage.py test reports_feature

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from organisation_feature.models import Department
from teams_feature.models import Team

User = get_user_model()


# ── BASE TEST CLASS ───────────────────────────────────────────────────────────
# Shared setUp used by most test cases.
# Creates a logged-in user, two departments, and two teams (one managed, one not).

class ReportsBaseTest(TestCase):
    """Base test class – creates a logged-in user and sample data for all tests."""

    def setUp(self):
        # Create and log in a test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create two sample departments
        self.dept_alpha = Department.objects.create(department_name='Alpha Engineering')
        self.dept_beta  = Department.objects.create(department_name='Beta Systems')

        # Create one managed team and one unmanaged team
        self.team_managed = Team.objects.create(
            team_name='Phoenix Team',
            department=self.dept_alpha,
            manager=self.user,
        )

        self.team_no_mgr = Team.objects.create(
            team_name='Orphan Team',
            department=self.dept_beta,
            manager=None,  # No manager assigned – used to test no-manager report
        )


# ── POSITIVE TESTS ────────────────────────────────────────────────────────────
# These tests verify that the normal happy-path functionality works correctly.

# TC01
class TC01_DashboardLoadsForLoggedInUser(ReportsBaseTest):
    """TC01 – Dashboard returns HTTP 200 for authenticated user."""

    def test_dashboard_loads(self):
        response = self.client.get(reverse('reports:reports_dashboard'))
        self.assertEqual(response.status_code, 200)


# TC03
class TC03_DashboardShowsAllThreeCards(ReportsBaseTest):
    """TC03 – Dashboard page contains all three report card titles."""

    def test_dashboard_contains_report_cards(self):
        response = self.client.get(reverse('reports:reports_dashboard'))
        # Verify all three report card titles are present in the rendered HTML
        self.assertContains(response, 'Teams Summary Report')
        self.assertContains(response, 'All Teams Report')
        self.assertContains(response, 'Teams Without Managers')


# TC04
class TC04_PreviewTeamsByDept(ReportsBaseTest):
    """TC04 – Teams report preview loads and shows report title."""

    def test_preview_teams_by_dept(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teams Report')


# TC05
class TC05_PreviewAllTeams(ReportsBaseTest):
    """TC05 – All Teams preview loads and shows a team name from sample data."""

    def test_preview_all_teams(self):
        response = self.client.get(
            reverse('reports:preview', args=['all-teams'])
        )
        self.assertEqual(response.status_code, 200)
        # Phoenix Team was created in setUp so should appear in the table
        self.assertContains(response, 'Phoenix Team')


# TC06
class TC06_PreviewShowsStats(ReportsBaseTest):
    """TC06 – Report preview shows stat card labels."""

    def test_preview_shows_stats(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams'])
        )
        self.assertEqual(response.status_code, 200)
        # Both stat card labels should appear in the rendered HTML
        self.assertContains(response, 'Total Teams')
        self.assertContains(response, 'Total Departments')


# TC09
class TC09_PDFTeams(ReportsBaseTest):
    """TC09 – PDF download for Teams report returns correct content-type."""

    def test_download_pdf_teams(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'pdf'])
        )
        self.assertEqual(response.status_code, 200)
        # Response must be a PDF file
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC10
class TC10_ExcelTeams(ReportsBaseTest):
    """TC10 – Excel download for Teams report returns correct content-type."""

    def test_download_excel_teams(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'excel'])
        )
        self.assertEqual(response.status_code, 200)
        # Response must be an Excel-compatible content type
        self.assertIn('spreadsheetml', response['Content-Type'])


# TC11
class TC11_PDFAllTeams(ReportsBaseTest):
    """TC11 – PDF download for All Teams returns correct content-type."""

    def test_download_pdf_all_teams(self):
        response = self.client.get(
            reverse('reports:download_report', args=['all-teams', 'pdf'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC12
class TC12_ExcelAllTeams(ReportsBaseTest):
    """TC12 – Excel download for All Teams returns correct content-type."""

    def test_download_excel_all_teams(self):
        response = self.client.get(
            reverse('reports:download_report', args=['all-teams', 'excel'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])


# TC13
class TC13_PDFFilename(ReportsBaseTest):
    """TC13 – PDF download has correct filename in Content-Disposition header."""

    def test_pdf_filename(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'pdf'])
        )
        self.assertEqual(response.status_code, 200)
        # Filename in Content-Disposition must match the report type
        self.assertIn('teams_report.pdf', response['Content-Disposition'])


# TC14
class TC14_ExcelFilename(ReportsBaseTest):
    """TC14 – Excel download has correct filename in Content-Disposition header."""

    def test_excel_filename(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'excel'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('teams_report', response['Content-Disposition'])


# ── NEGATIVE / EDGE CASE TESTS ────────────────────────────────────────────────
# These tests verify that the module handles invalid inputs and edge cases correctly
# without crashing, returning appropriate HTTP status codes and error messages.

# TC02
class TC02_DashboardRedirectsAnonymous(ReportsBaseTest):
    """TC02 – Unauthenticated user is redirected away from dashboard."""

    def test_dashboard_redirects_anonymous(self):
        # Log out to simulate an unauthenticated user
        self.client.logout()
        response = self.client.get(reverse('reports:reports_dashboard'))
        # @login_required should redirect – response must not be 200
        self.assertNotEqual(response.status_code, 200)


# TC07
class TC07_PreviewUnknownTypeStillLoads(ReportsBaseTest):
    """TC07 – Unknown report_type loads preview with no data rather than crashing."""

    def test_preview_unknown_type(self):
        response = self.client.get(
            reverse('reports:preview', args=['nonsense_report'])
        )
        # Should return 200 with empty data, not a 500 server error
        self.assertEqual(response.status_code, 200)


# TC08
class TC08_PreviewEmptyData(TestCase):
    """TC08 – Preview with no teams/departments shows empty state message."""

    def setUp(self):
        # Use a clean database with no teams or departments
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser', password='pass')
        self.client.login(username='emptyuser', password='pass')

    def test_preview_empty_teams(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams'])
        )
        self.assertEqual(response.status_code, 200)
        # Template should show the empty state message when no data exists
        self.assertContains(response, 'No data available')


# TC15
class TC15_InvalidFormatReturns400(ReportsBaseTest):
    """TC15 – Invalid download format (csv) returns 400 Bad Request."""

    def test_invalid_format(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'csv'])
        )
        # 'csv' is not a supported format – should return 400 not crash
        self.assertEqual(response.status_code, 400)


# TC16
class TC16_AllTeamsHaveManagers(TestCase):
    """TC16 – All teams preview loads correctly when all teams are managed."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='mgr_user', password='pass')
        self.client.login(username='mgr_user', password='pass')
        dept = Department.objects.create(department_name='Fully Staffed Dept')
        Team.objects.create(
            team_name='Well Managed Team',
            department=dept,
            manager=self.user,  # All teams have a manager
        )

    def test_all_teams_preview_loads(self):
        response = self.client.get(
            reverse('reports:preview', args=['all-teams'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Well Managed Team')


# TC17
class TC17_PDFEmptyDatabase(TestCase):
    """TC17 – PDF download with empty database does not crash, returns valid PDF."""

    def setUp(self):
        # Empty database – no teams or departments
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser2', password='pass')
        self.client.login(username='emptyuser2', password='pass')

    def test_pdf_empty_database(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'pdf'])
        )
        # PDF should still be generated even with no data rows
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC18
class TC18_UnknownReportTypePDF(ReportsBaseTest):
    """TC18 – PDF download with unknown report type returns 400 Bad Request."""

    def test_unknown_type_pdf(self):
        response = self.client.get(
            reverse('reports:download_report', args=['nonsense_report', 'pdf'])
        )
        # download_report checks meta is not empty – returns 400 for unknown types
        self.assertEqual(response.status_code, 400)


# TC19
class TC19_PreviewRequiresLogin(TestCase):
    """TC19 – Unauthenticated user cannot access preview page directly."""

    def setUp(self):
        self.client = Client()  # Not logged in

    def test_preview_redirects_anonymous(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams'])
        )
        # @login_required should redirect – response must not be 200
        self.assertNotEqual(response.status_code, 200)


# TC20
class TC20_DownloadRequiresLogin(TestCase):
    """TC20 – Unauthenticated user cannot access download endpoint."""

    def setUp(self):
        self.client = Client()  # Not logged in

    def test_download_redirects_anonymous(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'pdf'])
        )
        # @login_required should redirect – response must not be 200
        self.assertNotEqual(response.status_code, 200)


# TC21
class TC21_UnsupportedFormat(ReportsBaseTest):
    """TC21 – Unsupported export format (xml) returns 400 Bad Request."""

    def test_unsupported_format(self):
        response = self.client.get(
            reverse('reports:download_report', args=['teams', 'xml'])
        )
        # Only 'pdf' and 'excel' are supported – all others return 400
        self.assertEqual(response.status_code, 400)


# TC22
class TC22_PDFAllTeamsEmptyData(TestCase):
    """TC22 – PDF for All Teams with empty database downloads correctly without crashing."""

    def setUp(self):
        # Empty database – no teams or departments
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser3', password='pass')
        self.client.login(username='emptyuser3', password='pass')

    def test_pdf_all_teams_empty(self):
        response = self.client.get(
            reverse('reports:download_report', args=['all-teams', 'pdf'])
        )
        # PDF should still generate cleanly with no data rows
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')