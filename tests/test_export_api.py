import pytest
import json
import uuid
from rest_framework import status


@pytest.mark.django_db
class TestProjectExportJSON:
    def test_export_json_returns_200(self, api_client, sample_project):
        response = api_client.get(f"/api/projects/{sample_project.pk}/export-json/")
        assert response.status_code == status.HTTP_200_OK

    def test_export_json_content_type_is_json(self, api_client, sample_project):
        response = api_client.get(f"/api/projects/{sample_project.pk}/export-json/")
        assert response["Content-Type"] == "application/json"

    def test_export_json_has_attachment_header(self, api_client, sample_project):
        response = api_client.get(f"/api/projects/{sample_project.pk}/export-json/")
        assert "attachment" in response["Content-Disposition"]
        assert ".json" in response["Content-Disposition"]

    def test_export_json_filename_includes_company_short_name(self, api_client, sample_project):
        response = api_client.get(f"/api/projects/{sample_project.pk}/export-json/")
        # sample_project has company_short_name="Test"
        assert "Test" in response["Content-Disposition"]

    def test_export_json_content_matches_project_state(self, api_client, sample_project):
        response = api_client.get(f"/api/projects/{sample_project.pk}/export-json/")
        exported_data = json.loads(response.content)
        assert exported_data == sample_project.state

    def test_export_json_nonexistent_project_returns_404(self, api_client):
        response = api_client.get(f"/api/projects/{uuid.uuid4()}/export-json/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProjectLoadJSON:
    def test_load_json_from_body_returns_200(self, api_client, sample_project):
        new_state = {"company_name": "PT Loaded", "fiscal_year": "2023"}
        response = api_client.post(
            f"/api/projects/{sample_project.pk}/load-json/",
            {"state": new_state},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_load_json_from_body_replaces_state(self, api_client, sample_project):
        new_state = {"company_name": "PT Loaded", "fiscal_year": "2023"}
        response = api_client.post(
            f"/api/projects/{sample_project.pk}/load-json/",
            {"state": new_state},
            format="json",
        )
        assert response.data["state"] == new_state
        sample_project.refresh_from_db()
        assert sample_project.state == new_state

    def test_load_json_without_payload_returns_400(self, api_client, sample_project):
        response = api_client.post(
            f"/api/projects/{sample_project.pk}/load-json/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_load_json_nonexistent_project_returns_404(self, api_client):
        response = api_client.post(
            f"/api/projects/{uuid.uuid4()}/load-json/",
            {"state": {}},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_load_json_roundtrip_with_export(self, api_client, sample_project):
        # Export the current state
        export_response = api_client.get(f"/api/projects/{sample_project.pk}/export-json/")
        exported_state = json.loads(export_response.content)

        # Modify the project state
        api_client.patch(
            f"/api/projects/{sample_project.pk}/",
            {"state": {"company_name": "PT Modified"}},
            format="json",
        )

        # Re-load the original exported state
        load_response = api_client.post(
            f"/api/projects/{sample_project.pk}/load-json/",
            {"state": exported_state},
            format="json",
        )
        assert load_response.status_code == status.HTTP_200_OK
        assert load_response.data["state"]["company_name"] == "PT Test Company"
