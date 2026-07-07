# Requirements Document

## Introduction

基于 QwenPaw 开源底座 AI 端到端测试平台，覆盖迭代管理、需求导入、Story 拆解、测试用例生成、UI 自动化脚本生成、批量执行、智能报告、缺陷同步、知识库自动归档的完整测试闭环。

## Glossary

- **QwenPaw**: 基于 agentscope 框架的 AI 助手平台，提供 Agent 管理、插件系统、记忆系统、MCP 工具网关等能力
- **BaseAgent**: agentscope 框架的 Agent 基类，所有 Agent 继承自此
- **MultiAgentManager**: QwenPaw 的多 Agent 管理器，负责 Agent 生命周期管理和任务流转
- **ReMe**: QwenPaw 的三层记忆系统，支持短期会话记忆、长期快照记忆和 RAG 向量检索
- **MCP (Model Context Protocol)**: 工具集成协议，用于注册和调用外部工具能力
- **Plugin System**: QwenPaw 的插件市场框架，支持插件的加载、卸载和启停
- **Workspace**: QwenPaw 的工作目录（默认 ~/.qwenpaw），所有持久化数据存储于此
- **Tauri**: 桌面应用打包框架，将 Web 应用打包为跨平台桌面应用
- **FastAPI**: QwenPaw 后端 Web 框架
- **EARS**: Easy Approach to Requirements Syntax，标准化需求表述模式

---

## Core Constraints (开发红线)

### R-0.1 底座复用约束
**User Story:** AS 平台架构师, I want 所有测试扩展不侵入 QwenPaw 内核, so that 上游版本可无冲突升级。

