from django.contrib.auth.forms import UserCreationForm

from booking_tables.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Форма регистрации пользователя"""

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
