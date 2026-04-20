from rest_framework import serializers

from .models import Medication


class MedicationSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Medication
        fields = ["id", "name", "scheduled_for", "status", "status_label", "completed_at"]
