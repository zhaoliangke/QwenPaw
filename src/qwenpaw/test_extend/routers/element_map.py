# -*- coding: utf-8 -*-
"""Element map API routes at /api/test/element-map/."""

import logging

from fastapi import APIRouter

from common.trace_id import generate_trace_id
from models.element_map import ElementMap
from infra.storage_factory import StorageFactory
from qwenpaw.constant import WORKING_DIR

router = APIRouter()

logger = logging.getLogger(__name__)


def _get_store():
    return StorageFactory(str(WORKING_DIR)).create_element_map_store()


@router.post("/")
async def create_element_map(body: dict):
    item = ElementMap(
        id=generate_trace_id(),
        project_id=body.get("project_id", ""),
        page_name=body.get("page_name", ""),
        mapping=body.get("mapping", {}),
    )
    result = await _get_store().create(item)
    return result.model_dump()


@router.get("/")
async def list_element_maps(project_id: str = "", page_name: str = ""):
    filters = {}
    if project_id:
        filters["project_id"] = project_id
    if page_name:
        filters["page_name"] = page_name
    items = await _get_store().list_all(**filters)
    return {"element_maps": [m.model_dump() for m in items], "count": len(items)}


@router.get("/{map_id}")
async def get_element_map(map_id: str):
    item = await _get_store().get(map_id)
    if item:
        return item.model_dump()
    return {"error": "Element map not found"}


@router.put("/{map_id}")
async def update_element_map(map_id: str, body: dict):
    existing = await _get_store().get(map_id)
    if not existing:
        return {"error": "Element map not found"}
    for key in ("project_id", "page_name", "mapping"):
        if key in body:
            setattr(existing, key, body[key])
    result = await _get_store().update(existing)
    return result.model_dump()


@router.delete("/{map_id}")
async def delete_element_map(map_id: str):
    deleted = await _get_store().delete(map_id)
    return {"deleted": deleted}
