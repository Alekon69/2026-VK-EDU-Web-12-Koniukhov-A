from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from pathlib import Path

from .models import Profile


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "login-border",
            "placeholder": "Введите логин",
        })

        self.fields["password"].widget.attrs.update({
            "class": "login-border",
            "placeholder": "Введите пароль",
        })



class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Имя")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "login-border"

    @transaction.atomic
    def save(self):
        user = super().save()
        Profile.objects.create(user=user)
        return user


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")
    avatar = forms.ImageField(required=False, label="Аватар")

    class Meta:
        model = User
        fields = ("username", "email", "first_name")
        labels = {
            "username": "Логин",
            "first_name": "Имя",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "login-border"

        self.fields["avatar"].widget.attrs["class"] = "form-control w-auto"



    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")

        if not avatar:
            return avatar

        extension = Path(avatar.name).suffix.lower()

        if extension not in (".jpg", ".jpeg", ".png"):
            raise forms.ValidationError(
                "Допустимы только JPG и PNG."
            )

        if avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Размер файла не должен превышать 5 МБ."
            )

        return avatar


    def save(self, commit=True):
        user = super().save(commit=commit)

        avatar = self.cleaned_data.get("avatar")

        if avatar:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.avatar = avatar
            profile.save()

        return user
