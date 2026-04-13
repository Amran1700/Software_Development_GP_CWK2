from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from .models import Message


# =========================
# INBOX
# =========================
@login_required
def inbox(request):
    messages = request.user.received_messages.filter(
        status='sent'
    ).order_by('-timestamp')

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/inbox.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# =========================
# SENT
# =========================
@login_required
def sent(request):
    messages = request.user.sent_messages.filter(
        status='sent'
    ).order_by('-timestamp')

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/sent.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# =========================
# DRAFTS
# =========================
@login_required
def drafts(request):
    messages = request.user.sent_messages.filter(
        status='draft'
    ).order_by('-timestamp')

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/drafts.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# =========================
# DELETED
# =========================
@login_required
def deleted(request):
    messages = Message.objects.filter(
        status='deleted'
    ).filter(
        models.Q(sender=request.user) |
        models.Q(receiver=request.user)
    ).distinct().order_by('-timestamp')

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/deleted.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# =========================
# MESSAGE DETAIL
# =========================
@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('inbox')

    # mark as read (only receivers)
    if request.user in message.receiver.all() and not message.read_status:
        message.read_status = True
        message.save()

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/message_detail.html', {
        'message': message,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# =========================
# DELETE MESSAGE (SOFT DELETE)
# =========================
@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('inbox')

    message.status = 'deleted'
    message.save()

    return redirect('inbox')


# =========================
# DELETED MESSAGE DETAIL
# =========================
@login_required
def deleted_message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.status != 'deleted':
        return redirect('inbox')

    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('deleted')

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/deleted_message_detail.html', {
        'message': message,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# =========================
# COMPOSE MESSAGE
# =========================
@login_required
def compose(request):
    users = User.objects.exclude(id=request.user.id)

    initial_receiver = request.GET.get('to')
    initial_subject = request.GET.get('subject', '')

    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    if request.method == 'POST':

        recipient_ids = request.POST.getlist('recipient')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        status = request.POST.get('status', 'sent')

        # validation
        if status == 'sent' and (not recipient_ids or not body):
            return render(request, 'messages_feature/compose.html', {
                'error': "Recipient and message body are required",
                'users': users,
                'subject': subject,
                'body': body,
                'recipient_ids': [int(r) for r in recipient_ids] if recipient_ids else [],
                'inbox_count': inbox_count,
                'drafts_count': drafts_count,
                'initial_subject': initial_subject
            })

        message = Message.objects.create(
            sender=request.user,
            subject=subject,
            body=body,
            status=status
        )

        recipients = User.objects.filter(id__in=recipient_ids)
        message.receiver.set(recipients)

        if status == 'draft':
            return redirect('drafts')

        return redirect('sent')

    context = {
        'users': users,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count,
        'initial_subject': initial_subject
    }

    if initial_receiver:
        context['initial_receiver'] = [int(i) for i in initial_receiver.split(',')]

    return render(request, 'messages_feature/compose.html', context)