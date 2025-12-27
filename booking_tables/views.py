from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
import datetime
import logging
from django.core.mail import send_mail
from django.contrib import messages

from booking_tables.forms import BookingForm
from booking_tables.models import Table, Booking

from config.settings import EMAIL_HOST_USER


logger = logging.getLogger(__name__)


class AboutTemplateView(TemplateView):
    template_name = 'about.html'


class HomeTemplateView(TemplateView):
    template_name = 'home.html'



class TableListView(ListView):
    model = Table
    template_name = 'tables.html'

    def get_queryset(self):
        '''Сортируем столики по порядковому номеру'''

        queryset = Table.objects.filter(is_publish=True)
        sort_by = self.request.GET.get('sort', 'number')
        queryset = queryset.order_by(sort_by)

        return queryset


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'booking_create.html'
    form_class = BookingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все доступные столики
        context['tables'] = Table.objects.filter(is_publish=True).order_by('number')
        return context

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.guest = self.request.user
        booking.save()

        self.object = booking
        
        try:
            send_mail(
                subject=f'Вы успешно забронировали столик №{booking.table.number}',
                message=f'Ждём Вас в Кафе Краснодар {booking.date} в {booking.time}. Ваш столик №'
                        f'{booking.table.number} на {booking.number_of_guests} гостей успешно забронирован.',
                from_email=EMAIL_HOST_USER,
                recipient_list=[booking.guest.email],
                fail_silently=False
            )

            messages.success(
                self.request,
                'Столик успешно забронирован! На вашу почту отправлено письмо с информацией о бронировании.'
            )

        except Exception as e:

            logger.error(f'Ошибка отправки email для пользователя {booking.guest.email}: {str(e)}')

            messages.warning(
                self.request,
                'Столик успешно забронирован, но на Вашу почту не удалось отправить письмо с информацией о '
                'бронировании.'
            )
        
        return super().form_valid(form)

    def get_success_url(self):

        if hasattr(self, 'object') and self.object and self.object.pk:
            return reverse('booking_tables:booking', kwargs={'pk': self.object.pk})

        return reverse('booking_tables:bookings')
    

@csrf_exempt
def check_table_availability(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')

        if not date_str or not time_str:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.datetime.strptime(time_str, '%H:%M').time()

            # Находим занятые столики на это время
            occupied_bookings = Booking.objects.filter(
                date=date,
                time=time
            )

            occupied_table_ids = list(occupied_bookings.values_list('table_id', flat=True))

            return JsonResponse({
                'occupied_tables': occupied_table_ids,
                'date': date_str,
                'time': time_str
            })

        except ValueError:
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset.order_by("-date", "-time")
        return queryset.filter(guest=self.request.user).order_by("-date", "-time")


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'booking.html'

    def get_object(self, queryset=None):
        '''Проверяем, что бронирование принадлежит текущему пользователю или персоналу'''

        booking = get_object_or_404(Booking, id=self.kwargs.get('pk'))

        if booking.guest != self.request.user and self.request.user.is_staff == False:
            from django.http import Http404
            raise Http404("Бронирование не найдено")

        return booking


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    template_name = 'booking_update.html'
    form_class = BookingForm
    success_url = reverse_lazy('booking_tables:bookings')

    def get_success_url(self):
        return reverse('booking_tables:booking', args=[self.kwargs.get('pk')])

    def get_form_class(self):
        user = self.request.user
        if user == self.object.guest or self.request.user.is_staff:
            return BookingForm
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все доступные столики
        context['tables'] = Table.objects.filter(is_publish=True).order_by('number')
        return context

    def form_valid(self, form):
        booking = form.save(commit=False)

        try:
            send_mail(
                subject=f'Ваше бронирование изменено',
                message=f'Ждём Вас в Кафе Краснодар {booking.date} в {booking.time}. Ваш столик №'
                        f'{booking.table.number} на {booking.number_of_guests} гостей успешно забронирован.',
                from_email=EMAIL_HOST_USER,
                recipient_list=[booking.guest.email],
                fail_silently=False
            )

            messages.success(
                self.request,
                'Столик успешно забронирован! На вашу почту отправлено письмо с информацией о бронировании.'
            )

        except Exception as e:

            logger.error(f'Ошибка отправки email для пользователя {booking.guest.email}: {str(e)}')

            messages.warning(
                self.request,
                'Столик успешно забронирован, но на Вашу почту не удалось отправить письмо с информацией о '
                'бронировании.'
            )

        return super().form_valid(form)


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'booking_confirm_delete.html'
    success_url = reverse_lazy('booking_tables:home')

    def get_object(self, queryset=None):
        '''Проверяем, что бронирование принадлежит текущему пользователю или персоналу'''

        booking = get_object_or_404(Booking, id=self.kwargs.get('pk'))

        if booking.guest != self.request.user and self.request.user.is_staff == False:
            from django.http import Http404
            raise Http404("Бронирование не найдено")

        return booking

    def form_valid(self, form):

        booking = get_object_or_404(Booking, id=self.kwargs.get('pk'))

        try:
            send_mail(
                subject=f'Ваша бронирование отменено',
                message=f'Ваша бронь в Кафе Краснодар отменена.',
                from_email=EMAIL_HOST_USER,
                recipient_list=[booking.guest.email],
                fail_silently=False
            )

            messages.success(
                self.request,
                'Ваша бронь отменена.'
            )

        except Exception as e:

            logger.error(f'Ошибка отправки email для пользователя {booking.guest.email}: {str(e)}')

            messages.warning(
                self.request,
                'Ваша бронь отменена.'
            )

        return super().form_valid(form)
