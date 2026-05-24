import ast
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AnalyzeRequest, AnalyzeResponse, CourseRequest, CourseResponse,
    PathCompareRequest, PathCompareResponse, Lesson, Course, PathDiffResult,
    Explanation, ErrorResponse
)
from app.services.analyzer import StaticAnalyzer
from app.services.tracer import RuntimeTracer
from app.services.structurer import TraceStructurer
from app.services.explainer import ExplanationGenerator

router = APIRouter()

MAX_CODE_LENGTH = 50000  # 50KB max
MAX_INPUTS = 10

def validate_code(code: str) -> None:
    """Validate code input"""
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(code) > MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail=f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters")
    # Try to parse the code to validate syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Syntax error: {str(e)}")

def validate_inputs(inputs: dict) -> None:
    """Validate inputs dictionary"""
    if inputs and len(inputs) > MAX_INPUTS:
        raise HTTPException(status_code=400, detail=f"Too many inputs (max {MAX_INPUTS})")

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    """分析代码并返回执行轨迹和解释"""
    validate_code(request.code)
    validate_inputs(request.inputs)

    try:
        # 静态分析
        analyzer = StaticAnalyzer()
        code_structure = analyzer.analyze(request.code)
        learning_units = analyzer.get_learning_path()
        code_structure.learning_units = learning_units

        # 动态执行
        tracer = RuntimeTracer()
        trace = tracer.trace(request.code, request.inputs)

        # 轨迹压缩
        structurer = TraceStructurer()
        structured_trace = structurer.structure(trace)

        # 生成解释
        explainer = ExplanationGenerator()
        explanation = explainer.generate_explanation(structured_trace, request.code)

        return AnalyzeResponse(
            code_structure=code_structure,
            trace=trace,
            structured_trace=structured_trace,
            explanation=explanation
        )
    except HTTPException:
        raise
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Syntax error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest):
    """生成完整的代码学习课程"""
    validate_code(request.code)
    validate_inputs(request.inputs)

    try:
        # 静态分析
        analyzer = StaticAnalyzer()
        code_structure = analyzer.analyze(request.code)
        learning_units = analyzer.get_learning_path()

        tracer = RuntimeTracer()
        structurer = TraceStructurer()
        explainer = ExplanationGenerator()

        lessons = []
        for i, unit in enumerate(learning_units):
            # 获取该单元的代码片段
            unit_code = unit.content

            try:
                # 执行并追踪
                trace = tracer.trace(unit_code, request.inputs)
                structured_trace = structurer.structure(trace)
                explanation = explainer.generate_explanation(structured_trace, unit_code)

                lesson = Lesson(
                    id=i + 1,
                    title=f"Lesson {i+1}: {unit.name}",
                    type=unit.type,
                    content=unit_code,
                    explanation=explanation,
                    trace=structured_trace,
                    key_insights=explanation.key_insights
                )
            except Exception as e:
                # 如果某个单元执行失败，仍创建lesson但不含trace
                lesson = Lesson(
                    id=i + 1,
                    title=f"Lesson {i+1}: {unit.name}",
                    type=unit.type,
                    content=unit_code,
                    explanation=Explanation(
                        summary=f"无法执行此代码单元: {str(e)}",
                        step_explanations=[],
                        variable_changes=[],
                        key_insights=[]
                    ),
                    trace=None,
                    key_insights=[]
                )
            lessons.append(lesson)

        total_steps = 0
        for l in lessons:
            if l.trace:
                total_steps += len(l.trace.compressed_steps)

        course = Course(
            title="代码学习课程",
            description=f"共 {len(lessons)} 个学习单元",
            lessons=lessons,
            total_steps=total_steps
        )

        return CourseResponse(course=course)
    except HTTPException:
        raise
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Syntax error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course generation failed: {str(e)}")

@router.post("/compare-paths", response_model=PathCompareResponse)
async def compare_paths(request: PathCompareRequest):
    """对比不同输入的执行路径差异"""
    validate_code(request.code)

    if not request.inputs_list:
        raise HTTPException(status_code=400, detail="inputs_list cannot be empty")

    if len(request.inputs_list) > MAX_INPUTS:
        raise HTTPException(status_code=400, detail=f"Too many inputs (max {MAX_INPUTS})")

    for inputs in request.inputs_list:
        validate_inputs(inputs)

    try:
        tracer = RuntimeTracer()
        structurer = TraceStructurer()

        results = []
        for inputs in request.inputs_list:
            try:
                trace = tracer.trace(request.code, inputs)
                structured_trace = structurer.structure(trace)
                results.append({
                    "inputs": inputs,
                    "path": structured_trace.execution_path,
                    "steps": structured_trace.compressed_steps
                })
            except Exception as e:
                results.append({
                    "inputs": inputs,
                    "path": [],
                    "steps": [],
                    "error": str(e)
                })

        # 分析路径差异
        diff_results = []
        if len(results) >= 2:
            for i in range(len(results) - 1):
                result_a = results[i]
                result_b = results[i + 1]

                if "error" in result_a or "error" in result_b:
                    continue

                path_a = set(result_a["path"])
                path_b = set(result_b["path"])

                # 找到分歧点
                diff_points = []
                all_steps = set(result_a["path"] + result_b["path"])

                for step_id in all_steps:
                    if step_id in path_a and step_id not in path_b:
                        diff_points.append({
                            "step_id": step_id,
                            "type": "only_a",
                            "code": _get_step_code(result_a, step_id)
                        })
                    elif step_id not in path_a and step_id in path_b:
                        diff_points.append({
                            "step_id": step_id,
                            "type": "only_b",
                            "code": _get_step_code(result_b, step_id)
                        })

                diff_results.append(PathDiffResult(
                    input_a=result_a["inputs"],
                    input_b=result_b["inputs"],
                    path_a=result_a["path"],
                    path_b=result_b["path"],
                    diff_points=diff_points
                ))

        return PathCompareResponse(results=diff_results)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Path comparison failed: {str(e)}")

def _get_step_code(result, step_id):
    """获取指定步骤的代码"""
    if "steps" in result:
        for step in result["steps"]:
            if step.step_id == step_id:
                return step.code
    return ""
