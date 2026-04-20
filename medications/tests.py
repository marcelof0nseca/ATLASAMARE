from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from users.models import User

from .models import Medication
from .services import complete_medication_dose


class MedicationCompletionTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            email="patient@amare.local",
            password="amare123!",
            full_name="Paciente",
            role=User.Role.PATIENT,
        )
        self.medication = Medication.objects.create(
            patient=self.patient,
            name="Progesterona",
            scheduled_for=timezone.now(),
        )

    def test_medication_can_only_be_completed_once(self):
        complete_medication_dose(self.medication, self.patient)
        self.medication.refresh_from_db()
        self.assertEqual(self.medication.status, Medication.Status.COMPLETED)

        with self.assertRaises(ValidationError):
            complete_medication_dose(self.medication, self.patient)
