from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, UpdateView, View

from core.mixins import DoctorRequiredMixin

from .forms import LoginForm, PasswordResetRequestForm, ProfileForm
from .models import User
from .services import build_doctor_patient_context, get_managed_patient


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("core:root")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:root")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(self.request, "Que bom ter você por aqui. Sua área está pronta.")
        return super().form_valid(form)


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Seu acesso foi encerrado com segurança.")
        return redirect("users:login")


class PasswordResetRequestView(FormView):
    template_name = "auth/password_reset_request.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("users:password-reset-request")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Se esse email estiver cadastrado, você receberá as próximas orientações em breve.",
        )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "patient/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Suas preferências foram atualizadas com cuidado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "profile"
        return context


class DoctorPatientListView(DoctorRequiredMixin, ListView):
    template_name = "doctor/patients_list.html"
    context_object_name = "patients"
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        queryset = User.objects.filter(role=User.Role.PATIENT, primary_doctor=self.request.user)
        if query:
            queryset = queryset.filter(Q(full_name__icontains=query) | Q(email__icontains=query))
        return queryset.order_by("full_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["active_nav"] = "patients"
        return context


class DoctorPatientDetailView(DoctorRequiredMixin, DetailView):
    template_name = "doctor/patient_detail.html"
    context_object_name = "patient"

    def get_object(self, queryset=None):
        return get_managed_patient(self.request.user, self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_doctor_patient_context(self.object))
        context["active_nav"] = "patients"
        return context

# Create your views here.
