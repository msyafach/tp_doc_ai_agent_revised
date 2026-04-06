import pytest
import uuid
from rest_framework import status
from api.models import Project


@pytest.mark.django_db
class TestProjectsList:
    def test_list_projects_when_empty(self, api_client):
        response = api_client.get("/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_projects_returns_all(self, api_client, sample_project):
        Project.objects.create(name="Second Project")
        response = api_client.get("/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_projects_omits_state_field(self, api_client, sample_project):
        response = api_client.get("/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        project_data = response.data[0]
        assert "state" not in project_data
        assert "id" in project_data
        assert "name" in project_data
        assert "created_at" in project_data
        assert "updated_at" in project_data

    def test_create_project_with_name(self, api_client):
        response = api_client.post("/api/projects/", {"name": "New TP Report"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New TP Report"
        assert "id" in response.data
        assert "state" in response.data

    def test_create_project_without_name(self, api_client):
        response = api_client.post("/api/projects/", {}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == ""

    def test_create_project_initializes_default_state(self, api_client):
        response = api_client.post("/api/projects/", {"name": "Test"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        state = response.data["state"]
        assert "company_name" in state
        assert "fiscal_year" in state
        assert "selected_method" in state
        assert state["selected_method"] == "TNMM"
        assert state["agent_ran"] is False
        assert state["step"] == 0

    def test_create_project_persists_to_db(self, api_client):
        response = api_client.post("/api/projects/", {"name": "Persisted"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        project_id = response.data["id"]
        assert Project.objects.filter(pk=project_id).exists()


@pytest.mark.django_db
class TestProjectDetail:
    def test_get_project_returns_full_state(self, api_client, sample_project):
        response = api_client.get(f"/api/projects/{sample_project.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(sample_project.pk)
        assert "state" in response.data
        assert response.data["state"]["company_name"] == "PT Test Company"

    def test_get_nonexistent_project_returns_404(self, api_client):
        response = api_client.get(f"/api/projects/{uuid.uuid4()}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_project_name(self, api_client, sample_project):
        response = api_client.patch(
            f"/api/projects/{sample_project.pk}/",
            {"name": "Updated Name"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
        sample_project.refresh_from_db()
        assert sample_project.name == "Updated Name"

    def test_patch_project_state_merges_fields(self, api_client, sample_project):
        response = api_client.patch(
            f"/api/projects/{sample_project.pk}/",
            {"state": {"company_name": "PT Updated", "new_key": "new_value"}},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        state = response.data["state"]
        assert state["company_name"] == "PT Updated"
        assert state["new_key"] == "new_value"
        # Pre-existing keys not in the patch should remain
        assert state["fiscal_year"] == "2024"

    def test_patch_project_state_and_name_together(self, api_client, sample_project):
        response = api_client.patch(
            f"/api/projects/{sample_project.pk}/",
            {"name": "Renamed", "state": {"fiscal_year": "2025"}},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Renamed"
        assert response.data["state"]["fiscal_year"] == "2025"

    def test_patch_nonexistent_project_returns_404(self, api_client):
        response = api_client.patch(
            f"/api/projects/{uuid.uuid4()}/",
            {"name": "Ghost"},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project(self, api_client, sample_project):
        project_pk = sample_project.pk
        response = api_client.delete(f"/api/projects/{project_pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project_pk).exists()

    def test_delete_nonexistent_project_returns_404(self, api_client):
        response = api_client.delete(f"/api/projects/{uuid.uuid4()}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_after_patch_reflects_changes(self, api_client, sample_project):
        api_client.patch(
            f"/api/projects/{sample_project.pk}/",
            {"state": {"company_name": "PT Patched"}},
            format="json",
        )
        response = api_client.get(f"/api/projects/{sample_project.pk}/")
        assert response.data["state"]["company_name"] == "PT Patched"
