from django.shortcuts import render, get_object_or_404, redirect # Import shortcuts to simplify common Django tasks
from .models import Message # Import your Message model
from django.contrib.auth.decorators import login_required # Ensures only logged-in users can access views
from django.contrib.auth.models import User # Import User model (used in compose view)


# INBOX VIEW
@login_required
def inbox(request):
    """
    Shows all messages RECEIVED by the logged-in user
    """
    # Get messages where:
    # - current user is a receiver
    # - message status is 'sent'
    messages = request.user.received_messages.filter(status='sent')
    
    inbox_count = messages.count()
    drafts_count = request.user.sent_messages.filter(status='draft').count()

    # Render template and pass messages to HTML
    return render(request, 'messages_feature/inbox.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })  

# SENT VIEW
@login_required
def sent(request):
    """
    Shows messages SENT by the user
    """

    messages = request.user.sent_messages.filter(status='sent')
    inbox_count = request.user.received_messages.filter(status='sent').count()
    drafts_count = request.user.sent_messages.filter(status='draft').count()

    return render(request, 'messages_feature/sent.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })

# DRAFTS VIEW
@login_required
def drafts(request):
    """
    Shows messages saved as drafts
    """

    messages = request.user.sent_messages.filter(status='draft')
    inbox_count = request.user.received_messages.filter(status='sent').count()
    drafts_count = request.user.sent_messages.filter(status='draft').count()
    return render(request, 'messages_feature/drafts.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# DELETED VIEW
@login_required
def deleted(request):
    """
    Shows deleted messages (basic version)
    """

    messages = request.user.received_messages.filter(status='deleted')

    inbox_count = request.user.received_messages.filter(status='sent').count()
    drafts_count = request.user.sent_messages.filter(status='draft').count()
    return render(request, 'messages_feature/deleted.html', {
        'messages': messages,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })



# MESSAGE DETAIL VIEW
@login_required
def message_detail(request, message_id):
    """
    Shows a single message in detail.
    """

    # Get message or return 404 if it doesn't exist
    message = get_object_or_404(Message, id=message_id)

    # SECURITY CHECK: only sender or receivers can view message
    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('inbox')

    # --- MARK AS READ ---
    # If the current user is a recipient and hasn't read the message yet
    if request.user in message.receiver.all():
        message.read_status = True
        message.save()

    # Prepare inbox/draft counts for template
    inbox_count = request.user.received_messages.filter(status='sent').count()
    drafts_count = request.user.sent_messages.filter(status='draft').count()

    # Render the message detail template
    return render(request, 'messages_feature/message_detail.html', {
        'message': message,
        'inbox_count': inbox_count,
        'drafts_count': drafts_count
    })


# DELETE MESSAGE VIEW
@login_required
def delete_message(request, message_id):
    """
    Marks a message as deleted
    """

    message = get_object_or_404(Message, id=message_id)

    # Only allow receiver to delete message
    if request.user in message.receiver.all():
        message.status = 'deleted'
        message.save()

    return redirect('inbox')



@login_required
def compose(request):
    """
    Handles composing new messages, replying, forwarding, and saving drafts.

    - GET request: displays the compose form.
    - POST request: validates and saves message as 'sent' or 'draft'.
    - Ensures only logged-in users can send messages.
    """

    # Exclude the current user from recipients (you cannot send to yourself)
    users = User.objects.exclude(id=request.user.id)

    # Retrieve GET parameters for reply/forward pre-filling
    initial_receiver = request.GET.get('to')        # e.g., /compose/?to=3
    initial_subject = request.GET.get('subject', '')  # e.g., /compose/?subject=Re: Hello

    if request.method == 'POST':
        # Get list of selected recipients from form (can be multiple)
        recipient_ids = request.POST.getlist('recipient')

        # Strip whitespace from subject and body
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        status = request.POST.get('status', 'sent')  # Default to 'sent' if not provided

        # --- VALIDATION ---
        # Only enforce recipient/body requirement if message is being SENT
        if status == 'sent' and (not recipient_ids or not body):
            # Prepare error message
            error = "Recipient and message body are required"

            # Pass context back to template so user input is not lost
            context = {
                'error': error,
                'users': users,
                'subject': subject,  # preserves stripped subject
                'body': request.POST.get('body', ''),  # preserve original input, even if whitespace
                'recipient_ids': [int(r) for r in recipient_ids] if recipient_ids else []
            }

            # Re-render compose page with error message
            return render(request, 'messages_feature/compose.html', context)

        # --- SAVE MESSAGE ---
        # Create message instance
        message = Message.objects.create(
            sender=request.user,
            subject=subject,
            body=body,
            status=status
        )

        # Set recipients using ManyToMany relationship
        recipients = User.objects.filter(id__in=recipient_ids)
        message.receiver.set(recipients)

        # Save message to database
        message.save()

        # --- REDIRECT BASED ON STATUS ---
        if status == 'draft':
            return redirect('drafts')  # Send to drafts folder
        return redirect('sent')        # Otherwise, go to Sent messages

    else:
        # --- GET REQUEST ---
        # Prepare context for initial render
        context = {'users': users}

        # Pre-fill recipient(s) if "to" parameter exists (for reply/forward)
        if initial_receiver:
            context['initial_receiver'] = [int(i) for i in initial_receiver.split(',')]

        # Pre-fill subject if provided
        context['initial_subject'] = initial_subject

        # Render compose template
        return render(request, 'messages_feature/compose.html', context)