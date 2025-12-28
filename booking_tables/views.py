import datetime
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from booking_tables.forms import BookingForm
from booking_tables.models import Booking, Table
from config.settings import EMAIL_HOST_USER

logger = logging.getLogger(__name__)


class AboutTemplateView(TemplateView):
    """Страница о ресторане"""

    template_name = "about.html"


class HomeTemplateView(TemplateView):
    """Главная страница ресторана"""

    template_name = "home.html"


class TableListView(ListView):
    """Страница со списком столиков"""

    model = Table
    template_name = "tables.html"

    def get_queryset(self):
        """Сортируем столики по порядковому номеру"""

        queryset = Table.objects.filter(is_publish=True)
        sort_by = self.request.GET.get("sort", "number")
        queryset = queryset.order_by(sort_by)

        return queryset


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Станица нового бронирования"""

    model = Booking
    template_name = "booking_create.html"
    form_class = BookingForm

    def get_context_data(self, **kwargs):
        """Получаем все доступные столики и сортируем по номеру"""

        context = super().get_context_data(**kwargs)
        context["tables"] = Table.objects.filter(is_publish=True).order_by("number")
        return context

    def form_valid(self, form):
        """При успешном заполнении формы отправляем сообщение на почту и выводим сообщение на сайте"""

        booking = form.save(commit=False)
        booking.guest = self.request.user
        booking.save()

        self.object = booking

        try:
            send_mail(
                subject=f"Вы успешно забронировали столик №{booking.table.number}",
                message=f"Ждём Вас в Кафе Краснодар {booking.date} в {booking.time}. Ваш столик №"
                f"{booking.table.number} на {booking.number_of_guests} гостей успешно забронирован.",
                from_email=EMAIL_HOST_USER,
                recipient_list=[booking.guest.email],
                fail_silently=False,
            )

            messages.success(
                self.request,
                "Столик успешно забронирован! На вашу почту отправлено письмо с информацией о бронировании.",
            )

        except Exception as e:

            logger.error(
                f"Ошибка отправки email для пользователя {booking.guest.email}: {str(e)}"
            )

            messages.warning(
                self.request,
                "Столик успешно забронирован, но на Вашу почту не удалось отправить письмо с информацией о "
                "бронировании.",
            )

        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляем после"""

        if hasattr(self, "object") and self.object and self.object.pk:
            return reverse("booking_tables:booking", kwargs={"pk": self.object.pk})

        return reverse("booking_tables:bookings")


@csrf_exempt
def check_table_availability(request):
    """Проверка доступности столиков"""
    if request.method == "GET":
        date_str = request.GET.get("date")
        time_str = request.GET.get("time")

        if not date_str or not time_str:
            return JsonResponse({"error": "Missing parameters"}, status=400)

        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.datetime.strptime(time_str, "%H:%M").time()

            # Находим занятые столики на это время
            occupied_bookings = Booking.objects.filter(date=date, time=time)

            occupied_table_ids = list(
                occupied_bookings.values_list("table_id", flat=True)
            )

            return JsonResponse(
                {
                    "occupied_tables": occupied_table_ids,
                    "date": date_str,
                    "time": time_str,
                }
            )

        except ValueError:
            return JsonResponse({"error": "Invalid date or time format"}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


class BookingListView(LoginRequiredMixin, ListView):
    """Страница со списком броней"""

    model = Booking
    template_name = "bookings.html"

    def get_queryset(self):
        """Отбор и сортировка списка броней"""

        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset.order_by("-date", "-time")
        return queryset.filter(guest=self.request.user).order_by("-date", "-time")


class BookingDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница бронирования"""

    model = Booking
    template_name = "booking.html"

    def get_object(self, queryset=None):
        """Проверяем, что бронирование принадлежит текущему пользователю или персоналу"""

        booking = get_object_or_404(Booking, id=self.kwargs.get("pk"))

        if booking.guest != self.request.user and self.request.user.is_staff is False:
            from django.http import Http404

            raise Http404("Бронирование не найдено")

        return booking


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования брони"""

    model = Booking
    template_name = "booking_update.html"
    form_class = BookingForm
    success_url = reverse_lazy("booking_tables:bookings")

    def get_success_url(self):
        """Перенаправляем после"""

        return reverse("booking_tables:booking", args=[self.kwargs.get("pk")])

    def get_form_class(self):
        """Получение формы бронирования"""

        user = self.request.user
        if user == self.object.guest or self.request.user.is_staff:
            return BookingForm
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        """Получаем все доступные столики и сортируем по номеру"""

        context = super().get_context_data(**kwargs)
        context["tables"] = Table.objects.filter(is_publish=True).order_by("number")
        return context

    def form_valid(self, form):
        """При успешном заполнении формы отправляем сообщение на почту и выводим сообщение на сайте"""

        booking = form.save(commit=False)

        try:
            send_mail(
                subject="Ваше бронирование изменено",
                message=f"Ждём Вас в Кафе Краснодар {booking.date} в {booking.time}. Ваш столик №"
                f"{booking.table.number} на {booking.number_of_guests} гостей успешно забронирован.",
                from_email=EMAIL_HOST_USER,
                recipient_list=[booking.guest.email],
                fail_silently=False,
            )

            messages.success(
                self.request,
                "Столик успешно забронирован! На вашу почту отправлено письмо с информацией о бронировании.",
            )

        except Exception as e:

            logger.error(
                f"Ошибка отправки email для пользователя {booking.guest.email}: {str(e)}"
            )

            messages.warning(
                self.request,
                "Столик успешно забронирован, но на Вашу почту не удалось отправить письмо с информацией о "
                "бронировании.",
            )

        return super().form_valid(form)


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    """Страница подтверждения удаления брони"""

    model = Booking
    template_name = "booking_confirm_delete.html"
    success_url = reverse_lazy("booking_tables:home")

    def get_object(self, queryset=None):
        """Проверяем, что бронирование принадлежит текущему пользователю или персоналу"""

        booking = get_object_or_404(Booking, id=self.kwargs.get("pk"))

        if booking.guest != self.request.user and self.request.user.is_staff is False:
            from django.http import Http404

            raise Http404("Бронирование не найдено")

        return booking

    def form_valid(self, form):
        """При успешном выполнении отправляем сообщение на почту и выводим сообщение на сайте"""

        booking = get_object_or_404(Booking, id=self.kwargs.get("pk"))

        try:
            send_mail(
                subject="Ваша бронирование отменено",
                message="Ваша бронь в Кафе Краснодар отменена.",
                from_email=EMAIL_HOST_USER,
                recipient_list=[booking.guest.email],
                fail_silently=False,
            )

            messages.success(self.request, "Ваша бронь отменена.")

        except Exception as e:

            logger.error(
                f"Ошибка отправки email для пользователя {booking.guest.email}: {str(e)}"
            )

            messages.warning(self.request, "Ваша бронь отменена.")

        return super().form_valid(form)
