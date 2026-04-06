import pytest
from rest_framework import status


@pytest.mark.django_db
class TestConfigEndpoint:
    def test_config_returns_200(self, api_client):
        response = api_client.get("/api/config/")
        assert response.status_code == status.HTTP_200_OK

    def test_config_has_all_required_keys(self, api_client):
        response = api_client.get("/api/config/")
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert "TP_METHODS" in data
        assert "PLI_OPTIONS" in data
        assert "TRANSACTION_TYPES" in data
        assert "BUSINESS_TYPES" in data

    def test_config_values_are_lists(self, api_client):
        response = api_client.get("/api/config/")
        data = response.data
        assert isinstance(data["TP_METHODS"], list)
        assert isinstance(data["PLI_OPTIONS"], list)
        assert isinstance(data["TRANSACTION_TYPES"], list)
        assert isinstance(data["BUSINESS_TYPES"], list)

    def test_config_tp_methods_not_empty(self, api_client):
        response = api_client.get("/api/config/")
        assert len(response.data["TP_METHODS"]) > 0

    def test_config_pli_options_not_empty(self, api_client):
        response = api_client.get("/api/config/")
        assert len(response.data["PLI_OPTIONS"]) > 0

    def test_config_transaction_types_not_empty(self, api_client):
        response = api_client.get("/api/config/")
        assert len(response.data["TRANSACTION_TYPES"]) > 0

    def test_config_business_types_not_empty(self, api_client):
        response = api_client.get("/api/config/")
        assert len(response.data["BUSINESS_TYPES"]) > 0

    def test_config_contains_tnmm(self, api_client):
        response = api_client.get("/api/config/")
        assert "TNMM" in response.data["TP_METHODS"]

    def test_config_contains_ros_pli(self, api_client):
        response = api_client.get("/api/config/")
        assert "ROS" in response.data["PLI_OPTIONS"]

    def test_config_get_only_no_post(self, api_client):
        response = api_client.post("/api/config/", {}, format="json")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
