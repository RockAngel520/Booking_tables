from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView

from booking_tables.forms import BookingForm
from booking_tables.models import Table, Booking


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
    success_url = reverse_lazy('booking_tables:home')

    def form_valid(self, form):
        booking = form.save()
        user = self.request.user
        booking.guest = user
        booking.save()
        return super().form_valid(form)
