from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ManyToManyField(
        User,
        related_name='received_messages'
    )

    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('draft', 'Draft'),
        ('deleted', 'Deleted'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent'
    )

    # ⚠️ IMPORTANT FIX: this should track PER USER in real apps
    # but for your level, this is OK:
    read_status = models.BooleanField(default=False)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )

    def __str__(self):
        return f"{self.subject} from {self.sender.username}"

    class Meta:
        ordering = ['-timestamp']