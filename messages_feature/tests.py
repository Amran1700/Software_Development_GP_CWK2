from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Message

class MessagesFeatureTests(TestCase):
    def setUp(self):
        # Create regular users
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass1234')
        
        # Create admin user (for admin-specific tests)
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        
        self.client = Client()

    def login_user1(self):
        self.client.login(username='user1', password='pass1234')

    def login_admin(self):
        self.client.login(username='admin', password='admin123')

    # ---------- Compose & Send Message (TS1) ----------
    # TC1: Send Message with all fields filled
    def test_send_message_all_fields(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Practice email one',
            'body': 'This is a practice email to check if the system is working correctly.',
            'status': 'sent'
        }, follow=True)
        self.assertRedirects(response, reverse('sent'))
        self.assertTrue(Message.objects.filter(subject='Practice email one', sender=self.user1).exists())

    # TC2: Send message without a subject
    def test_send_message_no_subject(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': '',
            'body': 'Please review the following document etc..',
            'status': 'sent'
        }, follow=True)
        self.assertRedirects(response, reverse('sent'))
        msg = Message.objects.get(body='Please review the following document etc..')
        self.assertEqual(msg.subject, '')

    # TC3: Send message without recipient
    def test_send_message_no_recipient(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [],
            'subject': 'Upcoming meeting',
            'body': 'Please review the following meeting notes etc..',
            'status': 'sent'
        })
        self.assertContains(response, "Recipient and message body are required")

    # TC4: Send message without message body
    def test_send_message_no_body(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'hello',
            'body': '',
            'status': 'sent'
        })
        self.assertContains(response, "Recipient and message body are required")

    # ---------- Drafts (TS2) ----------
    # TC5: Save an unfinished message as a draft
    def test_save_draft(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': '',
            'body': 'Draft content',
            'status': 'draft'
        }, follow=True)
        self.assertRedirects(response, reverse('drafts'))
        self.assertTrue(Message.objects.filter(body='Draft content', status='draft').exists())

    # TC6: Get and edit a draft
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
        self.assertRedirects(response, reverse('drafts'))

    # TC7: Delete draft
    def test_delete_draft(self):
        self.login_user1()
        draft = Message.objects.create(sender=self.user1, subject='Draft to delete', body='Delete me', status='draft')
        draft.receiver.set([self.user2])
        response = self.client.get(reverse('delete_message', args=[draft.id]), follow=True)
        self.assertRedirects(response, reverse('inbox'))

    # ---------- Inbox (TS3) ----------
    # TC8: Display unread messages
    def test_inbox_unread_messages(self):
        self.login_user1()
        msg = Message.objects.create(sender=self.user2, subject='Hello', body='Unread', status='sent')
        msg.receiver.set([self.user1])
        response = self.client.get(reverse('inbox'))
        self.assertContains(response, 'Hello')

    # TC9/TC10: Display read messages and mark as read/unread
    def test_inbox_mark_read(self):
        self.login_user1()
        msg = Message.objects.create(sender=self.user2, subject='Read test', body='Read', status='sent')
        msg.receiver.set([self.user1])
        self.client.get(reverse('message_detail', args=[msg.id]))
        msg.refresh_from_db()
        self.assertTrue(msg.read_status)

    # ---------- Sent Messages (TS4) ----------
    # TC11: Display all sent messages
    def test_view_sent_messages(self):
        self.login_user1()
        msg = Message.objects.create(sender=self.user1, subject='Sent test', body='Sent body', status='sent')
        msg.receiver.set([self.user2])
        response = self.client.get(reverse('sent'))
        self.assertContains(response, 'Sent test')

    # ---------- Delete Messages (TS5) ----------
    # TC13: Delete message from inbox
    def test_delete_inbox_message(self):
        self.login_user1()
        msg = Message.objects.create(sender=self.user2, subject='Delete test', body='Delete this', status='sent')
        msg.receiver.set([self.user1])
        self.client.get(reverse('delete_message', args=[msg.id]))
        msg.refresh_from_db()
        self.assertEqual(msg.status, 'deleted')

    # ---------- Additional Negative Tests (New) ----------
    # TC-N1: Send message with invalid recipient ID
    def test_invalid_recipient_id(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [9999],  # non-existent user
            'subject': 'Invalid recipient',
            'body': 'Test body',
            'status': 'sent'
        })
        self.assertContains(response, "Recipient and message body are required")

    # TC-N2: Send message with whitespace body
    def test_whitespace_body(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': 'Whitespace body',
            'body': '    ',
            'status': 'sent'
        })
        self.assertContains(response, "Recipient and message body are required")

    # TC-N3: Send message with extremely long subject and body
    def test_extremely_long_subject_body(self):
        self.login_user1()
        long_text = 'x' * 10000
        response = self.client.post(reverse('compose'), {
            'recipient': [self.user2.id],
            'subject': long_text,
            'body': long_text,
            'status': 'sent'
        }, follow=True)
        self.assertRedirects(response, reverse('sent'))
        self.assertTrue(Message.objects.filter(subject=long_text).exists())

    # TC-N4: Access message detail for another user's message
    def test_access_other_user_message(self):
        self.login_user1()
        msg = Message.objects.create(sender=self.user2, subject='Private', body='Secret', status='sent')
        msg.receiver.set([])  # user1 is not a receiver
        response = self.client.get(reverse('message_detail', args=[msg.id]), follow=True)
        self.assertRedirects(response, reverse('inbox'))

    # TC-N5: Delete message user is not allowed to delete
    def test_delete_not_allowed(self):
        self.login_user1()
        msg = Message.objects.create(sender=self.user2, subject='Cannot delete', body='Protected', status='sent')
        msg.receiver.set([])  # user1 cannot delete
        self.client.get(reverse('delete_message', args=[msg.id]))
        msg.refresh_from_db()
        self.assertEqual(msg.status, 'sent')

    # TC-N6: Mark as read/unread for non-existent message
    def test_mark_nonexistent_message(self):
        self.login_user1()
        response = self.client.get(reverse('message_detail', args=[9999]), follow=True)
        self.assertEqual(response.status_code, 404)

    # TC-N7: Compose with no recipient and no body
    def test_compose_no_recipient_no_body(self):
        self.login_user1()
        response = self.client.post(reverse('compose'), {
            'recipient': [],
            'subject': 'Empty fields',
            'body': '',
            'status': 'sent'
        })
        self.assertContains(response, "Recipient and message body are required")

    # ---------- Admin Login Tests ----------
    def test_admin_can_login(self):
        self.login_admin()
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
