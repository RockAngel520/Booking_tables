from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""

    username = None
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        blank=True,
        null=True,
        help_text="Введите Ваше имя",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        blank=True,
        null=True,
        help_text="Введите фамилию",
    )
    email = models.EmailField(unique=True, verbose_name="Email")

    phone = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Сотрудник",
        help_text="Является ли пользователь " "сотрудником?",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
