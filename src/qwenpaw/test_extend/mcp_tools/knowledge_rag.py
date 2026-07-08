# -*- coding: utf-8 -*-
"""Knowledge Base RAG MCP Tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.knowledge_arch_agent import KnowledgeArchAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = KnowledgeArchAgent(WORKING_DIR)
    return _agent


async def archive_iteration_tool(iteration_id: str) -> dict:
    return await _get_agent().archive_iteration(iteration_id)


async def search_knowledge_tool(query: str, product_line: str = "", limit: int = 10) -> dict:
    return await _get_agent().search_knowledge(query, product_line or None, limit)


async def upload_document_tool(file_path: str, metadata: dict | None = None) -> dict:
    return await _get_agent().upload_document(file_path, metadata)


async def distill_knowledge_tool(product_line: str = "") -> dict:
    return await _get_agent().distill_knowledge(product_line)


async def schedule_backup_tool(cron_expression: str = "0 2 * * 0") -> dict:
    return await _get_agent().schedule_backup(cron_expression)
