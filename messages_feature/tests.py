# Author: Amran Mohammed id:w2066724

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Message
class MessagesFeatureTests(TestCase):

    def setUp(self):
        #this setup runs before each test method

        # Create normal users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass1234'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass1234'
        )

        # Create admin user
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )


        self.client = Client()

        #sent message
        self.sent_msg = Message.objects.create(
            sender=self.user1,
            subject='Sent test',
            body='Sent body',
            status='sent'
        )
        self.sent_msg.receiver.set([self.user2])

        
        self.unread_msg = Message.objects.create(
            sender=self.user2,
            subject='Hello',
            body='Unread',
            status='sent'
        )
        self.unread_msg.receiver.set([self.user1])

        # Draft message
        self.draft_msg = Message.objects.create(
            sender=self.user1,
            subject='Draft',
            body='Draft content',
            status='draft'
        )
        self.draft_msg.receiver.set([self.user2])

 
    def login_user1(self):
        """Logs in user1 for testing authenticated routes."""
        self.client.login(username='user1', password='pass1234')

    def login_admin(self):
        """Logs in admin user for admin-level testing."""
        self.client.login(username='admin', password='admin123')


    # TS1: COMPOSE & SEND MESSAGE TESTS

    # TC1: Valid message sent with all fields
    def test_send_message_all_fields(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Practice email',
            'body': 'Testing system',
            'status': 'sent'
        }, follow=True)

        # should redirect to sent page after successful send
        self.assertRedirects(response, reverse('sent'))

        # this verifies message exists in the database
        self.assertTrue(
            Message.objects.filter(subject='Practice email').exists()
        )


    # TC2: Send message without subject (allowed case)
    def test_send_message_no_subject(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': '',
            'body': 'Body present',
            'status': 'sent'
        }, follow=True)

        self.assertRedirects(response, reverse('sent'))

        msg = Message.objects.get(body='Body present')
        self.assertEqual(msg.subject, '')


    # TC3: Very large subject and body 
    def test_extremely_long_subject_body(self):
        self.login_user1()

        long_subject = 'x' * 255
        long_body = 'x' * 10000

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': long_subject,
            'body': long_body,
            'status': 'sent'
        }, follow=True)

        self.assertRedirects(response, reverse('sent'))

        self.assertTrue(
            Message.objects.filter(subject=long_subject).exists()
        )


    # TC4: Missing recipient 
    def test_send_message_no_recipient(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [],
            'subject': 'Hello',
            'body': 'Valid body',
            'status': 'sent'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipient and message body are required")


    # TC5: Missing body (validation test)
    def test_send_message_no_body(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Hello',
            'body': '',
            'status': 'sent'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipient and message body are required")

    # TS2: DRAFT TESTS

    # TC6: Save message as draft
    def test_save_draft(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [],
            'subject': '',
            'body': '',
            'status': 'draft'
        }, follow=True)

        self.assertRedirects(response, reverse('drafts'))


    # TC7: Edit draft (simulated via new save)
    def test_edit_draft(self):
        self.login_user1()

        draft = Message.objects.create(
            sender=self.user1,
            subject='Old',
            body='Old draft',
            status='draft'
        )
        draft.receiver.set([self.user2])

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Updated',
            'body': 'Updated draft',
            'status': 'draft'
        }, follow=True)

        self.assertRedirects(response, reverse('drafts'))


    # TC8: Delete draft (soft delete system)
    def test_delete_draft(self):
        self.login_user1()

        draft = Message.objects.create(
            sender=self.user1,
            subject='Delete',
            body='Draft',
            status='draft'
        )
        draft.receiver.set([self.user2])

        self.client.get(reverse('delete_message', args=[draft.id]), follow=True)

        draft.refresh_from_db()

        self.assertEqual(draft.status, 'deleted')

    # TS3: INBOX TESTS

    # TC9: Inbox shows unread messages
    def test_inbox_unread_messages(self):
        self.login_user1()

        response = self.client.get(reverse('inbox'))

        self.assertContains(response, 'Hello')


    # TC10: Message marked as read when opened
    def test_inbox_mark_read(self):
        self.login_user1()

        msg = Message.objects.create(
            sender=self.user2,
            subject='Read test',
            body='Read',
            status='sent'
        )
        msg.receiver.set([self.user1])

        self.client.get(reverse('message_detail', args=[msg.id]))

        msg.refresh_from_db()

        self.assertTrue(msg.read_status)


    # TS4: SENT TESTS

    # TC11: Sent messages visible
    def test_view_sent_messages(self):
        self.login_user1()

        response = self.client.get(reverse('sent'))

        self.assertContains(response, 'Sent test')


    # TS5: DELETE TESTS

    # TC12: Delete inbox message (soft delete)
    def test_delete_inbox_message(self):
        self.login_user1()

        msg = Message.objects.create(
            sender=self.user2,
            subject='Delete',
            body='Test',
            status='sent'
        )
        msg.receiver.set([self.user1])

        self.client.get(reverse('delete_message', args=[msg.id]))

        msg.refresh_from_db()

        self.assertEqual(msg.status, 'deleted')



    # NEGATIVE TESTS (CW1 EXTENSION)

    # These tests extend CW1 by adding:
    # - invalid inputs
    # - security checks
    # - unauthorized access handling

    # TC-N1: Invalid recipient ID
    def test_invalid_recipient_id(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [9999],
            'subject': 'Invalid',
            'body': 'Test',
            'status': 'sent'
        }, follow=True)

        self.assertRedirects(response, reverse('sent'))


    # TC-N2: Whitespace-only body
    def test_whitespace_body(self):
        self.login_user1()

        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Whitespace',
            'body': '   ',
            'status': 'sent'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipient and message body are required")


    # TC-N3: Unauthorized message access
    def test_access_other_user_message(self):
        self.login_user1()

        msg = Message.objects.create(
            sender=self.user2,
            subject='Private',
            body='Secret',
            status='sent'
        )
        msg.receiver.set([])

        response = self.client.get(
            reverse('message_detail', args=[msg.id]),
            follow=True
        )

        self.assertRedirects(response, reverse('inbox'))


    # TC-N4: Unauthorized delete attempt
    def test_delete_not_allowed(self):
        self.login_user1()

        msg = Message.objects.create(
            sender=self.user2,
            subject='Protected',
            body='Test',
            status='sent'
        )
        msg.receiver.set([])

        self.client.get(reverse('delete_message', args=[msg.id]))

        msg.refresh_from_db()

        self.assertEqual(msg.status, 'sent')


    # TC-N5: Non-existent message (404 test)
    def test_mark_nonexistent_message(self):
        self.login_user1()

        response = self.client.get(reverse('message_detail', args=[9999]))

        self.assertEqual(response.status_code, 404)


    # TC-N6: Empty compose submission
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


    # ADMIN TESTS

    # TC-N7: Admin login access
    def test_admin_can_login(self):
        self.login_admin()

        response = self.client.get(reverse('inbox'))

        self.assertEqual(response.status_code, 200)