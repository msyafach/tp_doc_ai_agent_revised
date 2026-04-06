import pytest
from rest_framework.test import APIClient
from api.models import Project


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_project(db):
    return Project.objects.create(
        name="Test Project",
        state={
            "company_name": "PT Test Company",
            "company_short_name": "Test",
            "fiscal_year": "2024",
            "step": 0,
        },
    )