#### Acceptance Criteria
1. The system SHALL NOT modify any file under agentscope/agent, agentscope/mcp, agentscope/memory, agentscope/sandbox directories.
2. The system SHALL NOT delete or refactor any existing frontend Vue/TypeScript components in the console directory.
3. All test business code SHALL be placed in the standalone agentscope/test_extend directory.
4. All test-specific agents SHALL be registered via MultiAgentManager dynamic registration without modifying the Agent base class.
5. All frontend test pages SHALL use the isolated /test/* route prefix.
6. All external tools (Playwright, Jira, document parsing) SHALL be encapsulated as standard MCP Tools.
7. All persistent data operations SHALL use the platform's native file utilities and ReMe memory interfaces.
8. New agents SHALL inherit from BaseAgent and use MultiAgentManager's standard creation interface.

### R-0.2 存储复用约束
**User Story:** AS 平台架构师, I want 所有测试数据复用原生存储体系, so that 不引入独立的数据库依赖。

#### Acceptance Criteria
1. The system SHALL store all test assets under the workspace/test/ directory within the platform's native working directory.
2. The system SHALL isolate data by iteration ID using subdirectories.
3. The vector knowledge base SHALL reuse the platform's native RAG vector storage with dedicated test vector collections.
4. The system SHALL NOT introduce any standalone database (SQL, NoSQL, or independent vector database).

### R-0.3 组件复用约束
**User Story:** AS 前端开发者, I want 测试页面直接复用原生 UI 组件, so that 保持统一的用户体验和开发效率。

#### Acceptance Criteria
1. All test frontend pages SHALL reuse native components: file upload, table pagination, modal, form, log console, model selector, notification config, export tools.
2. The Cron timing configuration SHALL reuse the platform's native timer dialog component.
3. The notification channel configuration SHALL reuse the platform's native push configuration page.
4. The execution log panel SHALL directly import the platform's native log console component.

---

## Requirements

### R-1: 迭代管理
**User Story:** AS 测试负责人, I want 创建和管理测试迭代, so that 测试活动可以按版本有序组织。

#### Acceptance Criteria
1. WHEN the user creates a new iteration, the system SHALL support configuring version, start/end dates, module, associated Git branch, and test environment.
2. The system SHALL provide iteration status workflow: Draft, Reviewing, Testing, Released, Archived.
3. The system SHALL generate a baseline snapshot of the current iteration's full assets.
4. WHEN the user requests a diff comparison between two iterations, the system SHALL display added, modified, and deprecated Stories.
5. WHEN the user configures a scheduled regression task, the system SHALL reuse the platform's native Cron component for configuration.
6. WHEN the user triggers one-click sync, the system SHALL synchronize iteration requirements from Jira/GitHub APIs.

### R-2: 需求解析
**User Story:** AS 测试工程师, I want 上传 PRD 文档并自动解析需求, so that 减少手工梳理需求的工作量。

#### Acceptance Criteria
1. WHEN the user uploads a PRD document (Word/PDF/Markdown), the system SHALL invoke PrdParseAgent to extract business processes, validation rules, and risk points.
2. The system SHALL support uploading OpenAPI specification documents and Figma design links as input sources.
3. WHEN parsing is complete, the system SHALL output a risk assessment checklist including requirement ambiguity, missing validation rules, and exception flow gaps.
4. Parsed results SHALL be stored in temporary memory and passed as context to downstream StoryAgent.
5. The system SHALL reuse the platform's native file parsing and multimodal VLM capabilities.

### R-3: Story 拆解
**User Story:** AS 产品经理, I want 自动拆解需求为可验收的 User Story, so that 开发和测试有明确的目标。

#### Acceptance Criteria
1. WHEN PrdParseAgent completes parsing, the system SHALL automatically decompose requirements into User Stories using the "As a/I want/So that" format.
2. The system SHALL generate acceptance criteria for each Story in Gherkin format.
3. The system SHALL support parent-child Story hierarchy and generate full-chain traceability IDs.
4. The system SHALL perform AI-driven Story completeness review and mark missing acceptance criteria.
5. Story data SHALL be stored in workspace/test/iteration/{id}/story/ directory using the platform's native file storage.

### R-4: 测试用例生成
**User Story:** AS 测试工程师, I want 批量生成多维度测试用例, so that 提高测试设计效率和覆盖率。

#### Acceptance Criteria
1. WHEN a Story is selected, the system SHALL batch-generate test cases across dimensions: Functional, Boundary, Exception, Security, and UI adaptation.
2. The system SHALL enhance generation quality by retrieving similar historical cases from the RAG knowledge base.
3. The system SHALL calculate and display Story coverage rate and requirement coverage rate.
4. The system SHALL support batch export of test cases to Excel format using the platform's native export tool.
5. The system SHALL support case classification by tags: priority, module, and type (Functional/UI/Security).
6. The system SHALL support batch editing, copying, disabling, and deleting of test cases.

### R-5: UI 自动化脚本
**User Story:** AS 自动化测试工程师, I want 通过自然语言生成 Playwright 脚本, so that 降低 UI 自动化编写门槛。

#### Acceptance Criteria
1. WHEN a UI test case is selected, the system SHALL generate Playwright automation scripts from natural language descriptions.
2. The system SHALL use VLM-based visual element positioning to reduce dependency on XPath/CSS selectors.
3. The system SHALL organize scripts by page using the Page Object (PO) layered architecture.
4. The system SHALL provide an online script debugging panel reusing the platform's native code editor component.
5. WHEN a script is executed in debug mode, the system SHALL display real-time operation screenshots and execution logs.
6. Execution screenshots and recordings SHALL be automatically saved to the iteration directory.

### R-6: 测试执行调度
**User Story:** AS 测试工程师, I want 批量执行测试用例并实时查看进度, so that 快速获取测试结果。

#### Acceptance Criteria
1. WHEN the user selects all test cases in an iteration, the system SHALL support batch execution with configurable concurrency.
2. The system SHALL support single case manual execution for debugging purposes.
3. The system SHALL reuse the platform's native task queue and multi-process parallel scheduling.
4. The system SHALL support configuration of dev/test/pre multi-environment variables.
5. WHEN an execution fails, the system SHALL automatically retry up to a configured maximum count and isolate failed cases.
6. The system SHALL push real-time execution progress to the frontend via the platform's native WebSocket channel.
7. The system SHALL support viewing historical execution records.

### R-7: 测试报告生成
**User Story:** AS 测试负责人, I want 自动生成可视化测试报告, so that 测试结果可以清晰地传达给团队。

#### Acceptance Criteria
1. WHEN test execution completes, the system SHALL aggregate execution data, logs, screenshots, and error stack traces.
2. The system SHALL auto-calculate pass rate, coverage, and defect classification charts.
3. The system SHALL generate HTML visualization reports using the platform's native static file service for output.
4. The system SHALL auto-classify failures as: Product Defect, Script Error, or Environment Fault.
5. WHEN the user triggers report push, the system SHALL send report summaries via DingTalk/Feishu/WeCom using the platform's native messaging module.
6. The system SHALL provide report download and archive to the knowledge base.

### R-8: 缺陷同步
**User Story:** AS 测试工程师, I want 一键提交缺陷到 Jira/禅道, so that 缺陷跟踪与测试流程无缝衔接。

#### Acceptance Criteria
1. WHEN a test case fails, the system SHALL support one-click defect submission to Jira or ZenTao.
2. The system SHALL auto-assemble defect tickets including: steps, expected results, actual results, screenshot attachments, and severity level.
3. The system SHALL establish traceability links between defects and Stories, test cases, and iterations.
4. Defect sync operations SHALL reuse the platform's native HTTP request MCP capability and encrypted key storage.

### R-9: 测试知识库
**User Story:** AS 测试工程师, I want 测试资产自动归档和智能检索, so that 历史经验可以在新项目中复用。

#### Acceptance Criteria
1. WHEN an iteration ends, the system SHALL auto-archive all assets: requirements, Stories, cases, scripts, reports, and defects.
2. The system SHALL provide natural language search for historical requirements, cases, defects, and business specifications.
3. The system SHALL support manual upload of test standards and business manuals to the knowledge base.
4. WHEN generating test cases for a new project, the system SHALL auto-retrieve similar historical cases from the knowledge base.
5. The system SHALL support scheduled AI knowledge distillation to output test best-practice documentation.
6. The system SHALL provide a scheduled backup configuration for the knowledge base reusing the platform's native Cron component.

### R-10: 前端页面
**User Story:** AS 测试工程师, I want 通过 Web 控制台管理测试全流程, so that 有一个统一的操作入口。

#### Acceptance Criteria
1. The system SHALL provide test pages under /test/* routes: iteration, prd_analysis, case_manage, ui_auto, test_exec, report_center, knowledge_lib.
2. The system SHALL add a top-level navigation menu item "AI Test Workbench" with a sub-sidebar reusing the native sidebar component.
3. All test pages SHALL reuse native UI components: table, file upload, modal, log console, code editor, chart rendering, etc.
4. The system SHALL NOT modify any existing frontend pages under the agent management, plugin marketplace, model configuration, or settings sections.

### R-11: 部署兼容性
**User Story:** AS DevOps 工程师, I want 测试平台无缝集成到现有部署流程, so that 部署成本最小化。

#### Acceptance Criteria
1. The system SHALL be deployable via the platform's existing pip one-click install, Docker image, and Tauri desktop packaging scripts.
2. The system SHALL append test extension auto-loading logic to the main entry without modifying the original kernel code.
3. The system SHALL support offline deployment using local Qwen series models without modifying model scheduling code.

### R-12: 安全管控
**User Story:** AS 安全工程师, I want 测试平台遵守平台安全策略, so that 不会引入新的安全风险。

#### Acceptance Criteria
1. UI automation script execution and knowledge base file operations SHALL reuse the platform's native FileGuard/ToolGuard sandbox.
2. Test environment credentials and Jira API keys SHALL be stored using the platform's native encrypted key storage.
3. The system SHALL use the platform's native user/role permission system and add new permission tags: Test Admin, Regular Tester, Read-Only.

---

## References

[^1]: QwenPaw 项目源码 - `/workspace/src/qwenpaw/`
[^2]: 插件系统实现 - `/workspace/src/qwenpaw/plugins/api.py`
[^3]: MultiAgentManager - `/workspace/src/qwenpaw/app/multi_agent_manager.py`
[^4]: ReMe 记忆系统 - `/workspace/src/qwenpaw/agents/memory/`
[^5]: 前端控制台 - `/workspace/console/src/`
[^6]: PRD 原始需求 - 用户提供的完整 PRD 文档
