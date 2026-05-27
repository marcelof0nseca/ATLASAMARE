from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

from .models import CommunityPost, CommunityReaction, PatientTask, TreatmentReport
from users.models import User


class RootRedirectTests(TestCase):
    def test_patient_is_redirected_to_dashboard(self):
        patient = User.objects.create_user(
            email="patient@amare.local",
            password="amare123!",
            full_name="Paciente",
            role=User.Role.PATIENT,
        )
        self.client.force_login(patient)
        response = self.client.get("/")
        self.assertRedirects(response, "/dashboard/")


class PatientExperienceTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            email="patient2@amare.local",
            password="amare123!",
            full_name="Paciente Dois",
            role=User.Role.PATIENT,
        )
        self.client.force_login(self.patient)

    def test_patient_can_create_and_complete_personal_task(self):
        response = self.client.post(
            reverse("core:task-create"),
            {"title": "Separar exames", "notes": "Levar documentos"},
        )
        self.assertRedirects(response, reverse("core:routine"))
        task = PatientTask.objects.get(patient=self.patient, title="Separar exames")

        response = self.client.post(reverse("core:task-complete", args=[task.id]))
        self.assertRedirects(response, reverse("core:routine"))
        task.refresh_from_db()
        self.assertEqual(task.status, PatientTask.Status.COMPLETED)

    def test_community_post_starts_pending_and_reaction_is_unique(self):
        response = self.client.post(
            reverse("core:community-create"),
            {"category": CommunityPost.Category.FEELINGS, "body": "Uma coisa por vez me ajudou hoje."},
        )
        self.assertRedirects(response, reverse("core:community"))
        post = CommunityPost.objects.get(author=self.patient)
        self.assertEqual(post.status, CommunityPost.Status.PENDING)

        post.status = CommunityPost.Status.APPROVED
        post.save(update_fields=["status"])
        self.client.post(reverse("core:community-react", args=[post.id]))
        self.client.post(reverse("core:community-react", args=[post.id]))
        self.assertEqual(CommunityReaction.objects.filter(post=post, patient=self.patient).count(), 1)

    def test_locked_report_does_not_download_and_available_report_does(self):
        locked = TreatmentReport.objects.create(patient=self.patient, title="Laudo")
        response = self.client.get(reverse("core:report-download", args=[locked.id]))
        self.assertEqual(response.status_code, 404)

        available = TreatmentReport.objects.create(
            patient=self.patient,
            title="Laudo liberado",
            status=TreatmentReport.Status.AVAILABLE,
        )
        available.file.save("laudo.txt", ContentFile("conteudo"), save=True)
        response = self.client.get(reverse("core:report-download", args=[available.id]))
        self.assertEqual(response.status_code, 200)
