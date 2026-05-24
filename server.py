#!/usr/bin/env python3
import sys
import builtins
import threading
import json
import ast
import os
import http.server
import socketserver
from io import StringIO
from typing import Any, Optional, List, Dict
from urllib.parse import urlparse, parse_qs


# ========== 数据模型 ==========
class TraceStep:
    def __init__(self, step_id: int, line: int, code: str, vars_before: Dict, vars_after: Dict, event: str, function_name: str):
        self.step_id = step_id
        self.line = line
        self.code = code
        self.vars_before = vars_before
        self.vars_after = vars_after
        self.event = event
        self.function_name = function_name

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "line": self.line,
            "code": self.code,
            "vars_before": self.vars_before,
            "vars_after": self.vars_after,
            "event": self.event,
            "function_name": self.function_name
        }


class ErrorInfo:
    def __init__(self, type: str, message: str, traceback: List[TraceStep]):
        self.type = type
        self.message = message
        self.traceback = traceback

    def to_dict(self):
        return {
            "type": self.type,
            "message": self.message,
            "traceback": [s.to_dict() for s in self.traceback]
        }


class ExecutionTrace:
    def __init__(self):
        self.steps: List[TraceStep] = []
        self.variables: Dict[str, Any] = {}
        self.call_stack: List[str] = []
        self.exception: Optional[ErrorInfo] = None

    def to_dict(self):
        return {
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables,
            "call_stack": self.call_stack,
            "exception": self.exception.to_dict() if self.exception else None
        }


class CompressedStep:
    def __init__(self, step_id: int, line: int, code: str, vars_snapshot: Dict, node_type: str = "normal", iteration_count: Optional[int] = None, branch_taken: Optional[str] = None):
        self.step_id = step_id
        self.line = line
        self.code = code
        self.vars_snapshot = vars_snapshot
        self.node_type = node_type
        self.iteration_count = iteration_count
        self.branch_taken = branch_taken

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "line": self.line,
            "code": self.code,
            "vars_snapshot": self.vars_snapshot,
            "node_type": self.node_type,
            "iteration_count": self.iteration_count,
            "branch_taken": self.branch_taken
        }


class StructuredTrace:
    def __init__(self, compressed_steps: List[CompressedStep], execution_path: List[int], key_nodes: Dict, path_summary: str):
        self.compressed_steps = compressed_steps
        self.execution_path = execution_path
        self.key_nodes = key_nodes
        self.path_summary = path_summary

    def to_dict(self):
        return {
            "compressed_steps": [s.to_dict() for s in self.compressed_steps],
            "execution_path": self.execution_path,
            "key_nodes": self.key_nodes,
            "path_summary": self.path_summary
        }


class StepExplanation:
    def __init__(self, step_id: int, line: int, explanation: str, citation: str):
        self.step_id = step_id
        self.line = line
        self.explanation = explanation
        self.citation = citation

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "line": self.line,
            "explanation": self.explanation,
            "citation": self.citation
        }


class VariableChangeExplanation:
    def __init__(self, var_name: str, old_value: Any, new_value: Any, reason: str):
        self.var_name = var_name
        self.old_value = old_value
        self.new_value = new_value
        self.reason = reason

    def to_dict(self):
        return {
            "var_name": self.var_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason
        }


class Explanation:
    def __init__(self, summary: str, step_explanations: List[StepExplanation], variable_changes: List[VariableChangeExplanation], key_insights: List[str]):
        self.summary = summary
        self.step_explanations = step_explanations
        self.variable_changes = variable_changes
        self.key_insights = key_insights

    def to_dict(self):
        return {
            "summary": self.summary,
            "step_explanations": [s.to_dict() for s in self.step_explanations],
            "variable_changes": [v.to_dict() for v in self.variable_changes],
            "key_insights": self.key_insights
        }


class FunctionInfo:
    def __init__(self, name: str, lineno: int, end_lineno: int, args: List[str], docstring: Optional[str]):
        self.name = name
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.args = args
        self.docstring = docstring

    def to_dict(self):
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "args": self.args,
            "docstring": self.docstring
        }


