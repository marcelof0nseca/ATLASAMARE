from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsPatientUser

from .models import Medication
from .serializers import MedicationSerializer
from .services import complete_medication_dose


class MedicationListAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        medications = Medication.objects.filter(patient=request.user).order_by("scheduled_for")
        return Response(MedicationSerializer(medications, many=True).data)


class MedicationCompleteAPIView(APIView):
    permission_classes = [IsPatientUser]

    def post(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk, patient=request.user)
        try:
            complete_medication_dose(medication=medication, actor=request.user)
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(MedicationSerializer(medication).data)
