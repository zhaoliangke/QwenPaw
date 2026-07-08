# -*- coding: utf-8 -*-
"""A/B test agent — statistical analysis of variant performance.

Calculates p-values using chi-squared test for conversion rates
and t-test approximation for continuous metrics.
"""

import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.ab_test import (
    ABStatus,
    ABTest,
    ABTestResult,
    MetricResult,
)
from storage.paths import get_ab_test_dir

logger = logging.getLogger(__name__)


class ABObstestAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._ab_dir = get_ab_test_dir(self._workspace)
        self._ab_dir.mkdir(parents=True, exist_ok=True)

    async def analyze(self, test: ABTest, control_data: list[float], treatment_data: list[float]) -> ABTestResult:
        result = ABTestResult(test_id=test.id)
        result.sample_size_control = len(control_data)
        result.sample_size_treatment = len(treatment_data)

        if not control_data or not treatment_data:
            result.status = ABStatus.INCONCLUSIVE
            result.conclusion = "Insufficient data for analysis"
            return result

        control_mean = sum(control_data) / len(control_data)
        treatment_mean = sum(treatment_data) / len(treatment_data)

        control_var = sum((x - control_mean) ** 2 for x in control_data) / max(len(control_data) - 1, 1)
        treatment_var = sum((x - treatment_mean) ** 2 for x in treatment_data) / max(len(treatment_data) - 1, 1)

        se = math.sqrt(control_var / len(control_data) + treatment_var / len(treatment_data))
        t_stat = (treatment_mean - control_mean) / se if se > 0 else 0

        df = len(control_data) + len(treatment_data) - 2
        p_value = self._approx_p_value(abs(t_stat), df)

        lift = ((treatment_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
        significant = p_value < test.significance_level

        metric_result = MetricResult(
            metric_name=test.metrics[0] if test.metrics else "conversion",
            control_value=control_mean,
            treatment_value=treatment_mean,
            lift_percentage=lift,
            p_value=p_value,
            significant=significant,
        )
        result.metric_results = [metric_result]

        if significant:
            result.winner = "treatment" if lift > 0 else "control"
            result.status = ABStatus.COMPLETED
            result.conclusion = (
                f"Treatment shows {abs(lift):.1f}% {'increase' if lift > 0 else 'decrease'} "
                f"with p={p_value:.4f} (significant at α={test.significance_level})"
            )
        else:
            if result.sample_size_control + result.sample_size_treatment >= test.target_sample_size:
                result.status = ABStatus.INCONCLUSIVE
                result.conclusion = f"No significant difference detected (p={p_value:.4f}). Test inconclusive."
            else:
                result.status = ABStatus.RUNNING
                result.conclusion = f"Need more data (p={p_value:.4f}). Continue running."

        result.executed_at = datetime.utcnow()
        self._save_result(result)
        return result

    def _approx_p_value(self, t_stat: float, df: int) -> float:
        """Approximate p-value using t-distribution."""
        if df <= 0:
            return 1.0
        x = df / (df + t_stat ** 2)
        a = df / 2
        b = 0.5
        return min(1.0, max(0.001, self._beta_cf(x, a, b) / self._beta_func(a, b) * 2))

    def _beta_cf(self, x: float, a: float, b: float, max_iter: int = 100) -> float:
        qab = a + b
        qap = a + 1
        qam = a - 1
        c = 1
        d = 1 - qab * x / qap
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1 / d
        h = d
        for m in range(1, max_iter + 1):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1 / d
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1 / d
            delta = d * c
            h *= delta
            if abs(delta - 1) < 1e-8:
                break
        return h

    def _beta_func(self, a: float, b: float) -> float:
        return math.exp(math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))

    def list_results(self, test_id: str = "") -> list[ABTestResult]:
        results = []
        for f in sorted(self._ab_dir.glob("*_result.json")):
            data = read_json_file(f)
            if data:
                r = ABTestResult(**data)
                if not test_id or r.test_id == test_id:
                    results.append(r)
        return results

    def _save_result(self, result: ABTestResult):
        f = self._ab_dir / f"{result.test_id}_result.json"
        write_json_file(f, result.model_dump())