class ClassInfo:
    def __init__(self, name: str, lineno: int, end_lineno: int, methods: List[str], docstring: Optional[str]):
        self.name = name
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.methods = methods
        self.docstring = docstring

    def to_dict(self):
        return {
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "methods": self.methods,
            "docstring": self.docstring
        }


class LearningUnit:
    def __init__(self, name: str, type: str, lineno: int, content: str, depends_on: List[str]):
        self.name = name
        self.type = type
        self.lineno = lineno
        self.content = content
        self.depends_on = depends_on

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "lineno": self.lineno,
            "content": self.content,
            "depends_on": self.depends_on
        }


class CodeStructure:
    def __init__(self, functions: List[FunctionInfo], classes: List[ClassInfo], dependencies: Dict[str, List[str]], learning_path: List[str], learning_units: List[LearningUnit]):
        self.functions = functions
        self.classes = classes
        self.dependencies = dependencies
        self.learning_path = learning_path
        self.learning_units = learning_units

    def to_dict(self):
        return {
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "dependencies": self.dependencies,
            "learning_path": self.learning_path,
            "learning_units": [u.to_dict() for u in self.learning_units]
        }


class Lesson:
    def __init__(self, id: int, title: str, type: str, content: str, explanation: Explanation, trace: Optional[StructuredTrace], key_insights: List[str]):
        self.id = id
        self.title = title
        self.type = type
        self.content = content
        self.explanation = explanation
        self.trace = trace
        self.key_insights = key_insights

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "content": self.content,
            "explanation": self.explanation.to_dict(),
            "trace": self.trace.to_dict() if self.trace else None,
            "key_insights": self.key_insights
        }


class Course:
    def __init__(self, title: str, description: str, lessons: List[Lesson], total_steps: int):
        self.title = title
        self.description = description
        self.lessons = lessons
        self.total_steps = total_steps

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "lessons": [l.to_dict() for l in self.lessons],
            "total_steps": self.total_steps
        }


class PathDiffResult:
    def __init__(self, input_a: Dict, input_b: Dict, path_a: List[int], path_b: List[int], diff_points: List[Dict]):
        self.input_a = input_a
        self.input_b = input_b
        self.path_a = path_a
        self.path_b = path_b
        self.diff_points = diff_points

    def to_dict(self):
        return {
            "input_a": self.input_a,
            "input_b": self.input_b,
            "path_a": self.path_a,
            "path_b": self.path_b,
            "diff_points": self.diff_points
        }


# ========== 运行时追踪器 ==========
class TimeoutError(Exception):
    pass


class SecurityRestrictedbuiltins:
    _allowed = {
        'print': print, 'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
        'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple, 'set': set, 'abs': abs,
        'min': min, 'max': max, 'sum': sum, 'sorted': sorted, 'reversed': reversed,
        'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter, 'isinstance': isinstance,
        'issubclass': issubclass, 'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
        'delattr': delattr, 'dir': dir, 'id': id, 'hash': hash, 'repr': repr, 'round': round,
        'pow': pow, 'divmod': divmod, 'oct': oct, 'hex': hex, 'chr': chr, 'ord': ord,
        'bin': bin, 'slice': slice, 'super': super, 'type': type, 'object': object,
        'Exception': Exception, 'BaseException': BaseException, 'ValueError': ValueError,
        'TypeError': TypeError, 'IndexError': IndexError, 'KeyError': KeyError,
        'ZeroDivisionError': ZeroDivisionError,
    }

    def __getitem__(self, name):
        if name in self._allowed:
            return self._allowed[name]
        raise AttributeError(f"'{name}' is not allowed")

    def __getattr__(self, name):
        if name in self._allowed:
            return self._allowed[name]
        if name.startswith('_'):
            raise AttributeError(f"'{name}' is not allowed")
        raise AttributeError(f"'{name}' is not allowed")


