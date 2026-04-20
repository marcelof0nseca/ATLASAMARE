from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["patient", "type", "scheduled_at"]
    list_filter = ["type"]

# Register your models here.
