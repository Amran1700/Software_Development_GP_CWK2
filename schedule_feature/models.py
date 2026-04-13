# Author : Ibrahim Chowdhury | Student Number: W1905510
from django.db import models
from django.contrib.auth.models import User


# Meeting model: stores all the details for a single meeting
class Meeting(models.Model):

    # The available platform choices for the meeting
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'MS Teams'),
        ('meet', 'Google Meet'),
    ]

    # The name/title of the meeting
    title = models.CharField(max_length=200)

    # Optional description for agenda or notes
    description = models.TextField(blank=True)

    # The date the meeting takes place
    date = models.DateField()

    # The time the meeting starts
    time = models.TimeField()

    # How long the meeting lasts in minutes (defaults to 60)
    duration_minutes = models.IntegerField(default=60)

    # Which platform the meeting is hosted on (Zoom, MS Teams or Google Meet)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)

    # The user who created the meeting
    # If the user is deleted, all their created meetings are also deleted
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')

    # Whether the meeting repeats on a regular schedule
    is_recurring = models.BooleanField(default=False)

    # Returns a readable string when the meeting is displayed (e.g. in admin)
    def __str__(self):
        return f"{self.title} on {self.date}"


# MeetingAttendee model: links a user to a meeting they have been invited to
# This is a many-to-many relationship handled through a separate table
class MeetingAttendee(models.Model):

    # The meeting this attendee is linked to
    # If the meeting is deleted, all its attendee records are also deleted
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')

    # The user who has been invited to this meeting
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Returns a readable string showing who is attending which meeting
    def __str__(self):
        return f"{self.user.username} → {self.meeting.title}"