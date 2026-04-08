from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("config/", views.config_view, name="config"),

    # ── Auth ──────────────────────────────────────────────────────────────────
    path("auth/login/", views.login_view, name="auth-login"),
    path("auth/logout/", views.logout_view, name="auth-logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", views.me_view, name="auth-me"),

    # ── Admin user management ─────────────────────────────────────────────────
    path("admin/users/", views.admin_users_list, name="admin-users-list"),
    path("admin/users/<int:pk>/", views.admin_user_detail, name="admin-user-detail"),

    # ── Projects CRUD ─────────────────────────────────────────────────────────
    path("projects/", views.projects_list, name="projects-list"),
    path("projects/<uuid:pk>/", views.project_detail, name="project-detail"),
    path("projects/<uuid:pk>/export-json/", views.project_export_json, name="project-export-json"),
    path("projects/<uuid:pk>/load-json/", views.project_load_json, name="project-load-json"),

    # ── Document upload ───────────────────────────────────────────────────────
    path("projects/<uuid:pk>/upload-documents/", views.upload_documents, name="upload-documents"),

    # ── AI agents ─────────────────────────────────────────────────────────────
    path("projects/<uuid:pk>/run-agents/", views.run_agents, name="run-agents"),
    path("projects/<uuid:pk>/run-single-agent/", views.run_single_agent, name="run-single-agent"),

    # ── Task polling ──────────────────────────────────────────────────────────
    path("tasks/<int:task_id>/", views.task_status, name="task-status"),

    # ── DOCX export ───────────────────────────────────────────────────────────
    path("projects/<uuid:pk>/export-docx/", views.export_docx, name="export-docx"),
]
