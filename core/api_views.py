from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsPatientUser

from .models import CommunityPost, CommunityReaction, Partner, PatientTask, TreatmentReport
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


class PatientTaskListCreateAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        tasks = PatientTask.objects.filter(patient=request.user)
        return Response(
            [
                {
                    "id": task.id,
                    "title": task.title,
                    "notes": task.notes,
                    "due_at": task.due_at,
                    "status": task.status,
                    "completed_at": task.completed_at,
                }
                for task in tasks
            ]
        )

    def post(self, request):
        title = str(request.data.get("title", "")).strip()
        if not title:
            return Response({"detail": "Informe uma tarefa."}, status=400)
        task = PatientTask.objects.create(
            patient=request.user,
            title=title[:120],
            notes=str(request.data.get("notes", "")).strip()[:220],
        )
        return Response({"id": task.id, "title": task.title, "status": task.status}, status=201)


class PartnerListAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        partners = Partner.objects.filter(is_active=True)
        category = request.query_params.get("category")
        if category:
            partners = partners.filter(category=category)
        return Response(
            [
                {
                    "id": partner.id,
                    "name": partner.name,
                    "category": partner.category,
                    "category_label": partner.get_category_display(),
                    "specialty": partner.specialty,
                    "description": partner.description,
                    "tags": partner.tag_list,
                    "contact_label": partner.contact_label,
                    "contact_url": partner.contact_url,
                }
                for partner in partners
            ]
        )


class CommunityPostListCreateAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        posts = CommunityPost.objects.filter(status=CommunityPost.Status.APPROVED).prefetch_related("reactions")
        return Response(
            [
                {
                    "id": post.id,
                    "category": post.category,
                    "category_label": post.get_category_display(),
                    "body": post.body,
                    "pseudonym": post.pseudonym,
                    "support_count": post.support_count,
                    "approved_at": post.approved_at,
                }
                for post in posts
            ]
        )

    def post(self, request):
        body = str(request.data.get("body", "")).strip()
        category = str(request.data.get("category", CommunityPost.Category.FEELINGS)).strip()
        if not body:
            return Response({"detail": "Escreva um relato antes de enviar."}, status=400)
        if category not in CommunityPost.Category.values:
            category = CommunityPost.Category.FEELINGS
        post = CommunityPost.objects.create(
            author=request.user,
            category=category,
            body=body[:900],
            pseudonym="Paciente AMARE",
        )
        return Response({"id": post.id, "status": post.status}, status=201)


class CommunityReactionAPIView(APIView):
    permission_classes = [IsPatientUser]

    def post(self, request, pk):
        post = CommunityPost.objects.filter(pk=pk, status=CommunityPost.Status.APPROVED).first()
        if not post:
            return Response({"detail": "Relato nao encontrado."}, status=404)
        CommunityReaction.objects.get_or_create(post=post, patient=request.user)
        return Response({"support_count": post.reactions.count()})


class CurrentReportAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        report = TreatmentReport.objects.filter(patient=request.user).first()
        if not report:
            return Response({"detail": "Nenhum laudo cadastrado."}, status=404)
        return Response(
            {
                "id": report.id,
                "title": report.title,
                "status": report.status,
                "is_available": report.is_available,
                "released_at": report.released_at,
                "release_note": report.release_note,
            }
        )
