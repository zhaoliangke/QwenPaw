# -*- coding: utf-8 -*-
"""Test Platform API router aggregation.

Creates a top-level APIRouter that aggregates all test platform
sub-routers. Each module (iteration, prd, case, etc.) will add
its own routes in later implementation phases.
"""

from fastapi import APIRouter


def create_test_router() -> APIRouter:
    """Create and return the top-level test platform APIRouter.

    This router is mounted at /api/test by the plugin registration
    logic. Sub-routers will be added as each module is implemented.

    Returns:
        FastAPI APIRouter with /api/test prefix.
    """
    router = APIRouter()

    @router.get("/health")
    async def test_platform_health():
        """Health check endpoint for the test platform."""
        return {"status": "ok", "platform": "ai-test-platform"}

    return router
