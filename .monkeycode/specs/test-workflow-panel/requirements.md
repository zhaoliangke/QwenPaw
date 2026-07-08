# Requirements Document

## Introduction

测试平台工作流面板——在 QwenPaw 聊天页面右侧添加一个产物工作流面板，将测试平台的核心能力（需求分析、功能用例生成、UI 用例生成、用例评审、自动测试执行、测试报告）以可视化步骤的形式集成到对话式交互中。AI 助手在聊天中驱动工作流，右侧面板实时展示各阶段产物与进度。

## Glossary

- **Workflow Panel**: 聊天页面右侧的工作流产物面板，展示 6 个测试阶段的状态和产物
- **Workflow Step**: 单个阶段（如"需求分析"），包含状态、产物摘要、操作按钮
- **ChatPage**: QwenPaw 已有的聊天页面（`/workspace/console/src/pages/Chat/index.tsx`）
- **ChatSessionDrawer**: 已有的右侧面板组件，支持 Drawer 和 Embedded 两种模式
- **产物 (Artifact)**: 每个阶段产生的数据对象（解析结果、Story 列表、Case 列表、报告等）
- **Step Status**: 步骤状态 —— `pending`（未开始）、`running`（进行中）、`completed`（已完成）、`error`（失败）、`skipped`（已跳过）

---

## Requirements

### R-1: 面板布局与入口
**User Story:** AS 测试工程师, I want 在聊天页面右侧看到工作流面板, so that 我能随时了解测试工作流的进度和产物。

#### Acceptance Criteria
1. WHEN 用户在聊天页面, the system SHALL 在聊天区域右侧显示一个可折叠的工作流面板（默认折叠为 icon 边栏）
2. WHEN 用户点击展开按钮, the system SHALL 展开面板至 360px 宽度，显示 6 个工作流步骤
3. The system SHALL 复用 `ChatSessionDrawer` 的 embedded 模式实现（CSS class: `.workflowPanel`）
4. The system SHALL 在 `ChatActionGroup` 中新增工作流面板切换按钮（图标：ordered-list 或 project）
5. The panel 状态 SHALL 持久化到 `localStorage`（key: `workflow-panel-visible`）
6. WHEN 面板展开时聊天区域 SHALL 自动压缩，保持消息可读性
7. The system SHALL 支持移动端以 Drawer 模式展示

### R-2: 工作流步骤展示（6 个阶段）
**User Story:** AS 测试工程师, I want 看到 6 个清晰的测试阶段及其状态, so that 我知道当前进行到了哪一步。

#### Acceptance Criteria

| 序号 | 步骤名称 | 对应后端接口 | 对应 Agent |
|------|---------|-------------|-----------|
| 1 | 需求分析 | `POST /api/test/prd/parse` | `PrdParseAgent` |
| 2 | 生成功能用例 | `POST /api/test/prd/story/generate` + `POST /api/test/case/generate` | `StoryAgent` + `CaseAgent` |
| 3 | 生成 UI 用例 | `POST /api/test/ui-auto/generate` | `UiAutoAgent` |
| 4 | 用例评审 | `POST /api/test/case/review` | `ReviewAgent` |
| 5 | 自动测试执行 | `POST /api/test/exec/submit` | `ExecAgent` |
| 6 | 端到端测试报告 | `POST /api/test/report/generate` | `ReportAgent` |

1. Each step SHALL 显示：状态图标、步骤名称、简要产物计数（如"3 个 Story"、"12 条用例"）
2. The current active step SHALL 使用高亮样式（蓝色左侧边框 + 淡蓝背景）
3. Completed steps SHALL 显示绿色勾选图标 + 产出数量
4. Failed steps SHALL 显示红色错误图标 + 错误摘要 tooltip
5. Pending steps SHALL 显示灰色圆点

### R-3: 步骤 1 —— 需求分析产物展示
**User Story:** AS 测试工程师, I want 在面板中看到 PRD 解析的概要信息, so that 我无需跳转到别的页面就能确认解析结果。

#### Acceptance Criteria
1. WHEN PRD 解析完成, the system SHALL 在"需求分析"步骤下展示：
   - 提取的功能模块数
   - 业务流程数（及流程步骤总数）
   - 验证规则数
   - 异常流数
   - 非功能性需求数
   - 风险清单数
2. The system SHALL 提供"查看详情"链接，点击跳转到 `/test/prd_analysis` 页面
3. WHEN 用户在聊天中上传 PRD, the panel SHALL 实时将"需求分析"状态从 `pending` 切换为 `running` 再切换为 `completed`

### R-4: 步骤 2 —— 功能用例生成产物展示
**User Story:** AS 测试工程师, I want 看到自动生成的 Story 和用例数量, so that 我确认覆盖范围。

