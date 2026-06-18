from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import PatientTask
from medications.models import Medication
from treatments.models import Treatment, TreatmentStep
from .models import User


class DoctorPatientPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.other_patient = User.objects.create_user(
            email="other@amare.local",
            password="amare123!",
            full_name="Outra Paciente",
            role=User.Role.PATIENT,
        )

    def test_doctor_sees_only_managed_patients_in_api(self):
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get("/api/v1/doctor/patients")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.patient.id)

    def test_doctor_cannot_access_unmanaged_patient_detail(self):
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get(f"/api/v1/doctor/patients/{self.other_patient.id}")
        self.assertEqual(response.status_code, 404)

    def test_doctor_can_create_patient_linked_to_self(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            "/doctor/patients/new/",
            {
                "full_name": "Nova Paciente",
                "email": "nova@amare.local",
                "initial_password": "amare123!",
                "wants_in_app_reminders": "on",
            },
        )

        patient = User.objects.get(email="nova@amare.local")
        self.assertRedirects(response, f"/doctor/patients/{patient.id}/")
        self.assertEqual(patient.role, User.Role.PATIENT)
        self.assertEqual(patient.primary_doctor, self.doctor)
        self.assertTrue(patient.check_password("amare123!"))

    def test_patient_cannot_create_patient_from_doctor_area(self):
        self.client.force_login(self.patient)
        response = self.client.get("/doctor/patients/new/")
        self.assertEqual(response.status_code, 403)

    def test_doctor_can_create_partner_linked_to_managed_patient(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("users:doctor-partner-create", args=[self.patient.id]),
            {
                "full_name": "Acompanhante da Paciente",
                "email": "acompanhante@amare.local",
                "phone": "(81) 99999-9999",
                "initial_password": "amare123!",
                "wants_in_app_reminders": "on",
            },
        )

        partner = User.objects.get(email="acompanhante@amare.local")
        self.assertRedirects(response, reverse("users:doctor-patient-detail", args=[self.patient.id]))
        self.assertEqual(partner.role, User.Role.PARTNER)
        self.assertEqual(partner.linked_patient, self.patient)
        self.assertTrue(partner.check_password("amare123!"))

    def test_doctor_cannot_create_partner_for_unmanaged_patient(self):
        self.client.force_login(self.doctor)
        response = self.client.get(reverse("users:doctor-partner-create", args=[self.other_patient.id]))
        self.assertEqual(response.status_code, 404)

    def test_patient_cannot_create_partner_from_doctor_area(self):
        self.client.force_login(self.patient)
        response = self.client.get(reverse("users:doctor-partner-create", args=[self.patient.id]))
        self.assertEqual(response.status_code, 403)

    def test_patient_detail_lists_linked_partner(self):
        partner = User.objects.create_user(
            email="linked-partner@amare.local",
            password="amare123!",
            full_name="Acompanhante Vinculado",
            role=User.Role.PARTNER,
            linked_patient=self.patient,
        )
        self.client.force_login(self.doctor)

        response = self.client.get(reverse("users:doctor-patient-detail", args=[self.patient.id]))

        self.assertContains(response, partner.full_name)
        self.assertContains(response, partner.email)
        self.assertContains(response, "Criar acesso")

    def test_partner_email_must_be_unique(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("users:doctor-partner-create", args=[self.patient.id]),
            {
                "full_name": "Email Repetido",
                "email": self.patient.email,
                "initial_password": "amare123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertFalse(User.objects.filter(full_name="Email Repetido").exists())


class PartnerModeTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            email="patient@amare.local",
            password="amare123!",
            full_name="Ana Beatriz",
            role=User.Role.PATIENT,
        )
        self.partner = User.objects.create_user(
            email="joao@amare.local",
            password="amare123!",
            full_name="João Santos",
            role=User.Role.PARTNER,
            linked_patient=self.patient,
        )
        self.treatment = Treatment.objects.create(
            patient=self.patient,
            name="Fertilização in vitro",
            is_active=True,
        )
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Coleta de óvulos",
            order=1,
            status=TreatmentStep.Status.IN_PROGRESS,
        )
        self.medication = Medication.objects.create(
            patient=self.patient,
            name="Progesterona",
            scheduled_for=timezone.now(),
        )

    def test_partner_properties(self):
        self.assertTrue(self.partner.is_partner)
        self.assertFalse(self.partner.is_patient)
        self.assertEqual(self.partner.linked_patient, self.patient)

    def test_partner_dashboard_access(self):
        self.client.force_login(self.partner)
        response = self.client.get(reverse("partner:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "João Santos")
        self.assertContains(response, "Ana Beatriz")

    def test_partner_profile_uses_settings_layout(self):
        self.client.force_login(self.partner)
        response = self.client.get(reverse("partner:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Foto e nome")
        self.assertContains(response, "Paciente acompanhada")
        self.assertContains(response, "Ana Beatriz")

    def test_partner_profile_section_redirects_to_partner_profile(self):
        self.client.force_login(self.partner)
        response = self.client.post(
            reverse("users:profile-update", args=["personal"]),
            {"phone": "(81) 98888-7777", "date_of_birth": ""},
        )
        self.assertRedirects(response, reverse("partner:profile"))
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.phone, "(81) 98888-7777")

    def test_partner_cannot_access_patient_dashboard(self):
        self.client.force_login(self.partner)
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 403)

    def test_partner_routine_unexpected_symptoms(self):
        self.client.force_login(self.partner)
        response = self.client.post(
            reverse("partner:routine"),
            {"unexpected_symptoms": "Dor de cabeça moderada no fim da tarde"}
        )
        self.assertRedirects(response, reverse("partner:routine"))
        task = PatientTask.objects.get(patient=self.patient)
        self.assertEqual(task.notes, "Dor de cabeça moderada no fim da tarde")
        self.assertEqual(task.title, "Sintoma inesperado registrado pelo acompanhante")

    def test_partner_can_confirm_medication(self):
        self.client.force_login(self.partner)
        response = self.client.get(reverse("medications:confirm", args=[self.medication.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("medications:complete", args=[self.medication.id]))
        self.assertRedirects(response, reverse("partner:routine"))
        self.medication.refresh_from_db()
        self.assertEqual(self.medication.status, Medication.Status.COMPLETED)

