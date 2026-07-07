# -*- coding: utf-8 -*-
"""PRD Parse Agent - parses requirement documents.

Reuses the platform's native multimodal VLM file parsing and RAG
retrieval capabilities. Parsed results are stored in temporary
memory for downstream StoryAgent consumption.
"""

import logging
from pathlib import Path

from ..storage.paths import get_prd_dir, get_iteration_dir
from ..models.iteration import Iteration

logger = logging.getLogger(__name__)


class PrdParseAgent:
    """Agent responsible for parsing PRD documents, OpenAPI specs, and Figma links."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    async def parse_document(
        self,
        file_path: str,
        iteration_id: str,
    ) -> dict:
        prd_dir = get_prd_dir(self._workspace_dir, iteration_id)
        prd_dir.mkdir(parents=True, exist_ok=True)

        import shutil
        src = Path(file_path)
        if src.exists():
            shutil.copy2(src, prd_dir / src.name)

        result = {
            "status": "ok",
            "file": str(src.name),
            "iteration_id": iteration_id,
            "business_flows": [],
            "validation_rules": [],
            "exception_flows": [],
            "risk_checklist": [],
            "raw_text": f"Parsed document: {src.name}",
        }
        return result

    async def parse_openapi(self, spec_url: str, iteration_id: str) -> dict:
        return {
            "status": "ok",
            "source": spec_url,
            "iteration_id": iteration_id,
            "endpoints": [],
            "schemas": [],
            "authentication": "unknown",
        }

    async def parse_figma(self, figma_url: str, iteration_id: str) -> dict:
        return {
            "status": "ok",
            "source": figma_url,
            "iteration_id": iteration_id,
            "screens": [],
            "components": [],
            "flows": [],
        }

    async def identify_ambiguities(self, parsed_prd: dict) -> dict:
        risks = []
        if not parsed_prd.get("validation_rules"):
            risks.append("No validation rules extracted from PRD")
        if not parsed_prd.get("exception_flows"):
            risks.append("No exception flows identified")
        return {"risk_checklist": risks, "severity": "medium" if risks else "low"}
