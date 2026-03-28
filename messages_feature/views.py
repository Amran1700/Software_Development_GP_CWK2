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

    # Render template and pass messages to HTML
    return render(request, 'inbox.html', {
        'messages': messages
    })


# SENT VIEW
@login_required
def sent(request):
    """
    Shows messages SENT by the user
    """

    messages = request.user.sent_messages.filter(status='sent')

    return render(request, 'messages_app/sent.html', {
        'messages': messages
    })

# DRAFTS VIEW
@login_required
def drafts(request):
    """
    Shows messages saved as drafts
    """

    messages = request.user.sent_messages.filter(status='draft')

    return render(request, 'messages_app/drafts.html', {
        'messages': messages
    })


# DELETED VIEW
@login_required
def deleted(request):
    """
    Shows deleted messages (basic version)
    """

    messages = request.user.received_messages.filter(status='deleted')

    return render(request, 'messages_app/deleted.html', {
        'messages': messages
    })



# COMPOSE VIEW
@login_required
def compose(request):
    """
    Handles creating a new message
    """

    # Get all users except the current user (so you can't message yourself)
    users = User.objects.exclude(id=request.user.id)

    # If form is submitted
    if request.method == 'POST':

        # Get list of selected recipient IDs
        recipient_ids = request.POST.getlist('recipient')

        # Get subject and body from form
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')

        # Get status (sent or draft)
        status = request.POST.get('status', 'sent')

        # Basic validation
        if recipient_ids and body:

            # Create message WITHOUT receivers first
            message = Message.objects.create(
                sender=request.user,
                subject=subject,
                body=body,
                status=status
            )

            # Add receivers (ManyToMany requires separate step)
            message.receiver.set(recipient_ids)

            # Save message
            message.save()

            # Redirect depending on status
            if status == 'draft':
                return redirect('drafts')

            return redirect('sent')

        else:
            # If validation fails
            error = "Recipient and message body are required"

            return render(request, 'messages_app/compose.html', {
                'error': error,
                'users': users
            })

    # If GET request → just show empty form
    return render(request, 'messages_app/compose.html', {
        'users': users
    })



# MESSAGE DETAIL VIEW
@login_required
def message_detail(request, message_id):
    """
    Shows a single message in detail
    """

    # Get message or return 404 if it doesn't exist
    message = get_object_or_404(Message, id=message_id)

    # SECURITY CHECK:
    # Only allow sender or receivers to view message
    if request.user != message.sender and request.user not in message.receiver.all():
        return redirect('inbox')

    # If user is a receiver → mark as read
    if request.user in message.receiver.all():
        message.read_status = True
        message.save()

    return render(request, 'messages_app/message_detail.html', {
        'message': message
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