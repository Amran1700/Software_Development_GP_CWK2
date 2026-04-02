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

@login_required  # Ensures only authenticated users can access this view
def compose(request):
    
    #this will get all of the users except the current user, so you can't send a message to yourself??
    users = User.objects.exclude(id=request.user.id)

    # Retrieve GET parameters if the compose page was opened via Reply/Forward
    # Example: /compose/?to=3&subject=Re: Hello
    initial_receiver = request.GET.get('to')        # Pre-select a single user ID in the dropdown
    initial_subject = request.GET.get('subject', '')  # Pre-fill the subject line, defaults to empty string

    # --- POST REQUEST HANDLING ---
    if request.method == 'POST':
        # Get list of selected recipients from the form submission (can be multiple for Reply All)
        recipient_ids = request.POST.getlist('recipient')
        

        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')

        status = request.POST.get('status', 'sent')

        # Basic validation: ensure at least one recipient is selected and body is not empty
        if recipient_ids and body:
            
            message = Message.objects.create(
                sender=request.user,  
                subject=subject,      
                body=body,            
                status=status         
            )

            # Add receivers using ManyToMany relationship (must be done after creation)
            recipients = User.objects.filter(id__in=recipient_ids)
            message.receiver.set(recipients)

            # Save message to the database
            message.save()

            # Redirect depending on message status
            if status == 'draft':
                return redirect('drafts')  # Send user to their drafts folder
            return redirect('sent')        # Otherwise, go to Sent messages

        else:
            # Validation failed → missing recipient or empty body
            error = "Recipient and message body are required"
            context = {
                'error': error,  
                'users': users  
            }
            return render(request, 'messages_feature/compose.html', context)

    # --- GET REQUEST HANDLING ---
    else:
        # GET request → show the form for composing a new message
        # This can also include pre-filled fields if accessed via Reply/Forward links
        context = {'users': users}  # Include all users for the dropdown

        # Pre-fill recipient if "to" parameter exists
        if initial_receiver:
            context['initial_receiver'] = [int(i) for i in initial_receiver.split(',')]

        # Pre-fill subject if provided in GET parameters
        context['initial_subject'] = initial_subject

        # Render the compose template with the context
        return render(request, 'messages_feature/compose.html', context)