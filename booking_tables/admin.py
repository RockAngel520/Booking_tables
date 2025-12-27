from django.contrib import admin
from booking_tables.models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "max_guests", "description")
    list_filter = ("max_guests",)
    search_fields = ("number", "description",)
