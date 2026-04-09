from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Message


class MessagesFeatureTests(TestCase):
    """Comprehensive tests for the Messages Feature."""

    def setUp(self):
        """Create users, client, and sample messages for tests."""

        # Create users
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass1234')
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')

        self.client = Client()

        # Create a sent message (user1 → user2)
        self.sent_msg = Message.objects.create(sender=self.user1, subject='Sent test', body='Sent body', status='sent')
        self.sent_msg.receiver.set([self.user2])

        # Create an unread message (user2 → user1)
        self.unread_msg = Message.objects.create(sender=self.user2, subject='Hello', body='Unread', status='sent')
        self.unread_msg.receiver.set([self.user1])

        # Create a draft message
        self.draft_msg = Message.objects.create(sender=self.user1, subject='Draft', body='Draft content', status='draft')
        self.draft_msg.receiver.set([self.user2])

    # ---------- Helper methods ----------
    def login_user1(self):
        """Login as user1."""
        self.client.login(username='user1', password='pass1234')

    def login_admin(self):
        """Login as admin."""
        self.client.login(username='admin', password='admin123')

    # ---------- TS1: Compose & Send Message ----------

    # TC1: Send message with all fields filled
    def test_send_message_all_fields(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],  # valid recipient
            'subject': 'Practice email',
            'body': 'Testing system',
            'status': 'sent'
        }, follow=True)

        # Expect redirect to sent page
        self.assertRedirects(response, reverse('sent'))

        # Check message was saved
        self.assertTrue(Message.objects.filter(subject='Practice email').exists())

    # TC2: Send message without a subject (allowed)
    def test_send_message_no_subject(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': '',  # empty subject
            'body': 'Body present',
            'status': 'sent'
        }, follow=True)

        # Still redirects (valid)
        self.assertRedirects(response, reverse('sent'))

        # Subject should be saved as empty
        msg = Message.objects.get(body='Body present')
        self.assertEqual(msg.subject, '')

    # TC3: Send message with extremely long subject/body
    def test_extremely_long_subject_body(self):
        self.login_user1()

        long_subject = 'x' * 255  # max subject length
        long_body = 'x' * 10000   # very large body

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': long_subject,
            'body': long_body,
            'status': 'sent'
        }, follow=True)

        # Should still work
        self.assertRedirects(response, reverse('sent'))

        # Check it was saved
        self.assertTrue(Message.objects.filter(subject=long_subject).exists())

    # TC4: Send message without recipient
    def test_send_message_no_recipient(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [],  # no recipient
            'subject': 'Hello',
            'body': 'Valid body',
            'status': 'sent'
        })
        # Form should re-render (error)
        self.assertEqual(response.status_code, 200)
        # Error message shown
        self.assertContains(response, "Recipient and message body are required")

    # TC5: Send message without body
    def test_send_message_no_body(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Hello',
            'body': '',  # empty body
            'status': 'sent'
        })
        # Form re-render
        self.assertEqual(response.status_code, 200)
        # Error message
        self.assertContains(response, "Recipient and message body are required")

    # ---------- TS2: Drafts ----------

    # TC6: Save message as draft
    def test_save_draft(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [],
            'subject': '',
            'body': '',
            'status': 'draft'
        }, follow=True)
        # Redirect to drafts page
        self.assertRedirects(response, reverse('drafts'))


    # TC7: Edit existing draft
    def test_edit_draft(self):
        self.login_user1()

        draft = Message.objects.create(sender=self.user1, subject='Old', body='Old draft', status='draft')
        draft.receiver.set([self.user2])

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Updated',
            'body': 'Updated draft',
            'status': 'draft'
        }, follow=True)

        # Redirect after edit
        self.assertRedirects(response, reverse('drafts'))

    # TC8: Delete draft
    def test_delete_draft(self):
        self.login_user1()

        draft = Message.objects.create(sender=self.user1, subject='Delete', body='Draft', status='draft')
        draft.receiver.set([self.user2])

        response = self.client.get(reverse('delete_message', args=[draft.id]), follow=True)

        # Redirect to inbox
        self.assertRedirects(response, reverse('inbox'))

    # ---------- TS3: Inbox ----------

    # TC9: Display unread messages
    def test_inbox_unread_messages(self):
        self.login_user1()

        response = self.client.get(reverse('inbox'))

        # Message should appear
        self.assertContains(response, 'Hello')

    # TC10: Mark message as read when opened
    def test_inbox_mark_read(self):
        self.login_user1()

        msg = Message.objects.create(sender=self.user2, subject='Read test', body='Read', status='sent')
        msg.receiver.set([self.user1])

        # Open message detail
        self.client.get(reverse('message_detail', args=[msg.id]))

        msg.refresh_from_db()

        # Should now be marked as read
        self.assertTrue(msg.read_status)

    # ---------- TS4: Sent ----------

    # TC11: View sent messages
    def test_view_sent_messages(self):
        self.login_user1()

        response = self.client.get(reverse('sent'))

        self.assertContains(response, 'Sent test')

    # ---------- TS5: Delete ----------

    # TC12: Delete inbox message
    def test_delete_inbox_message(self):
        self.login_user1()

        msg = Message.objects.create(sender=self.user2, subject='Delete', body='Test', status='sent')
        msg.receiver.set([self.user1])

        self.client.get(reverse('delete_message', args=[msg.id]))

        msg.refresh_from_db()

        # Should be marked deleted
        self.assertEqual(msg.status, 'deleted')

    # ---------- Negative Tests ----------

    # TC-N1: Invalid recipient ID
    def test_invalid_recipient_id(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [9999],  # invalid ID
            'subject': 'Invalid',
            'body': 'Test',
            'status': 'sent'
        }, follow=True)

        self.assertRedirects(response, reverse('sent'))

    # TC-N2: Whitespace body
    def test_whitespace_body(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Whitespace',
            'body': '   ',  # spaces only
            'status': 'sent'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipient and message body are required")

    # TC-N3: Access another user's message
    def test_access_other_user_message(self):
        self.login_user1()

        msg = Message.objects.create(sender=self.user2, subject='Private', body='Secret', status='sent')
        msg.receiver.set([])  # user1 not allowed

        response = self.client.get(reverse('message_detail', args=[msg.id]), follow=True)

        # Should redirect away
        self.assertRedirects(response, reverse('inbox'))

    # TC-N4: Delete not allowed
    def test_delete_not_allowed(self):
        self.login_user1()

        msg = Message.objects.create(sender=self.user2, subject='Protected', body='Test', status='sent')
        msg.receiver.set([])

        self.client.get(reverse('delete_message', args=[msg.id]))

        msg.refresh_from_db()

        # Should remain unchanged
        self.assertEqual(msg.status, 'sent')

    # TC-N5: Non-existent message
    def test_mark_nonexistent_message(self):
        self.login_user1()

        response = self.client.get(reverse('message_detail', args=[9999]))

        self.assertEqual(response.status_code, 404)

    # TC-N6: No recipient AND no body
    def test_compose_no_recipient_no_body(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [],
            'subject': 'Empty',
            'body': '',
            'status': 'sent'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipient and message body are required")

    # ---------- Admin ----------

    # TC-N7: Admin login works
    def test_admin_can_login(self):
        self.login_admin()

        response = self.client.get(reverse('inbox'))

        self.assertEqual(response.status_code, 200)