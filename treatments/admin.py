from django.contrib import admin

from .models import Treatment, TreatmentStep


class TreatmentStepInline(admin.TabularInline):
    model = TreatmentStep
    extra = 0


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ["name", "patient", "is_active", "created_at"]
    list_filter = ["is_active"]
    inlines = [TreatmentStepInline]

# Register your models here.
