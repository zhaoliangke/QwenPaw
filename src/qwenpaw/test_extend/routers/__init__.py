# -*- coding: utf-8 -*-
"""Test Platform API router aggregation.

Creates a top-level APIRouter that aggregates all test platform
sub-routers at /api/test/*. Each sub-router handles a specific
domain of the test platform.
"""

from fastapi import APIRouter


def create_test_router() -> APIRouter:
    """Create and return the top-level test platform APIRouter.

    Mounted at /api/test by the plugin registration logic.
    """
    router = APIRouter()

    from .iteration import router as iteration_router
    from .prd_analysis import router as prd_router
    from .case_manage import router as case_router
    from .ui_auto import router as ui_auto_router
    from .test_exec import router as exec_router
    from .report_center import router as report_router
    from .knowledge_lib import router as knowledge_router

    router.include_router(iteration_router, prefix="/iteration", tags=["Test Platform - Iteration"])
    router.include_router(prd_router, prefix="/prd", tags=["Test Platform - PRD"])
    router.include_router(case_router, prefix="/case", tags=["Test Platform - Case"])
    router.include_router(ui_auto_router, prefix="/ui-auto", tags=["Test Platform - UI Auto"])
    router.include_router(exec_router, prefix="/exec", tags=["Test Platform - Execution"])
    router.include_router(report_router, prefix="/report", tags=["Test Platform - Report"])
    router.include_router(knowledge_router, prefix="/knowledge", tags=["Test Platform - Knowledge"])

    # Story routes are mounted under /prd prefix for consistency
    router.include_router(prd_router, prefix="", tags=["Test Platform - Story"])

    @router.get("/health")
    async def test_platform_health():
        return {"status": "ok", "platform": "ai-test-platform", "modules": [
            "iteration", "prd", "story", "case", "ui-auto", "exec", "report", "knowledge"
        ]}

    return router
