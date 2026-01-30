"""
编排智能体模块
负责构造Task Graph、分发任务给执行Agent、合并结果
"""
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from .security_analysis import SecurityAnalysisAgent
from .knowledge import KnowledgeAgent
from .file_understanding import FileUnderstandingAgent
from ..config import config


class OrchestratorAgent:
    """编排智能体类"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        
        # 初始化各个专业智能体
        self.security_agent = SecurityAnalysisAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.file_agent = FileUnderstandingAgent()
        
        # 任务规划提示词模板
        self.planning_template = PromptTemplate(
            input_variables=["query", "intent_info"],
            template="""
你是网络安全助手的编排智能体。你的任务是分析用户查询，制定执行计划，并协调其他智能体完成任务。

用户查询：{query}
意图分析信息：{intent_info}

请分析如何最好地完成此任务，可能需要调用以下智能体：
1. SecurityAnalysisAgent - 用于威胁分析、漏洞评估、防护策略生成
2. KnowledgeAgent - 用于查询网络安全知识、ATT&CK框架、CVE信息等
3. FileUnderstandingAgent - 用于理解和分析上传的文件

请按照以下JSON格式返回执行计划：
{{
    "tasks": [
        {{
            "agent": "SecurityAnalysisAgent|KnowledgeAgent|FileUnderstandingAgent",
            "action": "具体要执行的操作",
            "input": "传递给智能体的输入",
            "dependencies": ["task_id_1", "task_id_2"]  // 可选，依赖的任务ID
        }}
    ],
    "result_combination_strategy": "如何组合各任务结果"
}}
"""
        )
    
    def plan_execution(self, query: str, intent_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        规划执行任务
        
        Args:
            query: 用户查询
            intent_info: 意图分析信息
            
        Returns:
            执行计划
        """
        try:
            chain = self.planning_template | self.llm
            result = chain.invoke({"query": query, "intent_info": intent_info})
            
            # 解析LLM返回的结果
            response_text = result.content.strip()
            
            # 尝试解析JSON格式的响应
            if response_text.startswith('{') and response_text.endswith('}'):
                import json
                try:
                    parsed_plan = json.loads(response_text)
                    return parsed_plan
                except json.JSONDecodeError:
                    pass
            
            # 如果无法解析JSON，返回默认计划
            return {
                "tasks": [],
                "result_combination_strategy": "无法解析执行计划，返回空任务列表"
            }
            
        except Exception as e:
            return {
                "tasks": [],
                "result_combination_strategy": f"执行计划生成异常：{str(e)}"
            }
    
    def execute_single_task(self, agent_name: str, action: str, input_data: str) -> Dict[str, Any]:
        """
        执行单个任务
        
        Args:
            agent_name: 智能体名称
            action: 要执行的操作
            input_data: 输入数据
            
        Returns:
            任务执行结果
        """
        try:
            if agent_name == "SecurityAnalysisAgent":
                return self.security_agent.process(input_data)
            elif agent_name == "KnowledgeAgent":
                return self.knowledge_agent.process(input_data)
            elif agent_name == "FileUnderstandingAgent":
                return self.file_agent.process(input_data)
            else:
                return {
                    "status": "error",
                    "message": f"未知的智能体名称: {agent_name}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行任务时发生错误: {str(e)}"
            }
    
    def execute_plan(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        执行任务计划
        
        Args:
            plan: 任务计划
            query: 原始查询
            
        Returns:
            执行结果
        """
        results = {}
        tasks = plan.get("tasks", [])
        
        # 按顺序执行任务
        for i, task in enumerate(tasks):
            task_id = f"task_{i}"
            
            # 检查依赖项
            dependencies = task.get("dependencies", [])
            for dep in dependencies:
                if dep not in results:
                    results[task_id] = {
                        "status": "error",
                        "message": f"依赖任务 {dep} 未完成"
                    }
                    continue
            
            # 执行任务
            agent_name = task.get("agent")
            action = task.get("action")
            input_data = task.get("input", query)
            
            task_result = self.execute_single_task(agent_name, action, input_data)
            results[task_id] = task_result
        
        # 合并结果
        combined_result = self.combine_results(results, plan.get("result_combination_strategy"))
        
        return {
            "status": "success",
            "original_query": query,
            "execution_plan": plan,
            "task_results": results,
            "final_result": combined_result
        }
    
    def combine_results(self, task_results: Dict[str, Any], strategy: str) -> str:
        """
        合并任务结果
        
        Args:
            task_results: 任务结果字典
            strategy: 结果组合策略
            
        Returns:
            合并后的结果字符串
        """
        combined = []
        
        for task_id, result in task_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                content = result.get("result", result.get("response", "无内容"))
                combined.append(f"任务 {task_id} 结果: {content}")
            else:
                error_msg = result.get("message", "未知错误")
                combined.append(f"任务 {task_id} 错误: {error_msg}")
        
        return "\n".join(combined)
    
    def process(self, query: str, intent_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            query: 用户查询
            intent_info: 意图分析信息
            
        Returns:
            处理结果
        """
        # 生成执行计划
        plan = self.plan_execution(query, intent_info)
        
        # 执行计划
        result = self.execute_plan(plan, query)
        
        return result