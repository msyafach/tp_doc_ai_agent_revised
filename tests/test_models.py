import pytest
import uuid
from api.models import Project, AgentTask


@pytest.mark.django_db
class TestProjectModel:
    def test_create_project_with_defaults(self):
        project = Project.objects.create()
        assert project.pk is not None
        assert isinstance(project.pk, uuid.UUID)
        assert project.name == ""
        assert project.state == {}
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_create_project_with_name_and_state(self):
        state = {"company_name": "PT Example", "fiscal_year": "2024"}
        project = Project.objects.create(name="My Project", state=state)
        assert project.name == "My Project"
        assert project.state == state

    def test_str_representation_with_name(self):
        project = Project.objects.create(name="TP Report")
        assert "TP Report" in str(project)
        assert str(project.pk) in str(project)

    def test_str_representation_without_name(self):
        project = Project.objects.create()
        assert "Untitled" in str(project)

    def test_uuid_primary_key_is_unique(self):
        p1 = Project.objects.create(name="First")
        p2 = Project.objects.create(name="Second")
        assert p1.pk != p2.pk

    def test_ordering_by_updated_at_desc(self):
        p1 = Project.objects.create(name="First")
        p2 = Project.objects.create(name="Second")
        projects = list(Project.objects.all())
        # p2 was created last so appears first in default ordering
        assert projects[0].pk == p2.pk
        assert projects[1].pk == p1.pk

    def test_state_field_stores_nested_json(self):
        state = {
            "shareholders": [{"name": "John", "shares": "1000"}],
            "financials": {"revenue": 500000},
        }
        project = Project.objects.create(state=state)
        project.refresh_from_db()
        assert project.state["shareholders"][0]["name"] == "John"
        assert project.state["financials"]["revenue"] == 500000


@pytest.mark.django_db
class TestAgentTaskModel:
    def test_create_agent_task(self, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="upload",
            status="pending",
        )
        assert task.pk is not None
        assert task.task_type == "upload"
        assert task.status == "pending"
        assert task.progress_log == []
        assert task.result is None
        assert task.error is None

    def test_task_str_representation(self, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="agents",
            status="running",
        )
        assert "agents" in str(task)
        assert "running" in str(task)

    def test_cascade_delete_removes_tasks(self, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="export",
            status="success",
        )
        task_id = task.pk
        sample_project.delete()
        assert not AgentTask.objects.filter(pk=task_id).exists()

    def test_all_task_types_are_valid(self, sample_project):
        for task_type in ["upload", "agents", "single_agent", "export"]:
            task = AgentTask.objects.create(
                project=sample_project,
                task_type=task_type,
                status="pending",
            )
            assert task.task_type == task_type

    def test_all_status_choices_are_valid(self, sample_project):
        for status_choice in ["pending", "running", "success", "error"]:
            task = AgentTask.objects.create(
                project=sample_project,
                task_type="upload",
                status=status_choice,
            )
            assert task.status == status_choice

    def test_task_with_progress_log(self, sample_project):
        log = [{"node": "extraction", "done": True}, {"node": "analysis", "done": False}]
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="agents",
            status="running",
            progress_log=log,
        )
        task.refresh_from_db()
        assert task.progress_log == log

    def test_task_with_result(self, sample_project):
        result = {"company_name": "PT Example", "fiscal_year": "2024"}
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="agents",
            status="success",
            result=result,
        )
        task.refresh_from_db()
        assert task.result == result

    def test_task_with_error(self, sample_project):
        task = AgentTask.objects.create(
            project=sample_project,
            task_type="upload",
            status="error",
            error="File processing failed due to timeout",
        )
        task.refresh_from_db()
        assert task.error == "File processing failed due to timeout"

    def test_multiple_tasks_per_project(self, sample_project):
        AgentTask.objects.create(project=sample_project, task_type="upload", status="success")
        AgentTask.objects.create(project=sample_project, task_type="agents", status="pending")
        assert sample_project.tasks.count() == 2
