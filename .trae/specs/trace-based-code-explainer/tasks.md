# Tasks - trace-based-code-learning

## 项目初始化

- [ ] Task 1: 初始化项目结构
  - [ ] SubTask 1.1: 创建前后端目录结构
  - [ ] SubTask 1.2: 初始化Node.js前端项目 (React + TypeScript)
  - [ ] SubTask 1.3: 初始化Python后端项目 (FastAPI)

- [ ] Task 2: 配置开发环境
  - [ ] SubTask 2.1: 配置前端依赖 (React, TypeScript, Monaco Editor, D3.js)
  - [ ] SubTask 2.2: 配置后端依赖 (FastAPI, uvicorn, AST utilities)
  - [ ] SubTask 2.3: 配置跨域和代理

## 后端核心开发

- [ ] Task 3: 实现静态分析模块
  - [ ] SubTask 3.1: 实现Python AST解析器
  - [ ] SubTask 3.2: 实现函数/类识别模块
  - [ ] SubTask 3.3: 实现依赖关系构建器
  - [ ] SubTask 3.4: 实现学习路径生成器

- [ ] Task 4: 实现动态执行模块（Runtime Tracing）
  - [ ] SubTask 4.1: 实现sys.settrace轨迹采集器
  - [ ] SubTask 4.2: 实现变量状态捕获（before/after）
  - [ ] SubTask 4.3: 实现调用栈追踪
  - [ ] SubTask 4.4: 实现异常轨迹捕获

- [ ] Task 5: 实现轨迹压缩与结构化
  - [ ] SubTask 5.1: 实现循环合并算法（loop summarization）
  - [ ] SubTask 5.2: 实现执行路径构建（execution path）
  - [ ] SubTask 5.3: 实现关键节点标注（分支、循环、函数调用）
  - [ ] SubTask 5.4: 实现轨迹数据结构化输出

- [ ] Task 6: 实现执行驱动讲解生成
  - [ ] SubTask 6.1: 实现trace-to-explanation映射
  - [ ] SubTask 6.2: 实现变量变化解释生成
  - [ ] SubTask 6.3: 实现分支选择解释生成
  - [ ] SubTask 6.4: 实现带citation的解释输出

- [ ] Task 7: 实现高阶功能 - 错误注入
  - [ ] SubTask 7.1: 实现潜在错误点识别（除零、越界等）
  - [ ] SubTask 7.2: 实现错误输入生成器
  - [ ] SubTask 7.3: 实现错误原因解释

- [ ] Task 8: 实现高阶功能 - 路径对比
  - [ ] SubTask 8.1: 实现多输入执行器
  - [ ] SubTask 8.2: 实现路径差异分析算法
  - [ ] SubTask 8.3: 实现差异高亮标记

- [ ] Task 9: 实现高阶功能 - 知识抽象
  - [ ] SubTask 9.1: 实现执行模式分析器
  - [ ] SubTask 9.2: 实现算法策略识别（分治、贪心等）
  - [ ] SubTask 9.3: 实现高层次算法思想生成

- [ ] Task 10: 实现FastAPI服务接口
  - [ ] SubTask 10.1: 实现代码分析接口 (POST /analyze)
  - [ ] SubTask 10.2: 实现课程生成接口 (POST /generate-course)
  - [ ] SubTask 10.3: 实现路径对比接口 (POST /compare-paths)
  - [ ] SubTask 10.4: 实现健康检查接口 (GET /health)

## 前端核心开发

- [ ] Task 11: 实现代码编辑器组件
  - [ ] SubTask 11.1: 集成Monaco Editor
  - [ ] SubTask 11.2: 实现Python语法高亮
  - [ ] SubTask 11.3: 实现当前执行行高亮

- [ ] Task 12: 实现变量状态面板
  - [ ] SubTask 12.1: 实现变量列表展示
  - [ ] SubTask 12.2: 实现变量值变化高亮
  - [ ] SubTask 12.3: 实现变量类型显示

- [ ] Task 13: 实现执行路径可视化
  - [ ] SubTask 13.1: 实现流程图组件
  - [ ] SubTask 13.2: 实现当前执行节点高亮
  - [ ] SubTask 13.3: 实现步骤导航控制

- [ ] Task 14: 实现课程结构导航
  - [ ] SubTask 14.1: 实现lesson列表展示
  - [ ] SubTask 14.2: 实现lesson切换功能
  - [ ] SubTask 14.3: 实现学习进度指示

- [ ] Task 15: 实现路径对比展示
  - [ ] SubTask 15.1: 实现多路径并列展示
  - [ ] SubTask 15.2: 实现差异点标记
  - [ ] SubTask 15.3: 实现切换输入功能

- [ ] Task 16: 实现主界面布局和交互
  - [ ] SubTask 16.1: 实现多栏布局
  - [ ] SubTask 16.2: 实现"生成课程"按钮和流程
  - [ ] SubTask 16.3: 实现加载状态和错误处理

## 集成与测试

- [ ] Task 17: 端到端集成测试
  - [ ] SubTask 17.1: 测试完整课程生成流程
  - [ ] SubTask 17.2: 测试执行驱动讲解
  - [ ] SubTask 17.3: 测试边界情况处理

## Task Dependencies

- Task 3, 4, 5（后端核心）可并行开发
- Task 6 依赖 Task 4, 5 完成
- Task 7, 8, 9（高阶功能）依赖 Task 4, 5, 6 完成
- Task 10 依赖 Task 3, 4, 5, 6 完成
- Task 11, 12, 13, 14, 15（前端组件）可并行开发
- Task 16 依赖 Task 11-15 完成
- Task 17 依赖 Task 16 和 Task 10 完成
