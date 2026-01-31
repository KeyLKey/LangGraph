"""
编排智能体模块
负责构造Task Graph、分发任务给执行Agent、合并结果
"""
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from .llm_factory import create_llm
from .security_analysis import SecurityAnalysisAgent
from .knowledge import KnowledgeAgent
from .file_understanding import FileUnderstandingAgent
from ..config import config


class OrchestratorAgent:
    """编排智能体类"""
    
    def __init__(self):
        self.llm = create_llm(temperature=0.1)
        
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
    
    def create_dynamic_graph(self, query: str, intent_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据意图动态创建执行图
        
        Args:
            query: 用户查询
            intent_info: 意图分析信息
            
        Returns:
            动态执行图配置
        """
        # 使用LLM来生成更复杂的动态任务图
        planning_prompt = f"""
        你是一个高级任务编排智能体。根据用户的查询和意图分析，你需要设计一个最优的任务执行图。
        
        用户查询: {query}
        意图分析: {intent_info}
        
        可用的智能体:
        1. SecurityAnalysisAgent - 用于威胁分析、漏洞评估、防护策略生成
        2. KnowledgeAgent - 用于查询网络安全知识、ATT&CK框架、CVE信息等
        3. FileUnderstandingAgent - 用于理解和分析上传的文件
        
        请设计一个任务执行图，考虑以下因素：
        - 任务之间的依赖关系
        - 是否需要并行执行某些任务
        - 任务的执行顺序
        - 如何组合最终结果
        
        请严格按照以下JSON格式返回:
        {{
            "tasks": [
                {{
                    "id": "唯一任务ID",
                    "agent": "智能体名称",
                    "action": "具体操作",
                    "input": "传递给智能体的输入",
                    "dependencies": ["依赖的其他任务ID列表"]
                }}
            ],
            "result_combination_strategy": "描述如何组合结果"
        }}
        """
        
        try:
            # 使用LLM来规划复杂任务
            llm_response = self.llm.invoke(planning_prompt)
            response_text = llm_response.content.strip()
            
            # 尝试解析JSON格式的响应
            if response_text.startswith('{') and response_text.endswith('}'):
                import json
                try:
                    parsed_plan = json.loads(response_text)
                    return parsed_plan
                except json.JSONDecodeError:
                    pass
            
            # 如果LLM无法生成有效的JSON，使用基于规则的回退方法
            print(f"LLM未能生成有效JSON，使用回退方法")
            return self._create_fallback_graph(query, intent_info)
                    
        except Exception as e:
            print(f"使用LLM规划任务图时出错: {str(e)}，使用回退方法")
            return self._create_fallback_graph(query, intent_info)
    
    def _create_fallback_graph(self, query: str, intent_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        回退方法：基于规则创建执行图
        
        Args:
            query: 用户查询
            intent_info: 意图分析信息
            
        Returns:
            执行图配置
        """
        # 根据意图类型创建不同的执行路径
        intents = intent_info.get("intents", [])
        tasks = []
        
        # 根据意图分析结果生成任务
        for idx, intent in enumerate(intents):
            task_id = f"{intent.lower()}_{idx}"
            
            if intent == "SecurityAnalysis":
                tasks.append({
                    "id": task_id,
                    "agent": "SecurityAnalysisAgent",
                    "action": "analyze_threat",
                    "input": query,
                    "dependencies": []
                })
            elif intent == "KnowledgeQuery":
                tasks.append({
                    "id": task_id,
                    "agent": "KnowledgeAgent",
                    "action": "process",
                    "input": query,
                    "dependencies": []
                })
            elif intent == "FileUnderstanding":
                # 如果是文件理解意图，需要特殊处理
                tasks.append({
                    "id": task_id,
                    "agent": "FileUnderstandingAgent",
                    "action": "process",
                    "input": query,
                    "dependencies": []
                })
            elif intent == "Fallback" or intent == "SafeAnswer":
                tasks.append({
                    "id": task_id,
                    "agent": "KnowledgeAgent",  # 使用知识智能体提供引导
                    "action": "search_web_knowledge",
                    "input": "网络安全基础知识 " + query,
                    "dependencies": []
                })
        
        # 如果没有识别出特定意图，创建默认安全分析任务
        if not tasks:
            tasks.append({
                "id": "default_security_analysis",
                "agent": "SecurityAnalysisAgent",
                "action": "analyze_threat",
                "input": query,
                "dependencies": []
            })
        
        # 如果有多个意图，考虑它们之间的依赖关系
        if len(intents) > 1:
            # 对于多意图情况，可能需要组合分析
            combination_task_id = f"combination_analysis_{len(tasks)}"
            tasks.append({
                "id": combination_task_id,
                "agent": "SecurityAnalysisAgent",
                "action": "synthesize_findings",
                "input": query,
                "dependencies": [task["id"] for task in tasks[:-1]]  # 依赖之前的所有任务
            })
        
        return {
            "tasks": tasks,
            "result_combination_strategy": self._get_combination_strategy(intent_info)
        }
    
    def _get_combination_strategy(self, intent_info: Dict[str, Any]) -> str:
        """
        根据意图信息获取结果组合策略
        
        Args:
            intent_info: 意图分析信息
            
        Returns:
            结果组合策略描述
        """
        intents = intent_info.get("intents", [])
        
        if len(intents) == 1:
            return "单一意图处理：直接返回对应智能体的结果"
        elif "FileUnderstanding" in intents:
            return "文件理解优先：先分析文件内容，再结合其他分析结果"
        elif "KnowledgeQuery" in intents and "SecurityAnalysis" in intents:
            return "知识+分析融合：先查询相关知识，再进行安全分析，最后整合结果"
        else:
            return "多意图并行：并行执行多个任务，然后汇总结果"
    
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
        # 生成动态执行图
        plan = self.create_dynamic_graph(query, intent_info)
        
        # 执行计划
        result = self.execute_plan(plan, query)
        
        return result