# -*- coding: utf-8 -*-
"""Environment management router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.environment_agent import EnvironmentAgent
from common.trace_id import generate_trace_id
from models.environment import Environment, EnvStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/env", tags=["environment"])

_agent: EnvironmentAgent | None = None


def init_env_agent(workspace_dir: str):
    global _agent
    _agent = EnvironmentAgent(workspace_dir)


@router.post("/")
async def register_env(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Environment agent not initialized")
    env = Environment(
        id=generate_trace_id("ENV"),
        name=body.get("name", ""),
        base_url=body.get("base_url", ""),
        description=body.get("description", ""),
        iteration_id=body.get("iteration_id", ""),
        health_check_url=body.get("health_check_url", ""),
        env_vars=body.get("env_vars", {}),
        headers=body.get("headers", {}),
        status=EnvStatus.UNKNOWN,
    )
    await _agent.register_env(env)
    return {"id": env.id, "name": env.name, "base_url": env.base_url, "status": env.status.value}


@router.get("/")
async def list_envs(iteration_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Environment agent not initialized")
    envs = _agent.list_envs(iteration_id)
    return {"environments": [e.model_dump() for e in envs], "total": len(envs)}


@router.get("/{env_id}")
async def get_env(env_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Environment agent not initialized")
    env = _agent.get_env(env_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")
    return env.model_dump()


@router.delete("/{env_id}")
async def delete_env(env_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Environment agent not initialized")
    ok = _agent.delete_env(env_id)
    return {"deleted": ok, "id": env_id}


@router.post("/{env_id}/health_check")
async def health_check(env_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Environment agent not initialized")
    result = await _agent.health_check(env_id)
    return result.model_dump()


@router.post("/health_check_all")
async def health_check_all() -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Environment agent not initialized")
    results = await _agent.health_check_all()
    return {"results": [r.model_dump() for r in results], "total": len(results)}
