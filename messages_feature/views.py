from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from .models import Message



# INBOX VIEW
# Shows messages RECEIVED by the logged-in user
@login_required
def inbox(request):
    # Gets the  messages that are current for the user who is a RECEIVER
    # Only show messages that were actually sent not the drafts/deleted
    messages = request.user.received_messages.filter(
        status='sent'
    ).order_by('-timestamp')
    # Count unread messages for badge display in sidebar
    # read_status = False means message has not been opened
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


# SENT VIEW
# Shows messages SENT by the logged-in user
@login_required
def sent(request):
    messages = request.user.sent_messages.filter(
        status='sent'
    ).order_by('-timestamp')
    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()
    # Count drafts for sidebar
    drafts_count = request.user.sent_messages.filter(
        status='draft'
    ).count()

    return render(request, 'messages_feature/sent.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# DRAFTS VIEW
# Shows messages saved as drafts by the user
@login_required
def drafts(request):
    messages = request.user.sent_messages.filter(
        status='draft'
    ).order_by('-timestamp')
    inbox_count = request.user.received_messages.filter(
        status='sent',
        read_status=False
    ).count()

    drafts_count = messages.count()

    return render(request, 'messages_feature/drafts.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })

# DELETED VIEW
# Shows soft-deleted messages related to the user
@login_required
def deleted(request):
    # Get deleted messages where user is sender OR receiver
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

# MESSAGE DETAIL VIEW
# Shows full message content
# Also marks message as READ if receiver opens it
@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Security check: only sender or receiver can view message
    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('inbox')
    # Mark as read ONLY if receiver has opened it
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



#  DELETE MESSAGE
# Marks message as deleted instead of removing from DB

@login_required
def delete_message(request, message_id):

    message = get_object_or_404(Message, id=message_id)

    # Security: only sender or receiver can delete
    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('inbox')
    # it can be considered a soft  delete beacuse it keeps data but hides it from normal views
    message.status = 'deleted'
    message.save()

    return redirect('inbox')

# DELETED MESSAGE DETAIL VIEW
# Shows full content of deleted message
@login_required
def deleted_message_detail(request, message_id):

    message = get_object_or_404(Message, id=message_id)
    # Only allow deleted messages
    if message.status != 'deleted':
        return redirect('inbox')
    # Security: only sender or receiver can view
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



# COMPOSE MESSAGE VIEW
# Handles:
# - sending messages
# - saving drafts
# - replying 

@login_required
def compose(request):
    # Get all users except current user (no self messaging)
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

    # If form is submitted
    if request.method == 'POST':
        recipient_ids = request.POST.getlist('recipient')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        # Determines whether message is sent or saved as draft
        status = request.POST.get('status', 'sent')

        # Validation: only required when sending
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

    # If replying to message, prefill recipient list with all the users in superadmins
    if initial_receiver:
        context['initial_receiver'] = [int(i) for i in initial_receiver.split(',')]

    return render(request, 'messages_feature/compose.html', context)



# EDIT DRAFT VIEW
# Allows user to modify saved drafts before sending
@login_required
def edit_draft(request, message_id):
    #only editing messages that are still drafts
    message = get_object_or_404(Message, id=message_id, status='draft')
    # only the original sender can edit draft
    if request.user != message.sender:
        return redirect('drafts')

    users = User.objects.exclude(id=request.user.id)

    if request.method == 'POST':
        recipient_ids = request.POST.getlist('recipient')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        status = request.POST.get('status', 'draft')
        
        # Validation before sending
        if status == 'sent' and (not recipient_ids or not body):
            return render(request, 'messages_feature/edit_draft.html', {
                'error': "Recipient and message body are required",
                'message': message,
                'users': users
            })

        message.subject = subject
        message.body = body
        message.status = status
        message.save()

        recipients = User.objects.filter(id__in=recipient_ids)
        message.receiver.set(recipients)

        if status == 'draft':
            return redirect('drafts')

        return redirect('sent')

    return render(request, 'messages_feature/edit_draft.html', {
        'message': message,
        'users': users
    })