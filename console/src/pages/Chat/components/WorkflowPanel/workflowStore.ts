import { create } from "zustand";
import { persist } from "zustand/middleware";

export type StepStatus = "pending" | "running" | "completed" | "error" | "skipped";

export interface WorkflowStep {
  stepId: string;
  name: string;
  status: StepStatus;
  resultSummary: Record<string, unknown>;
  error?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface WorkflowState {
  steps: WorkflowStep[];
  currentStep: number;
  iterationId: string;
  overallProgress: number;
  loading: boolean;
  error: string | null;

  updateStep: (stepId: string, update: Partial<WorkflowStep>) => void;
  resetWorkflow: () => void;
  goToStep: (index: number) => void;
  setIterationId: (id: string) => void;
  syncFromEvent: (detail: WorkflowStepEvent) => void;
  syncFromAPI: (data: WorkflowAPIResponse) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export interface WorkflowStepEvent {
  step_id: string;
  status: StepStatus;
  result_summary?: Record<string, unknown>;
  error?: string;
  iteration_id?: string;
}

export interface WorkflowAPIResponse {
  iteration_id: string;
  overall_progress: number;
  steps: Array<{
    step_id: string;
    name: string;
    status: StepStatus;
    result_summary: Record<string, unknown>;
    error?: string;
    started_at?: string;
    completed_at?: string;
  }>;
}

export const WORKFLOW_STEP_DEFS: { id: string; name: string }[] = [
  { id: "requirement", name: "需求分析" },
  { id: "functional", name: "生成功能用例" },
  { id: "ui-auto", name: "生成UI用例" },
  { id: "review", name: "用例评审" },
  { id: "execution", name: "自动测试执行" },
  { id: "report", name: "端到端测试报告" },
];

function createDefaultSteps(): WorkflowStep[] {
  return WORKFLOW_STEP_DEFS.map((d) => ({
    stepId: d.id,
    name: d.name,
    status: "pending" as StepStatus,
    resultSummary: {},
  }));
}

function calcCurrentStep(steps: WorkflowStep[]): number {
  const runningIdx = steps.findIndex((s) => s.status === "running");
  if (runningIdx >= 0) return runningIdx;
  const lastCompleted = steps.map((s) => s.status).lastIndexOf("completed");
  return lastCompleted >= 0 ? lastCompleted : 0;
}

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set, get) => ({
      steps: createDefaultSteps(),
      currentStep: 0,
      iterationId: "",
      overallProgress: 0,
      loading: false,
      error: null,

      updateStep: (stepId, update) =>
        set((state) => {
          const steps = state.steps.map((s) =>
            s.stepId === stepId ? { ...s, ...update } : s
          );
          const completedCount = steps.filter((s) => s.status === "completed").length;
          const overallProgress = Math.round((completedCount / steps.length) * 100);
          return {
            steps,
            overallProgress,
            currentStep: calcCurrentStep(steps),
          };
        }),

      resetWorkflow: () =>
        set({
          steps: createDefaultSteps(),
          currentStep: 0,
          overallProgress: 0,
          error: null,
        }),

      goToStep: (index) => set({ currentStep: index }),

      setIterationId: (id) => set({ iterationId: id }),

      setLoading: (loading) => set({ loading }),

      setError: (error) => set({ error }),

      syncFromEvent: (detail) => {
        const state = get();
        if (detail.iteration_id && !state.iterationId) {
          set({ iterationId: detail.iteration_id });
        }
        const update: Partial<WorkflowStep> = {
          status: detail.status,
        };
        if (detail.result_summary) {
          update.resultSummary = detail.result_summary;
        }
        if (detail.error) {
          update.error = detail.error;
        }
        if (detail.status === "running") {
          update.startedAt = new Date().toISOString();
        }
        if (detail.status === "completed" || detail.status === "error") {
          update.completedAt = new Date().toISOString();
        }
        state.updateStep(detail.step_id, update);
      },

      syncFromAPI: (data) => {
        const state = get();
        if (state.iterationId && state.iterationId !== data.iteration_id) {
          return;
        }
        const steps: WorkflowStep[] = WORKFLOW_STEP_DEFS.map((def) => {
          const apiStep = data.steps.find((s) => s.step_id === def.id);
          if (apiStep) {
            return {
              stepId: apiStep.step_id,
              name: apiStep.name,
              status: apiStep.status,
              resultSummary: apiStep.result_summary || {},
              error: apiStep.error,
              startedAt: apiStep.started_at,
              completedAt: apiStep.completed_at,
            };
          }
          return {
            stepId: def.id,
            name: def.name,
            status: "pending" as StepStatus,
            resultSummary: {},
          };
        });
        set({
          iterationId: data.iteration_id,
          overallProgress: data.overall_progress,
          steps,
          currentStep: calcCurrentStep(steps),
          loading: false,
          error: null,
        });
      },
    }),
    {
      name: "workflow-panel-state",
      partialize: (state) => ({
        steps: state.steps,
        currentStep: state.currentStep,
        overallProgress: state.overallProgress,
        iterationId: state.iterationId,
      }),
    }
  )
);
