from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsDoctorUser
from .serializers import PatientSummarySerializer, UserSerializer
from .services import build_doctor_patient_context, get_managed_patient


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"detail": "Não conseguimos entrar com esses dados."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        login(request, user)
        return Response({"user": UserSerializer(user).data, "redirect_url": reverse_landing(user)})


class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    def get(self, request):
        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            return Response({"detail": "Autenticação necessária."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserSerializer(request.user).data)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "detail": "Se esse email estiver cadastrado, você receberá as próximas orientações em breve."
            }
        )


class DoctorPatientsAPIView(APIView):
    permission_classes = [IsDoctorUser]

    def get(self, request):
        patients = User.objects.filter(role=User.Role.PATIENT, primary_doctor=request.user)
        return Response(PatientSummarySerializer(patients, many=True).data)


class DoctorPatientDetailAPIView(APIView):
    permission_classes = [IsDoctorUser]

    def get(self, request, pk):
        try:
            patient = get_managed_patient(request.user, pk)
        except Http404 as exc:
            raise Http404(str(exc))
        context = build_doctor_patient_context(patient)
        return Response(
            {
                "patient": UserSerializer(patient).data,
                "current_step": context["current_step"].name if context["current_step"] else None,
                "next_step": context["next_step"].name if context["next_step"] else None,
                "appointments_count": context["appointments"].count(),
            }
        )


def reverse_landing(user: User) -> str:
    return "/doctor/patients/" if user.is_doctor else "/dashboard/"
