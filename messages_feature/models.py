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
    read_status = models.BooleanField(default=False)
    # true = read, false = unread
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )
    # Self-referencing FK:
    # Used for reply chains (email threads)
    # Currently NOT used in views yet cause i havent implemented threading 

    def __str__(self):
        return f"{self.subject} from {self.sender.username}"

    class Meta:
        ordering = ['-timestamp']
        #  newest messages first