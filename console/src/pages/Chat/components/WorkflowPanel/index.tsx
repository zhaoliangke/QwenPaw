import React, { useEffect, useState, useCallback } from "react";
import {
  Button, Progress, Space, Tooltip, Empty, Select, Tag, Divider, Badge,
} from "antd";
import {
  CloseOutlined,
  DownOutlined,
  OrderedListOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  RightOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
  RetweetOutlined,
  FileTextOutlined,
  BugOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { api } from "../../../../api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ArtifactItem {
  id?: string;
  title?: string;
  name?: string;
  content?: string;
  [key: string]: unknown;
}

interface WorkflowStep {
  stepId: string;
  name: string;
  status: "pending" | "running" | "completed" | "error" | "skipped";
  resultSummary: Record<string, unknown>;
  artifact?: ArtifactItem | ArtifactItem[] | string;
  error?: string;
}

interface Project {
  id: string;
  name: string;
  target_url: string;
  env: string;
  tags: string[];
}

interface ElementMap {
  id: string;
  project_id: string;
  page_name: string;
  mapping: Record<string, string>;
}

type QuickAction = "smoke" | "regression" | "retry_failed" | "generate_only" | "defect_analysis";

interface QuickActionDef {
  key: QuickAction;
  label: string;
  icon: React.ReactNode;
  desc: string;
  color: string;
}

const QUICK_ACTIONS: QuickActionDef[] = [
  { key: "smoke", label: "冒烟测试", icon: <ThunderboltOutlined />, desc: "仅执行 P0 核心用例，5 分钟内出结果", color: "#1677ff" },
  { key: "regression", label: "全量回归", icon: <ExperimentOutlined />, desc: "全量执行测试用例并生成完整报告", color: "#722ed1" },
  { key: "retry_failed", label: "重跑失败", icon: <RetweetOutlined />, desc: "仅重新执行上次失败的用例", color: "#fa8c16" },
  { key: "generate_only", label: "仅生成用例", icon: <FileTextOutlined />, desc: "解析 PRD → 生成用例 → 暂停审阅", color: "#52c41a" },
  { key: "defect_analysis", label: "缺陷分析", icon: <BugOutlined />, desc: "分析执行结果并自动提交缺陷", color: "#ff4d4f" },
];

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const WORKFLOW_STEPS: { id: string; name: string; desc: string }[] = [
  { id: "requirement", name: "需求分析", desc: "解析 PRD / OpenAPI / Figma" },
  { id: "functional", name: "生成功能用例", desc: "基于 Story 生成测试用例" },
  { id: "ui-auto", name: "生成UI用例", desc: "生成 Playwright 脚本" },
  { id: "review", name: "用例评审", desc: "AI 评审用例完整性" },
  { id: "execution", name: "自动测试执行", desc: "批量执行测试用例" },
  { id: "report", name: "端到端测试报告", desc: "生成 HTML 报告" },
];

const QUICK_ACTION_PROMPTS: Record<QuickAction, (ctx: { projectName: string; projectId: string; env: string }) => string> = {
  smoke: (ctx) => `对项目【${ctx.projectName}】执行冒烟测试。仅运行 P0 优先级核心用例，快速验证基本功能可用性。项目 ID: ${ctx.projectId}`,
  regression: (ctx) => `对项目【${ctx.projectName}】执行全量回归测试。运行所有测试用例，生成完整的测试报告。项目 ID: ${ctx.projectId}`,
  retry_failed: (ctx) => `重新执行上次失败的测试用例，分析失败原因并更新测试报告。项目 ID: ${ctx.projectId}`,
  generate_only: (ctx) => `解析项目的 PRD 文档并生成测试用例，暂停等待我审阅后再决定是否执行。项目 ID: ${ctx.projectId}`,
  defect_analysis: (ctx) => `分析最新一次测试执行的失败结果，对产品缺陷自动提交到缺陷管理系统。项目 ID: ${ctx.projectId}`,
};

const ENV_COLORS: Record<string, string> = { test: "blue", staging: "orange", prod: "red" };

