from django.urls import path
from booking_tables.apps import BookingTablesConfig
from booking_tables.views import AboutTemplateView, HomeTemplateView, TableListView, BookingCreateView, \
    BookingListView, BookingDetailView, BookingUpdateView, BookingDeleteView
from . import views

app_name = BookingTablesConfig.name

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('about/', AboutTemplateView.as_view(), name='about'),
    path('tables/', TableListView.as_view(), name='tables'),
    path('bookings/', BookingListView.as_view(), name='bookings'),
    path('booking/<int:pk>/', (BookingDetailView.as_view()), name='booking'),
    path('booking_update/<int:pk>/', BookingUpdateView.as_view(), name='booking_update'),
    path('booking_confirm_delete/<int:pk>/', BookingDeleteView.as_view(), name='booking_confirm_delete'),
    path('booking_create/', BookingCreateView.as_view(), name='booking_create'),
    path('api/check-table-availability/', views.check_table_availability, name='check_table_availability'),
]
