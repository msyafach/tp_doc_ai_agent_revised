"""
Celery tasks for async operations (document processing, AI agents).
"""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


def _get_task_record(task_db_id: int):
    from .models import AgentTask

    return AgentTask.objects.get(pk=task_db_id)


@shared_task(bind=True)
def process_documents_task(
    self,
    task_db_id: int,
    project_id: str,
    files: list[dict],
    provider: str,
    api_key: str,
    model: str,
    tavily_key: str,
):
    """Process uploaded documents and run AI extraction."""
    from .models import AgentTask, Project

    task_record = _get_task_record(task_db_id)
    task_record.celery_task_id = self.request.id
    task_record.status = "running"
    task_record.save(update_fields=["celery_task_id", "status"])

    try:
        from .services.document_service import process_documents

        result = process_documents(files, provider, api_key, model, tavily_key)

        task_record.status = "success" if result.get("success") else "error"
        task_record.result = result
        if not result.get("success"):
            task_record.error = "; ".join(result.get("errors", []))
        task_record.save(update_fields=["status", "result", "error"])

        # If extraction succeeded, patch the project state
        if result.get("success") and result.get("extraction"):
            project = Project.objects.get(pk=project_id)
            project.state["doc_extraction_result"] = result["extraction"]
            project.state["uploaded_docs_processed"] = True
            project.save(update_fields=["state"])

        return result

    except Exception as exc:
        logger.exception("process_documents_task failed")
        task_record.status = "error"
        task_record.error = str(exc)
        task_record.save(update_fields=["status", "error"])
        raise


@shared_task(bind=True)
def run_agents_task(
    self,
    task_db_id: int,
    project_id: str,
    provider: str,
    api_key: str,
    model: str,
    tavily_key: str,
    langsmith_api_key: str = "",
    langsmith_project: str = "",
):
    """Run the full LangGraph agent pipeline."""
    from .models import AgentTask, Project

    task_record = _get_task_record(task_db_id)
    task_record.celery_task_id = self.request.id
    task_record.status = "running"
    task_record.save(update_fields=["celery_task_id", "status"])

    project = Project.objects.get(pk=project_id)

    def on_node_complete(node_name: str, label: str):
        task_record.progress_log.append({"node": node_name, "label": label})
        task_record.save(update_fields=["progress_log"])

    try:
        from .services.agent_service import run_all_agents

        updates = run_all_agents(
            state=project.state,
            provider=provider,
            api_key=api_key,
            model=model,
            tavily_key=tavily_key,
            langsmith_api_key=langsmith_api_key,
            langsmith_project=langsmith_project,
            progress_callback=on_node_complete,
        )

        # Merge agent outputs into project state
        project.refresh_from_db()
        project.state.update(updates)
        project.save(update_fields=["state"])

        task_record.status = "success"
        task_record.result = updates
        task_record.save(update_fields=["status", "result"])

        return updates

    except Exception as exc:
        logger.exception("run_agents_task failed")
        task_record.status = "error"
        task_record.error = str(exc)
        task_record.save(update_fields=["status", "error"])
        raise


@shared_task(bind=True)
def run_single_agent_task(
    self,
    task_db_id: int,
    project_id: str,
    agent_key: str,
    provider: str,
    api_key: str,
    model: str,
    tavily_key: str,
    langsmith_api_key: str = "",
    langsmith_project: str = "",
):
    """Regenerate a single AI section."""
    from .models import AgentTask, Project

    task_record = _get_task_record(task_db_id)
    task_record.celery_task_id = self.request.id
    task_record.status = "running"
    task_record.save(update_fields=["celery_task_id", "status"])

    project = Project.objects.get(pk=project_id)

    try:
        from .services.agent_service import run_single_agent

        updates = run_single_agent(
            agent_key=agent_key,
            state=project.state,
            provider=provider,
            api_key=api_key,
            model=model,
            tavily_key=tavily_key,
            langsmith_api_key=langsmith_api_key,
            langsmith_project=langsmith_project,
        )

        project.refresh_from_db()
        project.state.update(updates)
        project.save(update_fields=["state"])

        task_record.status = "success"
        task_record.result = updates
        task_record.save(update_fields=["status", "result"])

        return updates

    # exception
    except Exception as exc:
        logger.exception("run_single_agent_task failed")
        task_record.status = "error"
        task_record.error = str(exc)
        task_record.save(update_fields=["status", "error"])
        raise