const statusIconMap: Record<string, React.ReactNode> = {
  pending: <span style={{ color: "#999" }}>○</span>,
  running: <span style={{ color: "#1677ff" }}>◐</span>,
  completed: <span style={{ color: "#52c41a" }}>●</span>,
  error: <span style={{ color: "#ff4d4f" }}>✕</span>,
  skipped: <span style={{ color: "#999" }}>−</span>,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createDefaultSteps(): WorkflowStep[] {
  return WORKFLOW_STEPS.map((d) => ({
    stepId: d.id,
    name: d.name,
    status: "pending" as const,
    resultSummary: {},
  }));
}

function renderArtifactValue(key: string, val: unknown): React.ReactNode {
  if (val === null || val === undefined) return <span style={{ color: "#999" }}>—</span>;
  if (typeof val === "boolean") return <span>{val ? "是" : "否"}</span>;
  if (typeof val === "number") return <span>{val}</span>;
  if (typeof val === "string") {
    if (val.length > 200) return <span>{val.slice(0, 200)}...</span>;
    return <span>{val}</span>;
  }
  if (Array.isArray(val)) {
    if (val.length === 0) return <span style={{ color: "#999" }}>空列表</span>;
    return (
      <div style={{ paddingLeft: 8 }}>
        {val.slice(0, 20).map((item, i) => (
          <div key={i} style={{ marginBottom: 4 }}>
            • {typeof item === "object" ? JSON.stringify(item) : String(item)}
          </div>
        ))}
        {val.length > 20 && <div style={{ color: "#999" }}>...还有 {val.length - 20} 项</div>}
      </div>
    );
  }
  if (typeof val === "object") {
    const obj = val as Record<string, unknown>;
    const entries = Object.entries(obj).slice(0, 10);
    return (
      <div style={{ paddingLeft: 8 }}>
        {entries.map(([k, v]) => (
          <div key={k} style={{ marginBottom: 2 }}>
            <strong>{k}:</strong> {typeof v === "object" ? JSON.stringify(v).slice(0, 100) : String(v).slice(0, 100)}
          </div>
        ))}
        {Object.keys(obj).length > 10 && <div style={{ color: "#999" }}>...还有 {Object.keys(obj).length - 10} 字段</div>}
      </div>
    );
  }
  return <span>{String(val)}</span>;
}

function renderArtifactContent(artifact: ArtifactItem | ArtifactItem[] | string): React.ReactNode {
  if (typeof artifact === "string") {
    return <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0, fontSize: 12 }}>{artifact}</pre>;
  }
  if (Array.isArray(artifact)) {
    if (artifact.length === 0) return <Empty description="空列表" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    return (
      <div>
        {artifact.slice(0, 20).map((item, i) => {
          if (!item || typeof item !== "object") {
            return <div key={i} style={{ fontSize: 11, marginBottom: 3 }}>• {String(item)}</div>;
          }
          const entries = Object.entries(item).filter(([k]) => k !== "id" && k !== "title");
          return (
            <div key={i} style={{ marginBottom: 6, padding: "4px 8px", background: "#fff", borderRadius: 4, border: "1px solid #f0f0f0" }}>
              <div style={{ fontWeight: 500, fontSize: 12, marginBottom: 2 }}>
                {String((item as ArtifactItem).title || (item as ArtifactItem).name || `#${i + 1}`)}
              </div>
              {entries.slice(0, 3).map(([k, v]) => (
                <div key={k} style={{ fontSize: 11 }}>
                  <strong>{k}:</strong> {String(v).slice(0, 80)}
                </div>
              ))}
            </div>
          );
        })}
        {artifact.length > 20 && <div style={{ fontSize: 11, color: "#999" }}>...还有 {artifact.length - 20} 项</div>}
      </div>
    );
  }
  if (artifact && typeof artifact === "object") {
    const entries = Object.entries(artifact).filter(([k]) => k !== "id" && k !== "title" && k !== "name");
    return (
      <div>
        <div style={{ fontWeight: 500, fontSize: 12, color: "#333", marginBottom: 4 }}>
          {(artifact as ArtifactItem).title || (artifact as ArtifactItem).name || (artifact as ArtifactItem).id || "产物详情"}
        </div>
        {entries.map(([k, v]) => (
          <div key={k} style={{ fontSize: 11, marginBottom: 3 }}>
            <strong>{k}:</strong> {renderArtifactValue(k, v)}
          </div>
        ))}
      </div>
    );
  }
  return <Empty description="暂无产物" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface WorkflowPanelProps {
  open: boolean;
  onClose: () => void;
  iterationId?: string;
}

