from rest_framework import serializers

from treatments.serializers import TreatmentSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "role", "wants_in_app_reminders"]


class PatientSummarySerializer(serializers.ModelSerializer):
    current_treatment = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "current_treatment"]

    def get_current_treatment(self, obj):
        treatment = obj.treatments.filter(is_active=True).prefetch_related("steps").first()
        return TreatmentSerializer(treatment).data if treatment else None