#### Acceptance Criteria
1. WHEN Story + Case 生成完成, the system SHALL 展示：
   - 生成的 Story 总数
   - 测试用例总数（按类型分组：功能/边界/异常/安全）
   - 需求覆盖率（已关联 Story 的需求 / 总需求）
   - 高/中/低优先级用例分布
2. The system SHALL 提供"查看用例"链接，点击跳转到 `/test/case_manage` 页面

### R-5: 步骤 3 —— UI 用例生成产物展示
**User Story:** AS 测试工程师, I want 看到 UI 自动化用例的生成结果, so that 我能快速了解自动化覆盖情况。

#### Acceptance Criteria
1. WHEN UI 用例生成完成, the system SHALL 展示：
   - 生成的页面对象（Page Object）数量
   - UI 操作步骤总数
   - 涉及的页面/路由列表
   - 选择器稳定性评分（如有）
2. The system SHALL 提供"查看 UI 用例"链接，跳转到 `/test/ui_auto` 页面

### R-6: 步骤 4 —— 用例评审产物展示
**User Story:** AS 测试工程师, I want 看到 AI 给出的用例评审建议, so that 我能快速确认用例质量。

#### Acceptance Criteria
1. WHEN 用例评审完成, the system SHALL 展示：
   - 评审通过率（如 45/50 条通过）
   - 发现的问题数（按严重度分组：高/中/低）
   - 主要问题类型标签（如"缺少边界条件"、"描述不清晰"）
2. The system SHALL 提供"查看评审详情"链接，跳转到 `/test/case_manage?tab=review` 页面

### R-7: 步骤 5 —— 自动测试执行状态展示
**User Story:** AS 测试工程师, I want 实时看到测试执行进度, so that 我能了解当前执行的进展。

#### Acceptance Criteria
1. WHEN 测试执行开始, the system SHALL 显示实时进度：
   - 已完成用例 / 总用例数（进度条）
   - 通过/失败/跳过的计数（实时更新）
   - 当前正在执行的用例名称
   - 预计剩余时间
2. WHEN 单个用例失败, the system SHALL 在失败计数旁显示红色徽章，点击展示失败摘要
3. WHEN 执行完成, the system SHALL 显示执行总结 + "查看报告"链接

### R-8: 步骤 6 —— 端到端测试报告展示
**User Story:** AS 测试工程师, I want 在面板中看到测试报告的核心指标, so that 我能快速了解测试结果。

#### Acceptance Criteria
1. WHEN 报告生成完成, the system SHALL 展示：
   - 总用例数、通过数、失败数、跳过数
   - 通过率百分比（大号数字+环形进度图）
   - 缺陷发现数（按严重度分布）
   - 测试耗时
   - 对比上一次的通过率变化（↑/↓ 箭头）
2. The system SHALL 提供"查看完整报告"链接，跳转到 `/test/report_center` 页面
3. The system SHALL 提供"导出报告"操作按钮（PDF/HTML）

### R-9: 工作流联动与智能引导
**User Story:** AS 测试工程师, I want AI 聊天助手根据工作流进度主动引导下一步操作, so that 我不会遗漏任何步骤。

#### Acceptance Criteria
1. WHEN 当前步骤完成, the system SHALL 在聊天中发送"下一步建议"卡片：
   - 显示"✅ [步骤名] 已完成"摘要
   - 显示"下一步：[步骤名]"按钮，点击触发对应 Agent 调用
2. IF 当前步骤失败, the system SHALL 展示错误摘要 + "重试"按钮
3. The system SHALL 支持从任意步骤重新启动后续流程（下游步骤自动重置为 `pending`）
4. The system SHALL 在顶部显示全局进度条（整体完成百分比）

### R-10: 数据持久化与会话恢复
**User Story:** AS 测试工程师, I want 刷新页面后工作流进度和产物仍然保留, so that 我可以中断后继续工作。

#### Acceptance Criteria
1. The system SHALL 将工作流状态持久化到 `localStorage`（key: `workflow-state-{chatSessionId}`）
2. The system SHALL 将各阶段产物存储在 `workspace/test/iteration/{iterationId}/workflow/` 目录
3. WHEN 用户打开历史会话, the system SHALL 恢复工作流面板到上次关闭时的状态
4. The system SHALL 提供"重置工作流"按钮，点击后清除当前会话的所有工作流状态

### R-11: 工作流库表持久化 (保存库表)
**User Story:** AS 测试工程师, I want 后端将工作流各步骤的结构化状态保存在文件系统（或可选的 MySQL）, so that 可以从任意终端访问完整的工作流历史。

