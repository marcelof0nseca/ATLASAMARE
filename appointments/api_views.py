from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsPatientUser

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentListAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        appointments = Appointment.objects.filter(patient=request.user).order_by("scheduled_at")
        return Response(AppointmentSerializer(appointments, many=True).data)