class RuntimeTracer:
    def __init__(self, timeout_seconds=5, max_memory_mb=50):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self._step_id = 0
        self._trace = ExecutionTrace()
        self._current_vars = {}
        self._vars_before_line = {}
        self._old_trace_func = None
        self._timeout_flag = False
        self._source_lines = {}

    def trace(self, code, inputs):
        self._step_id = 0
        self._trace = ExecutionTrace()
        self._current_vars = inputs.copy() if inputs else {}
        self._vars_before_line = self._current_vars.copy()
        self._current_frame = None
        self._timeout_flag = False

        self._source_lines = {}
        for i, line in enumerate(code.splitlines(), start=1):
            self._source_lines[i] = line.strip()

        old_trace = sys.gettrace()
        timeout_timer = None

        def set_timeout():
            self._timeout_flag = True

        try:
            sys.settrace(self._trace_func)
            restricted_builtins = SecurityRestrictedbuiltins()
            scope = {'__builtins__': restricted_builtins, **inputs}
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()

            timeout_timer = threading.Timer(self.timeout_seconds, set_timeout)
            timeout_timer.start()

            try:
                exec(code, scope)
            except Exception as e:
                if not isinstance(self._trace.exception, ErrorInfo):
                    self._trace.exception = ErrorInfo(type(e).__name__, str(e), self._trace.steps.copy())
            finally:
                if timeout_timer:
                    timeout_timer.cancel()
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        finally:
            sys.settrace(old_trace)

        for key in list(scope.keys()):
            if not key.startswith('__') and key != 'builtins':
                try:
                    self._trace.variables[key] = scope[key]
                except:
                    pass

        if inputs:
            for k, v in inputs.items():
                if k in self._trace.variables:
                    self._trace.variables[k] = v

        return self._trace

    def _trace_func(self, frame, event, arg):
        if self._timeout_flag:
            return None

        try:
            self._current_frame = frame
            code = frame.f_code
            function_name = code.co_name
            lineno = frame.f_lineno

            if event == 'call':
                self._trace.call_stack.append(function_name)
                self._vars_before_line = self._current_vars.copy()
            elif event == 'return':
                self._vars_before_line = self._current_vars.copy()
                if self._trace.call_stack:
                    self._trace.call_stack.pop()
            elif event in ('line', 'exception'):
                self._vars_before_line = self._current_vars.copy()
                line_content = self._source_lines.get(lineno, f"<line {lineno}>")

                vars_after = {}
                for key, value in frame.f_locals.items():
                    try:
                        if not callable(value) and not hasattr(value, '__code__'):
                            vars_after[key] = repr(value)
                        else:
                            vars_after[key] = f"<{type(value).__name__}>"
                    except:
                        vars_after[key] = f"<{type(value).__name__}>"

                self._current_vars = vars_after.copy()

                step = TraceStep(
                    self._step_id, lineno, line_content,
                    self._vars_before_line.copy(), vars_after.copy(),
                    event, function_name
                )
                self._trace.steps.append(step)
                self._step_id += 1

                if event == 'exception':
                    exc_type, exc_value, _ = arg
                    self._trace.exception = ErrorInfo(
                        exc_type.__name__ if exc_type else 'Exception',
                        str(exc_value) if exc_value else '',
                        self._trace.steps.copy()
                    )

            return self._trace_func

        except Exception:
            return self._trace_func


