from django.contrib import admin
from .models import Project, AgentTask


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at", "updated_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "project", "task_type", "status", "created_at"]
    list_filter = ["task_type", "status"]
    readonly_fields = ["id", "created_at"]