export function WorkflowPanel({ open, onClose, iterationId }: WorkflowPanelProps) {
  const [steps, setSteps] = useState<WorkflowStep[]>(createDefaultSteps);
  const [currentStep, setCurrentStep] = useState(0);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  // Context state
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [elementMaps, setElementMaps] = useState<ElementMap[]>([]);
  const [contextLoading, setContextLoading] = useState(false);

  // -----------------------------------------------------------------------
  // Load context (projects + element maps)
  // -----------------------------------------------------------------------

  const loadContext = useCallback(async () => {
    setContextLoading(true);
    try {
      const [projRes, emRes] = await Promise.all([
        api.listProjects(),
        api.listElementMaps(),
      ]);
      const projList: Project[] = projRes?.projects || [];
      setProjects(projList);
      setElementMaps(emRes?.element_maps || []);
      if (!selectedProjectId && projList.length > 0) {
        setSelectedProjectId(projList[0].id);
      }
    } catch {
      // silent
    } finally {
      setContextLoading(false);
    }
  }, [selectedProjectId]);

  useEffect(() => {
    if (open) loadContext();
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  // -----------------------------------------------------------------------
  // Workflow step update listener
  // -----------------------------------------------------------------------

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail && detail.step_id && detail.status) {
        setSteps((prev) =>
          prev.map((s) =>
            s.stepId === detail.step_id
              ? {
                  ...s,
                  status: detail.status,
                  resultSummary: detail.result_summary || s.resultSummary,
                  artifact: detail.artifact || s.artifact,
                  error: detail.error,
                }
              : s
          )
        );
        api.updateWorkflowStep({
          step_id: detail.step_id,
          status: detail.status,
          result_summary: detail.result_summary,
          error: detail.error,
          iteration_id: detail.iteration_id || iterationId,
        }).catch(() => {});
      }
    };
    window.addEventListener("workflow-step-update", handler);
    return () => window.removeEventListener("workflow-step-update", handler);
  }, [iterationId]);

  // -----------------------------------------------------------------------
  // Derived state
  // -----------------------------------------------------------------------

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const overallProgress = Math.round((completedCount / steps.length) * 100);
  const hasError = steps.some((s) => s.status === "error");

  const selectedProject = projects.find((p) => p.id === selectedProjectId);
  const projectMaps = elementMaps.filter((m) => m.project_id === selectedProjectId);

  // -----------------------------------------------------------------------
  // Handlers
  // -----------------------------------------------------------------------

  const handleReset = () => {
    setSteps(createDefaultSteps());
    setCurrentStep(0);
    setExpandedSteps(new Set());
    api.resetWorkflow(iterationId || "").catch(() => {});
  };

  const toggleExpand = (stepId: string, idx: number) => {
    setCurrentStep(idx);
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) next.delete(stepId);
      else next.add(stepId);
      return next;
    });
  };

  const triggerQuickAction = (action: QuickAction) => {
    const projectName = selectedProject?.name || "当前项目";
    const env = selectedProject?.env || "test";
    const prompt = QUICK_ACTION_PROMPTS[action]({ projectName, projectId: selectedProjectId, env });
    window.dispatchEvent(
      new CustomEvent("workflow-quick-action", {
        detail: { action, prompt, projectId: selectedProjectId },
      })
    );
    if (!steps.some((s) => s.status !== "pending")) {
      handleReset();
    }
  };

  const triggerStart = () => {
    window.dispatchEvent(new CustomEvent("workflow-start"));
  };

  if (!open) return null;

  return (
    <div
      style={{
        width: 380,
        minWidth: 380,
        height: "100%",
        borderLeft: "1px solid #f0f0f0",
        background: "#fff",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 16px",
          borderBottom: "1px solid #f0f0f0",
          flexShrink: 0,
        }}
      >
        <Space>
          <OrderedListOutlined style={{ color: "#1677ff" }} />
          <span style={{ fontWeight: 500, fontSize: 14 }}>测试工作流</span>
        </Space>
        <Space size={4}>
          <Tooltip title="刷新上下文">
            <Button type="text" size="small" icon={<ReloadOutlined />} onClick={loadContext} loading={contextLoading} />
          </Tooltip>
          <Tooltip title="重置步骤">
            <Button type="text" size="small" icon={<ReloadOutlined />} onClick={handleReset} />
          </Tooltip>
          <Button type="text" size="small" icon={<CloseOutlined />} onClick={onClose} />
        </Space>
      </div>

      {/* Context Card */}
      <div
        style={{
          margin: "8px 12px",
          padding: "10px 12px",
          background: "#fafafa",
          borderRadius: 8,
          border: "1px solid #f0f0f0",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
          <span style={{ fontSize: 12, fontWeight: 500, color: "#666" }}>
            <SettingOutlined style={{ marginRight: 4 }} />测试上下文
          </span>
        </div>

        {/* Project Selector */}
        <div style={{ marginBottom: 6 }}>
          <Select
            size="small"
            style={{ width: "100%" }}
            placeholder="选择测试项目"
            value={selectedProjectId || undefined}
            onChange={(val) => setSelectedProjectId(val)}
            loading={contextLoading}
            notFoundContent="暂无项目，请先在项目管理中创建"
            optionLabelProp="label"
          >
            {projects.map((p) => (
              <Select.Option key={p.id} value={p.id} label={p.name}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>{p.name}</span>
                  <Tag color={ENV_COLORS[p.env] || "default"} style={{ fontSize: 10, lineHeight: "16px", marginLeft: 8 }}>
                    {p.env}
                  </Tag>
                </div>
              </Select.Option>
            ))}
          </Select>
        </div>

        {/* Project Info */}
        {selectedProject && (
          <div style={{ fontSize: 11, color: "#999", marginBottom: 4 }}>
            URL: {selectedProject.target_url}
            {projectMaps.length > 0 && (
              <span style={{ marginLeft: 8 }}>
                | 元素映射: <Badge count={projectMaps.length} size="small" style={{ backgroundColor: "#1677ff" }} />
              </span>
            )}
          </div>
        )}

        {/* Element Map quick view */}
        {projectMaps.length > 0 && (
          <div style={{ marginTop: 4, display: "flex", gap: 4, flexWrap: "wrap" }}>
            {projectMaps.map((m) => (
              <Tooltip
                key={m.id}
                title={Object.entries(m.mapping).map(([k, v]) => `${k} → ${v}`).join(" | ")}
              >
                <Tag color="blue" style={{ fontSize: 10, cursor: "pointer", margin: 0 }}>
                  {m.page_name} ({Object.keys(m.mapping).length})
                </Tag>
              </Tooltip>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div style={{ padding: "0 12px 8px", flexShrink: 0 }}>
        <div style={{ fontSize: 12, fontWeight: 500, color: "#666", marginBottom: 4 }}>
          <ThunderboltOutlined style={{ marginRight: 4 }} />快捷操作
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {QUICK_ACTIONS.map((qa) => (
            <Tooltip key={qa.key} title={qa.desc}>
              <Button
                size="small"
                icon={qa.icon}
                style={{ borderColor: qa.color, color: qa.color, fontSize: 11 }}
                onClick={() => triggerQuickAction(qa.key)}
              >
                {qa.label}
              </Button>
            </Tooltip>
          ))}
        </div>
      </div>

      <Divider style={{ margin: "0 12px 4px", flexShrink: 0 }} />

      {/* Progress */}
      <div style={{ padding: "4px 16px 8px", flexShrink: 0 }}>
        <Progress
          percent={overallProgress}
          size="small"
          status={hasError ? "exception" : overallProgress === 100 ? "success" : "active"}
          format={(p) => <span style={{ fontSize: 11 }}>{p}%</span>}
        />
      </div>

      {/* Full workflow trigger (fallback) */}
      <div style={{ padding: "0 16px 8px", flexShrink: 0 }}>
        <Button
          type="primary"
          size="small"
          block
          icon={<PlayCircleOutlined />}
          onClick={triggerStart}
        >
          开始端到端测试
        </Button>
      </div>

      {/* Steps */}
      <div style={{ flex: 1, overflowY: "auto", padding: "4px 8px" }}>
        {steps.map((step, idx) => {
          const isExpanded = expandedSteps.has(step.stepId);
          const hasArtifact = step.artifact !== undefined && step.artifact !== null;
          const isSelected = idx === currentStep;
          return (
            <div key={step.stepId} style={{ marginBottom: 4 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 8,
                  padding: "8px 12px",
                  cursor: "pointer",
                  borderRadius: 6,
                  background: isSelected ? "#e6f7ff" : "transparent",
                  borderLeft: isSelected ? "3px solid #1677ff" : "3px solid transparent",
                }}
                onClick={() => setCurrentStep(idx)}
              >
                <div style={{ marginTop: 2, flexShrink: 0 }}>{statusIconMap[step.status]}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, color: "#333", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span>
                      <span style={{ color: "#999", marginRight: 4, fontSize: 12 }}>{idx + 1}.</span>
                      {step.name}
                    </span>
                    {(hasArtifact || step.error) && (
                      <Button
                        type="text"
                        size="small"
                        icon={isExpanded ? <DownOutlined /> : <RightOutlined />}
                        style={{ width: 20, height: 20, minWidth: 20 }}
                        onClick={(e) => { e.stopPropagation(); toggleExpand(step.stepId, idx); }}
                      />
                    )}
                  </div>
                  {step.error && !isExpanded && (
                    <div style={{ fontSize: 11, color: "#ff4d4f", marginTop: 2 }}>{step.error}</div>
                  )}
                  {Object.keys(step.resultSummary).length > 0 && !isExpanded && (
                    <div style={{ fontSize: 11, color: "#999", marginTop: 2 }}>
                      {Object.entries(step.resultSummary)
                        .slice(0, 2)
                        .map(([k, v]) => `${k}: ${String(v).slice(0, 30)}`)
                        .join(", ")}
                    </div>
                  )}
                </div>
              </div>

              {isExpanded && (
                <div
                  style={{
                    margin: "0 12px 4px 28px",
                    padding: "8px 10px",
                    background: "#f9f9f9",
                    borderRadius: 4,
                    border: "1px solid #f0f0f0",
                    maxHeight: 300,
                    overflowY: "auto",
                  }}
                >
                  {step.error && (
                    <div style={{ fontSize: 11, color: "#ff4d4f", marginBottom: 8, padding: "4px 8px", background: "#fff2f0", borderRadius: 4 }}>
                      错误: {step.error}
                    </div>
                  )}
                  {hasArtifact ? (
                    <div>
                      {step.resultSummary && Object.keys(step.resultSummary).length > 0 && (
                        <div style={{ marginBottom: 8 }}>
                          {Object.entries(step.resultSummary).map(([k, v]) => (
                            <div key={k} style={{ fontSize: 11, marginBottom: 2 }}>
                              <strong>{k}:</strong> {renderArtifactValue(k, v)}
                            </div>
                          ))}
                          <div style={{ height: 1, background: "#e8e8e8", margin: "6px 0" }} />
                        </div>
                      )}
                      {renderArtifactContent(step.artifact!)}
                    </div>
                  ) : step.status === "completed" ? (
                    <Empty description="步骤已完成（无产物）" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                  ) : (
                    <div style={{ fontSize: 11, color: "#999", textAlign: "center", padding: "8px 0" }}>
                      {step.status === "running" ? "执行中..." : "等待执行"}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      {overallProgress === 100 && (
        <div
          style={{
            padding: "8px 16px",
            background: "#f6ffed",
            borderTop: "1px solid #b7eb8f",
            fontSize: 12,
            color: "#389e0d",
            textAlign: "center",
            flexShrink: 0,
          }}
        >
          所有步骤已完成
        </div>
      )}
    </div>
  );
}