# ========== 静态分析器 ==========
class StaticAnalyzer:
    def __init__(self):
        self._code = ""
        self._tree = None
        self._structure = None
        self._func_defs = {}
        self._class_defs = {}
        self._dependencies = {}

    def analyze(self, code):
        self._code = code
        self._tree = ast.parse(code)
        self._func_defs = {}
        self._class_defs = {}
        self._dependencies = {}
        self._extract_definitions()
        self._extract_dependencies()
        self._build_structure()
        self._build_learning_path()
        return self._structure

    def _extract_definitions(self):
        for node in ast.walk(self._tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                self._func_defs[node.name] = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'end_lineno': node.end_lineno or node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': docstring
                }
                self._dependencies[node.name] = set()
            elif isinstance(node, ast.ClassDef):
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                docstring = ast.get_docstring(node)
                self._class_defs[node.name] = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'end_lineno': node.end_lineno or node.lineno,
                    'methods': methods,
                    'docstring': docstring
                }
                self._dependencies[node.name] = set()

    def _extract_dependencies(self):
        for node in ast.walk(self._tree):
            if isinstance(node, ast.FunctionDef):
                self._resolve_calls(node, node.name)
            elif isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        self._resolve_calls(method, method.name)

    def _resolve_calls(self, node, caller):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    callee = child.func.id
                    if callee in self._func_defs or callee in self._class_defs:
                        self._dependencies.setdefault(caller, set()).add(callee)
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        method_name = f"{child.func.value.id}.{child.func.attr}"
                        self._dependencies.setdefault(caller, set()).add(method_name)

    def _build_structure(self):
        functions = [FunctionInfo(**info) for info in self._func_defs.values()]
        classes = [ClassInfo(**info) for info in self._class_defs.values()]
        dependencies_dict = {name: list(deps) for name, deps in self._dependencies.items()}
        self._structure = CodeStructure(functions, classes, dependencies_dict, [], [])

    def _build_learning_path(self):
        visiting = set()
        visited = set()
        path = []

        def topological_sort(name):
            if name in visited:
                return
            if name in visiting:
                return
            visiting.add(name)
            deps = self._dependencies.get(name, set())
            for dep in sorted(deps):
                if dep in self._func_defs or dep in self._class_defs:
                    topological_sort(dep)
            visiting.remove(name)
            visited.add(name)
            if name not in path:
                path.append(name)

        for func_name in self._func_defs:
            topological_sort(func_name)
        for class_name in self._class_defs:
            if class_name not in visited:
                topological_sort(class_name)
        self._structure.learning_path = path

    def get_learning_path(self):
        learning_units = []
        lines = self._code.splitlines(keepends=True)
        for name in self._structure.learning_path:
            if name in self._func_defs:
                func = self._func_defs[name]
                content = self._get_code_snippet(func['lineno'], func['end_lineno'], lines)
                learning_units.append(LearningUnit(
                    name, "function", func['lineno'], content,
                    list(self._dependencies.get(name, set()))
                ))
            elif name in self._class_defs:
                cls = self._class_defs[name]
                content = self._get_code_snippet(cls['lineno'], cls['end_lineno'], lines)
                learning_units.append(LearningUnit(
                    name, "class", cls['lineno'], content,
                    list(self._dependencies.get(name, set()))
                ))
        return learning_units

    def _get_code_snippet(self, start_lineno, end_lineno, lines):
        if start_lineno < 1 or start_lineno > len(lines):
            return ""
        start = start_lineno - 1
        end = end_lineno if end_lineno <= len(lines) else len(lines)
        return "".join(lines[start:end]).strip()


# ========== 轨迹结构化器 ==========
class TraceStructurer:
    def __init__(self):
        self.threshold = 10

    def structure(self, raw_trace):
        compressed_steps = self.compress_loops(raw_trace, self.threshold)
        execution_path = self._build_execution_path(compressed_steps)
        key_nodes = self._identify_key_nodes(compressed_steps)
        path_summary = self._generate_path_summary(compressed_steps)
        return StructuredTrace(compressed_steps, execution_path, key_nodes, path_summary)

    def compress_loops(self, trace, threshold=10):
        if not trace.steps:
            return []
        compressed_steps = []
        i = 0
        n = len(trace.steps)
        step_id_counter = 0

        while i < n:
            current_step = trace.steps[i]
            if current_step.line == 0:
                compressed_steps.append(CompressedStep(
                    step_id_counter, current_step.line, current_step.code,
                    current_step.vars_after, "normal"
                ))
                i += 1
                step_id_counter += 1
                continue

            repeat_count = 1
            j = i + 1
            while j < n and trace.steps[j].line == current_step.line:
                repeat_count += 1
                j += 1

            if repeat_count >= threshold:
                new_step = CompressedStep(
                    step_id_counter, current_step.line, current_step.code,
                    current_step.vars_after, "loop_start", repeat_count
                )
                compressed_steps.append(new_step)
                loop_end_step = CompressedStep(
                    step_id_counter + 1, current_step.line,
                    f"  # Loop compressed: {repeat_count} iterations",
                    current_step.vars_after, "loop_end", repeat_count
                )
                compressed_steps.append(loop_end_step)
                step_id_counter += 2
            else:
                for k in range(i, j):
                    step = trace.steps[k]
                    compressed_steps.append(CompressedStep(
                        step_id_counter, step.line, step.code,
                        step.vars_after, "normal"
                    ))
                    step_id_counter += 1
            i = j

        return compressed_steps

    def _build_execution_path(self, steps):
        return [step.step_id for step in steps]

    def _identify_key_nodes(self, steps):
        key_nodes = {
            "loop_start": [], "loop_end": [], "branch": [],
            "merge": [], "call": [], "return": []
        }
        for step in steps:
            if step.node_type in key_nodes:
                key_nodes[step.node_type].append(step.step_id)
        return key_nodes

    def _generate_path_summary(self, steps):
        total_steps = len(steps)
        loop_count = sum(1 for s in steps if s.node_type in ("loop_start", "loop_end"))
        call_count = sum(1 for s in steps if s.node_type == "call")
        branch_count = sum(1 for s in steps if s.node_type == "branch")
        summary_parts = [f"Total steps: {total_steps}"]
        if loop_count > 0:
            summary_parts.append(f"Loops: {loop_count // 2}")
        if call_count > 0:
            summary_parts.append(f"Function calls: {call_count}")
        if branch_count > 0:
            summary_parts.append(f"Branches: {branch_count}")
        return ", ".join(summary_parts) if summary_parts else "No execution steps"


