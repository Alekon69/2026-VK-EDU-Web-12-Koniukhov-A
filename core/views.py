from django.shortcuts import render


def login_page(request):
    return render(request, 'core/login.html')


def signup_page(request):
    return render(request, 'core/signup.html')


def profile_page(request):
    return render(request, 'core/profile.html', {
        'show_authorized_header': True
    })