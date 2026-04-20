from rest_framework import serializers

from .models import Treatment, TreatmentStep


class TreatmentStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentStep
        fields = ["id", "name", "order", "status"]


class TreatmentSerializer(serializers.ModelSerializer):
    steps = TreatmentStepSerializer(many=True, read_only=True)
    current_step = serializers.SerializerMethodField()
    next_step = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = ["id", "name", "is_active", "current_step", "next_step", "steps"]

    def get_current_step(self, obj):
        step = obj.current_step
        return TreatmentStepSerializer(step).data if step else None

    def get_next_step(self, obj):
        step = obj.next_step
        return TreatmentStepSerializer(step).data if step else None
