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


class PartnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and getattr(user, "role", None) == "partner"
            and user.linked_patient is not None
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_doctor:
                return redirect("users:doctor-patient-list")
            elif self.request.user.is_patient:
                return redirect("core:dashboard")
        return super().handle_no_permission()


class PatientOrPartnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and (user.is_patient or (user.is_partner and user.linked_patient is not None))
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.is_doctor:
            return redirect("users:doctor-patient-list")
        return super().handle_no_permission()
