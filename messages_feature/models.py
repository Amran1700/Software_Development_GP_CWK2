from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """
    This class defines the structure of your Message table in the database.
    Each attribute becomes a column in db.sqlite3.
    """

    sender = models.ForeignKey(
        User,  # Links to Django's User model
        on_delete=models.CASCADE,  # If user is deleted → their messages are deleted too
        related_name='sent_messages'  # Allows: user.sent_messages.all()
    )

    # RECEIVER(S) (who gets message)   
    receiver = models.ManyToManyField(
        User,  # A message can have multiple users
        related_name='received_messages'  # Allows: user.received_messages.all()
    )

    # MESSAGE CONTENT
    subject = models.CharField(
        max_length=255,  # Max length of subject line
        blank=True  # Subject is optional
    )

    body = models.TextField()  # Main message content (no max length limit)

    # TIMESTAMP
    timestamp = models.DateTimeField(
        auto_now_add=True  # Automatically set when message is created
    )


    # STATUS (sent, draft, deleted)
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('draft', 'Draft'),
        ('deleted', 'Deleted'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,  # Limits values to above choices
        default='sent'  # Default when message is created
    )


    # READ STATUS 
    read_status = models.BooleanField(
        default=False  # False = unread, True = read
    )

    # OPTIONAL: REPLY / THREADING
    parent = models.ForeignKey(
        'self',  # Refers to another Message
        null=True,  # Can be empty
        blank=True,
        on_delete=models.SET_NULL,  # If parent deleted → set to NULL
        related_name='replies'  # Allows: message.replies.all()
    )


    # STRING REPRESENTATION
    def __str__(self):
        # How message appears in admin panel / shell
        return f"{self.subject} from {self.sender.username}"


    # DEFAULT ORDERING
    class Meta:
        # Show newest messages first automatically
        ordering = ['-timestamp']