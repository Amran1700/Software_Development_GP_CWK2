# Standard library imports for calendar operations and date handling
import calendar
from datetime import date, timedelta

# Django imports for rendering templates, handling redirects and authentication
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

# Import the Meeting and MeetingAttendee models from this app
from .models import Meeting, MeetingAttendee


# ── MONTHLY CALENDAR VIEW ──────────────────────────────────────────────────────
# Displays all meetings for a given month in a calendar grid
# Accepts 'year' and 'month' as optional GET parameters for navigation
@login_required
def calendar_month(request):
    today = date.today()

    # Get the year and month from the URL, defaulting to the current month
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Build a list of weeks for the selected month
    cal = calendar.monthcalendar(year, month)

    # Get all meetings that fall within the selected month
    meetings = Meeting.objects.filter(date__year=year, date__month=month)

    # Group meetings by day number so the template can look them up easily
    meetings_by_day = {}
    for meeting in meetings:
        day = meeting.date.day
        meetings_by_day.setdefault(day, []).append(meeting)

    # Get all meetings happening today for the sidebar
    upcoming_today = Meeting.objects.filter(date=today)

    # Calculate the previous month (wraps from January back to December)
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    # Calculate the next month (wraps from December forward to January)
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    context = {
        'cal': cal,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'meetings_by_day': meetings_by_day,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'upcoming_today': upcoming_today,
    }
    return render(request, 'schedule/calendar_month.html', context)


# ── UPCOMING MEETINGS LIST VIEW ────────────────────────────────────────────────
# Displays all meetings from today onwards ordered by date and time
@login_required
def upcoming_meetings(request):
    today = date.today()

    # Filter meetings that are today or in the future, sorted by soonest first
    meetings = Meeting.objects.filter(date__gte=today).order_by('date', 'time')
    return render(request, 'schedule/upcoming_meetings.html', {'meetings': meetings})


# ── MEETING DETAIL VIEW ────────────────────────────────────────────────────────
# Displays full information for a single meeting including its attendees
@login_required
def meeting_detail(request, pk):

    # Get the meeting by its ID or return 404 if it does not exist
    meeting = get_object_or_404(Meeting, pk=pk)

    # Get all attendees linked to this meeting
    attendees = meeting.attendees.all()
    return render(request, 'schedule/meeting_detail.html', {
        'meeting': meeting,
        'attendees': attendees
    })


# ── CREATE MEETING VIEW ────────────────────────────────────────────────────────
# Handles the create meeting form
# On POST: saves the meeting and adds selected attendees
# On GET: shows a blank form
@login_required
def create_meeting(request):
    from .forms import MeetingForm
    from django.contrib.auth.models import User

    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():

            # Save the meeting but don't commit yet so we can set the creator
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()

            # Create a MeetingAttendee record for each selected user
            attendee_ids = request.POST.getlist('attendees')
            for uid in attendee_ids:
                MeetingAttendee.objects.create(meeting=meeting, user_id=uid)

            # Redirect to the monthly calendar after saving
            return redirect('schedule:calendar_month')
    else:
        form = MeetingForm()

    # Pass all users except the creator to the attendee selection list
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'schedule/create_meeting.html', {
        'form': form,
        'users': users,
    })


# ── WEEKLY CALENDAR VIEW ───────────────────────────────────────────────────────
# Displays all meetings for a 7-day week
# Accepts an 'offset' GET parameter to navigate between weeks
@login_required
def calendar_week(request):
    today = date.today()

    # Find the Monday of the current week
    week_start = today - timedelta(days=today.weekday())

    # Apply the offset to navigate to previous or next weeks
    offset = int(request.GET.get('offset', 0))
    week_start = week_start + timedelta(weeks=offset)
    week_end = week_start + timedelta(days=6)

    # Get all meetings within this week sorted by date and time
    meetings = Meeting.objects.filter(date__gte=week_start, date__lte=week_end).order_by('date', 'time')

    # Group meetings by date so each day column can show its own meetings
    meetings_by_day = {}
    for meeting in meetings:
        day = meeting.date
        meetings_by_day.setdefault(day, []).append(meeting)

    # Build a list of all 7 days in the week
    week_days = [week_start + timedelta(days=i) for i in range(7)]

    context = {
        'week_days': week_days,
        'meetings_by_day': meetings_by_day,
        'today': today,
        'offset': offset,
        'prev_offset': offset - 1,
        'next_offset': offset + 1,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'schedule/calendar_week.html', context)


# ── EDIT MEETING VIEW ──────────────────────────────────────────────────────────
# Handles the edit meeting form for an existing meeting
# On POST: updates the meeting and replaces the attendee list
# On GET: shows the form pre-filled with the existing meeting data
@login_required
def edit_meeting(request, pk):
    from .forms import MeetingForm
    from django.contrib.auth.models import User

    # Get the meeting to edit or return 404 if it does not exist
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()

            # Remove all existing attendees and replace with the new selection
            meeting.attendees.all().delete()
            attendee_ids = request.POST.getlist('attendees')
            for uid in attendee_ids:
                MeetingAttendee.objects.create(meeting=meeting, user_id=uid)

            # Redirect back to the meeting detail page after saving
            return redirect('schedule:meeting_detail', pk=pk)
    else:
        # Pre-fill the form with the existing meeting data
        form = MeetingForm(instance=meeting)

    # Pass all users except the current user to the attendee selection list
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'schedule/edit_meeting.html', {
        'form': form,
        'meeting': meeting,
        'users': users,
    })


# ── DELETE MEETING VIEW ────────────────────────────────────────────────────────
# Shows a confirmation page before deleting a meeting
# On POST: permanently deletes the meeting and redirects to upcoming meetings
# On GET: shows the confirmation page
@login_required
def delete_meeting(request, pk):

    # Get the meeting to delete or return 404 if it does not exist
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        # Delete the meeting and redirect to the upcoming meetings list
        meeting.delete()
        return redirect('schedule:upcoming_meetings')

    # Show the delete confirmation page
    return render(request, 'schedule/delete_meeting.html', {'meeting': meeting})


# ── DAILY CALENDAR VIEW ────────────────────────────────────────────────────────
# Displays all meetings for a single day on a 24-hour time grid
# Accepts an 'offset' GET parameter to navigate between days
@login_required
def calendar_day(request):
    today = date.today()

    # Apply the offset to navigate forward or backward by day
    offset = int(request.GET.get('offset', 0))
    selected_day = today + timedelta(days=offset)

    # Get all meetings for the selected day sorted by start time
    meetings_qs = Meeting.objects.filter(date=selected_day).order_by('time')

    # Build a list of hour labels from 0:00 to 23:00 for the time grid
    hours = [f"{h}:00" for h in range(0, 24)]

    # Calculate the pixel position and height for each meeting block
    # 1 minute = 1 pixel, so top_px = start time in minutes from midnight
    meetings = []
    for m in meetings_qs:
        top_px = m.time.hour * 60 + m.time.minute
        height_px = max(m.duration_minutes, 30)
        meetings.append({
            'pk': m.pk,
            'title': m.title,
            'time': m.time,
            'platform': m.platform,
            'top_px': top_px,
            'height_px': height_px,
        })

    context = {
        'selected_day': selected_day,
        'today': today,
        'offset': offset,
        'prev_offset': offset - 1,
        'next_offset': offset + 1,
        'hours': hours,
        'meetings': meetings,
    }
    return render(request, 'schedule/calendar_day.html', context)