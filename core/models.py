from django.conf import settings
from django.db import models
import uuid
from pathlib import Path

def avatar_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"avatars/{uuid.uuid4().hex}{extension}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь"
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        verbose_name="Аватар"
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"