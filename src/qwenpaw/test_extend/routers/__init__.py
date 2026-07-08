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
    from .project import router as project_router
    from .defect_sync import router as defect_router
    from .test_data import router as test_data_router
    from .coverage import router as coverage_router
    from .cicd import router as cicd_router
    from .regression import router as regression_router
    from .notification import router as notification_router
    from .api_test import router as api_test_router
    from .environment import router as env_router
    from .case_version import router as case_version_router
    from .masking import router as masking_router
    from .recording import router as recording_router
    from .execution_queue import router as queue_router
    from .performance import router as perf_router
    from .collaboration import router as collab_router
    from .visual_diff import router as visual_diff_router
    from .ab_test import router as ab_test_router
    from .chaos import router as chaos_router
    from .analytics import router as analytics_router
    from .workflow import router as workflow_router
    from .project import router as project_router
    from .element_map import router as element_map_router

    router.include_router(iteration_router, prefix="/iteration", tags=["Test Platform - Iteration"])
    router.include_router(prd_router, prefix="/prd", tags=["Test Platform - PRD"])
    router.include_router(case_router, prefix="/case", tags=["Test Platform - Case"])
    router.include_router(ui_auto_router, prefix="/ui-auto", tags=["Test Platform - UI Auto"])
    router.include_router(exec_router, prefix="/exec", tags=["Test Platform - Execution"])
    router.include_router(report_router, prefix="/report", tags=["Test Platform - Report"])
    router.include_router(knowledge_router, prefix="/knowledge", tags=["Test Platform - Knowledge"])
    router.include_router(defect_router, prefix="/defect", tags=["Test Platform - Defect"])
    router.include_router(test_data_router, tags=["Test Platform - Test Data"])
    router.include_router(coverage_router, tags=["Test Platform - Coverage"])
    router.include_router(cicd_router, tags=["Test Platform - CI/CD"])
    router.include_router(regression_router, tags=["Test Platform - Regression"])
    router.include_router(notification_router, tags=["Test Platform - Notification"])
    router.include_router(api_test_router, tags=["Test Platform - API Test"])
    router.include_router(env_router, tags=["Test Platform - Environment"])
    router.include_router(case_version_router, tags=["Test Platform - Case Version"])
    router.include_router(masking_router, tags=["Test Platform - Masking"])
    router.include_router(recording_router, tags=["Test Platform - Recording"])
    router.include_router(queue_router, tags=["Test Platform - Queue"])
    router.include_router(perf_router, tags=["Test Platform - Performance"])
    router.include_router(collab_router, tags=["Test Platform - Collaboration"])
    router.include_router(visual_diff_router, tags=["Test Platform - Visual Diff"])
    router.include_router(ab_test_router, tags=["Test Platform - AB Test"])
    router.include_router(chaos_router, tags=["Test Platform - Chaos"])
    router.include_router(analytics_router, tags=["Test Platform - Analytics"])
    router.include_router(workflow_router, prefix="/workflow", tags=["Test Platform - Workflow"])
    router.include_router(project_router, prefix="/project", tags=["Test Platform - Project"])
    router.include_router(element_map_router, prefix="/element-map", tags=["Test Platform - Element Map"])

    @router.get("/health")
    async def test_platform_health():
        return {"status": "ok", "platform": "ai-test-platform", "modules": [
            "iteration", "prd", "story", "case", "ui-auto", "exec", "report", "knowledge", "defect",
            "test_data", "coverage", "cicd", "regression", "notification", "api_test", "environment",
            "case_version", "masking", "recording", "queue", "performance", "collaboration",
            "visual_diff", "ab_test", "chaos", "analytics", "workflow", "project", "element_map"
        ]}

    return router
