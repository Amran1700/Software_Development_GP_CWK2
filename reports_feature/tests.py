# reports/tests.py
# Author: Student 5 – Reports Module

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportsDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_loads(self):
        """Dashboard returns 200 for logged-in user."""
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_anonymous(self):
        """Unauthenticated user is redirected to login."""
        self.client.logout()
        response = self.client.get(reverse('reports:dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_dashboard_contains_report_cards(self):
        """Dashboard template contains the three report card titles."""
        response = self.client.get(reverse('reports:dashboard'))
        self.assertContains(response, 'Teams by Department')
        self.assertContains(response, 'Teams Without Managers')
        self.assertContains(response, 'Summary Statistics')


class ReportPreviewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser2', password='testpass123'
        )
        self.client.login(username='testuser2', password='testpass123')

    def test_preview_teams_by_dept(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams_by_department'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teams by Department')

    def test_preview_no_managers(self):
        response = self.client.get(
            reverse('reports:preview', args=['teams_without_managers'])
        )
        self.assertEqual(response.status_code, 200)

    def test_preview_summary(self):
        response = self.client.get(
            reverse('reports:preview', args=['summary'])
        )
        self.assertEqual(response.status_code, 200)

    def test_preview_unknown_type_shows_error(self):
        response = self.client.get(
            reverse('reports:preview', args=['nonsense'])
        )
        self.assertContains(response, 'Unknown report type')


class ReportGenerateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser3', password='testpass123'
        )
        self.client.login(username='testuser3', password='testpass123')

    def test_generate_pdf_summary(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'summary',
            'format': 'pdf',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_generate_excel_summary(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'summary',
            'format': 'excel',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])

    def test_generate_pdf_teams_by_dept(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'teams_by_department',
            'format': 'pdf',
        })
        self.assertEqual(response.status_code, 200)

    def test_generate_excel_no_managers(self):
        response = self.client.post(reverse('reports:generate'), {
            'report_type': 'teams_without_managers',
            'format': 'excel',
        })
        self.assertEqual(response.status_code, 200)

    def test_get_request_not_allowed(self):
        response = self.client.get(reverse('reports:generate'))
        self.assertEqual(response.status_code, 405)
