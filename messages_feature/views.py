from django.shortcuts import render, get_object_or_404, redirect
from .models import Message
from django.contrib.auth.decorators import login_required

@login_required
def inbox(request):
    messages = request.user.received_messages.filter(status='sent')
    return render(request, 'messages_app/inbox.html', {'messages': messages})

@login_required
def sent(request):
    messages = request.user.sent_messages.filter(status='sent')
    return render(request, 'messages_app/sent.html', {'messages': messages})

@login_required
def drafts(request):
    messages = request.user.sent_messages.filter(status='draft')
    return render(request, 'messages_app/drafts.html', {'messages': messages})

@login_required
def deleted(request):
    messages = request.user.received_messages.filter(status='deleted')
    return render(request, 'messages_app/deleted.html', {'messages': messages})

@login_required
def compose(request):
    if request.method == 'POST':
        # Simplified: add validation later
        recipient_ids = request.POST.getlist('recipient')
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')
        status = request.POST.get('status', 'sent')

        if recipient_ids and body:
            message = Message.objects.create(
                sender=request.user,
                subject=subject,
                body=body,
                status=status
            )
            message.receiver.set(recipient_ids)
            message.save()
            return redirect('sent')
        else:
            error = "Recipient and message body are required"
            return render(request, 'messages_app/compose.html', {'error': error})

    return render(request, 'messages_app/compose.html')

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Mark as read
    if request.user in message.receiver.all():
        message.read_status = True
        message.save()
    return render(request, 'messages_app/message_detail.html', {'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Only allow receiver to delete
    if request.user in message.receiver.all():
        message.status = 'deleted'
        message.save()
    return redirect('inbox')