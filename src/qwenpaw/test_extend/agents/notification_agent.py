# -*- coding: utf-8 -*-
"""Notification engine — real push to DingTalk / Feishu / WeCom / generic webhook.

Each channel builds a platform-native message body (markdown card) and
sends an HTTP POST. Failures are captured, not raised, so one channel
error doesn't block others.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx

from models.notification import (
    ChannelType,
    NotifyMessage,
    NotifyRule,
    NotifyTrigger,
)

logger = logging.getLogger(__name__)

# In-memory rule + log storage (replace with DB in production)
_rules: dict[str, NotifyRule] = {}
_log: list[NotifyMessage] = []


class NotificationEngine:
    def __init__(self, workspace_dir: str):
        self._workspace = workspace_dir

    async def send(
        self,
        channel: ChannelType,
        webhook_url: str,
        title: str,
        content: str,
        trigger: NotifyTrigger = NotifyTrigger.MANUAL,
        rule_id: str = "",
        iteration_id: str = "",
        run_id: str = "",
    ) -> NotifyMessage:
        msg = NotifyMessage(
            rule_id=rule_id,
            trigger=trigger,
            channel=channel,
            title=title,
            content=content,
            iteration_id=iteration_id,
            run_id=run_id,
        )
        try:
            body = self._build_body(channel, title, content)
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(webhook_url, json=body)
                msg.raw_response = resp.text[:500]
                if resp.status_code == 200:
                    rdata = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    errcode = rdata.get("errcode", rdata.get("code", 0))
                    if errcode == 0:
                        msg.status = "sent"
                    else:
                        msg.status = "failed"
                        msg.error = f"API error: {rdata}"
                else:
                    msg.status = "failed"
                    msg.error = f"HTTP {resp.status_code}"
        except Exception as e:
            msg.status = "failed"
            msg.error = str(e)[:200]
            logger.warning("Notification send failed (%s): %s", channel, e)

        msg.sent_at = datetime.utcnow()
        _log.append(msg)
        return msg

    async def dispatch_by_trigger(
        self,
        trigger: NotifyTrigger,
        title: str,
        content: str,
        iteration_id: str = "",
        run_id: str = "",
    ) -> list[NotifyMessage]:
        results = []
        for rule in _rules.values():
            if not rule.enabled:
                continue
            if iteration_id and rule.iteration_id and rule.iteration_id != iteration_id:
                continue
            if trigger not in rule.triggers:
                continue
            tasks = []
            for ch in rule.channels:
                url = rule.webhook_urls.get(ch.value, "")
                if not url:
                    continue
                tasks.append(self.send(ch, url, title, content, trigger, rule.id, iteration_id, run_id))
            if tasks:
                results.extend(await asyncio.gather(*tasks, return_exceptions=False))
        return results

    def _build_body(self, channel: ChannelType, title: str, content: str) -> dict:
        if channel == ChannelType.DINGTALK:
            return {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": f"## {title}\n\n{content}"},
            }
        if channel == ChannelType.FEISHU:
            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": title}},
                    "elements": [{"tag": "markdown", "content": content}],
                },
            }
        if channel == ChannelType.WECOM:
            return {"msgtype": "markdown", "markdown": {"content": f"## {title}\n{content}"}}
        # Generic webhook
        return {"title": title, "content": content, "timestamp": datetime.utcnow().isoformat()}

    def save_rule(self, rule: NotifyRule) -> NotifyRule:
        _rules[rule.id] = rule
        return rule

    def get_rule(self, rule_id: str) -> NotifyRule | None:
        return _rules.get(rule_id)

    def list_rules(self, iteration_id: str = "") -> list[NotifyRule]:
        rules = list(_rules.values())
        if iteration_id:
            rules = [r for r in rules if r.iteration_id == iteration_id]
        return rules

    def delete_rule(self, rule_id: str) -> bool:
        return _rules.pop(rule_id, None) is not None

    def get_log(self, iteration_id: str = "", limit: int = 100) -> list[NotifyMessage]:
        msgs = _log
        if iteration_id:
            msgs = [m for m in msgs if m.iteration_id == iteration_id]
        return msgs[-limit:]
