from django.shortcuts import render

# Create your views here.
def DepartmentID(request):
    return render(request, 'messages_/DepartmentID.html')

def UpDownDependencies(request):
    return render(request, 'UpDownDependencies.html')

def TeamPage(request):
    return render(request, 'TeamPage.html')

