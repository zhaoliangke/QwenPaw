# -*- coding: utf-8 -*-
"""CI/CD integration webhook router.

Receives push/PR events from GitHub/GitLab and triggers
test execution automatically. Also provides CI config templates.
"""

import hashlib
import hmac
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from common.trace_id import generate_trace_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cicd", tags=["cicd"])

# In-memory registry of webhook configs (replace with DB in production)
_webhook_configs: dict[str, dict] = {}
# In-memory event log
_event_log: list[dict] = []


@router.post("/webhook/{iteration_id}")
async def receive_webhook(
    iteration_id: str,
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str = Header("push"),
    x_gitlab_event: str = Header(""),
) -> dict[str, Any]:
    """Receive webhook from GitHub/GitLab and trigger test execution."""
    body = await request.body()
    payload = await request.json()

    # Verify signature if configured
    config = _webhook_configs.get(iteration_id, {})
    secret = config.get("secret", "")
    if secret and x_hub_signature_256:
        expected = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Extract commit info
    commit_sha = (
        payload.get("after") or
        payload.get("checkout_sha") or
        payload.get("head_commit", {}).get("id", "unknown")
    )
    branch = (
        payload.get("ref", "").replace("refs/heads/", "") or
        payload.get("ref", "")
    )
    author = (
        payload.get("pusher", {}).get("name", "") or
        payload.get("user_name", "")
    )
    repo = (
        payload.get("repository", {}).get("full_name", "") or
        payload.get("project", {}).get("path_with_namespace", "")
    )

    event_record = {
        "id": generate_trace_id("EVT"),
        "iteration_id": iteration_id,
        "event_type": x_github_event or x_gitlab_event or "push",
        "branch": branch,
        "commit_sha": commit_sha[:12],
        "author": author,
        "repo": repo,
        "received_at": datetime.utcnow().isoformat(),
        "status": "received",
    }
    _event_log.append(event_record)

    logger.info(
        "Webhook received: %s@%s (commit %s) for iteration %s",
        repo, branch, commit_sha[:8], iteration_id,
    )

    return {
        "status": "ok",
        "event_id": event_record["id"],
        "trigger": {
            "type": event_record["event_type"],
            "branch": branch,
            "commit": commit_sha[:12],
        },
    }


@router.post("/config/{iteration_id}")
async def configure_webhook(iteration_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Configure webhook settings for an iteration."""
    _webhook_configs[iteration_id] = {
        "iteration_id": iteration_id,
        "secret": body.get("secret", ""),
        "events": body.get("events", ["push"]),
        "branches": body.get("branches", ["main", "master"]),
        "auto_trigger": body.get("auto_trigger", True),
        "target_path": body.get("target_path", ""),
    }
    return {
        "iteration_id": iteration_id,
        "configured": True,
        "events": _webhook_configs[iteration_id]["events"],
    }


@router.get("/config/{iteration_id}")
async def get_webhook_config(iteration_id: str) -> dict[str, Any]:
    config = _webhook_configs.get(iteration_id, {})
    return {"iteration_id": iteration_id, "config": config}


@router.get("/events")
async def list_events(iteration_id: str = "", limit: int = 50) -> dict[str, Any]:
    events = _event_log
    if iteration_id:
        events = [e for e in events if e["iteration_id"] == iteration_id]
    return {"events": events[-limit:], "total": len(events)}


@router.get("/template/github-actions")
async def github_actions_template() -> dict[str, Any]:
    """GitHub Actions workflow template for triggering test runs."""
    template = """name: AI Test Platform Trigger
on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master]

jobs:
  trigger-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Test Execution
        run: |
          curl -X POST "${API_URL}/api/test/cicd/webhook/${ITERATION_ID}" \\
            -H "Content-Type: application/json" \\
            -H "X-GitHub-Event: push" \\
            -d '{
              "ref": "${{ github.ref }}",
              "after": "${{ github.sha }}",
              "pusher": {"name": "${{ github.actor }}"},
              "repository": {"full_name": "${{ github.repository }}"}
            }'
"""
    return {"template": template, "format": "yaml", "filename": "ai-test-trigger.yml"}


@router.get("/template/gitlab-ci")
async def gitlab_ci_template() -> dict[str, Any]:
    """GitLab CI template for triggering test runs."""
    template = """trigger_ai_tests:
  stage: test
  script:
    - |
      curl -X POST "${API_URL}/api/test/cicd/webhook/${ITERATION_ID}" \\
        -H "Content-Type: application/json" \\
        -H "X-GitLab-Event: Push Hook" \\
        -d '{
          "ref": "$CI_COMMIT_REF_NAME",
          "checkout_sha": "$CI_COMMIT_SHA",
          "user_name": "$GITLAB_USER_NAME",
          "project": {"path_with_namespace": "$CI_PROJECT_PATH"}
        }'
  only:
    - main
    - master
    - develop
"""
    return {"template": template, "format": "yaml", "filename": ".gitlab-ci-ai-test.yml"}
