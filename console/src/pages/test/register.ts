/**
 * Test Platform Route Registration
 *
 * Registers /test/* routes into the QwenPaw routeRegistry.
 * All test pages live under console/src/pages/test/ and are
 * loaded lazily to keep the initial bundle small.
 */
import { lazy } from "react";
import { routeRegistry } from "@/plugins/registry/store";

const IterationPage = lazy(() => import("./iteration"));
const PrdAnalysisPage = lazy(() => import("./prd_analysis"));
const CaseManagePage = lazy(() => import("./case_manage"));
const UIAutoPage = lazy(() => import("./ui_auto"));
const TestExecPage = lazy(() => import("./test_exec"));
const ReportCenterPage = lazy(() => import("./report_center"));
const KnowledgeLibPage = lazy(() => import("./knowledge_lib"));

export const TEST_ROUTES = [
  {
    id: "test.iteration",
    path: "/test/iteration",
    component: IterationPage,
  },
  {
    id: "test.prd_analysis",
    path: "/test/prd_analysis",
    component: PrdAnalysisPage,
  },
  {
    id: "test.case_manage",
    path: "/test/case_manage",
    component: CaseManagePage,
  },
  {
    id: "test.ui_auto",
    path: "/test/ui_auto",
    component: UIAutoPage,
  },
  {
    id: "test.test_exec",
    path: "/test/test_exec",
    component: TestExecPage,
  },
  {
    id: "test.report_center",
    path: "/test/report_center",
    component: ReportCenterPage,
  },
  {
    id: "test.knowledge_lib",
    path: "/test/knowledge_lib",
    component: KnowledgeLibPage,
  },
];

export function registerTestRoutes(): void {
  routeRegistry.add("test-platform", TEST_ROUTES);
}
