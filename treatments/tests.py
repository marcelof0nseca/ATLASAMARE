from django.core.exceptions import ValidationError
from django.test import TestCase

from users.models import User

from .models import Treatment, TreatmentStep
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