# ========== 解释生成器 ==========
class ExplanationGenerator:
    def __init__(self):
        self._operator_keywords = {
            '+': '加', '-': '减', '*': '乘', '/': '除',
            '==': '等于', '!=': '不等于', '>': '大于',
            '<': '小于', '>=': '大于等于', '<=': '小于等于',
            'and': '且', 'or': '或', 'not': '非'
        }

    def generate_explanation(self, trace, code):
        step_explanations = []
        variable_changes = []
        key_insights = []
        prev_variables = {}

        for i, step in enumerate(trace.compressed_steps):
            current_vars = step.vars_snapshot.copy()
            step_exp = self.explain_step(step)
            step_explanations.append(StepExplanation(
                step.step_id, step.line, step_exp, f"→ Step {step.step_id}"
            ))
            for var_name, new_val in current_vars.items():
                old_val = prev_variables.get(var_name)
                if old_val != new_val and var_name not in prev_variables:
                    reason = self._explain_value_assignment(var_name, new_val, step.code)
                    variable_changes.append(VariableChangeExplanation(var_name, None, new_val, reason))
                elif old_val != new_val:
                    reason = self.explain_variable_change(var_name, old_val, new_val, step.code)
                    variable_changes.append(VariableChangeExplanation(var_name, old_val, new_val, reason))
            prev_variables = current_vars.copy()

        summary = self._generate_summary(trace, step_explanations, key_insights)
        if not key_insights:
            key_insights = self._extract_key_insights(trace, variable_changes)

        return Explanation(summary, step_explanations, variable_changes, key_insights)

    def explain_step(self, step):
        if step.node_type == "call":
            return "调用函数"
        elif step.node_type == "branch":
            return f"条件判断: {step.code}"
        elif step.node_type in ("loop_start", "loop_end"):
            if step.node_type == "loop_start" and step.iteration_count:
                return f"循环开始，执行 {step.iteration_count} 次"
            return "循环结束"
        elif step.node_type == "return":
            return f"返回结果: {self._format_value(step.vars_snapshot)}"
        else:
            return self._explain_assignment(step)

    def _explain_assignment(self, step):
        code = step.code.strip()
        if '=' in code and '==' not in code:
            var_part = code.split('=')[0].strip()
            val_part = code.split('=')[1].strip()
            return f"将变量 {var_part} 设置为 {self._format_value(step.vars_snapshot.get(var_part, val_part))}"
        return f"执行赋值操作: {code}"

    def explain_variable_change(self, var_name, old_val, new_val, context):
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
        return f"{var_name} 从 {old_f} 更新为 {new_f}"

    def explain_branch(self, condition, result, context):
        condition_clean = self._clean_condition(condition.strip())
        if result:
            return f"条件 '{condition_clean}' 为真，执行分支代码"
        return f"条件 '{condition_clean}' 为假，跳过分支代码"

    def _clean_condition(self, condition):
        for op, cn_op in self._operator_keywords.items():
            condition = condition.replace(op, cn_op)
        return condition

    def _format_value(self, value):
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

    def _explain_value_assignment(self, var_name, value, code):
        code_lower = code.lower()
        if 'input' in code_lower:
            return f"通过用户输入获取值并赋值给 {var_name}"
        val_type = type(value).__name__
        if val_type == 'int':
            return f"将整数值 {value} 赋值给 {var_name}"
        return f"初始化变量 {var_name} 为 {self._format_value(value)}"

    def _generate_summary(self, trace, step_explanations, key_insights):
        total_steps = len(trace.compressed_steps)
        lines_executed = len(set(s.line for s in trace.compressed_steps))
        calls = sum(1 for s in trace.compressed_steps if s.node_type == "call")
        branches = sum(1 for s in trace.compressed_steps if s.node_type == "branch")
        loops = sum(1 for s in trace.compressed_steps if s.node_type in ("loop_start", "loop_end"))
        summary_parts = [f"代码共执行 {total_steps} 个步骤，涉及 {lines_executed} 行代码"]
        if loops > 0:
            summary_parts.append(f"包含 {loops // 2} 次循环")
        if calls > 0:
            summary_parts.append(f"调用 {calls} 个函数")
        if branches > 0:
            summary_parts.append(f"进行 {branches} 次条件判断")
        return "，".join(summary_parts)

    def _extract_key_insights(self, trace, variable_changes):
        insights = []
        if len(variable_changes) > 10:
            insights.append(f"代码涉及 {len(variable_changes)} 次变量变化，表明有较多的状态更新操作")
        counter_vars = [vc for vc in variable_changes if vc.var_name in ['i', 'j', 'k', 'count', 'index', 'counter']]
        if len(counter_vars) >= 3:
            insights.append("代码使用了循环迭代变量进行计数操作")
        return insights


