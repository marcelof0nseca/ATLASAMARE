from django.contrib import admin
from django.utils import timezone

from .models import CommunityPost, CommunityReaction, Partner, PatientTask, TreatmentReport


@admin.register(PatientTask)
class PatientTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "status", "due_at", "created_at")
    list_filter = ("status", "due_at")
    search_fields = ("title", "patient__full_name", "patient__email")


@admin.register(TreatmentReport)
class TreatmentReportAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "status", "released_at", "updated_at")
    list_filter = ("status", "released_at")
    search_fields = ("title", "patient__full_name", "patient__email")
    actions = ["release_reports", "lock_reports"]

    @admin.action(description="Liberar laudos selecionados")
    def release_reports(self, request, queryset):
        queryset.update(status=TreatmentReport.Status.AVAILABLE, released_at=timezone.now())

    @admin.action(description="Bloquear laudos selecionados")
    def lock_reports(self, request, queryset):
        queryset.update(status=TreatmentReport.Status.LOCKED, released_at=None)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "specialty", "is_featured", "is_active", "sort_order")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "specialty", "description", "tags")
    list_editable = ("is_featured", "is_active", "sort_order")


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("pseudonym", "category", "author", "status", "approved_at", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("body", "author__full_name", "author__email", "pseudonym")
    actions = ["approve_posts", "reject_posts"]

    @admin.action(description="Aprovar relatos selecionados")
    def approve_posts(self, request, queryset):
        queryset.update(status=CommunityPost.Status.APPROVED, approved_at=timezone.now())

    @admin.action(description="Rejeitar relatos selecionados")
    def reject_posts(self, request, queryset):
        queryset.update(status=CommunityPost.Status.REJECTED)


@admin.register(CommunityReaction)
class CommunityReactionAdmin(admin.ModelAdmin):
    list_display = ("post", "patient", "kind", "created_at")
    list_filter = ("kind", "created_at")
    search_fields = ("patient__full_name", "post__body")
