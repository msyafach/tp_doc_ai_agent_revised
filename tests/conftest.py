import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from api.models import Project


@pytest.fixture
def api_client(db):
    """Authenticated APIClient — creates a test user and force-authenticates."""
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


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
