/**
 * Test Platform Route Registration
 *
 * Registers /test/* routes into the QwenPaw routeRegistry
 * and sidebar menu items into menuRegistry.
 * All test pages live under console/src/pages/test/ and are
 * loaded lazily to keep the initial bundle small.
 */
import { lazy } from "react";
import {
  SparkBarChartLine,
  SparkBrowseLine,
  SparkDataLine,
  SparkDateLine,
  SparkDebugLine,
  SparkEmailLine,
  SparkInternetLine,
  SparkLocalFileLine,
  SparkMagicWandLine,
  SparkMcpMcpLine,
  SparkMicLine,
  SparkModePlazaLine,
  SparkModifyLine,
  SparkOtherLine,
  SparkSaveLine,
  SparkScanLine,
  SparkToolLine,
  SparkUserGroupLine,
} from "@agentscope-ai/icons";
import { menuRegistry, routeRegistry } from "@/plugins/registry/store";
import type { MenuItem } from "@/plugins/registry/types";

const IterationPage = lazy(() => import("./iteration"));
const ProjectPage = lazy(() => import("./project"));
const ElementMapPage = lazy(() => import("./element_map"));
const PrdAnalysisPage = lazy(() => import("./prd_analysis"));
const CaseManagePage = lazy(() => import("./case_manage"));
const UIAutoPage = lazy(() => import("./ui_auto"));
const TestExecPage = lazy(() => import("./test_exec"));
const ReportCenterPage = lazy(() => import("./report_center"));
const KnowledgeLibPage = lazy(() => import("./knowledge_lib"));
const TestDataPage = lazy(() => import("./test_data"));
const CoveragePage = lazy(() => import("./coverage"));
const CICDPage = lazy(() => import("./cicd"));
const RegressionPage = lazy(() => import("./regression"));
const NotificationPage = lazy(() => import("./notification"));
const ApiTestPage = lazy(() => import("./api_test"));
const EnvironmentPage = lazy(() => import("./environment"));
const CaseVersionPage = lazy(() => import("./case_version"));
const MaskingPage = lazy(() => import("./masking"));
const RecordingPage = lazy(() => import("./recording"));
const ExecutionQueuePage = lazy(() => import("./execution_queue"));
const PerformancePage = lazy(() => import("./performance"));
const CollaborationPage = lazy(() => import("./collaboration"));
const VisualDiffPage = lazy(() => import("./visual_diff"));
const ABTestPage = lazy(() => import("./ab_test"));
const ChaosPage = lazy(() => import("./chaos"));
const AnalyticsPage = lazy(() => import("./analytics"));

