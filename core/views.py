from django.shortcuts import redirect
from django.views.generic import RedirectView, TemplateView

from .mixins import PatientRequiredMixin
from .services import build_patient_dashboard


class RootRedirectView(RedirectView):
    pattern_name = "users:login"

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return super().get_redirect_url(*args, **kwargs)
        if user.is_doctor:
            return "/doctor/patients/"
        return "/dashboard/"


class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = "patient/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_patient_dashboard(self.request.user))
        context["active_nav"] = "home"
        return context

# Create your views here.
