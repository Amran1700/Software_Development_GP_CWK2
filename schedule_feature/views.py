import calendar
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Meeting, MeetingAttendee

@login_required
def calendar_month(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.monthcalendar(year, month)
    meetings = Meeting.objects.filter(date__year=year, date__month=month)

    meetings_by_day = {}
    for meeting in meetings:
        day = meeting.date.day
        meetings_by_day.setdefault(day, []).append(meeting)

    upcoming_today = Meeting.objects.filter(date=today)

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

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


@login_required
def upcoming_meetings(request):
    today = date.today()
    meetings = Meeting.objects.filter(date__gte=today).order_by('date', 'time')
    return render(request, 'schedule/upcoming_meetings.html', {'meetings': meetings})


@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    attendees = meeting.attendees.all()
    return render(request, 'schedule/meeting_detail.html', {
        'meeting': meeting,
        'attendees': attendees
    })


@login_required
def create_meeting(request):
    from .forms import MeetingForm
    from django.contrib.auth.models import User

    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            attendee_ids = request.POST.getlist('attendees')
            for uid in attendee_ids:
                MeetingAttendee.objects.create(meeting=meeting, user_id=uid)
            return redirect('schedule:calendar_month')
    else:
        form = MeetingForm()

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'schedule/create_meeting.html', {
        'form': form,
        'users': users,
    })



@login_required
def calendar_week(request):
    from datetime import timedelta
    today = date.today()
    
    # Get the start of the week (Monday)
    week_start = today - timedelta(days=today.weekday())
    
    # Allow navigation via GET params
    offset = int(request.GET.get('offset', 0))
    week_start = week_start + timedelta(weeks=offset)
    week_end = week_start + timedelta(days=6)
    
    # Get meetings for this week
    meetings = Meeting.objects.filter(date__gte=week_start, date__lte=week_end).order_by('date', 'time')
    
    # Group by day
    meetings_by_day = {}
    for meeting in meetings:
        day = meeting.date
        meetings_by_day.setdefault(day, []).append(meeting)
    
    # Build list of 7 days
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


@login_required
def edit_meeting(request, pk):
    from .forms import MeetingForm
    from django.contrib.auth.models import User
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            meeting.attendees.all().delete()
            attendee_ids = request.POST.getlist('attendees')
            for uid in attendee_ids:
                MeetingAttendee.objects.create(meeting=meeting, user_id=uid)
            return redirect('schedule:meeting_detail', pk=pk)
    else:
        form = MeetingForm(instance=meeting)
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'schedule/edit_meeting.html', {
        'form': form,
        'meeting': meeting,
        'users': users,
    })


@login_required
def delete_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
        return redirect('schedule:upcoming_meetings')
    return render(request, 'schedule/delete_meeting.html', {'meeting': meeting})