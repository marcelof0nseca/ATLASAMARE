from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class RoleRedirectMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_doctor:
            return redirect("users:doctor-patient-list")
        return super().dispatch(request, *args, **kwargs)


class PatientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_patient

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.is_doctor:
            return redirect(reverse("users:doctor-patient-list"))
        return super().handle_no_permission()


class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_doctor
