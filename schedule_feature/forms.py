<<<<<<< HEAD
from django import forms
from django.contrib.auth.models import User
from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'time', 'duration_minutes', 'platform', 'description', 'is_recurring']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Weekly Team Sync, Project Kickoff...'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
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
            'platform': forms.RadioSelect(),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add meeting agenda, talking points, or any relevant information for attendees...'
            }),
            'is_recurring': forms.CheckboxInput(),
=======
from django import forms
from django.contrib.auth.models import User
from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'time', 'duration_minutes', 'platform', 'description', 'is_recurring']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Weekly Team Sync, Project Kickoff...'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
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
            'platform': forms.RadioSelect(),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add meeting agenda, talking points, or any relevant information for attendees...'
            }),
            'is_recurring': forms.CheckboxInput(),
>>>>>>> origin/main
        }