#### Acceptance Criteria
1. The system SHALL 为每个迭代新增 `workflow.json` 存储文件（path: `workspace/test/iteration/{id}/workflow.json`），包含所有步骤状态和产物摘要
2. The system SHALL 实现 `FileWorkflowStore`（文件模式）作为默认后端存储，接口与现有 `FileIterationStore` 一致
3. The system SHALL 实现 `POST /api/test/workflow/update` 端点接收步骤更新请求
4. The system SHALL 实现 `GET /api/test/workflow/{iteration_id}` 端点返回完整工作流状态
5. The system SHALL 实现 `POST /api/test/workflow/{iteration_id}/reset` 端点重置工作流
6. WHEN 配置 `TEST_PLATFORM_DB_BACKEND=mysql`, the system SHALL 使用 `MysqlWorkflowStore` 将状态持久化到 `test_workflow_state` 和 `test_workflow_step` 表
7. The `workflow.json`  SHALL 保留完整的产物快照（包括 API 返回的关键数据）
8. The system SHALL 在 `StorageFactory` 中注册 `WorkflowStore` 的创建逻辑

### R-12: 知识库自动归档 (保存知识袋)
**User Story:** AS 知识管理员, I want 测试工作流各阶段的产物自动归档到知识库, so that 历史测试资产可被 AI 检索和复用。

#### Acceptance Criteria
1. The system SHALL 在每个工作流步骤完成时自动将产物摘要归档为 `KnowledgeDocument`
2. The system SHALL 使用不同的 `doc_type` 标识不同步骤的产物类型：`prd_summary` / `case_pattern` / `ui_pattern` / `review_finding` / `execution_insight` / `test_report`
3. WHEN 步骤完成, the system SHALL 通过 `WorkflowArchiveAgent` 生成格式化的知识文档
4. The system SHALL 将知识文档写入 `KnowledgeStore`（复用现有 `FileKnowledgeStore`）
5. The system SHALL 自动调用平台 ReMe 向量存储接口对知识文档进行 RAG 索引
6. The system SHALL 基于 `iteration_id + step_id` 去重，同一步骤的重复归档自动更新已有文档而非新增
7. The system SHALL 归档失败时不阻塞工作流继续执行（降级为 warn 日志）
8. WHEN 用户通过自然语言搜索历史测试资产, the AI 助手 SHALL 通过 RAG 检索到相关的历史工作流产物

---

## Technical Notes

### 复用模式

工作流面板直接复用 `ChatSessionDrawer` 的 CSS 类名和状态管理逻辑：

```
已有模式:                   新增模式:
┌──────────────┐           ┌──────────────┐
│ historyPanel │           │ workflowPanel│
│ (SessionList)│           │ (WorkflowSteps)│
└──────────────┘           └──────────────┘
```

### 文件规划

```
console/src/pages/Chat/components/
├── WorkflowPanel/              # 工作流面板主组件
│   ├── index.tsx                # 主入口（注册在 ChatActionGroup 中）
│   ├── WorkflowStepItem.tsx     # 单个步骤展示组件
│   ├── step1Requirement.tsx     # 需求分析产物展示
│   ├── step2Functional.tsx      # 功能用例产物展示
│   ├── step3UiAuto.tsx          # UI 用例产物展示
│   ├── step4Review.tsx          # 评审产物展示
│   ├── step5Execution.tsx       # 执行进度展示
│   ├── step6Report.tsx          # 测试报告展示
│   └── workflowStore.ts          # Zustand 状态管理
```

### 状态管理

使用 Zustand store（复用项目中已有的状态管理方案），核心数据模型：

```ts
interface WorkflowStep {
  id: string;                   // 'requirement' | 'functional' | 'ui-auto' | 'review' | 'execution' | 'report'
  name: string;                 // 显示名称
  status: 'pending' | 'running' | 'completed' | 'error' | 'skipped';
  result: Record<string, any>;  // 产物数据（各步骤不同）
  error?: string;               // 错误信息
  startedAt?: string;           // ISO timestamp
  completedAt?: string;         // ISO timestamp
}

interface WorkflowState {
  steps: WorkflowStep[];
  currentStep: number;          // 当前活跃步骤索引
  iterationId: string;          // 当前迭代 ID
  overallProgress: number;      // 0-100
}
```

### 聊天→面板通信

AI 助手通过 tool_call 调用 `/api/test/*` 后端接口成功后，前端通过自定义事件通知面板更新：

```tsx
// 聊天收到 tool_call result 后
window.dispatchEvent(new CustomEvent('workflow-step-update', {
  detail: { step: 'requirement', status: 'completed', result: data }
}));
```
