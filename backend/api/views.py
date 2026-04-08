"""
API views for the TP Local File Generator.
"""
from __future__ import annotations
import json
import logging

from django.http import HttpResponse, StreamingHttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

from .models import Project, AgentTask
from .serializers import ProjectSerializer, ProjectListSerializer, AgentTaskSerializer

logger = logging.getLogger(__name__)

# ─── Default project state ────────────────────────────────────────────────────

DEFAULT_STATE = {
    "step": 0,
    "uploaded_docs_processed": False,
    "doc_extraction_result": {},
    "company_name": "",
    "company_short_name": "",
    "company_address": "",
    "establishment_info": "",
    "fiscal_year": "2024",
    "shareholders": [{"name": "", "shares": "", "capital": "", "percentage": ""}],
    "shareholders_source": "",
    "management": [{"position": "", "name": ""}],
    "management_source": "",
    "employee_count": "",
    "affiliated_parties": [{"name": "", "country": "", "relationship": "", "transaction_type": ""}],
    "parent_company": "",
    "parent_group": "",
    "brand_name": "",
    "business_activities_description": "",
    "products": [{"name": "", "description": ""}],
    "business_strategy": "",
    "business_restructuring": "",
    "transaction_type": "Purchase of tangible goods",
    "transaction_details_text": "",
    "pricing_policy": "",
    "affiliated_transactions": [{"name": "", "country": "", "affiliation_type": "", "transaction_type": "", "value": "", "note": ""}],
    "independent_transactions": [{"name": "", "country": "", "transaction_type": "", "type_of_product": "", "amount_idr": "", "quantity": "", "avg_price_per_unit": ""}],
    "financial_data": {},
    "financial_data_prior": {},
    "comparable_companies": [{"name": "", "country": "", "description": "", "ros_data": ""}],
    "search_criteria_results": [],
    "rejection_matrix": [],
    "selected_method": "TNMM",
    "selected_pli": "ROS",
    "tested_party": "",
    "analysis_period": "2020-2022",
    "quartile_range": {"q1": 0.0, "median": 0.0, "q3": 0.0},
    "tested_party_ratio": 0.0,
    "non_financial_events": "",
    "org_structure_description": "",
    "org_structure_departments": [{"name": "", "head": "", "employees": ""}],
    "industry_analysis_global": "",
    "industry_analysis_indonesia": "",
    "company_location_analysis": "",
    "company_location_sources": [],
    "industry_regulations_text": "",
    "industry_regulations_sources": [],
    "business_environment_overview": "",
    "business_environment_sources": [],
    "executive_summary": "",
    "conclusion_text": "",
    "background_transaction": "",
    "functional_analysis_narrative": "",
    "business_characterization_text": "",
    "method_selection_justification": "",
    "pli_selection_rationale": "",
    "comparability_analysis_narrative": "",
    "agent_ran": False,
    "agent_errors": [],
    "comparability_factors": [
        {"factor": "Contract Terms and Conditions", "description": ""},
        {"factor": "Product Characteristics",       "description": ""},
        {"factor": "Functional Analysis",           "description": ""},
        {"factor": "Business Strategy",             "description": ""},
        {"factor": "Economic Conditions",           "description": ""},
    ],
}


# ─── Config ───────────────────────────────────────────────────────────────────

@api_view(["GET"])
def config_view(request):
    """Return static config constants needed by the frontend."""
    import importlib.util, os, sys
    from django.conf import settings as dj_settings

    tp_config_path = os.path.join(dj_settings.TP_APP_DIR, "agent_config.py")
    spec = importlib.util.spec_from_file_location("tp_config", tp_config_path)
    tp_cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp_cfg)

    return Response({
        "TP_METHODS": tp_cfg.TP_METHODS,
        "PLI_OPTIONS": tp_cfg.PLI_OPTIONS,
        "TRANSACTION_TYPES": tp_cfg.TRANSACTION_TYPES,
        "BUSINESS_TYPES": tp_cfg.BUSINESS_TYPES,
    })


