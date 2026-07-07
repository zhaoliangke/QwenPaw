# -*- coding: utf-8 -*-
"""Knowledge Base API routes at /api/test/knowledge/."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/search")
async def search_knowledge(body: dict):
    from ..mcp_tools.knowledge_rag import search_knowledge_tool
    return await search_knowledge_tool(
        query=body["query"],
        product_line=body.get("product_line", ""),
        limit=body.get("limit", 10),
    )


@router.post("/archive")
async def archive_iteration(body: dict):
    from ..mcp_tools.knowledge_rag import archive_iteration_tool
    return await archive_iteration_tool(iteration_id=body["iteration_id"])


@router.post("/distill")
async def distill_knowledge(body: dict):
    from ..mcp_tools.knowledge_rag import distill_knowledge_tool
    return await distill_knowledge_tool(product_line=body.get("product_line", ""))
