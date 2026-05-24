from backend.app.services.analyzer import StaticAnalyzer

code = '''
def greet(name):
    return f"Hello, {name}!"

def calculate(x, y):
    return x + y

def main():
    result = calculate(1, 2)
    message = greet("World")
    return result

class Calculator:
    def add(self, a, b):
        return a + b
'''

analyzer = StaticAnalyzer()
structure = analyzer.analyze(code)

print("Functions:")
for f in structure.functions:
    print(f"  {f.name}: line {f.lineno}, args={f.args}")

print("\nClasses:")
for c in structure.classes:
    print(f"  {c.name}: line {c.lineno}, methods={c.methods}")

print("\nDependencies:", structure.dependencies)
print("Learning Path:", structure.learning_path)

units = analyzer.get_learning_path()
print("\nLearning Units:")
for u in units:
    print(f"  {u.type}: {u.name}, depends_on={u.depends_on}")
