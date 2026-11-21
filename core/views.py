from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from .forms import StyledAuthenticationForm, SignupForm, ProfileEditForm


class UserLoginView(LoginView):
    template_name = "core/login.html"
    authentication_form = StyledAuthenticationForm
    next_page = reverse_lazy("index")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("index")


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "core/signup.html"
    success_url = reverse_lazy("index")


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = "core/profile.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user