from django.db import models
from django.contrib.auth.models import User

class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'MS Teams'),
        ('meet', 'Google Meet'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} on {self.date}"


class MeetingAttendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} → {self.meeting.title}"