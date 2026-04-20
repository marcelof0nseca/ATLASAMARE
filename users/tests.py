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
