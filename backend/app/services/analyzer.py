import ast
from ast import AST
from typing import List, Dict, Set, Optional

from app.models.schemas import (
    FunctionInfo as PydanticFunctionInfo,
    ClassInfo as PydanticClassInfo,
    LearningUnit as PydanticLearningUnit,
    CodeStructure as PydanticCodeStructure
)


class StaticAnalyzer:
    def __init__(self):
        self._code: str = ""
        self._tree: Optional[AST] = None
        self._structure: Optional[PydanticCodeStructure] = None
        self._func_defs: Dict[str, Dict] = {}
        self._class_defs: Dict[str, Dict] = {}
        self._dependencies: Dict[str, Set[str]] = {}

    def analyze(self, code: str) -> PydanticCodeStructure:
        """分析代码并返回结构信息"""
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

    def _extract_definitions(self) -> None:
        """提取函数和类定义"""
        for node in ast.walk(self._tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                func_info = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'end_lineno': node.end_lineno or node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': docstring
                }
                self._func_defs[node.name] = func_info
                self._dependencies[node.name] = set()

            elif isinstance(node, ast.ClassDef):
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                docstring = ast.get_docstring(node)
                class_info = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'end_lineno': node.end_lineno or node.lineno,
                    'methods': methods,
                    'docstring': docstring
                }
                self._class_defs[node.name] = class_info
                self._dependencies[node.name] = set()

    def _extract_dependencies(self) -> None:
        """提取函数调用依赖关系"""
        for node in ast.walk(self._tree):
            if isinstance(node, ast.FunctionDef):
                caller = node.name
                self._resolve_calls(node, caller)

            elif isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        caller = method.name
                        self._resolve_calls(method, caller)

    def _resolve_calls(self, node: AST, caller: str) -> None:
        """解析函数调用"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    callee = child.func.id
                    if callee in self._func_defs or callee in self._class_defs:
                        if caller in self._dependencies:
                            self._dependencies[caller].add(callee)
                        else:
                            self._dependencies[caller] = {callee}
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        method_name = f"{child.func.value.id}.{child.func.attr}"
                        if caller in self._dependencies:
                            self._dependencies[caller].add(method_name)
                        else:
                            self._dependencies[caller] = {method_name}

    def _build_structure(self) -> None:
        """构建代码结构"""
        dependencies_dict = {
            name: list(deps) for name, deps in self._dependencies.items()
        }
        
        functions = [
            PydanticFunctionInfo(**info) for info in self._func_defs.values()
        ]
        classes = [
            PydanticClassInfo(**info) for info in self._class_defs.values()
        ]

        self._structure = PydanticCodeStructure(
            functions=functions,
            classes=classes,
            dependencies=dependencies_dict,
            learning_path=[]
        )

    def _build_learning_path(self) -> None:
        """基于依赖关系构建学习路径（从简单到复杂），带循环检测"""
        if self._structure is None:
            return

        # Track cycle detection: 'visiting' = in current DFS path, 'visited' = done
        visiting: Set[str] = set()
        visited: Set[str] = set()
        path: List[str] = []
        cycles: List[List[str]] = []

        def topological_sort(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                # Cycle detected - record it but don't recurse further
                cycles.append([name])
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

        # Store cycle info for later use if needed
        if cycles:
            self._cycles = cycles

    def get_learning_path(self) -> List[PydanticLearningUnit]:
        """获取排序后的学习单元列表"""
        if self._structure is None:
            return []

        learning_units: List[PydanticLearningUnit] = []
        lines = self._code.splitlines(keepends=True)

        for name in self._structure.learning_path:
            if name in self._func_defs:
                func = self._func_defs[name]
                content = self._get_code_snippet(func['lineno'], func['end_lineno'], lines)
                unit = PydanticLearningUnit(
                    name=name,
                    type="function",
                    lineno=func['lineno'],
                    content=content,
                    depends_on=list(self._dependencies.get(name, set()))
                )
                learning_units.append(unit)

            elif name in self._class_defs:
                cls = self._class_defs[name]
                content = self._get_code_snippet(cls['lineno'], cls['end_lineno'], lines)
                unit = PydanticLearningUnit(
                    name=name,
                    type="class",
                    lineno=cls['lineno'],
                    content=content,
                    depends_on=list(self._dependencies.get(name, set()))
                )
                learning_units.append(unit)

        return learning_units

    def _get_code_snippet(self, start_lineno: int, end_lineno: int, lines: List[str]) -> str:
        """获取指定行的代码片段，使用 AST 的 end_lineno"""
        if start_lineno < 1 or start_lineno > len(lines):
            return ""

        start = start_lineno - 1
        end = end_lineno

        if end < start or end > len(lines):
            end = len(lines)

        snippet = "".join(lines[start:end])
        return snippet.strip()
