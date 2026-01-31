# 多智能体网络安全防护助手

这是一个基于LangGraph 1.0+构建的多智能体网络安全防护助手，使用DeepSeek API作为LLM后端。

## 项目特点

- **动态任务编排**：OrchestratorAgent根据意图分析动态生成任务图
- **多智能体协作**：SecurityAnalysisAgent、KnowledgeAgent、FileUnderstandingAgent协同工作
- **安全护栏**：确保问题在网络安全服务范围内
- **意图识别**：支持复合意图处理（SecurityAnalysis、KnowledgeQuery、FileUnderstanding等）
- **DeepSeek API集成**：使用DeepSeek的LLM服务

## 架构设计

```
安全护栏 → 意图识别 → 动态任务规划 → [多智能体执行] → 结果聚合 → 最终输出
```

## 核心组件

1. **安全护栏** (`guardrails.py`)：确保查询在网络安全领域内
2. **意图识别** (`intent_recognition.py`)：识别用户查询的意图类型
3. **编排智能体** (`orchestrator.py`)：动态生成任务执行图
4. **安全分析智能体** (`security_analysis.py`)：威胁分析、漏洞评估
5. **知识查询智能体** (`knowledge.py`)：查询ATT&CK框架、CVE等
6. **文件理解智能体** (`file_understanding.py`)：处理安全相关文件
7. **工具层** (`tools/`)：文件处理、RAG、图数据库查询等

## 配置

复制 `.env.example` 为 `.env` 并填入相应的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入DeepSeek API密钥：

```
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
LLM_PROVIDER=deepseek
```

## 安装和运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行系统
python main.py
```

## 使用示例

系统可以处理多种类型的网络安全查询：

- "什么是勒索软件？" (知识查询)
- "分析这份CTI报告，判断是不是勒索软件攻击，并告诉我该怎么防御" (复合意图)
- "如何修复CVE-2023-1234漏洞？" (安全分析+知识查询)
- "ATT&CK框架中的T1566代表什么技术？" (知识查询)

非网络安全相关的查询将被安全护栏拦截。

## 项目结构

```
langgraph-cybersecurity-agent/
├── src/
│   ├── config.py                 # 配置管理
│   ├── guardrails.py             # 安全护栏
│   ├── intent_recognition.py     # 意图识别
│   ├── advanced_workflow.py      # 高级动态工作流
│   ├── workflow.py               # 原始工作流
│   ├── conversation_manager.py   # 对话管理
│   ├── agents/                   # 智能体定义
│   │   ├── llm_factory.py        # LLM工厂
│   │   ├── orchestrator.py       # 编排智能体
│   │   ├── security_analysis.py  # 安全分析智能体
│   │   ├── knowledge.py          # 知识查询智能体
│   │   └── file_understanding.py # 文件理解智能体
│   └── tools/                    # 工具层
│       ├── file_tools.py         # 文件工具
│       ├── rag_tools.py          # RAG工具
│       ├── graph_tools.py        # 图数据库工具
│       ├── web_tools.py          # 网页搜索工具
│       └── paper_tools.py        # 论文搜索工具
├── requirements.txt
├── .env                          # 环境变量配置
├── .env.example                  # 环境变量示例
└── main.py                       # 主程序入口
```

## 动态图生成机制

OrchestratorAgent具备两种任务规划方式：

1. **LLM驱动规划**：使用LLM分析查询并生成最优任务图
2. **规则回退规划**：当LLM不可用时的备用方案

系统会根据意图类型和复杂程度自动生成包含任务依赖关系的执行图，支持并行和串行任务执行。

## 扩展性

- 可轻松添加新的智能体类型
- 可扩展新的工具功能
- 支持多种LLM提供商
- 灵活的意图识别系统