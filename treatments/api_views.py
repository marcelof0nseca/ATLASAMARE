from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsDoctorUser, IsPatientUser

from .models import Treatment, TreatmentStep
from .serializers import TreatmentSerializer
from .services import complete_treatment_step, start_treatment_step


class CurrentTreatmentAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        treatment = Treatment.objects.filter(patient=request.user, is_active=True).prefetch_related("steps").first()
        if not treatment:
            return Response({"detail": "Tratamento ainda não iniciado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TreatmentSerializer(treatment).data)


class StartTreatmentStepAPIView(APIView):
    permission_classes = [IsDoctorUser]

    def post(self, request, treatment_id, step_id):
        step = get_object_or_404(TreatmentStep, pk=step_id, treatment_id=treatment_id)
        try:
            start_treatment_step(step=step, actor=request.user)
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(TreatmentSerializer(step.treatment).data)


class CompleteTreatmentStepAPIView(APIView):
    permission_classes = [IsDoctorUser]

    def post(self, request, treatment_id, step_id):
        step = get_object_or_404(TreatmentStep, pk=step_id, treatment_id=treatment_id)
        try:
            complete_treatment_step(step=step, actor=request.user)
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(TreatmentSerializer(step.treatment).data)
