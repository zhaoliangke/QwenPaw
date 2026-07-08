import React, { memo } from "react";
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  MinusCircleOutlined,
} from "@ant-design/icons";
import { WorkflowStep, StepStatus } from "./workflowStore";

interface WorkflowStepItemProps {
  step: WorkflowStep;
  index: number;
  isActive: boolean;
  onClick: () => void;
}

const statusIconMap: Record<StepStatus, React.ReactNode> = {
  pending: <ClockCircleOutlined style={{ color: "#999", fontSize: 14 }} />,
  running: <LoadingOutlined style={{ color: "#1677ff", fontSize: 14 }} />,
  completed: <CheckCircleOutlined style={{ color: "#52c41a", fontSize: 14 }} />,
  error: <CloseCircleOutlined style={{ color: "#ff4d4f", fontSize: 14 }} />,
  skipped: <MinusCircleOutlined style={{ color: "#999", fontSize: 14 }} />,
};

function getResultSummaryText(step: WorkflowStep): string {
  const r = step.resultSummary;
  switch (step.stepId) {
    case "requirement":
      if (r.modules != null) {
        const count = Array.isArray(r.modules) ? r.modules.length : r.modules;
        return `模块 ${count} 个`;
      }
      return "";
    case "functional":
      return r.caseCount ? `${r.caseCount} 条用例` : r.storyCount ? `${r.storyCount} 个 Story` : "";
    case "ui-auto":
      return r.pageObjects ? `${r.pageObjects} 个页面对象` : "";
    case "review":
      return r.passed ? `通过 ${r.passed} 条` : "";
    case "execution":
      return r.total && r.passed != null ? `${r.passed}/${r.total} 通过` : "";
    case "report":
      return r.passRate != null ? `通过率 ${r.passRate}%` : "";
    default:
      return "";
  }
}

const WorkflowStepItemInner = ({ step, index, isActive, onClick }: WorkflowStepItemProps) => {
  const summary = getResultSummaryText(step);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: 8,
        padding: "8px 12px",
        cursor: "pointer",
        borderRadius: 6,
        background: isActive ? "#e6f7ff" : "transparent",
        borderLeft: isActive ? "3px solid #1677ff" : "3px solid transparent",
        transition: "background 0.2s",
      }}
      onClick={onClick}
    >
      <div style={{ marginTop: 2, flexShrink: 0 }}>
        {statusIconMap[step.status]}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: isActive ? 500 : 400, color: "#333" }}>
          <span style={{ color: "#999", marginRight: 4, fontSize: 12 }}>{index + 1}.</span>
          {step.name}
        </div>
        {summary && (
          <div style={{ fontSize: 12, color: "#52c41a", marginTop: 2 }}>
            {summary}
          </div>
        )}
        {step.error && (
          <div style={{ fontSize: 11, color: "#ff4d4f", marginTop: 2 }}>
            {step.error}
          </div>
        )}
      </div>
    </div>
  );
};

export const WorkflowStepItem = memo(WorkflowStepItemInner);
