# -*- coding: utf-8 -*-
"""ReMe vector store integration for the test platform knowledge base.

The test knowledge base is a dedicated ReMe vault that stores and indexes
test documents (PRDs, test cases, bug reports, test design docs, etc.).

Architecture:
  - A separate ReMe instance (not shared with agent memory) manages the
    test_knowledge vault directory.
  - Documents are stored as .md files in workspace/test/knowledge/vault/.
  - ReMe's index_update_loop automatically chunks, embeds, and indexes them.
  - RAG search returns relevant document chunks with hybrid (vector+BM25) ranking.

Usage:
    from qwenpaw.test_extend.infra.reme_knowledge import (
        init_knowledge_base, close_knowledge_base, search_test_knowledge
    )
    await init_knowledge_base(workspace_dir="/path/to/workspace")
    results = await search_test_knowledge("登录页面的测试策略", limit=10)
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_reme_app = None
_knowledge_dir: Optional[Path] = None


def _get_knowledge_vault_dir(workspace_dir: str) -> Path:
    return Path(workspace_dir) / "test" / "knowledge" / "vault"


def _get_knowledge_daily_dir(workspace_dir: str) -> Path:
    return Path(workspace_dir) / "test" / "knowledge" / "daily"


def _get_knowledge_digest_dir(workspace_dir: str) -> Path:
    return Path(workspace_dir) / "test" / "knowledge" / "digest"


async def init_knowledge_base(workspace_dir: str):
    """Initialize the test knowledge ReMe vault.

    Creates the vault directory structure and starts a dedicated ReMe
    instance for indexing test documents.

    Args:
        workspace_dir: Root workspace path (e.g., ~/.qwenpaw/)
    """
    global _reme_app, _knowledge_dir

    vault = _get_knowledge_vault_dir(workspace_dir)
    daily = _get_knowledge_daily_dir(workspace_dir)
    digest = _get_knowledge_digest_dir(workspace_dir)

    vault.mkdir(parents=True, exist_ok=True)
    daily.mkdir(parents=True, exist_ok=True)
    digest.mkdir(parents=True, exist_ok=True)
    _knowledge_dir = vault

    try:
        from reme import ReMe as ReMeApp

        _reme_app = ReMeApp(
            workspace_dir=str(vault),
            metadata_dir=str(vault / ".reme_meta"),
            session_dir=str(vault / ".reme_session"),
            resource_dir=str(vault / "resources"),
            daily_dir=str(daily),
            digest_dir=str(digest),
            language="zh",
            timezone="Asia/Shanghai",
            enable_logo=False,
            log_to_console=False,
        )
        await _reme_app.start()
        logger.info("Test knowledge ReMe vault started at %s", vault)
    except Exception as e:
        logger.error("Failed to start test knowledge ReMe vault: %s", e)
        _reme_app = None


async def close_knowledge_base():
    """Shut down the test knowledge ReMe vault."""
    global _reme_app, _knowledge_dir
    if _reme_app:
        try:
            await _reme_app.close()
        except Exception as e:
            logger.warning("Error closing ReMe vault: %s", e)
        _reme_app = None
        _knowledge_dir = None


def is_knowledge_base_ready() -> bool:
    return _reme_app is not None


async def add_knowledge_document(
    title: str,
    content: str,
    *,
    doc_type: str = "general",
    product_line: str = "",
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> str:
    """Add a test knowledge document to the vault for indexing.

    The document is written as a .md file into the daily_dir.
    ReMe's index_update_loop will automatically pick it up,
    chunk it, compute embeddings, and add it to the vector index.

    Args:
        title: Document title (used as filename prefix).
        content: Document body in Markdown.
        doc_type: Category (prd, test_case, bug_report, design, general).
        product_line: Associated product line for filtering.
        tags: Optional tags for metadata filtering.
        metadata: Additional metadata dict.

    Returns:
        The file path of the created document.
    """
    global _reme_app
    if _reme_app is None:
        raise RuntimeError("Knowledge base not initialized")

    vault = _knowledge_dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "._-" else "_" for c in title)[:80]
    filename = f"{timestamp}_{safe_title}.md"
    filepath = str(vault / "resources" / filename)

    os.makedirs(str(vault / "resources"), exist_ok=True)

    frontmatter = {
        "doc_type": doc_type,
        "product_line": product_line,
        "tags": tags or [],
        "title": title,
        "created_at": datetime.now().isoformat(),
    }
    if metadata:
        frontmatter.update(metadata)

    full_text = f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n{content}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_text)

    logger.info("Knowledge document added: %s (type=%s, tags=%s)", filename, doc_type, tags)
    return filepath


async def add_knowledge_batch(documents: list[dict]) -> list[str]:
    """Batch-add multiple knowledge documents.

    Args:
        documents: List of dicts with keys: title, content, doc_type,
                   product_line, tags, metadata.

    Returns:
        List of file paths.
    """
    paths = []
    for doc in documents:
        path = await add_knowledge_document(
            title=doc["title"],
            content=doc["content"],
            doc_type=doc.get("doc_type", "general"),
            product_line=doc.get("product_line", ""),
            tags=doc.get("tags"),
            metadata=doc.get("metadata"),
        )
        paths.append(path)
    return paths


async def search_test_knowledge(
    query: str,
    *,
    limit: int = 10,
    min_score: float = 0.0,
    filter_doc_type: str | None = None,
    filter_product_line: str | None = None,
) -> list[dict]:
    """Search the test knowledge base with hybrid (vector+BM25) retrieval.

    Args:
        query: Natural language search query.
        limit: Maximum number of results to return.
        min_score: Minimum relevance score threshold (0.0 ~ 1.0).
        filter_doc_type: Optional filter by document type.
        filter_product_line: Optional filter by product line.

    Returns:
        List of result dicts with keys: score, title, content, file_path,
        doc_type, product_line, tags.
    """
    global _reme_app
    if _reme_app is None:
        logger.warning("Knowledge base not initialized, returning empty results")
        return []

    try:
        response = await _reme_app.run_job(
            "search",
            query=query,
            limit=max(1, limit),
            min_score=max(0.0, min_score),
        )

        if response is None or not response.success:
            return []

        answer_text = str(response.answer or "").strip()
        results = _parse_search_results(answer_text)

        if filter_doc_type:
            results = [r for r in results if r.get("doc_type") == filter_doc_type]
        if filter_product_line:
            results = [r for r in results if r.get("product_line") == filter_product_line]

        return results[:limit]

    except Exception as e:
        logger.error("Knowledge search failed: %s", e)
        return []


def _parse_search_results(text: str) -> list[dict]:
    """Parse ReMe search job output into structured results.

    ReMe search output format varies by version. We try multiple
    parsing strategies to extract structured fields:
    1. JSON-per-line format (newer ReMe versions)
    2. Markdown list with file paths (older versions)
    3. Raw text split by paragraph blocks
    """
    if not text:
        return []

    import re

    results = []

    # Strategy 1: JSON lines (newer ReMe)
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                results.append({
                    "content": obj.get("content", obj.get("text", "")),
                    "file_path": obj.get("file_path", obj.get("source", "")),
                    "title": obj.get("title", obj.get("name", "")),
                    "doc_type": obj.get("doc_type", ""),
                    "product_line": obj.get("product_line", ""),
                    "tags": obj.get("tags", []),
                    "score": float(obj.get("score", obj.get("relevance", 0.5))),
                })
            except (json.JSONDecodeError, ValueError):
                pass

    if results:
        return sorted(results, key=lambda x: x["score"], reverse=True)

    # Strategy 2: Markdown bullet with file path patterns
    file_pattern = re.compile(r'[`*]?(.+?\.(?:md|json|txt|yml|yaml))[`*]?', re.IGNORECASE)
    score_pattern = re.compile(r'(?:score|relevance|rank)[:\s]*([0-9.]+)', re.IGNORECASE)

    blocks = text.split("\n\n")
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        file_match = file_pattern.search(block)
        score_match = score_pattern.search(block)

        lines = block.split("\n")
        content = lines[-1].strip() if len(lines) > 1 else block[:500]
        score = float(score_match.group(1)) if score_match else 0.4

        results.append({
            "content": content,
            "file_path": file_match.group(1) if file_match else "",
            "title": file_match.group(1).split("/")[-1] if file_match else "",
            "doc_type": "",
            "product_line": "",
            "tags": [],
            "score": min(score, 1.0),
        })

    if results:
        return sorted(results, key=lambda x: x["score"], reverse=True)

    # Strategy 3: Raw text split by newlines
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) > 20:
            results.append({
                "content": line[:1000],
                "file_path": "",
                "title": "",
                "doc_type": "",
                "product_line": "",
                "tags": [],
                "score": 0.3,
            })

    return results[:50]


async def rebuild_knowledge_index():
    """Force-rebuild the entire knowledge base vector index.

    Useful after bulk-adding documents or changing embedding config.
    """
    global _reme_app
    if _reme_app is None:
        raise RuntimeError("Knowledge base not initialized")

    await _reme_app.run_job("reindex")
    logger.info("Knowledge base index rebuilt")


async def delete_knowledge_document(file_path: str):
    """Delete a knowledge document and its vector embeddings.

    Removing the file triggers ReMe's file_store to remove
    corresponding vector chunks from the index.
    """
    path = Path(file_path)
    if path.exists():
        path.unlink()
        logger.info("Knowledge document deleted: %s", path)
