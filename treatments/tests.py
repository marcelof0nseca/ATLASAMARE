import shutil
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from users.models import User

from .models import JourneyDocument, JourneyVideo, Treatment, TreatmentStep
from .services import complete_treatment_step, start_treatment_step


class TreatmentTransitionTests(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            email="doctor@amare.local",
            password="amare123!",
            full_name="Médica",
            role=User.Role.DOCTOR,
        )
        self.patient = User.objects.create_user(
            email="patient@amare.local",
            password="amare123!",
            full_name="Paciente",
            role=User.Role.PATIENT,
            primary_doctor=self.doctor,
        )
        self.treatment = Treatment.objects.create(patient=self.patient, name="FIV", is_active=True)
        self.first_step = TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Preparação",
            order=1,
            status=TreatmentStep.Status.PENDING,
        )
        self.second_step = TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Coleta",
            order=2,
            status=TreatmentStep.Status.PENDING,
        )

    def test_starting_first_pending_step_sets_it_in_progress(self):
        start_treatment_step(self.first_step, self.doctor)
        self.first_step.refresh_from_db()
        self.assertEqual(self.first_step.status, TreatmentStep.Status.IN_PROGRESS)

    def test_completing_current_step_promotes_next_step(self):
        start_treatment_step(self.first_step, self.doctor)
        complete_treatment_step(self.first_step, self.doctor)
        self.first_step.refresh_from_db()
        self.second_step.refresh_from_db()
        self.assertEqual(self.first_step.status, TreatmentStep.Status.COMPLETED)
        self.assertEqual(self.second_step.status, TreatmentStep.Status.IN_PROGRESS)

    def test_starting_second_step_before_first_completion_raises_error(self):
        with self.assertRaises(ValidationError):
            start_treatment_step(self.second_step, self.doctor)


class JourneyDocumentTests(TestCase):
    def setUp(self):
        self.temp_media = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.temp_media, ignore_errors=True)

        self.patient = User.objects.create_user(
            email="patient.docs@amare.local",
            password="amare123!",
            full_name="Paciente Docs",
            role=User.Role.PATIENT,
        )
        self.doctor = User.objects.create_user(
            email="doctor.docs@amare.local",
            password="amare123!",
            full_name="Medica Docs",
            role=User.Role.DOCTOR,
        )
        self.patient.primary_doctor = self.doctor
        self.patient.save()
        self.partner = User.objects.create_user(
            email="partner.docs@amare.local",
            password="amare123!",
            full_name="Parceiro Docs",
            role=User.Role.PARTNER,
            linked_patient=self.patient,
        )
        self.treatment = Treatment.objects.create(patient=self.patient, name="FIV", is_active=True)
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Semana 1",
            order=1,
            status=TreatmentStep.Status.COMPLETED,
        )
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Semana 2",
            order=2,
            status=TreatmentStep.Status.IN_PROGRESS,
        )
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Semana 3",
            order=3,
            status=TreatmentStep.Status.PENDING,
        )
        self.document = JourneyDocument.objects.create(
            treatment=self.treatment,
            name="Ultrassom.pdf",
            week=1,
            uploaded_at=timezone.now(),
            size_label="18 KB",
        )
        self.document.file.save("ultrassom.pdf", ContentFile("arquivo demo"), save=True)

    def test_patient_sees_documents_entry_and_unlocked_weeks(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:documents"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Semana 1")
        self.assertContains(response, "Desbloqueado")
        self.assertContains(response, "Bloqueado")

    def test_locked_week_redirects_without_listing_documents(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:documents-week", args=[3]))
        self.assertRedirects(response, reverse("treatments:documents"))

    def test_unlocked_week_lists_documents(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:documents-week", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ultrassom.pdf")
        self.assertContains(response, "18 KB")

    def test_partner_can_see_linked_patient_documents(self):
        self.client.force_login(self.partner)
        response = self.client.get(reverse("treatments:partner-documents-week", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ultrassom.pdf")

    def test_download_preserves_document_name(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:documents-download", args=[self.document.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ultrassom.pdf", response["Content-Disposition"])

    def test_doctor_can_manage_linked_patient_documents(self):
        self.client.force_login(self.doctor)
        response = self.client.get(reverse("treatments:doctor-documents"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ultrassom.pdf")

        upload = SimpleUploadedFile("novo.pdf", b"documento demo", content_type="application/pdf")
        response = self.client.post(
            reverse("treatments:doctor-document-create"),
            {
                "treatment": self.treatment.id,
                "name": "Novo exame.pdf",
                "week": 2,
                "uploaded_at": "2026-01-20T10:00",
                "size_label": "12 KB",
                "file": upload,
            },
        )
        self.assertRedirects(response, reverse("treatments:doctor-documents"))
        self.assertTrue(JourneyDocument.objects.filter(name="Novo exame.pdf").exists())


class JourneyVideoTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            email="patient.video@amare.local",
            password="amare123!",
            full_name="Paciente Video",
            role=User.Role.PATIENT,
        )
        self.doctor = User.objects.create_user(
            email="doctor.video@amare.local",
            password="amare123!",
            full_name="Medica Video",
            role=User.Role.DOCTOR,
        )
        self.active_video = JourneyVideo.objects.create(
            title="Preparacao para o exame",
            description="Orientacoes para esta etapa.",
            step=1,
            video_url="https://example.com/video",
            duration="4 min",
            is_active=True,
        )
        self.inactive_video = JourneyVideo.objects.create(
            title="Video interno",
            description="Conteudo ainda em revisao.",
            step=2,
            video_url="https://example.com/interno",
            is_active=False,
        )

    def test_patient_sees_only_active_videos(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:videos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preparacao para o exame")
        self.assertNotContains(response, "Video interno")

    def test_patient_cannot_open_inactive_video(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:video-detail", args=[self.inactive_video.id]))
        self.assertEqual(response.status_code, 404)

    def test_doctor_can_create_video(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("treatments:doctor-video-create"),
            {
                "title": "Aplicacao da medicacao",
                "description": "Passo a passo da aplicacao.",
                "step": 5,
                "duration": "6 min",
                "video_url": "https://example.com/medicacao",
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("treatments:doctor-videos"))
        self.assertTrue(JourneyVideo.objects.filter(title="Aplicacao da medicacao", is_active=True).exists())

    def test_doctor_can_toggle_video_status(self):
        self.client.force_login(self.doctor)
        response = self.client.post(reverse("treatments:doctor-video-toggle", args=[self.active_video.id]))
        self.assertRedirects(response, reverse("treatments:doctor-videos"))
        self.active_video.refresh_from_db()
        self.assertFalse(self.active_video.is_active)

    def test_patient_cannot_access_doctor_video_management(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("treatments:doctor-videos"))
        self.assertEqual(response.status_code, 403)
