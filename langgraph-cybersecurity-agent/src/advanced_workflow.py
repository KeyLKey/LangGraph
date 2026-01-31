"""
高级动态工作流模块
实现更灵活的多智能体网络安全防护助手流程，支持动态子图生成
"""
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.tools import BaseTool
from langchain_core.agents import AgentFinish
from .guardrails import SecurityGuardrails
from .intent_recognition import IntentRecognizer
from .agents.orchestrator import OrchestratorAgent


# 定义状态结构
class AgentState(TypedDict):
    """工作流状态定义"""
    query: str                    # 用户原始查询
    guardrail_result: Dict[str, Any]  # 安全护栏检查结果
    intent_info: Dict[str, Any]   # 意图识别结果
    dynamic_tasks: List[Dict[str, Any]]  # 动态生成的任务列表
    task_results: Dict[str, Any]  # 任务执行结果
    final_response: str           # 最终响应


class AdvancedCybersecurityWorkflow:
    """高级网络安全助手工作流类，支持动态子图生成"""
    
    def __init__(self):
        self.guardrails = SecurityGuardrails()
        self.intent_recognizer = IntentRecognizer()
        self.orchestrator = OrchestratorAgent()
        
        # 构建高级工作流
        self.workflow = self._build_advanced_workflow()
    
    def _build_advanced_workflow(self) -> StateGraph:
        """构建支持动态子图的LangGraph工作流"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("guardrails_check", self._guardrails_check)
        workflow.add_node("intent_recognition", self._intent_recognition)
        workflow.add_node("dynamic_planning", self._dynamic_planning)
        workflow.add_node("execute_tasks", self._execute_tasks)
        workflow.add_node("aggregate_results", self._aggregate_results)
        workflow.add_node("format_response", self._format_response)
        
        # 设置入口点
        workflow.set_entry_point("guardrails_check")
        
        # 添加边
        workflow.add_edge("guardrails_check", "intent_recognition")
        workflow.add_edge("intent_recognition", "dynamic_planning")
        workflow.add_edge("dynamic_planning", "execute_tasks")
        workflow.add_edge("execute_tasks", "aggregate_results")
        workflow.add_edge("aggregate_results", "format_response")
        workflow.add_edge("format_response", END)
        
        # 编译工作流
        return workflow.compile()
    
    def _guardrails_check(self, state: AgentState) -> Dict[str, Any]:
        """
        安全护栏检查节点
        """
        print("执行安全护栏检查...")
        guardrail_result = self.guardrails.check_query(state["query"])
        
        return {
            "guardrail_result": guardrail_result
        }
    
    def _intent_recognition(self, state: AgentState) -> Dict[str, Any]:
        """
        意图识别节点
        """
        print("执行意图识别...")
        
        # 检查安全护栏结果
        if state["guardrail_result"]["status"] != "ALLOWED":
            intent_info = {
                "intents": ["Fallback"],
                "confidence": "高",
                "explanation": "查询未通过安全护栏检查，转至兜底处理"
            }
        else:
            # 执行意图识别
            intent_info = self.intent_recognizer.recognize_intent(state["query"])
        
        return {
            "intent_info": intent_info
        }
    
    def _dynamic_planning(self, state: AgentState) -> Dict[str, Any]:
        """
        动态任务规划节点
        """
        print("执行动态任务规划...")
        
        # 检查安全护栏结果
        if state["guardrail_result"]["status"] != "ALLOWED":
            dynamic_tasks = []
        else:
            # 让OrchestratorAgent根据意图动态创建执行图
            plan = self.orchestrator.create_dynamic_graph(
                state["query"],
                state["intent_info"]
            )
            dynamic_tasks = plan.get("tasks", [])
        
        return {
            "dynamic_tasks": dynamic_tasks
        }
    
    def _execute_tasks(self, state: AgentState) -> Dict[str, Any]:
        """
        执行动态任务节点
        """
        print("执行动态任务...")
        
        task_results = {}
        tasks = state["dynamic_tasks"]
        
        if not tasks:
            # 如果没有动态任务，返回空结果
            return {"task_results": {}}
        
        # 按依赖关系执行任务
        remaining_tasks = tasks[:]
        executed_tasks = set()
        
        while remaining_tasks:
            # 找到可以执行的任务（依赖已完成）
            executable_tasks = []
            for task in remaining_tasks:
                dependencies = task.get("dependencies", [])
                if all(dep in executed_tasks for dep in dependencies):
                    executable_tasks.append(task)
            
            if not executable_tasks:
                # 如果没有可执行的任务但还有剩余任务，说明存在循环依赖
                print("警告: 存在循环依赖，无法继续执行剩余任务")
                break
            
            # 执行可执行的任务（这里简化为顺序执行，实际可以并行）
            for task in executable_tasks:
                task_id = task["id"]
                
                print(f"执行任务: {task_id}")
                
                # 执行任务
                result = self.orchestrator.execute_single_task(
                    task["agent"],
                    task["action"],
                    task["input"]
                )
                
                task_results[task_id] = result
                executed_tasks.add(task_id)
                remaining_tasks.remove(task)
        
        return {
            "task_results": task_results
        }
    
    def _aggregate_results(self, state: AgentState) -> Dict[str, Any]:
        """
        聚合任务结果节点
        """
        print("聚合任务结果...")
        
        # 获取意图信息和任务结果
        intent_info = state["intent_info"]
        task_results = state["task_results"]
        
        # 获取组合策略
        plan = self.orchestrator.create_dynamic_graph(
            state["query"],
            intent_info
        )
        strategy = plan.get("result_combination_strategy", "默认组合策略")
        
        # 组合结果
        aggregated_result = self.orchestrator.combine_results(task_results, strategy)
        
        return {
            "final_response": aggregated_result
        }
    
    def _format_response(self, state: AgentState) -> Dict[str, Any]:
        """
        格式化响应节点
        """
        print("格式化最终响应...")
        
        # 如果查询被安全护栏阻止，返回相应消息
        if state["guardrail_result"]["status"] != "ALLOWED":
            formatted_response = f"查询被安全护栏阻止: {state['guardrail_result']['reason']}"
        else:
            formatted_response = state["final_response"]
        
        return {
            "final_response": formatted_response
        }
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        运行高级工作流
        
        Args:
            query: 用户查询字符串
            
        Returns:
            包含最终响应的工作流结果
        """
        # 初始化状态
        initial_state = {
            "query": query,
            "guardrail_result": {},
            "intent_info": {},
            "dynamic_tasks": [],
            "task_results": {},
            "final_response": ""
        }
        
        # 执行工作流
        result = self.workflow.invoke(initial_state)
        
        return result


# 为了保持兼容性，也保留原来的类名
CybersecurityWorkflow = AdvancedCybersecurityWorkflow