# ─── Projects ─────────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
def projects_list(request):
    if request.method == "GET":
        projects = Project.objects.all()
        return Response(ProjectListSerializer(projects, many=True).data)

    # POST — create new project
    state = DEFAULT_STATE.copy()
    name = request.data.get("name", "")
    project = Project.objects.create(name=name, state=state)
    return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ProjectSerializer(project).data)

    if request.method == "PATCH":
        # Partial state merge — only update provided keys
        new_state = request.data.get("state")
        if new_state is not None:
            project.state.update(new_state)

        new_name = request.data.get("name")
        if new_name is not None:
            project.name = new_name

        project.save()
        return Response(ProjectSerializer(project).data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def project_export_json(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    filename = (
        f"tp_project_{project.state.get('company_short_name', 'project')}"
        f"_{project.state.get('fiscal_year', '')}.json"
    )
    response = HttpResponse(
        json.dumps(project.state, indent=2, default=str),
        content_type="application/json",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["POST"])
def project_load_json(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if "file" in request.FILES:
        try:
            data = json.loads(request.FILES["file"].read())
        except Exception:
            return Response({"detail": "Invalid JSON file."}, status=400)
    elif "state" in request.data:
        data = request.data["state"]
    else:
        return Response({"detail": "Provide a 'file' or 'state' in the request body."}, status=400)

    project.state = data
    project.save(update_fields=["state"])
    return Response(ProjectSerializer(project).data)


# ─── Document upload ──────────────────────────────────────────────────────────

@api_view(["POST"])
@parser_classes([MultiPartParser])
def upload_documents(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    files = request.FILES.getlist("files")
    if not files:
        return Response({"detail": "No files uploaded."}, status=400)

    provider = request.data.get("llm_provider", "groq")
    api_key = request.data.get("api_key", "")
    model = request.data.get("model", "llama-3.3-70b-versatile")
    tavily_key = request.data.get("tavily_key", "")

    MAX_MB = 20
    file_data = []
    for f in files:
        if f.size > MAX_MB * 1024 * 1024:
            return Response(
                {"detail": f"{f.name} exceeds {MAX_MB} MB limit."},
                status=400,
            )
        file_data.append({"name": f.name, "data": f.read()})

    # Create AgentTask record
    task_record = AgentTask.objects.create(
        project=project,
        task_type="upload",
        status="pending",
    )

    from .tasks import process_documents_task
    # Convert bytes to hex strings for JSON-serializable Celery args
    serializable_files = [
        {"name": fd["name"], "data_hex": fd["data"].hex()}
        for fd in file_data
    ]
    process_documents_task.delay(
        task_db_id=task_record.pk,
        project_id=str(project.pk),
        files=serializable_files,
        provider=provider,
        api_key=api_key,
        model=model,
        tavily_key=tavily_key,
    )

    return Response(
        {"task_id": task_record.pk, "celery_task_id": ""},
        status=status.HTTP_202_ACCEPTED,
    )


# ─── Agent tasks ──────────────────────────────────────────────────────────────

@api_view(["POST"])
def run_agents(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    provider = request.data.get("llm_provider", "groq")
    api_key = request.data.get("api_key", "")
    model = request.data.get("model", "llama-3.3-70b-versatile")
    tavily_key = request.data.get("tavily_key", "")
    langsmith_api_key = request.data.get("langsmith_api_key", "")
    langsmith_project = request.data.get("langsmith_project", "")

    task_record = AgentTask.objects.create(
        project=project,
        task_type="agents",
        status="pending",
    )

    from .tasks import run_agents_task
    run_agents_task.delay(
        task_db_id=task_record.pk,
        project_id=str(project.pk),
        provider=provider,
        api_key=api_key,
        model=model,
        tavily_key=tavily_key,
        langsmith_api_key=langsmith_api_key,
        langsmith_project=langsmith_project,
    )

    return Response({"task_id": task_record.pk}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
def run_single_agent(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    agent_key = request.data.get("agent_key", "")
    provider = request.data.get("llm_provider", "groq")
    api_key = request.data.get("api_key", "")
    model = request.data.get("model", "llama-3.3-70b-versatile")
    tavily_key = request.data.get("tavily_key", "")
    langsmith_api_key = request.data.get("langsmith_api_key", "")
    langsmith_project = request.data.get("langsmith_project", "")

    if not agent_key:
        return Response({"detail": "agent_key is required."}, status=400)

    task_record = AgentTask.objects.create(
        project=project,
        task_type="single_agent",
        status="pending",
    )

    from .tasks import run_single_agent_task
    run_single_agent_task.delay(
        task_db_id=task_record.pk,
        project_id=str(project.pk),
        agent_key=agent_key,
        provider=provider,
        api_key=api_key,
        model=model,
        tavily_key=tavily_key,
        langsmith_api_key=langsmith_api_key,
        langsmith_project=langsmith_project,
    )

    return Response({"task_id": task_record.pk}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def task_status(request, task_id):
    try:
        task = AgentTask.objects.get(pk=task_id)
    except AgentTask.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(AgentTaskSerializer(task).data)


# ─── DOCX Export ──────────────────────────────────────────────────────────────

@api_view(["GET"])
def export_docx(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    export_type = request.query_params.get("type", "builder")

    try:
        from .services.export_service import export_docx as _export
        doc_bytes = _export(project.state, export_type=export_type)
    except Exception as exc:
        logger.exception("DOCX export failed")
        return Response({"detail": str(exc)}, status=500)

    company = project.state.get("company_name", "") or project.state.get("company_short_name", "project")
    fy = project.state.get("fiscal_year", "")
    # Sanitize for filename
    safe_company = "".join(c if c.isalnum() or c in " _-" else "_" for c in company).strip()
    suffix = "_template" if export_type == "template" else ""
    filename = f"TP_{safe_company}_FY{fy}{suffix}.docx"

    response = HttpResponse(
        doc_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
