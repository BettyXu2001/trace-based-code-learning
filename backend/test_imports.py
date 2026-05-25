import sys
sys.path.insert(0, '.')

print("Testing imports...")

try:
    from app.services.analyzer import StaticAnalyzer
    print('analyzer OK')
except Exception as e:
    print(f'analyzer ERROR: {e}')

try:
    from app.services.tracer import RuntimeTracer
    print('tracer OK')
except Exception as e:
    print(f'tracer ERROR: {e}')

try:
    from app.services.structurer import TraceStructurer
    print('structurer OK')
except Exception as e:
    print(f'structurer ERROR: {e}')

try:
    from app.services.explainer import ExplanationGenerator
    print('explainer OK')
except Exception as e:
    print(f'explainer ERROR: {e}')

try:
    from app.services.orchestrator import CodeAnalysisOrchestrator
    print('orchestrator OK')
except Exception as e:
    print(f'orchestrator ERROR: {e}')

try:
    from app.models.schemas import AnalyzeRequest
    print('schemas OK')
except Exception as e:
    print(f'schemas ERROR: {e}')

try:
    from app.main import app
    print('main app OK')
except Exception as e:
    print(f'main app ERROR: {e}')

print("\n--- Testing StaticAnalyzer ---")
try:
    code = '''
def add(a, b):
    return a + b
result = add(1, 2)
'''
    analyzer = StaticAnalyzer()
    structure = analyzer.analyze(code)
    print(f"Functions found: {[f.name for f in structure.functions]}")
    print("StaticAnalyzer test PASSED")
except Exception as e:
    print(f"StaticAnalyzer test FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Testing CodeAnalysisOrchestrator ---")
try:
    code = '''
def add(a, b):
    return a + b
result = add(1, 2)
'''
    orchestrator = CodeAnalysisOrchestrator()
    result = orchestrator.analyze_full_code(code, {})
    print(f"Code structure functions: {[f.name for f in result.code_structure.functions]}")
    print(f"Structured trace steps: {len(result.structured_trace.compressed_steps)}")
    print(f"Explanation summary: {result.explanation.summary[:50]}...")
    print("CodeAnalysisOrchestrator test PASSED")
except Exception as e:
    print(f"CodeAnalysisOrchestrator test FAILED: {e}")
    import traceback
    traceback.print_exc()