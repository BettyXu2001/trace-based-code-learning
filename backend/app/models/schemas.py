from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Request models
class AnalyzeRequest(BaseModel):
    code: str
    inputs: Optional[Dict[str, Any]] = {}

class CourseRequest(BaseModel):
    code: str
    inputs: Optional[Dict[str, Any]] = {}
    mode: Optional[str] = "basic"  # basic, error_injection, path_diff, concept

class PathCompareRequest(BaseModel):
    code: str
    inputs_list: List[Dict[str, Any]]

# Response models
class FunctionInfo(BaseModel):
    name: str
    lineno: int
    end_lineno: int
    args: List[str]
    docstring: Optional[str]


class ClassInfo(BaseModel):
    name: str
    lineno: int
    end_lineno: int
    methods: List[str]
    docstring: Optional[str]

class LearningUnit(BaseModel):
    name: str
    type: str
    lineno: int
    content: str
    depends_on: List[str]

class CodeStructure(BaseModel):
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    dependencies: Dict[str, List[str]]
    learning_path: List[str]
    learning_units: List[LearningUnit] = []

class TraceStep(BaseModel):
    step_id: int
    line: int
    code: str
    vars_before: Dict[str, Any]
    vars_after: Dict[str, Any]
    event: str
    function_name: str

class ErrorInfo(BaseModel):
    type: str
    message: str
    traceback: List[TraceStep]

class ExecutionTrace(BaseModel):
    steps: List[TraceStep] = []
    variables: Dict[str, Any] = {}
    call_stack: List[str] = []
    exception: Optional[ErrorInfo] = None

class CompressedStep(BaseModel):
    step_id: int
    line: int
    code: str
    vars_snapshot: Dict[str, Any]
    node_type: str  # normal/loop_start/loop_end/branch/merge/call/return
    iteration_count: Optional[int] = None
    branch_taken: Optional[str] = None

class StructuredTrace(BaseModel):
    compressed_steps: List[CompressedStep] = []
    execution_path: List[int] = []
    key_nodes: Dict[str, List[int]] = {}
    path_summary: str = ""

class StepExplanation(BaseModel):
    step_id: int
    line: int
    explanation: str
    citation: str

class VariableChangeExplanation(BaseModel):
    var_name: str
    old_value: Any
    new_value: Any
    reason: str

class Explanation(BaseModel):
    summary: str
    step_explanations: List[StepExplanation]
    variable_changes: List[VariableChangeExplanation]
    key_insights: List[str]

class Lesson(BaseModel):
    id: int
    title: str
    type: str  # function/class/concept
    content: str  # code snippet
    explanation: Explanation
    trace: Optional[StructuredTrace]
    key_insights: List[str]

class Course(BaseModel):
    title: str
    description: str
    lessons: List[Lesson]
    total_steps: int

class PathDiffResult(BaseModel):
    input_a: Dict[str, Any]
    input_b: Dict[str, Any]
    path_a: List[int]
    path_b: List[int]
    diff_points: List[Dict[str, Any]]  # {step_id, line, code, type}

class AnalyzeResponse(BaseModel):
    code_structure: CodeStructure
    trace: ExecutionTrace
    structured_trace: StructuredTrace
    explanation: Explanation

class CourseResponse(BaseModel):
    course: Course

class PathCompareResponse(BaseModel):
    results: List[PathDiffResult]

class ErrorResponse(BaseModel):
    detail: str
