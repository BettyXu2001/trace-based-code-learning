# CodeTrace - 轻量级版本

## 🎉 项目已轻量化完成！

我们已经成功将 CodeTrace 转换为一个超轻量级的单文件服务器 + 纯 HTML/CSS/JS 前端的项目。

## 🚀 主要变化

### 后端
- **之前**: FastAPI + Pydantic + Uvicorn (多个依赖)
- **现在**: 纯 Python 标准库 (无需安装任何外部依赖！)
- 文件: `server.py` - 单个文件包含所有核心逻辑

### 前端
- **之前**: React + TypeScript + Vite + Monaco Editor + D3.js
- **现在**: 纯 HTML + CSS + JavaScript (无任何构建工具！)
- 文件: `frontend/index.html`, `frontend/style.css`, `frontend/app.js`

## 📦 安装与启动

### 1. 启动服务器
```bash
python server.py
```

或者在 Windows 上双击运行：
```
start.bat
```

### 2. 打开浏览器
访问: `http://localhost:8000`

## ✨ 功能保持完整

所有原有功能都保留：
- 🔍 代码静态分析
- 🎯 运行时执行追踪
- 📊 执行时间轴可视化
- 💡 智能解释生成
- 📚 学习课程生成
- 🎨 浅色/深色主题切换
- ⚙️ AI 设置面板

## 📁 项目结构

```
trace-based-code-learning/
├── server.py                  # 轻量级后端服务器（单文件）
├── frontend/
│   ├── index.html            # 主页面
│   ├── style.css             # 样式表
│   └── app.js                # 前端逻辑
├── start.bat                 # Windows 启动脚本
└── test_server.py            # 核心逻辑测试脚本
```

## 🎯 使用方法

1. 在代码编辑器中输入或粘贴 Python 代码
2. 点击「运行」按钮分析代码
3. 在执行时间轴中查看每一步
4. 查看右侧的执行解释和变量状态
5. 点击时间轴中的任意步骤跳转到对应执行点

## 📝 技术对比

| 项目 | 原始版本 | 轻量版本 |
|------|---------|---------|
| 后端框架 | FastAPI | 标准库 http.server |
| 依赖管理 | requirements.txt | 无依赖 |
| 前端框架 | React + TypeScript | 原生 JavaScript |
| 代码编辑器 | Monaco Editor | 原生 textarea |
| 可视化库 | D3.js | 原生 DOM 操作 |
| 构建工具 | Vite | 无需构建 |
| 启动速度 | 较慢 | 瞬间启动 |
| 项目大小 | 较大 | 极小 |
| 功能完整性 | ✅ 完整 | ✅ 完整 |

## 🛡️ 安全特性

- 受限的代码执行环境
- 超时保护
- 安全的内置函数限制

## 🎉 享受超轻量的开发体验吧！

所有核心功能保持不变，但项目变得更加简洁、快速、易部署！
