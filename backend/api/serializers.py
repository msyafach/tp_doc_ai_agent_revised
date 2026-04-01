from rest_framework import serializers
from .models import Project, AgentTask


class AgentTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentTask
        fields = [
            "id", "celery_task_id", "task_type", "status",
            "progress_log", "result", "error", "created_at",
        ]
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "state", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (omits heavy state blob)."""
    class Meta:
        model = Project
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = fields
