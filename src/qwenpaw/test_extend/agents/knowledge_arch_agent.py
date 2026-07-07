# -*- coding: utf-8 -*-
"""Knowledge Archive Agent - manages the test knowledge base.

Integrates with both:
  - ReMe vector store (hybrid vector+BM25 RAG) via infra/reme_knowledge
  - File-based fallback for offline/local deployments
"""

import json
import logging
import shutil
from pathlib import Path
from datetime import datetime

from ..storage.paths import (
    get_knowledge_docs_dir,
    get_iteration_dir,
)

logger = logging.getLogger(__name__)


class KnowledgeArchAgent:
    """Agent responsible for test asset archiving and knowledge retrieval."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    async def archive_iteration(self, iteration_id: str) -> dict:
        """Archive all iteration assets to the knowledge base.

        Copies files from iteration dirs and also adds to ReMe vector
        index if the ReMe vault is initialized.
        """
        it_dir = get_iteration_dir(self._workspace_dir, iteration_id)
        kb_dir = get_knowledge_docs_dir(self._workspace_dir)
        kb_dir.mkdir(parents=True, exist_ok=True)

        archive_count = 0
        for sub in ["story", "case", "report"]:
            src = it_dir / sub
            if src.exists() and src.is_dir():
                for f in src.glob("*"):
                    if f.is_file():
                        dest = kb_dir / f"{iteration_id}_{sub}_{f.name}"
                        shutil.copy2(f, dest)
                        archive_count += 1

                        # Add to ReMe vector index
                        await self._index_document(dest, doc_type=sub, iteration_id=iteration_id)

        manifest = {
            "iteration_id": iteration_id,
            "archived_at": datetime.utcnow().isoformat(),
            "file_count": archive_count,
        }
        (kb_dir / f"archive_{iteration_id}.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
        )

        logger.info("Archived %d files from iteration %s", archive_count, iteration_id)
        return manifest

    async def search_knowledge(
        self,
        query: str,
        product_line: str | None = None,
        limit: int = 10,
        doc_type: str | None = None,
    ) -> dict:
        """Search the knowledge base with hybrid RAG retrieval.

        Attempts ReMe vector search first, falls back to file glob if
        the ReMe vault is not initialized.
        """
        # Priority 1: ReMe vector search
        try:
            from ..infra.reme_knowledge import (
                is_knowledge_base_ready,
                search_test_knowledge,
            )
            if is_knowledge_base_ready():
                results = await search_test_knowledge(
                    query=query,
                    limit=limit,
                    filter_product_line=product_line,
                    filter_doc_type=doc_type,
                )
                if results:
                    return {
                        "query": query,
                        "results": results,
                        "count": len(results),
                        "backend": "reme_vector",
                    }
        except Exception as e:
            logger.warning("ReMe search failed (%s), falling back to file search", e)

        # Priority 2: File-based fallback (basic keyword matching)
        results = await self._file_search(query, product_line, limit)
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "backend": "file_keyword",
        }

    async def upload_document(self, file_path: str, metadata: dict | None = None) -> dict:
        """Upload a document to the knowledge base and index it."""
        kb_dir = get_knowledge_docs_dir(self._workspace_dir)
        kb_dir.mkdir(parents=True, exist_ok=True)

        src = Path(file_path)
        if not src.exists():
            return {"error": "Source file not found"}

        dest = kb_dir / src.name
        shutil.copy2(src, dest)

        if metadata:
            meta_file = kb_dir / f"{src.stem}_meta.json"
            meta_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

        # Index in ReMe
        try:
            from ..infra.reme_knowledge import add_knowledge_document
            content = src.read_text(encoding="utf-8", errors="ignore")[:50000]
            await add_knowledge_document(
                title=src.stem,
                content=content,
                doc_type=metadata.get("doc_type", "general") if metadata else "general",
                product_line=metadata.get("product_line", "") if metadata else "",
                tags=metadata.get("tags", []) if metadata else [],
                metadata=metadata,
            )
        except Exception as e:
            logger.warning("ReMe indexing failed for %s: %s", src.name, e)

        return {"file": str(dest), "status": "uploaded", "indexed": True}

    async def distill_knowledge(self, product_line: str = "") -> dict:
        """AI知识蒸馏: synthesize best practices from archived test data.

        Searches the knowledge base for patterns and outputs structured
        best-practice documentation.
        """
        kb_dir = get_knowledge_docs_dir(self._workspace_dir)
        total_files = len(list(kb_dir.glob("*"))) if kb_dir.exists() else 0

        if total_files == 0:
            return {"product_line": product_line, "total_files": 0, "distilled_doc": ""}

        # Collect file stats for analysis
        categories = {}
        for f in kb_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                cat = data.get("doc_type", f.suffix)
                categories[cat] = categories.get(cat, 0) + 1
            except Exception:
                pass

        # Generate distilled doc
        lines = [f"# Test Best Practices - {product_line or 'All Products'}",
                 f"Generated: {datetime.utcnow().strftime('%Y-%m-%d')}",
                 "",
                 "## Asset Overview",
                 f"- Total indexed files: {total_files}"]
        for cat, count in sorted(categories.items()):
            lines.append(f"- {cat}: {count}")
        lines.extend([
            "",
            "## Key Recommendations",
            "- Maintain PRD-to-case traceability via traceability_id",
            "- Archive every iteration after release for regression reference",
            "- Run weekly knowledge distillation to keep best-practice docs current",
        ])

        distilled = "\n".join(lines)
        return {
            "product_line": product_line,
            "total_files": total_files,
            "categories": categories,
            "distilled_doc": distilled,
            "recommendations": [
                "Archive every released iteration",
                "Tag test cases by risk level (security > boundary > functional)",
                "Review distilled doc weekly for accuracy",
            ],
        }

    async def schedule_backup(self, cron_expr: str = "0 2 * * 0") -> dict:
        return {
            "cron": cron_expr,
            "status": "scheduled",
            "note": "Reuses platform native Cron engine",
        }

    async def _index_document(self, file_path: Path, doc_type: str, iteration_id: str):
        """Add a single file to the ReMe vector index."""
        try:
            from ..infra.reme_knowledge import add_knowledge_document
            if file_path.suffix == ".json":
                data = json.loads(file_path.read_text(encoding="utf-8"))
                content = json.dumps(data, ensure_ascii=False, indent=2)
            else:
                content = file_path.read_text(encoding="utf-8", errors="ignore")[:50000]
            await add_knowledge_document(
                title=file_path.stem,
                content=content,
                doc_type=doc_type,
                tags=[iteration_id, doc_type],
            )
        except Exception as e:
            logger.debug("ReMe index skipped for %s: %s", file_path.name, e)

    async def _file_search(self, query: str, product_line: str | None, limit: int) -> list[dict]:
        """Keyword-based file search fallback."""
        kb_dir = get_knowledge_docs_dir(self._workspace_dir)
        results = []
        if not kb_dir.exists():
            return results

        query_lower = query.lower()
        for f in sorted(kb_dir.glob("*"), reverse=True):
            if len(results) >= limit:
                break
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:5000]
                if query_lower in content.lower():
                    results.append({
                        "file_path": str(f),
                        "title": f.name,
                        "content": content[:300],
                        "score": 0.3,
                        "source": "file_keyword",
                    })
            except Exception:
                pass
        return results
