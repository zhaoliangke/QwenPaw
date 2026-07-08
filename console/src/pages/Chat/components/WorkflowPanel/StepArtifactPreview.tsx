import React, { memo } from "react";
import { WorkflowStep } from "./workflowStore";

interface StepArtifactPreviewProps {
  step: WorkflowStep;
}

function renderRequirementDetails(step: WorkflowStep) {
  const r = step.resultSummary;
  return (
    <div style={{ fontSize: 12, color: "#666", padding: "4px 0" }}>
      {r.modules != null && <div>功能模块: <b>{Array.isArray(r.modules) ? r.modules.length : r.modules}</b></div>}
      {r.flows != null && <div>业务流程: <b>{typeof r.flows === "number" ? r.flows : Array.isArray(r.flows) ? r.flows.length : r.flows}</b></div>}
      {r.rules != null && <div>验证规则: <b>{typeof r.rules === "number" ? r.rules : Array.isArray(r.rules) ? r.rules.length : r.rules}</b></div>}
      {r.exceptions != null && <div>异常流: <b>{typeof r.exceptions === "number" ? r.exceptions : Array.isArray(r.exceptions) ? r.exceptions.length : r.exceptions}</b></div>}
      {r.nonFunctional != null && <div>非功能性: <b>{r.nonFunctional}</b></div>}
      {r.risks != null && <div>风险项: <b>{typeof r.risks === "number" ? r.risks : Array.isArray(r.risks) ? r.risks.length : r.risks}</b></div>}
    </div>
  );
}

function renderFunctionalDetails(step: WorkflowStep) {
  const r = step.resultSummary;
  return (
    <div style={{ fontSize: 12, color: "#666", padding: "4px 0" }}>
      {r.storyCount != null && <div>User Story: <b>{r.storyCount}</b></div>}
      {r.caseCount != null && <div>测试用例: <b>{r.caseCount}</b></div>}
      {r.coverage != null && <div>需求覆盖率: <b>{r.coverage}%</b></div>}
    </div>
  );
}

function renderUiAutoDetails(step: WorkflowStep) {
  const r = step.resultSummary;
  return (
    <div style={{ fontSize: 12, color: "#666", padding: "4px 0" }}>
      {r.pageObjects != null && <div>Page Objects: <b>{r.pageObjects}</b></div>}
      {r.totalSteps != null && <div>操作步骤: <b>{r.totalSteps}</b></div>}
      {r.pages != null && <div>涉及页面: <b>{Array.isArray(r.pages) ? r.pages.join(", ") : r.pages}</b></div>}
    </div>
  );
}

function renderReviewDetails(step: WorkflowStep) {
  const r = step.resultSummary;
  return (
    <div style={{ fontSize: 12, color: "#666", padding: "4px 0" }}>
      {r.totalCases != null && <div>总用例: <b>{r.totalCases}</b></div>}
      {r.passed != null && <div>通过: <b style={{ color: "#52c41a" }}>{r.passed}</b></div>}
      {r.failed != null && <div>失败: <b style={{ color: "#ff4d4f" }}>{r.failed}</b></div>}
    </div>
  );
}

function renderExecutionDetails(step: WorkflowStep) {
  const r = step.resultSummary;
  return (
    <div style={{ fontSize: 12, color: "#666", padding: "4px 0" }}>
      {r.total != null && <div>总用例: <b>{r.total}</b></div>}
      {r.passed != null && <div>通过: <b style={{ color: "#52c41a" }}>{r.passed}</b></div>}
      {r.failed != null && <div>失败: <b style={{ color: "#ff4d4f" }}>{r.failed}</b></div>}
      {r.skipped != null && <div>跳过: <b>{r.skipped}</b></div>}
    </div>
  );
}

function renderReportDetails(step: WorkflowStep) {
  const r = step.resultSummary;
  return (
    <div style={{ fontSize: 12, color: "#666", padding: "4px 0" }}>
      {r.passRate != null && (
        <div style={{ fontSize: 18, fontWeight: 600, color: "#52c41a" }}>
          {r.passRate}%
          {r.previousPassRate != null && (
            <span style={{ fontSize: 12, marginLeft: 8, color: r.passRate >= r.previousPassRate ? "#52c41a" : "#ff4d4f" }}>
              {r.passRate >= r.previousPassRate ? "↑" : "↓"} {Math.abs(r.passRate - (r.previousPassRate as number))}%
            </span>
          )}
        </div>
      )}
      {r.total != null && <div>总计: <b>{r.total}</b> 条</div>}
      {r.duration != null && <div>耗时: <b>{r.duration}s</b></div>}
    </div>
  );
}

const DETAIL_RENDERERS: Record<string, (step: WorkflowStep) => React.ReactNode> = {
  requirement: renderRequirementDetails,
  functional: renderFunctionalDetails,
  "ui-auto": renderUiAutoDetails,
  review: renderReviewDetails,
  execution: renderExecutionDetails,
  report: renderReportDetails,
};

const StepArtifactPreviewInner = ({ step }: StepArtifactPreviewProps) => {
  if (step.status !== "completed") return null;
  const renderer = DETAIL_RENDERERS[step.stepId];
  if (!renderer) return null;
  return (
    <div style={{ padding: "4px 12px 8px 28px", borderBottom: "1px solid #f0f0f0" }}>
      {renderer(step)}
    </div>
  );
};

export const StepArtifactPreview = memo(StepArtifactPreviewInner);
