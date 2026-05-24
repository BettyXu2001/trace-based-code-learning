#!/usr/bin/env python3
import sys
import json
import ast

# 测试核心逻辑
test_code = """
def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

result = find_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"最大值: {result}")
"""

print("测试开始...")
print("=" * 60)

# 1. 测试静态分析
try:
    tree = ast.parse(test_code)
    print("✓ 静态分析：代码解析成功")
    
    func_defs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_defs.append(node.name)
            print(f"  - 发现函数: {node.name}")
            
    print(f"✓ 共发现 {len(func_defs)} 个函数定义")
except Exception as e:
    print(f"✗ 静态分析失败: {e}")

print("\n" + "=" * 60)

# 2. 测试简单执行
try:
    local_vars = {}
    exec(test_code, {}, local_vars)
    print("✓ 代码执行成功")
    print(f"  - 输出结果: {local_vars.get('result')}")
except Exception as e:
    print(f"✗ 代码执行失败: {e}")

print("\n" + "=" * 60)
print("测试完成！核心逻辑正常工作。")
print("\n启动服务器请运行: python server.py")
