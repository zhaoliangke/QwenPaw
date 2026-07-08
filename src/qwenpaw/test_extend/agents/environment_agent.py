# -*- coding: utf-8 -*-
"""Environment management agent — register, health-check, and track test environments."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.environment import (
    EnvHealthResult,
    EnvStatus,
    Environment,
)
from storage.paths import get_env_dir

logger = logging.getLogger(__name__)


class EnvironmentAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._env_dir = get_env_dir(self._workspace)
        self._env_dir.mkdir(parents=True, exist_ok=True)

    async def register_env(self, env: Environment) -> Environment:
        self._save_env(env)
        return env

    async def health_check(self, env_id: str) -> EnvHealthResult:
        env = self._load_env(env_id)
        if not env:
            return EnvHealthResult(env_id=env_id, status=EnvStatus.UNKNOWN, error="Environment not found")
        return await self._do_health_check(env)

    async def health_check_all(self) -> list[EnvHealthResult]:
        results = []
        for env_file in sorted(self._env_dir.glob("*.json")):
            data = read_json_file(env_file)
            if data:
                env = Environment(**data)
                results.append(await self._do_health_check(env))
        return results

    async def _do_health_check(self, env: Environment) -> EnvHealthResult:
        check_url = env.health_check_url or env.base_url
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(check_url)
                rt = resp.elapsed.total_seconds() * 1000
                if resp.status_code < 400:
                    env.status = EnvStatus.READY
                else:
                    env.status = EnvStatus.DOWN
                env.response_time_ms = rt
                env.last_check = datetime.utcnow()
                result = EnvHealthResult(
                    env_id=env.id, status=env.status,
                    response_time_ms=rt, status_code=resp.status_code,
                )
        except Exception as e:
            env.status = EnvStatus.DOWN
            env.last_check = datetime.utcnow()
            result = EnvHealthResult(
                env_id=env.id, status=EnvStatus.DOWN, error=str(e)[:200],
            )

        self._save_env(env)
        return result

    def list_envs(self, iteration_id: str = "") -> list[Environment]:
        envs = []
        for f in sorted(self._env_dir.glob("*.json")):
            data = read_json_file(f)
            if data:
                env = Environment(**data)
                if not iteration_id or env.iteration_id == iteration_id:
                    envs.append(env)
        return envs

    def get_env(self, env_id: str) -> Environment | None:
        return self._load_env(env_id)

    def delete_env(self, env_id: str) -> bool:
        f = self._env_dir / f"{env_id}.json"
        if f.exists():
            f.unlink()
            return True
        return False

    def _save_env(self, env: Environment):
        f = self._env_dir / f"{env.id}.json"
        write_json_file(f, env.model_dump())

    def _load_env(self, env_id: str) -> Environment | None:
        f = self._env_dir / f"{env_id}.json"
        if f.exists():
            data = read_json_file(f)
            return Environment(**data) if data else None
        return None