export const TEST_ROUTES = [
  {
    id: "test.iteration",
    path: "/test/iteration",
    component: IterationPage,
  },
  {
    id: "test.project",
    path: "/test/project",
    component: ProjectPage,
  },
  {
    id: "test.element_map",
    path: "/test/element_map",
    component: ElementMapPage,
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
  {
    id: "test.test_data",
    path: "/test/test_data",
    component: TestDataPage,
  },
  {
    id: "test.coverage",
    path: "/test/coverage",
    component: CoveragePage,
  },
  {
    id: "test.cicd",
    path: "/test/cicd",
    component: CICDPage,
  },
  {
    id: "test.regression",
    path: "/test/regression",
    component: RegressionPage,
  },
  {
    id: "test.notification",
    path: "/test/notification",
    component: NotificationPage,
  },
  {
    id: "test.api_test",
    path: "/test/api_test",
    component: ApiTestPage,
  },
  {
    id: "test.environment",
    path: "/test/environment",
    component: EnvironmentPage,
  },
  {
    id: "test.case_version",
    path: "/test/case_version",
    component: CaseVersionPage,
  },
  {
    id: "test.masking",
    path: "/test/masking",
    component: MaskingPage,
  },
  {
    id: "test.recording",
    path: "/test/recording",
    component: RecordingPage,
  },
  {
    id: "test.execution_queue",
    path: "/test/execution_queue",
    component: ExecutionQueuePage,
  },
  {
    id: "test.performance",
    path: "/test/performance",
    component: PerformancePage,
  },
  {
    id: "test.collaboration",
    path: "/test/collaboration",
    component: CollaborationPage,
  },
  {
    id: "test.visual_diff",
    path: "/test/visual_diff",
    component: VisualDiffPage,
  },
  {
    id: "test.ab_test",
    path: "/test/ab_test",
    component: ABTestPage,
  },
  {
    id: "test.chaos",
    path: "/test/chaos",
    component: ChaosPage,
  },
  {
    id: "test.analytics",
    path: "/test/analytics",
    component: AnalyticsPage,
  },
];

export function registerTestRoutes(): void {
  for (const route of TEST_ROUTES) {
    routeRegistry.add("test-platform", route);
  }
}

registerTestRoutes();

// ── Sidebar Menu ──────────────────────────────────────────────────────

const TEST_MENU: MenuItem[] = [
  {
    id: "test.platform-group",
    location: "primary.agentScoped",
    label: "测试平台",
    isGroup: true,
    order: 25,
  },
  {
    id: "test.iteration",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "迭代管理",
    icon: SparkDateLine,
    route: "test.iteration",
    order: 10,
  },
  {
    id: "test.project",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "项目管理",
    icon: SparkLocalFileLine,
    route: "test.project",
    order: 12,
  },
  {
    id: "test.element_map",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "元素映射",
    icon: SparkOtherLine,
    route: "test.element_map",
    order: 14,
  },
  {
    id: "test.prd_analysis",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "PRD 解析",
    icon: SparkMagicWandLine,
    route: "test.prd_analysis",
    order: 20,
  },
  {
    id: "test.case_manage",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "用例管理",
    icon: SparkToolLine,
    route: "test.case_manage",
    order: 30,
  },
  {
    id: "test.ui_auto",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "UI 自动化",
    icon: SparkScanLine,
    route: "test.ui_auto",
    order: 40,
  },
  {
    id: "test.test_exec",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "测试执行",
    icon: SparkModifyLine,
    route: "test.test_exec",
    order: 50,
  },
  {
    id: "test.report_center",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "测试报告",
    icon: SparkBarChartLine,
    route: "test.report_center",
    order: 60,
  },
  {
    id: "test.knowledge_lib",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "知识库",
    icon: SparkUserGroupLine,
    route: "test.knowledge_lib",
    order: 70,
  },
  {
    id: "test.test_data",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "测试数据",
    icon: SparkDataLine,
    route: "test.test_data",
    order: 80,
  },
  {
    id: "test.coverage",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "覆盖率",
    icon: SparkBarChartLine,
    route: "test.coverage",
    order: 90,
  },
  {
    id: "test.cicd",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "CI/CD",
    icon: SparkMcpMcpLine,
    route: "test.cicd",
    order: 100,
  },
  {
    id: "test.regression",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "回归测试",
    icon: SparkDebugLine,
    route: "test.regression",
    order: 110,
  },
  {
    id: "test.notification",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "通知管理",
    icon: SparkEmailLine,
    route: "test.notification",
    order: 120,
  },
  {
    id: "test.api_test",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "API 测试",
    icon: SparkInternetLine,
    route: "test.api_test",
    order: 130,
  },
  {
    id: "test.environment",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "环境管理",
    icon: SparkModePlazaLine,
    route: "test.environment",
    order: 140,
  },
  {
    id: "test.case_version",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "用例版本",
    icon: SparkSaveLine,
    route: "test.case_version",
    order: 150,
  },
  {
    id: "test.masking",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "数据脱敏",
    icon: SparkBrowseLine,
    route: "test.masking",
    order: 160,
  },
  {
    id: "test.recording",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "录制回放",
    icon: SparkMicLine,
    route: "test.recording",
    order: 170,
  },
  {
    id: "test.execution_queue",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "执行队列",
    icon: SparkLocalFileLine,
    route: "test.execution_queue",
    order: 180,
  },
  {
    id: "test.performance",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "性能测试",
    icon: SparkBarChartLine,
    route: "test.performance",
    order: 190,
  },
  {
    id: "test.collaboration",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "协同审阅",
    icon: SparkUserGroupLine,
    route: "test.collaboration",
    order: 200,
  },
  {
    id: "test.visual_diff",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "视觉对比",
    icon: SparkScanLine,
    route: "test.visual_diff",
    order: 210,
  },
  {
    id: "test.ab_test",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "A/B 测试",
    icon: SparkOtherLine,
    route: "test.ab_test",
    order: 220,
  },
  {
    id: "test.chaos",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "混沌工程",
    icon: SparkModifyLine,
    route: "test.chaos",
    order: 230,
  },
  {
    id: "test.analytics",
    location: "primary.agentScoped",
    parentId: "test.platform-group",
    label: "分析看板",
    icon: SparkBarChartLine,
    route: "test.analytics",
    order: 240,
  },
];

for (const item of TEST_MENU) {
  menuRegistry.add("test-platform", item);
}
