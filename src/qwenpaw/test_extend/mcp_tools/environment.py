# -*- coding: utf-8 -*-
"""Environment management MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.environment_agent import EnvironmentAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = EnvironmentAgent(WORKING_DIR)
    return _agent


async def register_env_tool(
    name: str,
    base_url: str,
    description: str = "",
    iteration_id: str = "",
    health_check_url: str = "",
    env_vars: dict | None = None,
    headers: dict | None = None,
) -> dict:
    from models.environment import Environment, EnvStatus
    env = Environment(
        name=name, base_url=base_url, description=description,
        iteration_id=iteration_id, health_check_url=health_check_url,
        env_vars=env_vars or {}, headers=headers or {},
        status=EnvStatus.UNKNOWN,
    )
    await _get_agent().register_env(env)
    return {"id": env.id, "name": env.name, "base_url": env.base_url}


async def health_check_env_tool(env_id: str) -> dict:
    return await _get_agent().health_check(env_id)


async def list_envs_tool(iteration_id: str = "") -> dict:
    envs = _get_agent().list_envs(iteration_id)
    return {"environments": [e.model_dump() for e in envs], "total": len(envs)}


async def delete_env_tool(env_id: str) -> dict:
    ok = _get_agent().delete_env(env_id)
    return {"deleted": ok, "id": env_id}
