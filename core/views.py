from datetime import datetime, time

from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView

from .forms import CommunityPostForm, PatientTaskForm
from .mixins import PatientRequiredMixin
from .models import CommunityPost, CommunityReaction, Partner, PatientTask, TreatmentReport
from .services import build_patient_dashboard, build_patient_routine, get_explore_context


class LandingView(TemplateView):
    template_name = "landing/index.html"


class RootRedirectView(RedirectView):
    pattern_name = "core:landing"

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.is_doctor:
                return "/doctor/patients/"
            return "/dashboard/"
        return "/landing/"


class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = "patient/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_patient_dashboard(self.request.user))
        context["active_nav"] = "home"
        return context


class PatientRoutineView(PatientRequiredMixin, TemplateView):
    template_name = "patient/routine.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_patient_routine(self.request.user))
        context["task_form"] = PatientTaskForm()
        context["active_nav"] = "routine"
        return context


class PatientTaskCreateView(PatientRequiredMixin, RedirectView):
    pattern_name = "core:routine"

    def post(self, request, *args, **kwargs):
        form = PatientTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.patient = request.user
            task.due_at = _build_due_at(form.cleaned_data.get("due_date"), form.cleaned_data.get("due_time"))
            task.save()
            messages.success(request, "Tarefa adicionada a sua rotina.")
        else:
            messages.error(request, "Nao foi possivel criar essa tarefa agora.")
        return redirect("core:routine")


class PatientTaskUpdateView(PatientRequiredMixin, RedirectView):
    pattern_name = "core:routine"

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(PatientTask, pk=pk, patient=request.user)
        form = PatientTaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save(commit=False)
            updated_task.due_at = _build_due_at(form.cleaned_data.get("due_date"), form.cleaned_data.get("due_time"))
            updated_task.save()
            messages.success(request, "Tarefa atualizada.")
        else:
            messages.error(request, "Nao foi possivel atualizar essa tarefa.")
        return redirect("core:routine")


class PatientTaskCompleteView(PatientRequiredMixin, RedirectView):
    pattern_name = "core:routine"

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(PatientTask, pk=pk, patient=request.user)
        task.complete()
        messages.success(request, "Tarefa concluida.")
        return redirect("core:routine")


class ExploreHomeView(PatientRequiredMixin, TemplateView):
    template_name = "patient/explore.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_explore_context(self.request.user))
        context["active_nav"] = "explore"
        return context


class PartnerListView(PatientRequiredMixin, TemplateView):
    template_name = "patient/partners.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_category = self.request.GET.get("category", "").strip()
        partners = Partner.objects.filter(is_active=True)
        if selected_category:
            partners = partners.filter(category=selected_category)
        context.update(
            {
                "partners": partners,
                "categories": Partner.Category.choices,
                "selected_category": selected_category,
                "active_nav": "explore",
            }
        )
        return context


class CommunityFeedView(PatientRequiredMixin, TemplateView):
    template_name = "patient/community.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = CommunityPost.objects.filter(status=CommunityPost.Status.APPROVED).prefetch_related("reactions")
        my_reactions = set(
            CommunityReaction.objects.filter(patient=self.request.user, post__in=posts).values_list("post_id", flat=True)
        )
        context.update(
            {
                "posts": posts,
                "post_form": CommunityPostForm(),
                "my_pending_posts": CommunityPost.objects.filter(
                    author=self.request.user,
                    status=CommunityPost.Status.PENDING,
                ),
                "my_reactions": my_reactions,
                "active_nav": "explore",
            }
        )
        return context


class CommunityPostCreateView(PatientRequiredMixin, RedirectView):
    pattern_name = "core:community"

    def post(self, request, *args, **kwargs):
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pseudonym = "Paciente AMARE"
            post.status = CommunityPost.Status.PENDING
            post.save()
            messages.success(request, "Seu relato foi enviado para revisao antes de aparecer na comunidade.")
        else:
            messages.error(request, "Revise o relato antes de enviar.")
        return redirect("core:community")


class CommunityReactView(PatientRequiredMixin, RedirectView):
    pattern_name = "core:community"

    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(CommunityPost, pk=pk, status=CommunityPost.Status.APPROVED)
        CommunityReaction.objects.get_or_create(post=post, patient=request.user)
        messages.success(request, "Seu apoio foi registrado.")
        return redirect("core:community")


class ReportDownloadView(PatientRequiredMixin, RedirectView):
    pattern_name = "treatments:timeline"

    def get(self, request, pk, *args, **kwargs):
        report = get_object_or_404(TreatmentReport, pk=pk, patient=request.user)
        if not report.is_available:
            raise Http404("Laudo ainda nao liberado.")
        return FileResponse(report.file.open("rb"), as_attachment=True, filename=report.file.name.split("/")[-1])


def _build_due_at(due_date, due_time):
    if not due_date:
        return None
    due_time = due_time or time(hour=9)
    return timezone.make_aware(datetime.combine(due_date, due_time))
