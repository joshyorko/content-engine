from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from items.models import Item
from projects.decorators import project_required

@project_required
def dashboard_view(request):
    return render(request, "dashboard/home.html", {})

def home_page_view(request):
    if not request.user.is_authenticated:
        return render(request, "landing/home.html", {})
    return dashboard_view(request)

def about_page_view(request):
    print(request.project)
    return render(request, "landing/home.html", {})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def server_error_page(request):
    raise Exception
    return render(request, "landing/error.html", {})