from django.shortcuts import render


#this is to create stub views for the messages app. These views will render the corresponding templates for each page in the messages app. The templates will need to be created in the 'messages_app/templates/messages_app/' directory.

def inbox(request):
    return render(request, 'messages_/inbox.html')

def sent(request):
    return render(request, 'messages_/sent.html')

def drafts(request):
    return render(request, 'messages_feature/drafts.html')

def compose(request):
    return render(request, 'messages_feature/compose.html')

def message_detail(request):
    return render(request, 'messages_feature/message_detail.html')