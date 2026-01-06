from django.contrib import admin

from booking_tables.models import Booking, Table, Staff


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "max_guests", "description")
    list_filter = ("max_guests",)
    search_fields = (
        "number",
        "description",
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("guest", "number_of_guests", "date", "time", "created_at", "table")
    list_filter = ("table",)
    search_fields = (
        "guest",
        "comment",
    )


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("job_title", "full_name")
    search_fields = (
        "job_title",
        "full_name",
    )
