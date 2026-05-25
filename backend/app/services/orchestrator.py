from dataclasses import dataclass
from typing import Any, Optional, Tuple

from app.models.schemas import (
    CodeStructure, StructuredTrace, ExecutionTrace, Explanation, LearningUnit
)
from app.services.analyzer import StaticAnalyzer
from app.services.tracer import RuntimeTracer
from app.services.structurer import TraceStructurer
from app.services.explainer import ExplanationGenerator


@dataclass
class AnalysisResult:
    """代码分析结果"""
    code_structure: CodeStructure
    raw_trace: ExecutionTrace
    structured_trace: StructuredTrace
    explanation: Explanation


class CodeAnalysisOrchestrator:
    """代码分析编排服务，统一管理分析流程"""

    def __init__(self):
        self._analyzer: Optional[StaticAnalyzer] = None
        self._tracer: Optional[RuntimeTracer] = None
        self._structurer: Optional[TraceStructurer] = None
        self._explainer: Optional[ExplanationGenerator] = None

    def _initialize_services(self):
        """延迟初始化服务实例"""
        if self._analyzer is None:
            self._analyzer = StaticAnalyzer()
        if self._tracer is None:
            self._tracer = RuntimeTracer()
        if self._structurer is None:
            self._structurer = TraceStructurer()
        if self._explainer is None:
            self._explainer = ExplanationGenerator()

    def analyze_full_code(self, code: str, inputs: dict) -> AnalysisResult:
        """
        对完整代码进行完整分析，包括静态分析和动态追踪

        Args:
            code: 待分析的代码字符串
            inputs: 输入参数字典

        Returns:
            AnalysisResult: 包含代码结构、原始轨迹、结构化轨迹和解释
        """
        self._initialize_services()

        # 静态分析
        code_structure = self._analyzer.analyze(code)
        learning_units = self._analyzer.get_learning_path()
        code_structure.learning_units = learning_units

        # 动态执行
        trace = self._tracer.trace(code, inputs)

        # 轨迹压缩
        structured_trace = self._structurer.structure(trace)

        # 生成解释
        explanation = self._explainer.generate_explanation(structured_trace, code)

        return AnalysisResult(
            code_structure=code_structure,
            raw_trace=trace,
            structured_trace=structured_trace,
            explanation=explanation
        )

    def analyze_code_unit(self, code: str, inputs: dict) -> Tuple[ExecutionTrace, StructuredTrace, Explanation]:
        """
        对单个代码单元进行分析（用于课程生成）

        Args:
            code: 代码单元字符串
            inputs: 输入参数字典

        Returns:
            Tuple[Trace, StructuredTrace, Explanation]: 原始轨迹、结构化轨迹和解释
        """
        self._initialize_services()

        # 动态执行
        trace = self._tracer.trace(code, inputs)

        # 轨迹压缩
        structured_trace = self._structurer.structure(trace)

        # 生成解释
        explanation = self._explainer.generate_explanation(structured_trace, code)

        return trace, structured_trace, explanation

    def get_learning_units(self, code: str) -> list[LearningUnit]:
        """
        获取代码的学习单元列表（仅静态分析）

        Args:
            code: 待分析的代码字符串

        Returns:
            list[LearningUnit]: 学习单元列表
        """
        self._initialize_services()

        self._analyzer.analyze(code)
        return self._analyzer.get_learning_path()
