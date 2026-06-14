import { useState, useEffect } from 'react';
import { CodeEditor } from './components/CodeEditor';
import { VariablePanel } from './components/VariablePanel';
import { ExecutionTimeline } from './components/ExecutionTimeline';
import { ExplanationPanel } from './components/ExplanationPanel';
import { analyzeCode } from './api';
import type { AnalyzeResponse, Course } from './types';

// 示例代码
const EXAMPLE_CODE = `# 示例：斐波那契数列计算
def fibonacci(n):
    """计算第n个斐波那契数"""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    
    return b

# 计算前10个斐波那契数
results = []
for i in range(10):
    fib_num = fibonacci(i)
    results.append(fib_num)

print(f"斐波那契数列: {results}")

# 示例2：简单计算
x = 10
y = 20
sum_val = x + y
product = x * y
print(f"和: {sum_val}, 积: {product}")`;

const DEFAULT_CODE = `# Python 代码示例
def find_max(numbers):
    """找出列表中的最大值"""
    if not numbers:
        return None
    
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

# 测试
result = find_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"最大值: {result}")
`;

function App() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Analysis results
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null);
  const [course] = useState<Course | null>(null);

  // UI state
  const [currentLessonId] = useState(1);
  const [currentStepId, setCurrentStepId] = useState(0);

  // Theme state
  const [theme, setTheme] = useState<'light' | 'dark' | 'blue' | 'green'>('light');

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'blue' | 'green';
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    }
  }, []);

  // Change theme
  const changeTheme = (newTheme: 'light' | 'dark' | 'blue' | 'green') => {
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  // Load example code
  const loadExample = () => {
    setCode(EXAMPLE_CODE);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCode(code, {});
      setAnalyzeResult(result);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const currentLesson = course?.lessons.find(l => l.id === currentLessonId);
  const currentTrace = currentLesson?.trace;
  const currentExplanation = currentLesson?.explanation || analyzeResult?.explanation;
  const currentSteps = currentTrace?.compressed_steps || analyzeResult?.structured_trace?.compressed_steps || [];

  const currentStepData = currentSteps.find(s => s.step_id === currentStepId);
  const prevStepData = currentSteps.find(s => s.step_id === currentStepId - 1);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>CodeTrace</h1>
          <span className="header-title">代码分析工具平台</span>
        </div>
        <div className="header-right">
          <button className="header-btn" title="搜索">🔍</button>
          <select
            className="theme-select"
            value={theme}
            onChange={(e) => changeTheme(e.target.value as 'light' | 'dark' | 'blue' | 'green')}
          >
            <option value="light">浅色主题</option>
            <option value="dark">深色主题</option>
            <option value="blue">蓝色主题</option>
            <option value="green">绿色主题</option>
          </select>
        </div>
      </header>

      <div className="toolbar">
        <button onClick={loadExample} className="example-btn">
          📚 示例
        </button>
        <input
          type="text"
          placeholder="请输入代码片段..."
          className="code-input"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <button onClick={handleAnalyze} disabled={loading} className="run-btn">
          {loading ? '运行中...' : '运行'}
        </button>
        <button onClick={() => setCode(DEFAULT_CODE)} className="reset-btn">
          重置
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="main-content">
        {/* Left Column: Code Editor + Results */}
        <div className="left-column">
          <div className="panel code-panel">
            <div className="panel-header">
              <div className="panel-tabs">
                <button className="tab active">编译</button>
                <button className="tab">控制台</button>
                <button className="tab">依赖包</button>
              </div>
              <div className="panel-actions">
                <button className="action-btn">...</button>
              </div>
            </div>
            <CodeEditor
              code={code}
              onChange={setCode}
              highlightedLine={currentStepData?.line}
            />
          </div>

          <div className="panel results-panel">
            <div className="panel-header">
              <h3>结果展示</h3>
              <div className="panel-actions">
                <button className="action-btn">📊</button>
                <button className="action-btn">📈</button>
                <button className="action-btn">📉</button>
                <button className="action-btn">...</button>
              </div>
            </div>
            <ExecutionTimeline
              steps={currentSteps}
              currentStep={currentStepId}
              onStepClick={setCurrentStepId}
            />
          </div>
        </div>

        {/* Right Column: Explanation + Variables */}
        <div className="right-column">
          <div className="panel explanation-panel">
            <div className="panel-header">
              <h3>执行解释</h3>
              <div className="panel-actions">
                <button className="action-btn">▼</button>
              </div>
            </div>
            <ExplanationPanel
              explanation={currentExplanation || {
                summary: '点击"运行"开始分析代码',
                step_explanations: [],
                variable_changes: [],
                key_insights: []
              }}
              currentStep={currentStepId}
            />
          </div>

          <div className="panel variables-panel">
            <div className="panel-header">
              <h3>变量状态</h3>
              <div className="panel-actions">
                <button className="action-btn">▼</button>
              </div>
            </div>
            <VariablePanel
              variables={currentStepData?.vars_snapshot || {}}
              prevVariables={prevStepData?.vars_snapshot}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
