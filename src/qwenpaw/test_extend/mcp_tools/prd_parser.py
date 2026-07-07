# -*- coding: utf-8 -*-
"""PRD Parsing MCP Tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from ...agents.prd_parse_agent import PrdParseAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = PrdParseAgent(WORKING_DIR)
    return _agent


async def parse_document_tool(file_path: str, iteration_id: str) -> dict:
    return await _get_agent().parse_document(file_path, iteration_id)


async def parse_openapi_tool(spec_url: str, iteration_id: str) -> dict:
    return await _get_agent().parse_openapi(spec_url, iteration_id)


async def parse_figma_tool(figma_url: str, iteration_id: str) -> dict:
    return await _get_agent().parse_figma(figma_url, iteration_id)


async def identify_ambiguities_tool(parsed_prd_json: str) -> dict:
    import json
    parsed_prd = json.loads(parsed_prd_json) if isinstance(parsed_prd_json, str) else parsed_prd_json
    return await _get_agent().identify_ambiguities(parsed_prd)
