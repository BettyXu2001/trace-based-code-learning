# CodeTrace - 基于执行语义的代码学习平台

A code learning platform that uses static analysis and runtime tracing to help developers understand code execution flow.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18.2-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-orange.svg)

## 项目简介

CodeTrace 是一个创新的代码学习工具，它通过**静态分析**和**运行时追踪**相结合的方式，帮助开发者深入理解代码的执行过程。

### 核心创新

| 传统方式 | CodeTrace |
|---------|-----------|
| 只看代码（静态） | 结构理解 + 执行理解统一 |
| 静态解释容易产生幻觉 | 动态追踪有真实执行证据 |
| 面向开发者（Debug工具） | 面向学习者（AI学习系统） |

## 功能特性

### 核心功能
- **代码结构解析**：AST解析、函数/类识别、依赖关系构建
- **执行轨迹采集**：实时采集代码执行数据，包括行号、变量状态、调用栈
- **轨迹压缩**：智能合并循环执行过程，精简长轨迹
- **分支路径记录**：清晰展示条件分支的选择过程
- **执行驱动讲解**：基于真实执行数据生成step-by-step解释
- **课程生成**：自动生成结构化的学习路径和课程内容

### 高级功能
- **错误注入**：自动识别潜在错误点，生成错误案例
- **路径对比**：对比不同输入的执行路径差异
- **知识抽象**：从执行中提取算法思想

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (React)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 代码编辑器   │  │ 执行时间轴   │  │ 解释面板/变量面板   │  │
│  │ Monaco      │  │ D3.js       │  │ AI生成内容          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端 (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 静态分析层   │  │ 动态执行层   │  │  AI生成层           │  │
│  │ AST解析     │  │ trace采集   │  │  Prompt模板         │  │
│  │ 结构切分    │  │ 轨迹压缩    │  │  LLM调用            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React + TypeScript | 现代响应式UI |
| 前端编辑器 | Monaco Editor | VS Code同款代码编辑器 |
| 可视化 | D3.js | 执行时间轴可视化 |
| 后端 | Python FastAPI | 高性能API服务 |
| 静态分析 | Python AST | 代码结构解析 |
| 轨迹采集 | sys.settrace | 运行时数据采集 |
| AI | OpenAI API | 智能讲解生成 |

## 项目结构

```
trace-based-code-learning/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   ├── routers/           # API路由
│   │   ├── services/          # 核心服务
│   │   │   ├── analyzer.py    # 代码分析器
│   │   │   ├── tracer.py      # 执行追踪器
│   │   │   ├── structurer.py  # 轨迹结构化
│   │   │   └── explainer.py   # AI解释器
│   │   └── main.py           # FastAPI入口
│   ├── requirements.txt       # Python依赖
│   └── run.py                 # 启动脚本
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── CodeEditor.tsx       # 代码编辑器
│   │   │   ├── ExecutionTimeline.tsx # 执行时间轴
│   │   │   ├── ExplanationPanel.tsx # 解释面板
│   │   │   ├── VariablePanel.tsx    # 变量状态面板
│   │   │   └── CourseNavigator.tsx  # 课程导航
│   │   ├── App.tsx           # 主应用组件
│   │   ├── api.ts            # API调用
│   │   └── types.ts          # TypeScript类型
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+

### 安装

1. **克隆项目**
```bash
git clone <repository-url>
cd trace-based-code-learning
```

2. **安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
npm install
```

### 启动

1. **启动后端服务**
```bash
cd backend
python run.py
```
后端服务运行在 `http://localhost:8000`

2. **启动前端服务**（新终端）
```bash
cd frontend
npm run dev
```
前端应用运行在 `http://localhost:5173`

## 使用指南

### 基本用法

1. **输入代码**：在代码编辑器中输入Python代码
2. **运行分析**：点击「运行」按钮
3. **查看轨迹**：在执行时间轴中查看每一步的执行过程
4. **阅读解释**：在右侧面板查看AI生成的执行解释

### 功能说明

#### 代码编辑器
- 支持语法高亮
- 当前执行行高亮显示
- 可编辑和修改代码

#### 执行时间轴
- 展示代码执行的每一步
- 点击任意步骤可查看该时刻的变量状态
- 循环执行会被压缩显示

#### 变量面板
- 实时展示当前执行步骤的变量状态
- 高亮显示发生变化的变量

#### 解释面板
- AI生成的执行解释
- 每一步都有对应的说明
- 包含关键洞察和知识点

### 生成课程

点击相关按钮，系统将自动：
1. 分析代码结构
2. 按依赖关系生成学习路径
3. 为每个模块生成讲解内容

## API 文档

启动后端服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/analyze` | POST | 分析代码并返回执行轨迹 |
| `/api/generate-course` | POST | 生成完整课程 |
| `/health` | GET | 健康检查 |

## 开发指南

### 后端开发

```bash
cd backend

# 运行测试
python -m pytest

# 代码分析
python test_analyzer.py
```

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 类型检查
npm run typecheck

# 代码检查
npm run lint
```

## License

MIT License
