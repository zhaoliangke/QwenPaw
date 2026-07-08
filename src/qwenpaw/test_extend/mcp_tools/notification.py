# -*- coding: utf-8 -*-
"""Notification MCP tools."""

import logging

logger = logging.getLogger(__name__)

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from agents.notification_agent import NotificationEngine
        from qwenpaw.constant import WORKING_DIR
        _engine = NotificationEngine(WORKING_DIR)
    return _engine


async def send_notification_tool(
    channel: str,
    webhook_url: str,
    title: str,
    content: str,
    trigger: str = "manual",
    iteration_id: str = "",
) -> dict:
    return await _get_engine().send(
        channel=channel, webhook_url=webhook_url, title=title,
        content=content, trigger=trigger, iteration_id=iteration_id,
    )


async def dispatch_notification_tool(
    trigger: str,
    title: str,
    content: str,
    iteration_id: str = "",
    run_id: str = "",
) -> dict:
    messages = await _get_engine().dispatch_by_trigger(
        trigger=trigger, title=title, content=content,
        iteration_id=iteration_id, run_id=run_id,
    )
    return {"dispatched": len(messages), "messages": [m.model_dump() for m in messages]}


async def create_notify_rule_tool(
    name: str,
    triggers: list[str],
    channels: list[str],
    webhook_urls: dict,
    iteration_id: str = "",
) -> dict:
    from models.notification import NotifyRule, NotifyTrigger, ChannelType
    rule = NotifyRule(
        name=name, iteration_id=iteration_id,
        triggers=[NotifyTrigger(t) for t in triggers],
        channels=[ChannelType(c) for c in channels],
        webhook_urls=webhook_urls,
    )
    _get_engine().save_rule(rule)
    return rule.model_dump()


async def list_notify_rules_tool(iteration_id: str = "") -> dict:
    rules = _get_engine().list_rules(iteration_id)
    return {"rules": [r.model_dump() for r in rules], "total": len(rules)}