# ========== API 处理逻辑 ==========
MAX_CODE_LENGTH = 50000
MAX_INPUTS = 10


def validate_code(code):
    if not code or not code.strip():
        raise ValueError("Code cannot be empty")
    if len(code) > MAX_CODE_LENGTH:
        raise ValueError(f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters")
    try:
        ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {str(e)}")


def validate_inputs(inputs):
    if inputs and len(inputs) > MAX_INPUTS:
        raise ValueError(f"Too many inputs (max {MAX_INPUTS})")


def handle_analyze(code, inputs=None):
    validate_code(code)
    inputs = inputs or {}
    validate_inputs(inputs)

    analyzer = StaticAnalyzer()
    code_structure = analyzer.analyze(code)
    learning_units = analyzer.get_learning_path()
    code_structure.learning_units = learning_units

    tracer = RuntimeTracer()
    trace = tracer.trace(code, inputs)

    structurer = TraceStructurer()
    structured_trace = structurer.structure(trace)

    explainer = ExplanationGenerator()
    explanation = explainer.generate_explanation(structured_trace, code)

    return {
        "code_structure": code_structure.to_dict(),
        "trace": trace.to_dict(),
        "structured_trace": structured_trace.to_dict(),
        "explanation": explanation.to_dict()
    }


def handle_generate_course(code, inputs=None):
    validate_code(code)
    inputs = inputs or {}
    validate_inputs(inputs)

    analyzer = StaticAnalyzer()
    code_structure = analyzer.analyze(code)
    learning_units = analyzer.get_learning_path()

    tracer = RuntimeTracer()
    structurer = TraceStructurer()
    explainer = ExplanationGenerator()

    lessons = []
    for i, unit in enumerate(learning_units):
        try:
            trace = tracer.trace(unit.content, inputs)
            structured_trace = structurer.structure(trace)
            exp = explainer.generate_explanation(structured_trace, unit.content)
            lesson = Lesson(
                i + 1, f"Lesson {i + 1}: {unit.name}",
                unit.type, unit.content, exp, structured_trace, exp.key_insights
            )
        except Exception as e:
            empty_exp = Explanation(
                f"无法执行此代码单元: {str(e)}", [], [], []
            )
            lesson = Lesson(
                i + 1, f"Lesson {i + 1}: {unit.name}",
                unit.type, unit.content, empty_exp, None, []
            )
        lessons.append(lesson)

    total_steps = sum(len(l.trace.compressed_steps) for l in lessons if l.trace)
    course = Course("代码学习课程", f"共 {len(lessons)} 个学习单元", lessons, total_steps)

    return {"course": course.to_dict()}


def handle_compare_paths(code, inputs_list):
    validate_code(code)
    if not inputs_list:
        raise ValueError("inputs_list cannot be empty")
    if len(inputs_list) > MAX_INPUTS:
        raise ValueError(f"Too many inputs (max {MAX_INPUTS})")
    for inputs in inputs_list:
        validate_inputs(inputs)

    tracer = RuntimeTracer()
    structurer = TraceStructurer()
    results = []

    for inputs in inputs_list:
        try:
            trace = tracer.trace(code, inputs)
            structured_trace = structurer.structure(trace)
            results.append({
                "inputs": inputs,
                "path": structured_trace.execution_path,
                "steps": [s.to_dict() for s in structured_trace.compressed_steps]
            })
        except Exception as e:
            results.append({
                "inputs": inputs, "path": [], "steps": [], "error": str(e)
            })

    diff_results = []
    if len(results) >= 2:
        for i in range(len(results) - 1):
            result_a = results[i]
            result_b = results[i + 1]
            if "error" in result_a or "error" in result_b:
                continue
            path_a = set(result_a["path"])
            path_b = set(result_b["path"])
            diff_points = []
            all_steps = set(result_a["path"] + result_b["path"])

            for step_id in all_steps:
                if step_id in path_a and step_id not in path_b:
                    diff_points.append({
                        "step_id": step_id, "type": "only_a",
                        "code": _get_step_code(result_a, step_id)
                    })
                elif step_id not in path_a and step_id in path_b:
                    diff_points.append({
                        "step_id": step_id, "type": "only_b",
                        "code": _get_step_code(result_b, step_id)
                    })

            diff_results.append(PathDiffResult(
                result_a["inputs"], result_b["inputs"],
                result_a["path"], result_b["path"], diff_points
            ).to_dict())

    return {"results": diff_results}


def _get_step_code(result, step_id):
    if "steps" in result:
        for step in result["steps"]:
            if step["step_id"] == step_id:
                return step["code"]
    return ""


# ========== HTTP 服务器 ==========
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html')
        elif self.path.startswith('/static/'):
            filename = self.path[len('/static/'):]
            self.serve_file(filename)
        elif self.path == '/health':
            self.send_json({"status": "healthy"})
        else:
            self.serve_file(self.path.lstrip('/'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            self.send_error(400, "Invalid JSON")
            return

        try:
            if self.path == '/api/analyze':
                result = handle_analyze(data.get('code', ''), data.get('inputs', {}))
                self.send_json(result)
            elif self.path == '/api/generate-course':
                result = handle_generate_course(data.get('code', ''), data.get('inputs', {}))
                self.send_json(result)
            elif self.path == '/api/compare-paths':
                result = handle_compare_paths(data.get('code', ''), data.get('inputs_list', []))
                self.send_json(result)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(400, str(e))

    def serve_file(self, filename):
        if filename == '':
            filename = 'index.html'
        filepath = os.path.join(os.path.dirname(__file__), 'frontend', filename)

        if os.path.exists(filepath):
            self.send_response(200)
            if filename.endswith('.html'):
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            elif filename.endswith('.css'):
                self.send_header('Content-Type', 'text/css; charset=utf-8')
            elif filename.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.end_headers()
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({"detail": message}, ensure_ascii=False).encode('utf-8'))


def main():
    PORT = 8000
    Handler = RequestHandler
    os.chdir(os.path.dirname(__file__))

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"CodeTrace 轻量级服务器启动在 http://localhost:{PORT}")
        print("按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器停止")
            httpd.shutdown()


if __name__ == "__main__":
    main()
