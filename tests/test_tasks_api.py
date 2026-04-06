import pytest
from rest_framework import status
from api.models import AgentTask


@pytest.mark.django_db
class TestTaskStatus:
    def test_get_task_returns_200(self, api_client, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="upload",
            status="pending",
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.status_code == status.HTTP_200_OK

    def test_get_task_returns_correct_fields(self, api_client, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="upload",
            status="pending",
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        data = response.data
        assert data["id"] == task.pk
        assert data["task_type"] == "upload"
        assert data["status"] == "pending"
        assert data["progress_log"] == []
        assert data["result"] is None
        assert data["error"] is None
        assert "celery_task_id" in data
        assert "created_at" in data

    def test_get_task_running_with_progress_log(self, api_client, sample_project):
        log = [{"node": "extraction", "done": True}, {"node": "analysis", "done": False}]
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="agents",
            status="running",
            progress_log=log,
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "running"
        assert response.data["progress_log"] == log

    def test_get_task_success_with_result(self, api_client, sample_project):
        result = {"industry_analysis_global": "Global market is growing..."}
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="agents",
            status="success",
            result=result,
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert response.data["result"] == result

    def test_get_task_error_with_message(self, api_client, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="upload",
            status="error",
            error="File processing failed: timeout after 30s",
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "error"
        assert response.data["error"] == "File processing failed: timeout after 30s"

    def test_get_nonexistent_task_returns_404(self, api_client):
        response = api_client.get("/api/tasks/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_task_type_single_agent(self, api_client, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="single_agent",
            status="pending",
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.data["task_type"] == "single_agent"

    def test_task_type_export(self, api_client, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="export",
            status="success",
        )
        response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.data["task_type"] == "export"
        assert response.data["status"] == "success"
