# -*- coding: utf-8 -*-
"""Notification API router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.notification_agent import NotificationEngine
from models.notification import (
    ChannelType,
    NotifyRule,
    NotifyTrigger,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notify", tags=["notification"])

_engine: NotificationEngine | None = None


def init_notification_engine(workspace_dir: str):
    global _engine
    _engine = NotificationEngine(workspace_dir)


@router.post("/send")
async def send_notification(body: dict[str, Any]) -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    channel = ChannelType(body.get("channel", "webhook"))
    webhook_url = body.get("webhook_url", "")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="webhook_url required")
    msg = await _engine.send(
        channel=channel,
        webhook_url=webhook_url,
        title=body.get("title", "Test Notification"),
        content=body.get("content", ""),
        trigger=NotifyTrigger(body.get("trigger", "manual")),
        iteration_id=body.get("iteration_id", ""),
        run_id=body.get("run_id", ""),
    )
    return msg.model_dump()


@router.post("/dispatch")
async def dispatch_by_trigger(body: dict[str, Any]) -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    trigger = NotifyTrigger(body.get("trigger", "manual"))
    messages = await _engine.dispatch_by_trigger(
        trigger=trigger,
        title=body.get("title", ""),
        content=body.get("content", ""),
        iteration_id=body.get("iteration_id", ""),
        run_id=body.get("run_id", ""),
    )
    return {"dispatched": len(messages), "messages": [m.model_dump() for m in messages]}


@router.post("/rules")
async def create_rule(body: dict[str, Any]) -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    rule = NotifyRule(
        name=body.get("name", ""),
        iteration_id=body.get("iteration_id", ""),
        triggers=[NotifyTrigger(t) for t in body.get("triggers", [])],
        channels=[ChannelType(c) for c in body.get("channels", [])],
        webhook_urls=body.get("webhook_urls", {}),
        min_severity=body.get("min_severity", "info"),
        enabled=body.get("enabled", True),
    )
    _engine.save_rule(rule)
    return rule.model_dump()


@router.get("/rules")
async def list_rules(iteration_id: str = "") -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    rules = _engine.list_rules(iteration_id)
    return {"rules": [r.model_dump() for r in rules], "total": len(rules)}


@router.get("/rules/{rule_id}")
async def get_rule(rule_id: str) -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    rule = _engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    return rule.model_dump()


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str) -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    ok = _engine.delete_rule(rule_id)
    return {"deleted": ok, "id": rule_id}


@router.get("/log")
async def get_log(iteration_id: str = "", limit: int = 100) -> dict[str, Any]:
    if not _engine:
        raise HTTPException(status_code=503, detail="Notification engine not initialized")
    msgs = _engine.get_log(iteration_id, limit)
    return {"messages": [m.model_dump() for m in msgs], "total": len(msgs)}
