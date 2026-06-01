from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

from .models import CommunityPost, CommunityReaction, PatientTask, SupportCommunity, TreatmentReport
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

    def test_support_community_tag_list_and_ordering(self):
        second = SupportCommunity.objects.create(
            name="Rede B",
            category=SupportCommunity.Category.EMOTIONAL,
            audience="Pacientes",
            description="Apoio emocional em grupo.",
            support_type="Grupo online",
            contact_url="https://example.com/b",
            tags="ansiedade, online, acolhimento",
            sort_order=2,
        )
        first = SupportCommunity.objects.create(
            name="Rede A",
            category=SupportCommunity.Category.FERTILITY,
            audience="Pacientes em tratamento",
            description="Conteúdo educativo.",
            support_type="Comunidade educativa",
            contact_url="https://example.com/a",
            sort_order=1,
        )

        self.assertEqual(second.tag_list, ["ansiedade", "online", "acolhimento"])
        self.assertEqual(list(SupportCommunity.objects.all()), [first, second])

    def test_community_page_shows_only_active_support_communities_and_keeps_posts(self):
        active = SupportCommunity.objects.create(
            name="Rede Ativa",
            category=SupportCommunity.Category.FERTILITY,
            audience="Pacientes",
            description="Apoio externo para pacientes.",
            support_type="Grupo online",
            contact_url="https://example.com/ativa",
            is_active=True,
        )
        SupportCommunity.objects.create(
            name="Rede Inativa",
            category=SupportCommunity.Category.ROUTINE,
            audience="Pacientes",
            description="Não deve aparecer.",
            support_type="Grupo",
            contact_url="https://example.com/inativa",
            is_active=False,
        )
        post = CommunityPost.objects.create(
            author=self.patient,
            category=CommunityPost.Category.FEELINGS,
            body="Uma coisa por vez me ajudou.",
            status=CommunityPost.Status.APPROVED,
        )

        response = self.client.get(reverse("core:community"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, active.name)
        self.assertNotContains(response, "Rede Inativa")
        self.assertContains(response, post.body)
        self.assertContains(response, "Enviar para revisão")

    def test_support_communities_page_has_dedicated_external_links(self):
        SupportCommunity.objects.create(
            name="Fórum anônimo de tentantes",
            category=SupportCommunity.Category.FERTILITY,
            audience="Tentantes",
            description="Comunidade BabyCenter Brasil.",
            support_type="BabyCenter Brasil",
            contact_label="Conhecer Comunidade",
            contact_url="https://brasil.babycenter.com/comunidade",
            is_active=True,
            sort_order=1,
        )
        SupportCommunity.objects.create(
            name="Relatos reais e acolhimento",
            category=SupportCommunity.Category.EMOTIONAL,
            audience="Tentantes",
            description="Relatos no Instagram.",
            support_type="Instagram #vidadetentante",
            contact_label="Explorar Relatos no Instagram",
            contact_url="https://www.instagram.com/explore/search/keyword/?q=%23vidadetentante",
            is_active=True,
            sort_order=2,
        )

        response = self.client.get(reverse("core:communities"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fórum anônimo de tentantes")
        self.assertContains(response, "https://brasil.babycenter.com/comunidade")
        self.assertContains(response, "Relatos reais e acolhimento")
        self.assertContains(response, "https://www.instagram.com/explore/search/keyword/?q=%23vidadetentante")

    def test_locked_report_does_not_download_and_available_report_does(self):
        locked = TreatmentReport.objects.create(patient=self.patient, title="Laudo")
        response = self.client.get(reverse("core:report-download", args=[locked.id]))
        self.assertEqual(response.status_code, 404)

        available = TreatmentReport.objects.create(
            patient=self.patient,
            title="Laudo liberado",
            status=TreatmentReport.Status.AVAILABLE,
        )
        available.file.save("laudo.txt", ContentFile("conteúdo"), save=True)
        response = self.client.get(reverse("core:report-download", args=[available.id]))
        self.assertEqual(response.status_code, 200)
