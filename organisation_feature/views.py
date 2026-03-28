from django.http import HttpResponse


def home(request):
    """Landing page until organisation routes are added."""
    return HttpResponse(
        "<h1>Sky Engineering</h1>"
        "<p>Try "
        '<a href="/messages/inbox/">Messages</a>, '
        '<a href="/reports/">Reports</a>, or '
        '<a href="/admin/">Admin</a>.'
        "</p>"
    )
