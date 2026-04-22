import uuid
from django.db import models


class SystemSetting(models.Model):
    """Key-value store for admin-managed API settings (LLM provider, keys, etc.)."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key

    @classmethod
    def get_all(cls) -> dict:
        return {s.key: s.value for s in cls.objects.all()}

    @classmethod
    def as_api_settings(cls) -> dict:
        raw = cls.get_all()
        return {
            "llm_provider":      raw.get("llm_provider", "groq"),
            "api_key":           raw.get("api_key", ""),
            "model":             raw.get("model", "llama-3.3-70b-versatile"),
            "tavily_key":        raw.get("tavily_key", ""),
            "langsmith_api_key": raw.get("langsmith_api_key", ""),
            "langsmith_project": raw.get("langsmith_project", "tp-local-file-generator"),
        }

    @classmethod
    def save_api_settings(cls, data: dict) -> None:
        allowed = {"llm_provider", "api_key", "model", "tavily_key", "langsmith_api_key", "langsmith_project"}
        for key, value in data.items():
            if key in allowed:
                cls.objects.update_or_create(key=key, defaults={"value": str(value)})


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
