# 聊天工作流面板 — 实施计划

Feature: chat-workflow-panel
Created: 2026-07-07
Source: `.monkeycode/specs/test-workflow-panel/`

---

## Phase 1: 后端基础 — 数据模型与存储

### 1.1 新增 WorkflowState 数据模型
- [x] 新建 `models/workflow_state.py`
- [x] 定义 WorkflowStepRecord（step_id, name, status, result_summary, error, started_at, completed_at）
- [x] 定义 WorkflowState（iteration_id, chat_session_id, steps, overall_progress, updated_at）
- [x] 在 `models/__init__.py` 中导出

### 1.2 新增 FileWorkflowStore
- [x] 在 `storage/file_stores.py` 中新增 `FileWorkflowStore` 类
- [x] 实现 `update_step(iteration_id, step_id, update)` 方法（含进度自动计算）
- [x] 实现 `reset_workflow(iteration_id)` 方法
- [x] 实现标准 CRUD（create/get/list_all）

### 1.3 注册 MySQL WorkflowStore（可选）
- [ ] 在 `storage/mysql_stores.py` 中新增 `MysqlWorkflowStore` 类
- [ ] 实现 update_step / reset_workflow 方法
- [ ] 在 `StorageFactory` 中注册

### 1.4 Workflow API 路由
- [x] 新建 `routers/workflow.py`
- [x] 实现 `POST /api/test/update` 端点
- [x] 实现 `GET /api/test/{iteration_id}` 端点
- [x] 实现 `POST /api/test/{iteration_id}/reset` 端点
- [x] 在 `routers/__init__.py` 中注册

---

## Phase 2: 知识库归档

### 2.1 WorkflowArchiveAgent
- [x] 新建 `agents/workflow_archive_agent.py`
- [x] 实现 `archive_step_result()` 主入口
- [x] 实现 6 个步骤各自的归档格式化方法
- [x] 实现 RAG 索引调用
- [ ] 在 `agents/__init__.py` 中导出

### 2.2 在 workflow/update 中触发归档
- [x] 在 `POST /workflow/update` 中，检测到 status=completed 时调用 WorkflowArchiveAgent
- [x] 归档失败不影响主流程（try/except + warn）

---

## Phase 3: 前端工作流面板 UI

### 3.1 Zustand Store
- [ ] 新增 `console/src/pages/Chat/components/WorkflowPanel/workflowStore.ts`
- [ ] 定义 WorkflowStep 接口
- [ ] 定义 6 个步骤的常量
- [ ] 实现 updateStep / resetWorkflow / syncFromChatMessage actions
- [ ] 持久化到 localStorage

### 3.2 WorkflowPanel 主组件
- [ ] 新建 `WorkflowPanel/index.tsx`
- [ ] 复用 ChatSessionDrawer 的 embedded 模式 CSS
- [ ] 标题栏 + 全局进度条
- [ ] 步骤列表渲染

### 3.3 WorkflowStepItem 步骤组件
- [ ] 新建 `WorkflowPanel/WorkflowStepItem.tsx`
- [ ] 状态图标映射（pending/running/completed/error/skipped）
- [ ] 激活态高亮样式
- [ ] 错误摘要 tooltip

### 3.4 StepArtifactPreview 产物摘要组件
- [ ] 新建 `WorkflowPanel/StepArtifactPreview.tsx`
- [ ] 根据步骤类型渲染对应的产物摘要卡片

### 3.5 入口集成
- [ ] 在 `ChatActionGroup` 中新增工作流面板切换按钮
- [ ] 在 `ChatPage` 中新增面板渲染区域
- [ ] 状态持久化（localStorage key: workflow-panel-visible）

---

## Phase 4: 聊天→面板联动

### 4.1 事件机制
- [ ] 在聊天消息处理中监听 tool_call 结果
- [ ] 匹配到测试平台工具时派发 `workflow-step-update` 自定义事件
- [ ] 面板 store 监听事件并更新状态

### 4.2 后续步骤建议卡片
- [ ] 当步骤完成时，在聊天中渲染"下一步建议"卡片
- [ ] 卡片包含：完成摘要 + 下一步触发按钮

---

## 依赖关系

```
1.1 → 1.2 → 1.4 → 2.2
           ↘ 1.3 (parallel)

3.1 → 3.2 → 3.5
  ↘ 3.3 ↗
  ↘ 3.4 ↗

1.4 + 3.1 → 4.1 → 4.2
```

---

## 实施顺序

1. Phase 1.1 → 1.2 → 1.4 (后端 API 跑通)
2. Phase 2.1 → 2.2 (知识库归档跑通)
3. Phase 3.1 → 3.2 → 3.3 → 3.4 → 3.5 (前端面板完整)
4. Phase 4.1 → 4.2 (联动 + 智能引导)
