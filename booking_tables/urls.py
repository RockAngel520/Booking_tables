from django.urls import path
from booking_tables.apps import BookingTablesConfig
from booking_tables.views import AboutTemplateView, HomeTemplateView, TableListView, BookingCreateView

app_name = BookingTablesConfig.name

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('about/', AboutTemplateView.as_view(), name='about'),
    path('tables/', TableListView.as_view(), name='tables'),
    path('booking_create/', BookingCreateView.as_view(), name='booking_create'),
]
