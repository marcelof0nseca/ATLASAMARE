from django.test import TestCase

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
