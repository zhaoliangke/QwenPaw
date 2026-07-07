# 需求实施计划

- [x] 1. 设置项目结构和核心接口
  - 创建 `src/qwenpaw/test_extend/` 完整目录结构（agents/, mcp_tools/, routers/, storage/, models/, common/）
  - 创建 `console/src/pages/test/` 前端页面目录结构和注册入口
  - 创建 `plugin.json` 和 `plugin.py` Bundle 插件骨架
  - 定义 `requirements.md` 中 R-0.1 至 R-0.3 的核心约束接口边界
  - _需求: R-0.1, R-0.2, R-0.3_

  - [x] 1.1 创建后端扩展目录骨架
    - 在 `src/qwenpaw/test_extend/` 下创建 `__init__.py`、`plugin.py`、`plugin.json`
    - 创建 `agents/`、`mcp_tools/`、`routers/`、`storage/`、`models/`、`common/` 各子包 `__init__.py`
    - _需求: R-0.1 (所有测试业务代码置于 test_extend 目录)_

  - [x] 1.2 创建前端页面目录骨架
    - 创建 `console/src/pages/test/` 目录
    - 创建 `register.ts` 实现 `registerTestRoutes()` 函数，调用 `routeRegistry.add()` 注册 7 个 `/test/*` 路由
    - 创建 `menu.ts` 定义 `TEST_MENU_ITEMS` 侧边栏菜单数据
    - _需求: R-0.1, R-10 (新增 /test/* 路由页面)_

  - [x] 1.3 实现插件注册入口 (TestPlatformPlugin)
    - 编写 `plugin.py` 中 `TestPlatformPlugin.register(api)` 方法
    - 在 `register()` 中调用 `api.register_http_router()` 挂载 `/api/test` 前缀路由
    - 调用 `api.register_startup_hook()` 注册启动钩子
    - 调用 `api.register_shutdown_hook()` 注册关闭钩子
    - _需求: R-0.1, R-11_

  - [x] 1.4 实现存储路径管理模块
    - 编写 `storage/paths.py`，实现 `get_test_root()`、`get_iteration_dir()`、`get_prd_dir()` 等路径工具函数
    - 所有路径基于 `workspace_dir / "test"` 前缀，按迭代 ID 隔离
    - _需求: R-0.2_

  - [x] 1.5 实现基础数据模型
    - 编写 `models/iteration.py`：`Iteration`, `IterationStatus`
    - 编写 `models/traceability.py`：`TraceRecord`
    - 编写 `common/trace_id.py`：全链路追溯 ID 生成器
    - _需求: R-1, R-3 (追溯 ID 生成)_

  - [x] 1.6 创建前端布局与路由框架
    - 创建 7 个页面组件的占位文件（`iteration/index.tsx` 等），每个导出 lazy import 组件
    - 在 `register.ts` 中使用 `lazy()` 动态导入所有页面组件
    - 确保 `MainLayout` 的 `Routes` 能正确渲染 `/test/*` 路径
    - _需求: R-10_

  - [ ]* 1.7 编写基础结构的单元测试
    - 为 `storage/paths.py` 编写路径生成逻辑单元测试
    - 为 `models/` 数据模型的序列化/反序列化编写测试
    - _需求: R-0.2_

- [ ] 2. 检查点 - 确保项目骨架可正常加载
  - 验证 `python -c "from qwenpaw.test_extend.plugin import TestPlatformPlugin"` 无导入错误

- [ ] 3. 实现迭代管理模块
  - 实现迭代 CRUD、快照、Diff、Jira 同步、定时回归等全部后端能力
  - 开发迭代管理前端页面
  - _需求: R-1_

  - [ ] 3.1 实现迭代存储层 (iteration_store.py)
    - 编写 `IterationStore` 类，基于 JSON 文件实现迭代的 CRUD 操作
    - 数据存储于 `{workspace}/test/iteration/{id}/` 目录
    - 支持按状态过滤列表查询
    - _需求: R-1, R-0.2_

  - [ ] 3.2 实现 IterationAgent
    - 在 `agents/iteration_agent.py` 中实现 `IterationAgent(TestBaseAgent)`
    - 通过 `MultiAgentManager` 动态注册，不修改 Agent 基类
    - 注入 ReMe 长期记忆用于迭代快照存储
    - _需求: R-1, R-0.1_

  - [ ] 3.3 实现迭代管理 MCP 工具 (mcp_tools/iteration_mgr.py)
    - 实现 `create_iteration()`、`get_iteration()`、`list_iterations()`
    - 实现 `update_iteration_status()` 状态流转（Draft → Reviewing → Testing → Released → Archived）
    - 实现 `create_snapshot()`：打包迭代全部资产为快照包
    - 实现 `diff_iterations()`：比较两个迭代的 Story 变更（新增/废弃/修改）
    - 实现 `schedule_regression()`：配置定时回归，调用原生 Cron API
    - 在 `mcp_tools/__init__.py` 中通过 `api.register_tool()` 注册所有工具
    - _需求: R-1_

  - [ ] 3.4 实现迭代管理 API 路由 (routers/iteration.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/iteration/`
    - 接口：`POST /`, `GET /`, `GET /{id}`, `PUT /{id}`, `POST /{id}/snapshot`, `GET /diff?a={id}&b={id}`
    - 在 `plugin.py` 中通过 `api.register_http_router()` 挂载
    - _需求: R-1_

  - [ ] 3.5 开发迭代管理前端页面 (pages/test/iteration/)
    - 新建迭代表单：版本、起止日期、模块、Git 分支、测试环境
    - 迭代列表：复用原生表格分页组件，按状态 Tab 筛选
    - 基线快照按钮：调用后端 API 触发快照创建
    - 迭代 Diff 对比视图：展示双迭代的 Story 变更
    - 同步 Jira 按钮：触发一键同步
    - 定时回归配置：复用原生 Cron 弹窗组件
    - _需求: R-1, R-10, R-0.3_

  - [ ] 3.6 实现 Jira/GitHub 同步适配器
    - 在 `mcp_tools/iteration_mgr.py` 中实现 `sync_from_jira()` 工具
    - 复用平台原生 HTTP 请求 MCP 能力和加密密钥存储
    - 按项目 Key 拉取迭代需求并转换为 Story 结构
    - _需求: R-1_

  - [ ]* 3.7 编写迭代管理单元测试
    - 为 `IterationStore` CRUD 操作编写测试
    - 为快照打包/还原编写测试
    - 为 Diff 算法编写测试
    - _需求: R-1_

- [ ] 4. 检查点 - 确保迭代管理模块完整可测
  - 验证迭代 CRUD API 全流程可用，前端页面正常渲染

- [ ] 5. 实现需求解析模块
  - 实现文档/OpenAPI/Figma 解析能力，AI 歧义识别和风险清单
  - 开发需求解析前端页面
  - _需求: R-2_

  - [ ] 5.1 实现 PrdParseAgent
    - 在 `agents/prd_parse_agent.py` 中实现 `PrdParseAgent(TestBaseAgent)`
    - 复用平台原生多模态 VLM 文件解析能力
    - 复用平台原生 RAG 检索接口，解析结果存入临时记忆
    - _需求: R-2, R-0.1_

  - [ ] 5.2 实现需求解析 MCP 工具 (mcp_tools/prd_parser.py)
    - 实现 `parse_document()`：解析 Word/PDF/Markdown PRD，提取业务流程、校验规则
    - 实现 `parse_openapi()`：解析 OpenAPI 规范文件
    - 实现 `parse_figma()`：解析 Figma 设计链接
    - 实现 `identify_ambiguities()`：AI 分析需求歧义，输出风险清单
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-2_

  - [ ] 5.3 实现需求解析 API 路由 (routers/prd_analysis.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/prd/`
    - 接口：`POST /parse`（上传文件并解析）
    - 在 `plugin.py` 中挂载路由
    - _需求: R-2_

  - [ ] 5.4 开发需求解析 & Story 管理前端页面 (pages/test/prd_analysis/)
    - 文件上传区域：复用原生文件上传组件，支持 Word/PDF/MD/OpenAPI
    - Figma 链接输入框
    - 解析结果展示区：业务流程、校验规则、风险清单，复用原生表格和标签组件
    - Story 自动生成面板：调用 StoryAgent，复用原生富文本编辑器
    - Story 手动增删改交互
    - 需求-Story 追溯树状视图
    - AI 一键评审 Story 完整性，标记缺失验收准则
    - _需求: R-2, R-10, R-0.3_

  - [ ]* 5.5 编写需求解析单元测试
    - 为文档解析工具编写测试（各格式输入输出验证）
    - 为歧义识别逻辑编写测试
    - _需求: R-2_

- [ ] 6. 检查点 - 确保需求解析模块完整可测
  - 验证文档上传解析全流程可用，Story 生成面板正常渲染

- [ ] 7. 实现 Story 拆解与用例生成模块
  - 实现 Story 自动拆解、验收准则生成、用例批量生成、覆盖率计算
  - 开发用例管理前端页面
  - _需求: R-3, R-4_

  - [ ] 7.1 实现 StoryAgent
    - 在 `agents/story_agent.py` 中实现 `StoryAgent(TestBaseAgent)`
    - 接收 PrdParseAgent 解析结果，生成 As a/I want/So that 格式 Story
    - 生成 Gherkin 格式验收准则
    - 输出结构化 Story，写入 `{workspace}/test/iteration/{id}/story/`
    - _需求: R-3, R-0.1_

  - [ ] 7.2 实现 CaseGenAgent
    - 在 `agents/case_gen_agent.py` 中实现 `CaseGenAgent(TestBaseAgent)`
    - 基于 Story + RAG 知识库历史用例增强生成多维度用例
    - 调用 ReMe 向量检索获取相似业务历史案例
    - _需求: R-4, R-0.1_

  - [ ] 7.3 实现 Story 生成 MCP 工具 (mcp_tools/story_generator.py)
    - 实现 `generate_stories()`：输入解析结果，输出 Story 列表
    - 实现 `validate_story()`：AI 校验 Story 完整性，标记缺失验收准则
    - 实现 `generate_traceability()`：生成全链路追溯 ID
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-3_

  - [ ] 7.4 实现用例生成 MCP 工具 (mcp_tools/case_generator.py)
    - 实现 `generate_cases()`：按功能/边界/异常/安全/UI 维度批量生成
    - 实现 `enhance_with_knowledge_base()`：RAG 检索增强
    - 实现 `calculate_coverage()`：计算 Story 覆盖率、需求覆盖率
    - 实现 `export_cases()`：批量导出 Excel，复用平台原生导出工具
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-4_

  - [ ] 7.5 实现 Story 管理 API 路由 (routers/prd_analysis.py 补充)
    - 追加接口：`POST /api/test/story/generate`, `GET /api/test/story/{id}`, `PUT /api/test/story/{id}`
    - _需求: R-3_

  - [ ] 7.6 实现用例管理 API 路由 (routers/case_manage.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/case/`
    - 接口：`POST /generate`, `GET /{id}`, `PUT /{id}`, `GET /export`
    - _需求: R-4_

  - [ ] 7.7 开发用例管理前端页面 (pages/test/case_manage/)
    - 选中 Story 触发批量生成，展示生成进度
    - 用例表格：复用原生表格组件，列：标题/类型/优先级/模块/标签
    - 分类筛选：按优先级、模块、功能/UI/安全标签筛选
    - 覆盖率可视化图表：复用原生图表渲染组件
    - 批量编辑、复制、停用、删除操作
    - 检索知识库历史相似用例一键复用的检索输入框
    - Excel 导出按钮：复用原生导出工具
    - _需求: R-4, R-10, R-0.3_

  - [ ]* 7.8 编写 Story/用例模块单元测试
    - 为 Story 生成逻辑编写测试
    - 为用例生成多维度输出验证编写测试
    - 为覆盖率计算编写测试
    - _需求: R-3, R-4_

- [ ] 8. 检查点 - 确保 Story 拆解与用例生成完整可测
  - 验证 Story 生成→用例生成→覆盖度计算全流程可用

- [ ] 9. 实现 UI 自动化脚本模块
  - 实现 Playwright 脚本生成、VLM 视觉定位、在线调试
  - 开发 UI 自动化前端页面
  - _需求: R-5_

  - [ ] 9.1 实现 UIAutoAgent
    - 在 `agents/ui_auto_agent.py` 中实现 `UIAutoAgent(TestBaseAgent)`
    - 复用平台 MCP 外部进程沙箱启动 Playwright
    - 利用平台沙箱 FileGuard/ToolGuard 管控执行权限
    - _需求: R-5, R-0.1, R-12_

  - [ ] 9.2 实现 Playwright MCP 工具 (mcp_tools/ui_auto_tool.py)
    - 实现 `generate_script()`：自然语言→Playwright PO 分层代码
    - 实现 `debug_script()`：单脚本调试执行，采集截图
    - 实现 `execute_script()`：正式执行脚本，回传结果
    - 实现 `capture_screenshot()`：按步骤截图，存入 `{workspace}/test/iteration/{id}/exec_log/`
    - 封装 Playwright 子进程为 MCP Tool，不直接新建进程
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-5_

  - [ ] 9.3 实现 VLM 视觉元素定位
    - 在 `ui_auto_tool.py` 中基于平台 VLM 能力实现视觉元素定位
    - 弱化 XPath/CSS 选择器依赖
    - _需求: R-5_

  - [ ] 9.4 实现 UI 自动化 API 路由 (routers/ui_auto.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/ui-auto/`
    - 接口：`POST /generate`, `POST /debug`, `GET /script/{id}`, `PUT /script/{id}`
    - _需求: R-5_

  - [ ] 9.5 开发 UI 自动化前端页面 (pages/test/ui_auto/)
    - 单条/批量 UI 用例选中后生成 Playwright 脚本
    - 脚本编辑器：复用平台原生 Web IDE 代码编辑器组件
    - 文件树：按页面 PO 分层展示脚本组织
    - 在线调试面板：执行脚本，实时展示操作截图、执行日志
    - 日志输出区：复用平台原生日志控制台组件
    - 脚本格式化与保存功能
    - _需求: R-5, R-10, R-0.3_

  - [ ]* 9.6 编写 UI 自动化模块单元测试
    - 为 Playwright 脚本生成逻辑编写测试
    - 为 VLM 元素定位编写测试
    - _需求: R-5_

- [ ] 10. 检查点 - 确保 UI 自动化模块完整可测
  - 验证脚本生成→在线调试→截图采集全流程可用

- [ ] 11. 实现测试执行调度模块
  - 实现批量/单条执行、并行调度、多环境配置、实时进度推送
  - 开发执行调度前端页面
  - _需求: R-6_

  - [ ] 11.1 实现 TestScheduleAgent
    - 在 `agents/test_schedule_agent.py` 中实现 `TestScheduleAgent(TestBaseAgent)`
    - 复用平台原生任务队列、多进程并行调度
    - 复用 WebSocket 通道推送实时执行进度
    - _需求: R-6, R-0.1_

  - [ ] 11.2 实现测试调度 MCP 工具 (mcp_tools/test_scheduler.py)
    - 实现 `run_batch()`：批量执行，可配置并发数，重用沙箱进程调度
    - 实现 `run_single()`：单条用例执行，用于调试
    - 实现 `retry_failed()`：失败用例自动重试，失败用例单独归集
    - 实现 `get_execution_progress()`：查询执行进度
    - 支持 dev/test/pre 多环境配置，复用平台密钥隔离存储
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-6_

  - [ ] 11.3 实现执行调度 API 路由 (routers/test_exec.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/exec/`
    - 接口：`POST /run`, `POST /run-single`, `GET /progress/{run_id}`, `GET /history?iteration={id}`
    - _需求: R-6_

  - [ ] 11.4 开发测试执行调度前端页面 (pages/test/test_exec/)
    - 用例选择区：选中迭代全部用例，自定义并发数
    - 单条执行按钮：手动执行调试
    - 执行进度条：复用原生任务进度条组件
    - 实时日志：复用平台原生日志控制台组件
    - 每步截图展示区
    - 失败用例归集区：一键重跑
    - 历史执行记录列表
    - 环境配置：复用原生环境配置弹窗
    - _需求: R-6, R-10, R-0.3_

  - [ ]* 11.5 编写执行调度模块单元测试
    - 为批量执行调度逻辑编写测试
    - 为失败重试策略编写测试
    - _需求: R-6_

- [ ] 12. 检查点 - 确保执行调度模块完整可测
  - 验证批量执行→实时进度→失败归集全流程可用

- [ ] 13. 实现测试报告生成模块
  - 实现报告聚合、HTML 生成、失败分类、多渠道推送
  - 开发报告中心前端页面
  - _需求: R-7_

  - [ ] 13.1 实现 ReportAgent
    - 在 `agents/report_agent.py` 中实现 `ReportAgent(TestBaseAgent)`
    - 复用平台原生文件导出、日志解析能力
    - _需求: R-7, R-0.1_

  - [ ] 13.2 实现报告生成 MCP 工具 (mcp_tools/report_builder.py)
    - 实现 `generate_report()`：汇总执行数据、日志、截图、报错堆栈
    - 实现 `analyze_failures()`：自动判定失败根因为 Product Defect/Script Error/Environment Fault
    - 实现 `push_report()`：推送报告摘要至钉钉/飞书/企业微信，复用平台原生消息推送模块
    - 实现 `export_report()`：导出 HTML 报告文件，复用平台原生静态文件服务
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-7_

  - [ ] 13.3 实现报告中心 API 路由 (routers/report_center.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/report/`
    - 接口：`POST /generate`, `GET /{id}`, `GET /export/{id}`, `POST /push/{id}`
    - _需求: R-7_

  - [ ] 13.4 开发测试报告中心前端页面 (pages/test/report_center/)
    - 报告列表：展示所有迭代历史测试报告，复用原生表格组件
    - HTML 报告预览：复用原生 HTML 预览组件，展示通过率/覆盖度/失败详情/截图
    - AI 高频缺陷/风险分析展示区
    - 一键推送按钮：复用原生消息推送弹窗，支持钉钉/飞书渠道
    - 报告下载按钮：复用原生文件下载组件
    - 归档至知识库按钮
    - _需求: R-7, R-10, R-0.3_

  - [ ]* 13.5 编写报告生成模块单元测试
    - 为失败分类算法编写测试
    - 为 HTML 报告模板编写测试
    - _需求: R-7_

- [ ] 14. 检查点 - 确保报告生成模块完整可测
  - 验证执行结果→报告生成→推送全流程可用

- [ ] 15. 实现缺陷同步模块
  - 实现 Jira/禅道缺陷自动提交、追溯关联
  - _需求: R-8_

  - [ ] 15.1 实现缺陷同步 MCP 工具 (mcp_tools/defect_sync.py)
    - 实现 `submit_defect()`：自动组装缺陷单（步骤/预期/实际/截图附件/严重等级）
    - 实现 `sync_defect_status()`：同步缺陷状态
    - 对接 Jira REST API 和禅道 OpenAPI，复用平台原生 HTTP 请求 MCP 能力
    - 缺陷与 Story/用例/迭代自动关联追溯，写入 `TraceRecord`
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-8_

  - [ ] 15.2 实现缺陷同步 API 路由 (routers/report_center.py 补充)
    - 追加接口：`POST /api/test/defect/submit`
    - _需求: R-8_

  - [ ] 15.3 在报告中心前端页面中集成缺陷提交功能
    - 失败用例旁添加「提交缺陷」按钮
    - 弹窗预览缺陷单内容（步骤/预期/实际/截图/严重等级）
    - 提交后回显 Jira/禅道 单号
    - _需求: R-8, R-10, R-0.3_

  - [ ]* 15.4 编写缺陷同步模块单元测试
    - 为缺陷单组装的输入输出验证编写测试
    - 为追溯关联逻辑编写测试
    - _需求: R-8_

- [ ] 16. 检查点 - 确保缺陷同步模块完整可测
  - 验证失败用例→一键提交缺陷→Jira 同步全流程可用

- [ ] 17. 实现测试知识库模块
  - 实现知识归档、RAG 检索、知识蒸馏、定时备份
  - 开发知识库前端页面
  - _需求: R-9_

  - [ ] 17.1 实现 KnowledgeArchAgent
    - 在 `agents/knowledge_arch_agent.py` 中实现 `KnowledgeArchAgent(TestBaseAgent)`
    - 复用平台 ReMe 向量记忆，新增独立测试向量集合
    - 复用原生 Embedding 调用逻辑
    - _需求: R-9, R-0.1, R-0.2_

  - [ ] 17.2 实现知识库 MCP 工具 (mcp_tools/knowledge_rag.py)
    - 实现 `archive_iteration()`：迭代结束自动归档全部资产（需求/Story/用例/脚本/报告/缺陷）
    - 实现 `search_knowledge()`：自然语言检索历史资产，复用原生 RAG 向量检索接口
    - 实现 `upload_document()`：手动上传测试标准/业务手册入库
    - 实现 `distill_knowledge()`：AI 蒸馏知识库，输出测试避坑文档
    - 实现 `schedule_backup()`：知识库定时备份，复用原生 Cron
    - 在 `mcp_tools/__init__.py` 中注册所有工具
    - _需求: R-9_

  - [ ] 17.3 实现知识库 API 路由 (routers/knowledge_lib.py)
    - 编写 FastAPI APIRouter，前缀 `/api/test/knowledge/`
    - 接口：`POST /search`, `POST /archive`, `POST /distill`
    - _需求: R-9_

  - [ ] 17.4 开发测试知识库前端页面 (pages/test/knowledge_lib/)
    - 资产归档视图：按产品线/模块/迭代展示全量测试资产树
    - 自然语言搜索：复用原生向量检索输入框
    - 分类树：复用原生分类树组件
    - 手动上传：复用原生批量上传组件
    - AI 蒸馏按钮：触发知识蒸馏，展示生成的测试规范文档
    - 定时备份配置：复用原生 Cron 弹窗
    - _需求: R-9, R-10, R-0.3_

  - [ ]* 17.5 编写知识库模块单元测试
    - 为归档流程编写测试
    - 为 RAG 检索增强生成编写测试
    - _需求: R-9_

- [ ] 18. 检查点 - 确保知识库模块完整可测
  - 验证迭代归档→知识检索→蒸馏文档全流程可用

- [ ] 19. 实现通知告警集成
  - 集成迭代完成、执行失败、报告生成的推送通知
  - _需求: R-7, R-0.3_

  - [ ] 19.1 实现报告推送调用原生推送模块
    - 在 `report_builder.py` 中实现 `push_report()` 调用钉钉/飞书/企业微信原生消息发送接口
    - 复用原生渠道配置、消息模板、异步发送逻辑
    - _需求: R-7_

  - [ ] 19.2 实现执行失败实时告警
    - 在 `test_scheduler.py` 中实现批量执行结束后的自动告警推送
    - 失败用例数量超过阈值时触发即时通知
    - _需求: R-6, R-7_

  - [ ] 19.3 实现迭代完成通知
    - 在 `iteration_mgr.py` 中实现迭代状态变更为 Released 时自动通知
    - _需求: R-1_

- [ ] 20. 实现权限与安全管控
  - _需求: R-12_

  - [ ] 20.1 注册测试平台权限标签
    - 在 `plugin.py` 启动钩子中注册「测试管理员/普通测试/只读」权限标签
    - 复用平台原生用户/角色权限体系，不重写鉴权中间件
    - _需求: R-12_

  - [ ] 20.2 集成密钥安全存储
    - 测试环境账号、Jira/ZenTao 密钥存储使用平台原生加密密钥存储
    - UI 自动化脚本文件操作通过 FileGuard/ToolGuard 沙箱校验
    - _需求: R-12_

- [ ] 21. 全链路集成与验证
  - _需求: R-0.1, R-0.3, R-11_

  - [ ] 21.1 在注册入口中整合所有模块
    - 编写 `mcp_tools/__init__.py` 中 `register_test_mcp_tools()` 函数注册全部 9 个 MCP 工具
    - 编写 `agents/__init__.py` 中 `register_test_agents()` 函数，通过 MultiAgentManager 注册全部 8 个 Agent
    - 确保 `plugin.py` 的 `_on_startup` 中按正确顺序调用所有注册函数
    - _需求: R-0.1_

  - [ ] 21.2 编写全链路端到端验证脚本
    - 编写 `tests/e2e/test_extend/test_full_pipeline.py`
    - 验证迭代→需求解析→Story 生成→用例生成→UI 脚本生成→执行→报告→缺陷同步→归档 全闭环
    - _需求: R-1 至 R-9_

  - [ ] 21.3 验证原生功能不受影响
    - 运行原有全量测试：`python -m pytest tests/ -x -q`
    - 人工验证原生页面：Agent 管理、插件市场、模型配置、定时任务、设置页面正常渲染
    - _需求: R-0.1, R-0.3, R-11_

  - [ ]* 21.4 编写升级兼容性验证脚本
    - 验证 `git merge upstream/main` 无冲突（test_extend/ 目录隔离）
    - 验证 Docker 镜像构建时自动加载 test_extend 扩展
    - _需求: R-11_
