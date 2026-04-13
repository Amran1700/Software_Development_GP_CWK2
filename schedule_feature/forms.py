# Author : Ibrahim Chowdhury | Student Number: W1905510
from django import forms
from django.contrib.auth.models import User
from .models import Meeting

# Form for creating and editing a Meeting
# Uses Django's ModelForm to automatically generate fields from the Meeting model
class MeetingForm(forms.ModelForm):

    class Meta:
        # Links this form to the Meeting model
        model = Meeting

        # Only these fields will be shown in the form
        fields = ['title', 'date', 'time', 'duration_minutes', 'platform', 'description', 'is_recurring']

        # Custom widgets: controls how each field is displayed in the HTML
        widgets = {

            # Title: a single line text input with a helpful placeholder
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Weekly Team Sync, Project Kickoff...'
            }),

            # Date: uses the browser's built-in date picker
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            # Time: uses the browser's built-in time picker
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),

            # Duration: a dropdown with preset options from 15 minutes to 2 hours
            'duration_minutes': forms.Select(
                choices=[
                    (15,'15 minutes'),
                    (30,'30 minutes'),
                    (60,'1 hour'),
                    (90,'1.5 hours'),
                    (120,'2 hours')
                ],
                attrs={'class': 'form-control'}
            ),

            # Platform: radio buttons so the user can pick one platform (Zoom, Teams, Meet)
            'platform': forms.RadioSelect(),

            # Description: a multi-line text area for agenda or meeting notes
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add meeting agenda, talking points, or any relevant information for attendees...'
            }),

            # Is Recurring: a simple checkbox to mark the meeting as repeating
            'is_recurring': forms.CheckboxInput(),
        }