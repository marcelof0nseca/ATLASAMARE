from django.contrib import admin

from .models import Medication


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ["patient", "name", "scheduled_for", "status"]
    list_filter = ["status"]

# Register your models here.
