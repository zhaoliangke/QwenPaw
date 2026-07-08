# -*- coding: utf-8 -*-
"""Element map MCP tools - let AI agents read/write element mappings."""

import logging

logger = logging.getLogger(__name__)


async def list_element_maps_tool(project_id: str = "", page_name: str = ""):
    """List element maps, optionally filtered by project or page."""
    from routers.element_map import _get_store
    items = await _get_store().list_all(
        project_id=project_id,
        page_name=page_name,
    )
    return {"element_maps": [m.model_dump() for m in items], "count": len(items)}


async def get_element_map_tool(map_id: str):
    """Get a single element map by ID."""
    from routers.element_map import _get_store
    item = await _get_store().get(map_id)
    if item:
        return item.model_dump()
    return {"error": "Element map not found"}


async def create_element_map_tool(project_id: str, page_name: str, mapping: dict):
    """Create a new element map for a project page.

    mapping is a dict of semantic name -> CSS/data-testid selector, e.g.:
    {"login_btn": "[data-testid=\"submit-btn\"]", "username": "[data-testid=\"username\"]"}
    """
    from common.trace_id import generate_trace_id
    from models.element_map import ElementMap
    from routers.element_map import _get_store
    item = ElementMap(
        id=generate_trace_id(),
        project_id=project_id,
        page_name=page_name,
        mapping=mapping,
    )
    result = await _get_store().create(item)
    return result.model_dump()


async def update_element_map_tool(map_id: str, mapping: dict, project_id: str = "", page_name: str = ""):
    """Update an existing element map. Only provided fields are updated."""
    from routers.element_map import _get_store
    existing = await _get_store().get(map_id)
    if not existing:
        return {"error": "Element map not found"}
    if project_id:
        existing.project_id = project_id
    if page_name:
        existing.page_name = page_name
    if mapping:
        existing.mapping = mapping
    result = await _get_store().update(existing)
    return result.model_dump()


async def delete_element_map_tool(map_id: str):
    """Delete an element map by ID."""
    from routers.element_map import _get_store
    deleted = await _get_store().delete(map_id)
    return {"deleted": deleted}
