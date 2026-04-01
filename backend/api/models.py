import uuid
from django.db import models


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, default="")
    state = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name or 'Untitled'} ({self.id})"


class AgentTask(models.Model):
    TASK_TYPES = [
        ("upload", "Document Upload"),
        ("agents", "Run All Agents"),
        ("single_agent", "Single Agent"),
        ("export", "Export DOCX"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("error", "Error"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    progress_log = models.JSONField(default=list)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task_type} / {self.status} ({self.project_id})"
