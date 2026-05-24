from pydantic import BaseModel
from typing import List, Any, Optional

from app.models.schemas import CompressedStep, StructuredTrace, Explanation, StepExplanation, VariableChangeExplanation


class ExplanationGenerator:
    """基于规则的分析器，为代码执行轨迹生成自然语言解释"""

    def __init__(self):
        self._operator_keywords = {
            '+': '加', '-': '减', '*': '乘', '/': '除',
            '==': '等于', '!=': '不等于', '>': '大于',
            '<': '小于', '>=': '大于等于', '<=': '小于等于',
            'and': '且', 'or': '或', 'not': '非'
        }

    def generate_explanation(self, trace: StructuredTrace, code: str) -> Explanation:
        """生成完整的执行解释"""
        step_explanations: List[StepExplanation] = []
        variable_changes: List[VariableChangeExplanation] = []
        key_insights: List[str] = []

        prev_variables: dict[str, Any] = {}

        for i, step in enumerate(trace.compressed_steps):
            current_vars = step.vars_snapshot.copy()

            step_explanation = self.explain_step(step)
            step_explanations.append(StepExplanation(
                step_id=step.step_id,
                line=step.line,
                explanation=step_explanation,
                citation=f"→ Step {step.step_id}"
            ))

            for var_name, new_val in current_vars.items():
                old_val = prev_variables.get(var_name)
                if old_val != new_val and var_name not in prev_variables:
                    change_reason = self._explain_value_assignment(
                        var_name, new_val, step.code
                    )
                    variable_changes.append(VariableChangeExplanation(
                        var_name=var_name,
                        old_value=None,
                        new_value=new_val,
                        reason=change_reason
                    ))
                elif old_val != new_val:
                    change_reason = self.explain_variable_change(
                        var_name, old_val, new_val, step.code
                    )
                    variable_changes.append(VariableChangeExplanation(
                        var_name=var_name,
                        old_value=old_val,
                        new_value=new_val,
                        reason=change_reason
                    ))

            if step.node_type == "branch":
                branch_insight = self.explain_branch(
                    step.code, True, ""
                )
                key_insights.append(branch_insight)

            prev_variables = current_vars.copy()

        summary = self._generate_summary(trace, step_explanations, key_insights)

        if not key_insights:
            key_insights = self._extract_key_insights(trace, variable_changes)

        return Explanation(
            summary=summary,
            step_explanations=step_explanations,
            variable_changes=variable_changes,
            key_insights=key_insights
        )

    def explain_step(self, step: CompressedStep) -> str:
        """解释单个执行步骤"""
        if step.node_type == "call":
            return self._explain_call(step)
        elif step.node_type == "branch":
            return self._explain_branch_step(step)
        elif step.node_type in ("loop_start", "loop_end"):
            return self._explain_loop(step)
        elif step.node_type == "return":
            return self._explain_return(step)
        else:
            return self._explain_assignment(step)

    def _explain_assignment(self, step: CompressedStep) -> str:
        """解释赋值语句"""
        code = step.code.strip()
        if '=' in code and '==' not in code:
            var_part = code.split('=')[0].strip()
            val_part = code.split('=')[1].strip()
            return f"将变量 {var_part} 设置为 {self._format_value(step.vars_snapshot.get(var_part, val_part))}"
        return f"执行赋值操作: {code}"

    def _explain_call(self, step: CompressedStep) -> str:
        """解释函数调用"""
        return f"调用函数"

    def _explain_branch_step(self, step: CompressedStep) -> str:
        """解释分支步骤"""
        return f"条件判断: {step.code}"

    def _explain_loop(self, step: CompressedStep) -> str:
        """解释循环语句"""
        if step.node_type == "loop_start" and step.iteration_count:
            return f"循环开始，执行 {step.iteration_count} 次"
        elif step.node_type == "loop_end":
            return f"循环结束"
        return f"循环迭代: {step.code}"

    def _explain_return(self, step: CompressedStep) -> str:
        """解释返回语句"""
        return f"返回结果: {self._format_value(step.vars_snapshot)}"

    def explain_variable_change(
        self, var_name: str, old_val: Any, new_val: Any, context: str
    ) -> str:
        """解释变量变化"""
        if old_val is None:
            return f"变量 {var_name} 被初始化为 {self._format_value(new_val)}"

        old_f = self._format_value(old_val)
        new_f = self._format_value(new_val)

        if isinstance(new_val, (int, float)) and isinstance(old_val, (int, float)):
            diff = new_val - old_val
            if diff > 0:
                return f"{var_name} 从 {old_f} 增加到 {new_f} (增加 {diff})"
            elif diff < 0:
                return f"{var_name} 从 {old_f} 减少到 {new_f} (减少 {abs(diff)})"
            else:
                return f"{var_name} 保持不变为 {new_f}"

        if isinstance(new_val, str) and isinstance(old_val, str):
            if len(new_val) > len(old_val):
                return f"{var_name} 从 '{old_f}' 更新为 '{new_f}'"
            return f"{var_name} 从 '{old_f}' 变为 '{new_f}'"

        if isinstance(new_val, bool) or isinstance(old_val, bool):
            return f"{var_name} 从 {old_f} 变为 {new_f}"

        return f"{var_name} 从 {old_f} 更新为 {new_f}"

    def explain_branch(self, condition: str, result: bool, context: str) -> str:
        """解释分支决策"""
        condition_clean = self._clean_condition(condition)

        if result:
            return f"条件 '{condition_clean}' 为真，执行分支代码"
        else:
            return f"条件 '{condition_clean}' 为假，跳过分支代码"

    def _clean_condition(self, condition: str) -> str:
        """清理条件表达式使其更易读"""
        condition = condition.strip()
        for op, cn_op in self._operator_keywords.items():
            condition = condition.replace(op, cn_op)
        return condition

    def _format_value(self, value: Any) -> str:
        """格式化值为可读字符串"""
        if value is None:
            return "空值"
        if isinstance(value, str):
            if len(value) > 50:
                return f"'{value[:50]}...'"
            return f"'{value}'"
        if isinstance(value, list):
            if len(value) > 5:
                return f"[{', '.join(str(v) for v in value[:5])}, ...]"
            return f"[{', '.join(str(v) for v in value)}]"
        if isinstance(value, dict):
            keys = list(value.keys())
            if len(keys) > 3:
                return f"{{{', '.join(str(k) for k in keys[:3])}, ...}}"
            return str(value)
        return str(value)

    def _explain_value_assignment(self, var_name: str, value: Any, code: str) -> str:
        """解释变量赋值的原因"""
        code_lower = code.lower()

        if 'input' in code_lower:
            return f"通过用户输入获取值并赋值给 {var_name}"
        if 'random' in code_lower:
            return f"生成随机数赋值给 {var_name}"
        if 'open' in code_lower:
            return f"从文件读取数据赋值给 {var_name}"

        val_type = type(value).__name__
        if val_type == 'int':
            return f"将整数值 {value} 赋值给 {var_name}"
        if val_type == 'str':
            return f"将字符串值赋值给 {var_name}"
        if val_type == 'list':
            return f"创建列表并赋值给 {var_name}"
        if val_type == 'dict':
            return f"创建字典并赋值给 {var_name}"

        return f"初始化变量 {var_name} 为 {self._format_value(value)}"

    def _generate_summary(
        self, trace: StructuredTrace,
        step_explanations: List[StepExplanation],
        key_insights: List[str]
    ) -> str:
        """生成执行摘要"""
        total_steps = len(trace.compressed_steps)
        lines_executed = len(set(s.line for s in trace.compressed_steps))

        calls = sum(1 for s in trace.compressed_steps if s.node_type == "call")
        branches = sum(1 for s in trace.compressed_steps if s.node_type == "branch")
        loops = sum(1 for s in trace.compressed_steps if s.node_type in ("loop_start", "loop_end"))

        summary_parts = [
            f"代码共执行 {total_steps} 个步骤，",
            f"涉及 {lines_executed} 行代码"
        ]

        if loops > 0:
            summary_parts.append(f"包含 {loops // 2} 次循环")
        if calls > 0:
            summary_parts.append(f"调用 {calls} 个函数")
        if branches > 0:
            summary_parts.append(f"进行 {branches} 次条件判断")

        return "，".join(summary_parts)

    def _extract_key_insights(
        self, trace: StructuredTrace,
        variable_changes: List[VariableChangeExplanation]
    ) -> List[str]:
        """从执行轨迹中提取关键洞察"""
        insights: List[str] = []

        if len(variable_changes) > 10:
            insights.append(f"代码涉及 {len(variable_changes)} 次变量变化，表明有较多的状态更新操作")

        counter_vars = [vc for vc in variable_changes
                        if vc.var_name in ['i', 'j', 'k', 'count', 'index', 'counter']]
        if len(counter_vars) >= 3:
            insights.append("代码使用了循环迭代变量进行计数操作")

        str_vars = [vc for vc in variable_changes if isinstance(vc.new_value, str)]
        if len(str_vars) >= 3:
            insights.append("代码包含多个字符串操作")

        bool_changes = [vc for vc in variable_changes
                       if isinstance(vc.new_value, bool) or isinstance(vc.old_value, bool)]
        if len(bool_changes) >= 2:
            insights.append("代码包含布尔逻辑判断和状态切换")

        return insights
