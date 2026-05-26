
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.analyzer import StaticAnalyzer
from app.services.tracer import RuntimeTracer
from app.services.structurer import TraceStructurer
from app.services.explainer import ExplanationGenerator

# 测试静态分析
print("=" * 50)
print("测试静态分析...")
code = '''
def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num &gt; max_val:
            max_val = num
    return max_val

result = find_max([3, 1, 4, 1, 5])
print(f"最大值: {result}")
'''

analyzer = StaticAnalyzer()
structure = analyzer.analyze(code)
print(f"✓ 静态分析成功！")
print(f"  发现 {len(structure.functions)} 个函数")

# 测试运行时追踪
print("\n" + "=" * 50)
print("测试运行时追踪...")
tracer = RuntimeTracer()
trace = tracer.trace(code, {})
print(f"✓ 运行时追踪成功！")
print(f"  记录了 {len(trace.steps)} 个步骤")

# 测试轨迹结构化
print("\n" + "=" * 50)
print("测试轨迹结构化...")
structurer = TraceStructurer()
structured_trace = structurer.structure(trace)
print(f"✓ 轨迹结构化成功！")
print(f"  压缩后有 {len(structured_trace.compressed_steps)} 个步骤")

# 测试解释生成
print("\n" + "=" * 50)
print("测试解释生成...")
explainer = ExplanationGenerator()
explanation = explainer.generate_explanation(structured_trace, code)
print(f"✓ 解释生成成功！")
print(f"  生成了 {len(explanation.step_explanations)} 个步骤解释")
print(f"  摘要: {explanation.summary}")

print("\n" + "=" * 50)
print("✅ 所有测试通过！项目无需大模型 API 即可运行！")
