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

# 简单计算
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
print(f"最大值: {result}")`;

// 状态管理
let currentState = {
    code: DEFAULT_CODE,
    inputs: {},
    analyzeResult: null,
    currentStepId: 0,
    loading: false
};

// DOM 元素
const elements = {
    codeEditor: document.getElementById('codeEditor'),
    lineNumbers: document.getElementById('lineNumbers'),
    runBtn: document.getElementById('runBtn'),
    resetBtn: document.getElementById('resetBtn'),
    loadExample: document.getElementById('loadExample'),
    errorMessage: document.getElementById('errorMessage'),
    timelineContainer: document.getElementById('timelineContainer'),
    explanationContent: document.getElementById('explanationContent'),
    variablesContent: document.getElementById('variablesContent'),
    themeSelect: document.getElementById('themeSelect'),
    settingsBtn: document.getElementById('settingsBtn'),
    settingsPanel: document.getElementById('settingsPanel'),
    settingsClose: document.getElementById('settingsClose'),
    saveSettings: document.getElementById('saveSettings'),
    cancelSettings: document.getElementById('cancelSettings')
};

// 初始化
function init() {
    elements.codeEditor.value = currentState.code;
    updateLineNumbers();
    loadSettings();
    setupEventListeners();
}

// 设置事件监听器
function setupEventListeners() {
    elements.codeEditor.addEventListener('input', handleCodeChange);
    elements.codeEditor.addEventListener('scroll', syncScroll);
    elements.runBtn.addEventListener('click', handleRun);
    elements.resetBtn.addEventListener('click', handleReset);
    elements.loadExample.addEventListener('click', handleLoadExample);
    elements.themeSelect.addEventListener('change', handleThemeChange);
    elements.settingsBtn.addEventListener('click', () => {
        elements.settingsPanel.style.display = 'flex';
    });
    elements.settingsClose.addEventListener('click', () => {
        elements.settingsPanel.style.display = 'none';
    });
    elements.saveSettings.addEventListener('click', handleSaveSettings);
    elements.cancelSettings.addEventListener('click', () => {
        elements.settingsPanel.style.display = 'none';
    });
    elements.settingsPanel.addEventListener('click', (e) => {
        if (e.target === elements.settingsPanel) {
            elements.settingsPanel.style.display = 'none';
        }
    });
}

// 处理代码变化
function handleCodeChange() {
    currentState.code = elements.codeEditor.value;
    updateLineNumbers();
}

// 更新行号
function updateLineNumbers() {
    const lines = currentState.code.split('\n');
    let lineNumbersHtml = '';
    for (let i = 1; i <= lines.length; i++) {
        lineNumbersHtml += i + '\n';
    }
    elements.lineNumbers.textContent = lineNumbersHtml;
}

// 同步滚动
function syncScroll() {
    elements.lineNumbers.scrollTop = elements.codeEditor.scrollTop;
}

// 处理主题变化
function handleThemeChange(e) {
    const theme = e.target.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// 加载设置
function loadSettings() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        elements.themeSelect.value = savedTheme;
    }
    
    const savedAiProvider = localStorage.getItem('aiProvider');
    const savedApiKey = localStorage.getItem('aiApiKey');
    const savedModel = localStorage.getItem('aiModel');
    
    if (savedAiProvider) document.getElementById('aiProvider').value = savedAiProvider;
    if (savedApiKey) document.getElementById('apiKey').value = savedApiKey;
    if (savedModel) document.getElementById('model').value = savedModel;
}

// 保存设置
function handleSaveSettings() {
    localStorage.setItem('aiProvider', document.getElementById('aiProvider').value);
    localStorage.setItem('aiApiKey', document.getElementById('apiKey').value);
    localStorage.setItem('aiModel', document.getElementById('model').value);
    elements.settingsPanel.style.display = 'none';
}

// 加载示例
function handleLoadExample() {
    currentState.code = EXAMPLE_CODE;
    elements.codeEditor.value = currentState.code;
    updateLineNumbers();
}

// 重置
function handleReset() {
    currentState.code = DEFAULT_CODE;
    elements.codeEditor.value = currentState.code;
    updateLineNumbers();
    clearResults();
}

// 清除结果
function clearResults() {
    currentState.analyzeResult = null;
    currentState.currentStepId = 0;
    elements.timelineContainer.innerHTML = '';
    elements.explanationContent.innerHTML = '<p class="placeholder">点击"运行"开始分析代码</p>';
    elements.variablesContent.innerHTML = '<p class="placeholder">变量将在此显示</p>';
    elements.errorMessage.style.display = 'none';
}

// 显示错误
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.style.display = 'block';
}

// 运行分析
async function handleRun() {
    if (currentState.loading) return;
    
    currentState.loading = true;
    elements.runBtn.disabled = true;
    elements.runBtn.textContent = '运行中...';
    elements.errorMessage.style.display = 'none';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: currentState.code,
                inputs: currentState.inputs
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '分析失败');
        }
        
        const result = await response.json();
        currentState.analyzeResult = result;
        currentState.currentStepId = 0;
        renderResults();
    } catch (error) {
        showError(error.message);
        console.error(error);
    } finally {
        currentState.loading = false;
        elements.runBtn.disabled = false;
        elements.runBtn.textContent = '运行';
    }
}

// 渲染结果
function renderResults() {
    if (!currentState.analyzeResult) return;
    
    renderTimeline();
    renderExplanation();
    renderVariables();
}

// 渲染时间轴
function renderTimeline() {
    const { structured_trace } = currentState.analyzeResult;
    const steps = structured_trace.compressed_steps;
    
    let html = '';
    steps.forEach((step, index) => {
        const isActive = index === currentState.currentStepId;
        html += `
            <div class="timeline-step ${isActive ? 'active' : ''}" data-step-id="${step.step_id}" onclick="selectStep(${index})">
                <div class="step-number">${step.step_id + 1}</div>
                <div class="step-content">
                    <div class="step-line">第 ${step.line} 行</div>
                    <div class="step-code">${escapeHtml(step.code)}</div>
                </div>
            </div>
        `;
    });
    
    elements.timelineContainer.innerHTML = html;
}

// 选择步骤
function selectStep(stepIndex) {
    currentState.currentStepId = stepIndex;
    renderTimeline();
    renderExplanation();
    renderVariables();
}

// 渲染解释
function renderExplanation() {
    const { explanation } = currentState.analyzeResult;
    const { structured_trace } = currentState.analyzeResult;
    const currentStepData = structured_trace.compressed_steps[currentState.currentStepId];
    
    let html = `
        <div class="explanation-summary">
            ${escapeHtml(explanation.summary)}
        </div>
        <div class="explanation-steps">
    `;
    
    explanation.step_explanations.forEach((stepExp, index) => {
        const isActive = index === currentState.currentStepId;
        html += `
            <div class="explanation-step ${isActive ? 'active' : ''}" onclick="selectStep(${index})">
                <div class="step-explanation-text">
                    <strong>步骤 ${stepExp.step_id + 1}:</strong> ${escapeHtml(stepExp.explanation)}
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    if (explanation.key_insights && explanation.key_insights.length > 0) {
        html += `
            <div class="key-insights">
                <h4>关键洞察</h4>
                ${explanation.key_insights.map(insight => `
                    <div class="insight-item">💡 ${escapeHtml(insight)}</div>
                `).join('')}
            </div>
        `;
    }
    
    elements.explanationContent.innerHTML = html;
}

// 渲染变量
function renderVariables() {
    const { structured_trace } = currentState.analyzeResult;
    const currentStepData = structured_trace.compressed_steps[currentState.currentStepId];
    
    if (!currentStepData || !currentStepData.vars_snapshot) {
        elements.variablesContent.innerHTML = '<p class="placeholder">没有变量数据</p>';
        return;
    }
    
    let html = '<div class="variables-grid">';
    
    for (const [varName, varValue] of Object.entries(currentStepData.vars_snapshot)) {
        html += `
            <div class="variable-card">
                <div class="variable-name">${escapeHtml(varName)}</div>
                <div class="variable-value">${escapeHtml(String(varValue))}</div>
            </div>
        `;
    }
    
    html += '</div>';
    elements.variablesContent.innerHTML = html;
}

// 工具函数：HTML 转义
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 启动应用
document.addEventListener('DOMContentLoaded', init);

// 暴露 selectStep 到全局
window.selectStep = selectStep;
