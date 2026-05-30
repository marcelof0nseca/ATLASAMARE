from django.contrib import admin

from .models import JourneyDocument, JourneyVideo, Treatment, TreatmentStep


class TreatmentStepInline(admin.TabularInline):
    model = TreatmentStep
    extra = 0


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ["name", "patient", "is_active", "created_at"]
    list_filter = ["is_active"]
    inlines = [TreatmentStepInline]


@admin.register(JourneyDocument)
class JourneyDocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "treatment", "week", "uploaded_at", "size_label"]
    list_filter = ["week", "uploaded_at"]
    search_fields = ["name", "treatment__patient__full_name"]


@admin.register(JourneyVideo)
class JourneyVideoAdmin(admin.ModelAdmin):
    list_display = ["title", "step", "duration", "is_active", "updated_at"]
    list_filter = ["is_active", "step"]
    search_fields = ["title", "description"]

# Register your models here.
