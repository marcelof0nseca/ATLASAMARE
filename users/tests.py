from django.test import TestCase
from rest_framework.test import APIClient

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
