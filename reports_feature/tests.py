# reports_feature/tests.py
# Author: Sadana Suresh w21162895
# Full test suite for the Reports module, TC01 to TC24.
# Covers dashboard, preview, PDF/Excel downloads, auth redirects, edge cases.
# Run with: python manage.py test reports_feature

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from organisation_feature.models import Department
from teams_feature.models import Team

User = get_user_model()


# shared setUp for most tests - creates a user, two departments, one managed team, one without a manager
class ReportsBaseTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        self.dept_alpha = Department.objects.create(department_name='Alpha Engineering')
        self.dept_beta  = Department.objects.create(department_name='Beta Systems')

        self.team_managed = Team.objects.create(
            team_name='Phoenix Team',
            department=self.dept_alpha,
            manager=self.user,
        )

        # no manager on this one - used by the no-manager report tests
        self.team_no_mgr = Team.objects.create(
            team_name='Orphan Team',
            department=self.dept_beta,
            manager=None,
        )


# TC01
class TC01_DashboardLoadsForLoggedInUser(ReportsBaseTest):

    def test_dashboard_loads(self):
        response = self.client.get(reverse('reports:reports_dashboard'))
        self.assertEqual(response.status_code, 200)


# TC03
class TC03_DashboardShowsAllThreeCards(ReportsBaseTest):

    def test_dashboard_contains_report_cards(self):
        response = self.client.get(reverse('reports:reports_dashboard'))
        self.assertContains(response, 'Teams Summary Report')
        self.assertContains(response, 'All Teams Report')
        self.assertContains(response, 'Teams Without Managers')


# TC04
class TC04_PreviewTeamsByDept(ReportsBaseTest):

    def test_preview_teams_by_dept(self):
        response = self.client.get(reverse('reports:preview', args=['teams']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teams Report')


# TC05
class TC05_PreviewAllTeams(ReportsBaseTest):

    def test_preview_all_teams(self):
        response = self.client.get(reverse('reports:preview', args=['all-teams']))
        self.assertEqual(response.status_code, 200)
        # Phoenix Team was created in setUp so should show up here
        self.assertContains(response, 'Phoenix Team')


# TC06
class TC06_PreviewShowsStats(ReportsBaseTest):

    def test_preview_shows_stats(self):
        response = self.client.get(reverse('reports:preview', args=['teams']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Teams')
        self.assertContains(response, 'Total Departments')


# TC09
class TC09_PDFTeams(ReportsBaseTest):

    def test_download_pdf_teams(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'pdf']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC10
class TC10_ExcelTeams(ReportsBaseTest):

    def test_download_excel_teams(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'excel']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])
        self.assertIn('.xlsx', response['Content-Disposition'])


# TC11
class TC11_PDFAllTeams(ReportsBaseTest):

    def test_download_pdf_all_teams(self):
        response = self.client.get(reverse('reports:download_report', args=['all-teams', 'pdf']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC12
class TC12_ExcelAllTeams(ReportsBaseTest):

    def test_download_excel_all_teams(self):
        response = self.client.get(reverse('reports:download_report', args=['all-teams', 'excel']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])
        self.assertIn('.xlsx', response['Content-Disposition'])


# TC13
class TC13_PDFFilename(ReportsBaseTest):

    def test_pdf_filename(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'pdf']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('teams_report.pdf', response['Content-Disposition'])


# TC14
class TC14_ExcelFilename(ReportsBaseTest):

    def test_excel_filename(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'excel']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('teams_report.xlsx', response['Content-Disposition'])


# TC23
class TC23_PreviewNoManager(ReportsBaseTest):

    def test_preview_no_manager(self):
        response = self.client.get(reverse('reports:preview', args=['no-manager']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orphan Team')      # unmanaged team should appear
        self.assertNotContains(response, 'Phoenix Team')  # managed team should not appear


# TC24
class TC24_PDFNoManager(ReportsBaseTest):

    def test_pdf_no_manager(self):
        response = self.client.get(reverse('reports:download_report', args=['no-manager', 'pdf']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC02
class TC02_DashboardRedirectsAnonymous(ReportsBaseTest):

    def test_dashboard_redirects_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('reports:reports_dashboard'))
        self.assertNotEqual(response.status_code, 200)


# TC07
class TC07_PreviewUnknownTypeStillLoads(ReportsBaseTest):

    def test_preview_unknown_type(self):
        # unknown slug should return 200 with no data, not crash
        response = self.client.get(reverse('reports:preview', args=['nonsense_report']))
        self.assertEqual(response.status_code, 200)


# TC08
class TC08_PreviewEmptyData(TestCase):

    def setUp(self):
        # clean database, no teams or departments
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser', password='pass')
        self.client.login(username='emptyuser', password='pass')

    def test_preview_empty_teams(self):
        response = self.client.get(reverse('reports:preview', args=['teams']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data available')


# TC15
class TC15_InvalidFormatReturns400(ReportsBaseTest):

    def test_invalid_format(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'csv']))
        self.assertEqual(response.status_code, 400)


# TC16
class TC16_AllTeamsHaveManagers(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='mgr_user', password='pass')
        self.client.login(username='mgr_user', password='pass')
        dept = Department.objects.create(department_name='Fully Staffed Dept')
        Team.objects.create(team_name='Well Managed Team', department=dept, manager=self.user)

    def test_all_teams_preview_loads(self):
        response = self.client.get(reverse('reports:preview', args=['all-teams']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Well Managed Team')


# TC17
class TC17_PDFEmptyDatabase(TestCase):

    def setUp(self):
        # empty database - PDF should still generate without crashing
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser2', password='pass')
        self.client.login(username='emptyuser2', password='pass')

    def test_pdf_empty_database(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'pdf']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


# TC18
class TC18_UnknownReportTypePDF(ReportsBaseTest):

    def test_unknown_type_pdf(self):
        response = self.client.get(reverse('reports:download_report', args=['nonsense_report', 'pdf']))
        self.assertEqual(response.status_code, 400)


# TC19
class TC19_PreviewRequiresLogin(TestCase):

    def setUp(self):
        self.client = Client()  # not logged in

    def test_preview_redirects_anonymous(self):
        response = self.client.get(reverse('reports:preview', args=['teams']))
        self.assertNotEqual(response.status_code, 200)


# TC20
class TC20_DownloadRequiresLogin(TestCase):

    def setUp(self):
        self.client = Client()  # not logged in

    def test_download_redirects_anonymous(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'pdf']))
        self.assertNotEqual(response.status_code, 200)


# TC21
class TC21_UnsupportedFormat(ReportsBaseTest):

    def test_unsupported_format(self):
        response = self.client.get(reverse('reports:download_report', args=['teams', 'xml']))
        self.assertEqual(response.status_code, 400)


# TC22
class TC22_PDFAllTeamsEmptyData(TestCase):

    def setUp(self):
        # empty database - PDF for all-teams should still work
        self.client = Client()
        self.user = User.objects.create_user(username='emptyuser3', password='pass')
        self.client.login(username='emptyuser3', password='pass')

    def test_pdf_all_teams_empty(self):
        response = self.client.get(reverse('reports:download_report', args=['all-teams', 'pdf']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
