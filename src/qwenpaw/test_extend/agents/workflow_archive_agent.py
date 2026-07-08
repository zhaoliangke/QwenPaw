# -*- coding: utf-8 -*-
"""Workflow Archive Agent.

Archives workflow step results into the knowledge base so that historical
test assets can be retrieved by AI via RAG search.

Triggered automatically by POST /api/test/update when a step completes.
"""

import logging
from datetime import datetime
from pathlib import Path

from models.knowledge import KnowledgeDocument
from models.workflow_state import WORKFLOW_STEP_NAMES
from storage.file_stores import FileKnowledgeStore

logger = logging.getLogger(__name__)

# Doc type mapping for each workflow step
STEP_DOC_TYPES = {
    "requirement": "prd_summary",
    "functional": "case_pattern",
    "ui-auto": "ui_pattern",
    "review": "review_finding",
    "execution": "execution_insight",
    "report": "test_report",
}


class WorkflowArchiveAgent:
    """Archives workflow step results into the knowledge base."""

    def __init__(self, workspace_dir: str):
        self._workspace_dir = workspace_dir

    async def archive_step_result(
        self,
        iteration_id: str,
        step_id: str,
        result: dict,
    ) -> dict:
        """Archive a completed step's result as a knowledge document.

        Creates or updates a KnowledgeDocument in the knowledge store.
        Returns {"status": "ok", "doc_id": "...", "doc_type": "..."} on success.
        """
        doc_type = STEP_DOC_TYPES.get(step_id, "general")
        title = f"{WORKFLOW_STEP_NAMES.get(step_id, step_id)} [{iteration_id}]"

        # Generate formatted content
        content = self._format_content(step_id, iteration_id, result)

        store = FileKnowledgeStore(self._workspace_dir)

        existing_docs = await store.list_all(doc_type=doc_type, iteration_id=iteration_id)
        for doc in existing_docs:
                # Update existing
                doc.content = content
                doc.title = title
                doc.tags = self._build_tags(step_id, iteration_id)
                await store.update(doc)
                logger.info("Updated knowledge doc %s for step %s", doc.id, step_id)
                return {"status": "updated", "doc_id": doc.id, "doc_type": doc_type}

        # Create new
        doc = KnowledgeDocument(
            title=title,
            content=content,
            doc_type=doc_type,
            tags=self._build_tags(step_id, iteration_id),
            iteration_id=iteration_id,
        )
        await store.create(doc)
        logger.info("Created knowledge doc %s for step %s", doc.id, step_id)

        # Index to RAG (optional, failure-tolerant)
        await self._index_to_rag(doc)

        return {"status": "ok", "doc_id": doc.id, "doc_type": doc_type}

    def _format_content(self, step_id: str, iteration_id: str, result: dict) -> str:
        """Format step result as readable markdown content."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        sections = [
            f"# {WORKFLOW_STEP_NAMES.get(step_id, step_id)}",
            f"",
            f"- **迭代 ID**: {iteration_id}",
            f"- **归档时间**: {timestamp}",
            f"",
        ]

        # Step-specific formatting
        if step_id == "requirement":
            sections.extend(self._format_requirement(result))
        elif step_id == "functional":
            sections.extend(self._format_functional(result))
        elif step_id == "ui-auto":
            sections.extend(self._format_ui_auto(result))
        elif step_id == "review":
            sections.extend(self._format_review(result))
        elif step_id == "execution":
            sections.extend(self._format_execution(result))
        elif step_id == "report":
            sections.extend(self._format_report(result))
        else:
            sections.append("## 产物数据")
            for k, v in result.items():
                sections.append(f"- **{k}**: {v}")

        return "\n".join(sections)

    def _format_requirement(self, result: dict) -> list[str]:
        lines = ["## 需求解析摘要", ""]
        if "modules" in result:
            lines.append(f"- 功能模块数: **{result['modules']}**")
        if "flows" in result:
            flow_count = result["flows"] if isinstance(result["flows"], int) else len(result["flows"])
            lines.append(f"- 业务流程数: **{flow_count}**")
        if "rules" in result:
            lines.append(f"- 验证规则数: **{result['rules']}**")
        if "exceptions" in result:
            lines.append(f"- 异常流数: **{result['exceptions']}**")
        if "nonFunctional" in result:
            lines.append(f"- 非功能性需求数: **{result['nonFunctional']}**")
        if "risks" in result:
            lines.append(f"- 风险项数: **{result['risks']}**")
        return lines

    def _format_functional(self, result: dict) -> list[str]:
        lines = ["## 功能用例生成摘要", ""]
        if "storyCount" in result:
            lines.append(f"- User Story 数: **{result['storyCount']}**")
        if "caseCount" in result:
            lines.append(f"- 测试用例数: **{result['caseCount']}**")
        if "coverage" in result:
            lines.append(f"- 需求覆盖率: **{result['coverage']}%**")
        return lines

    def _format_ui_auto(self, result: dict) -> list[str]:
        lines = ["## UI 自动化用例摘要", ""]
        if "pageObjects" in result:
            lines.append(f"- Page Object 数: **{result['pageObjects']}**")
        if "totalSteps" in result:
            lines.append(f"- 操作步骤总数: **{result['totalSteps']}**")
        if "pages" in result:
            pages = result["pages"] if isinstance(result["pages"], list) else [result["pages"]]
            lines.append(f"- 涉及页面: {', '.join(pages)}")
        return lines

    def _format_review(self, result: dict) -> list[str]:
        lines = ["## 用例评审摘要", ""]
        if "passed" in result:
            lines.append(f"- 评审通过: **{result['passed']}**")
        if "failed" in result:
            lines.append(f"- 评审失败: **{result['failed']}**")
        if "issues" in result:
            issues = result["issues"]
            if isinstance(issues, dict):
                high = issues.get("high", 0)
                medium = issues.get("medium", 0)
                low = issues.get("low", 0)
                lines.append(f"- 发现问题: 高 **{high}** / 中 **{medium}** / 低 **{low}**")
        return lines

    def _format_execution(self, result: dict) -> list[str]:
        lines = ["## 自动测试执行摘要", ""]
        if "total" in result:
            lines.append(f"- 总用例数: **{result['total']}**")
        if "passed" in result:
            lines.append(f"- 通过: **{result['passed']}**")
        if "failed" in result:
            lines.append(f"- 失败: **{result['failed']}**")
        if "skipped" in result:
            lines.append(f"- 跳过: **{result['skipped']}**")
        if "duration" in result:
            lines.append(f"- 耗时: **{result['duration']}s**")
        return lines

    def _format_report(self, result: dict) -> list[str]:
        lines = ["## 端到端测试报告摘要", ""]
        if "passRate" in result:
            lines.append(f"- 通过率: **{result['passRate']}%**")
        if "defects" in result:
            defects = result["defects"]
            if isinstance(defects, dict):
                critical = defects.get("critical", 0)
                major = defects.get("major", 0)
                minor = defects.get("minor", 0)
                lines.append(f"- 缺陷: 致命 **{critical}** / 严重 **{major}** / 一般 **{minor}**")
        if "previousPassRate" in result:
            diff = result.get("passRate", 0) - result.get("previousPassRate", 0)
            arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
            lines.append(f"- 较上次: **{arrow} {abs(diff)}%**")
        return lines

    def _build_tags(self, step_id: str, iteration_id: str) -> list[str]:
        """Build knowledge document tags."""
        tags = [step_id, iteration_id]
        doc_type = STEP_DOC_TYPES.get(step_id, "")
        if doc_type:
            tags.append(doc_type)
        return tags

    async def _index_to_rag(self, doc: KnowledgeDocument):
        """Index the document into the platform's RAG vector store (optional).

        Note: ReMe RAG indexing is handled by the platform's built-in sync.
        Since we use FileKnowledgeStore, the platform's existing knowledge
        sync mechanism (session-sync) will pick up new/updated docs.
        """
        pass
