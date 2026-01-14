import logging

from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm
from users.models import User

logger = logging.getLogger(__name__)


class UserCreateView(CreateView):
    """Страница регистрации"""

    model = User
    template_name = "register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """При успешной регистрации - отправляется сообщение на почту"""

        user = form.save()

        try:
            send_mail(
                subject="Вы зарегистрированы на сайте Кафе Краснодар",
                message="Спасибо, что зарегистрировались в нашем сервисе бронирования столиков!",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(
                self.request,
                "Регистрация успешна! На вашу почту отправлено письмо. "
                "Вы можете войти в систему бронирования.",
            )

        except Exception as e:

            logger.error(
                f"Ошибка отправки email для пользователя {user.email}: {str(e)}"
            )

            messages.warning(
                self.request,
                "Регистрация успешна, но не удалось отправить приветственное письмо. "
                "Вы можете войти в систему бронирования.",
            )

        return super().form_valid(form)
