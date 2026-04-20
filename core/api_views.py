from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsPatientUser

from .services import build_patient_dashboard


class DashboardAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        dashboard = build_patient_dashboard(request.user)
        payload = {
            "current_step": dashboard["current_step"].name if dashboard["current_step"] else None,
            "next_step": dashboard["next_step"].name if dashboard["next_step"] else None,
            "appointments_count": dashboard["appointments"].count(),
            "medications_today_count": dashboard["medications_today"].count(),
        }
        return Response(payload)
