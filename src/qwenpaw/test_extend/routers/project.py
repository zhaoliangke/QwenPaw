# -*- coding: utf-8 -*-
"""Project Management API routes at /api/test/project/."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from common.trace_id import generate_trace_id
from models.project import Project
from qwenpaw.constant import WORKING_DIR

router = APIRouter()


async def _get_store():
    from infra.storage_factory import StorageFactory
    return StorageFactory(str(WORKING_DIR)).create_project_store()


@router.post("/")
async def create_project(body: dict):
    project = Project(
        id=generate_trace_id("PRJ"),
        name=body.get("name", ""),
        target_url=body.get("target_url", ""),
        description=body.get("description"),
        env=body.get("env", "test"),
        tags=body.get("tags", []),
        owner=body.get("owner", ""),
    )
    if not project.name:
        raise HTTPException(status_code=400, detail="Project name is required")
    if not project.target_url:
        raise HTTPException(status_code=400, detail="Target URL is required")
    store = await _get_store()
    saved = await store.create(project)
    return {"project": saved.model_dump(), "id": saved.id}


@router.get("/")
async def list_projects(is_active: Optional[bool] = None, env: str = ""):
    store = await _get_store()
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if env:
        filters["env"] = env
    projects = await store.list_all(**filters)
    return {"projects": [p.model_dump() for p in projects], "count": len(projects)}


@router.get("/{project_id}")
async def get_project(project_id: str):
    store = await _get_store()
    project = await store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project": project.model_dump()}


@router.put("/{project_id}")
async def update_project(project_id: str, body: dict):
    store = await _get_store()
    existing = await store.get(project_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Project not found")
    existing.name = body.get("name", existing.name)
    existing.target_url = body.get("target_url", existing.target_url)
    existing.description = body.get("description", existing.description)
    existing.env = body.get("env", existing.env)
    existing.tags = body.get("tags", existing.tags)
    existing.owner = body.get("owner", existing.owner)
    if "is_active" in body:
        existing.is_active = body["is_active"]
    existing.updated_at = datetime.utcnow()
    await store.update(existing)
    return {"project": existing.model_dump()}


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    store = await _get_store()
    deleted = await store.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True}
