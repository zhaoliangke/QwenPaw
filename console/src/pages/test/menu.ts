/**
 * Test Platform Sidebar Menu Declaration
 *
 * Menu items for the AI Test Workbench navigation group.
 * Registered via the QwenPaw plugin SDK menu registry.
 */
import type { MenuItem } from "@/plugins/registry/types";

export const TEST_MENU_ITEMS: MenuItem[] = [
  {
    id: "test-group",
    label: "AI 测试工作台",
    location: "primary.settings",
    icon: undefined,
    isGroup: true,
    route: undefined,
  },
  {
    id: "test.iteration",
    label: "迭代管理",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.iteration",
  },
  {
    id: "test.prd_analysis",
    label: "需求解析",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.prd_analysis",
  },
  {
    id: "test.case_manage",
    label: "用例管理",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.case_manage",
  },
  {
    id: "test.ui_auto",
    label: "UI 自动化",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.ui_auto",
  },
  {
    id: "test.test_exec",
    label: "执行调度",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.test_exec",
  },
  {
    id: "test.report_center",
    label: "报告中心",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.report_center",
  },
  {
    id: "test.knowledge_lib",
    label: "知识库",
    location: "primary.settings",
    parentId: "test-group",
    route: "test.knowledge_lib",
  },
];
