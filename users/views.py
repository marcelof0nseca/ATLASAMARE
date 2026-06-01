from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, UpdateView, View

from core.mixins import DoctorRequiredMixin
from core.models import CommunityPost

from .forms import (
    ChangePasswordForm,
    DoctorPatientCreateForm,
    ProfilePushForm,
    LoginForm,
    PasswordResetRequestForm,
    ProfileEmergencyForm,
    ProfileForm,
    ProfileNameForm,
    ProfileNotificationsForm,
    ProfilePersonalForm,
)
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        # handle avatar separately so existing avatar isn't cleared when not re-uploading
        if not request.FILES.get("avatar") and self.object.avatar:
            form.fields["avatar"].required = False
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["files"] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Suas preferências foram atualizadas com cuidado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "profile"
        context["form"] = ProfileForm(instance=self.request.user)
        if self.request.user.is_patient:
            context["community_posts"] = CommunityPost.objects.filter(author=self.request.user)[:5]
        return context


_SECTION_FORMS = {
    "name":          ProfileNameForm,
    "personal":      ProfilePersonalForm,
    "emergency":     ProfileEmergencyForm,
    "notifications": ProfileNotificationsForm,
    "push":          ProfilePushForm,
}


class ProfileSectionView(LoginRequiredMixin, View):
    def post(self, request, section):
        form_class = _SECTION_FORMS.get(section)
        if not form_class:
            return redirect("users:profile")
        form = form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Atualizado com sucesso.")
        else:
            for errs in form.errors.values():
                for e in errs:
                    messages.error(request, e)
        return redirect("users:profile")


class ChangePasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save(request)
            messages.success(request, "Senha alterada com sucesso.")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
        return redirect("users:profile")


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


class DoctorPatientCreateView(DoctorRequiredMixin, FormView):
    template_name = "doctor/patient_form.html"
    form_class = DoctorPatientCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["doctor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        patient = form.save()
        messages.success(self.request, "Paciente cadastrada e vinculada a voce.")
        return HttpResponseRedirect(reverse("users:doctor-patient-detail", args=[patient.id]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "new-patient"
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
