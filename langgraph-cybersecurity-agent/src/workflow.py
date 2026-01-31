"""
LangGraph工作流模块
实现完整的多智能体网络安全防护助手流程
"""
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from .guardrails import SecurityGuardrails
from .intent_recognition import IntentRecognizer
from .agents.orchestrator import OrchestratorAgent


# 定义状态结构
class AgentState(TypedDict):
    """工作流状态定义"""
    query: str                    # 用户原始查询
    guardrail_result: Dict[str, Any]  # 安全护栏检查结果
    intent_info: Dict[str, Any]   # 意图识别结果
    agent_response: Dict[str, Any] # 智能体响应结果
    final_response: str           # 最终响应


class CybersecurityWorkflow:
    """网络安全助手工作流类"""
    
    def __init__(self):
        self.guardrails = SecurityGuardrails()
        self.intent_recognizer = IntentRecognizer()
        self.orchestrator = OrchestratorAgent()
        
        # 构建工作流
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """构建LangGraph工作流"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("guardrails_check", self._guardrails_check)
        workflow.add_node("intent_recognition", self._intent_recognition)
        workflow.add_node("orchestration", self._orchestration)
        workflow.add_node("format_response", self._format_response)
        
        # 设置入口点
        workflow.set_entry_point("guardrails_check")
        
        # 添加边
        workflow.add_edge("guardrails_check", "intent_recognition")
        workflow.add_edge("intent_recognition", "orchestration")
        workflow.add_edge("orchestration", "format_response")
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
    
    def _orchestration(self, state: AgentState) -> Dict[str, Any]:
        """
        编排执行节点
        """
        print("执行任务编排...")
        
        # 检查安全护栏结果
        if state["guardrail_result"]["status"] != "ALLOWED":
            agent_response = {
                "status": "blocked",
                "result": f"查询被安全护栏阻止: {state['guardrail_result']['reason']}"
            }
        else:
            # 通过编排智能体处理
            agent_response = self.orchestrator.process(
                state["query"], 
                state["intent_info"]
            )
        
        return {
            "agent_response": agent_response
        }
    
    def _format_response(self, state: AgentState) -> Dict[str, Any]:
        """
        格式化响应节点
        """
        print("格式化最终响应...")
        
        # 根据处理结果生成最终响应
        if state["agent_response"]["status"] == "blocked":
            final_response = state["agent_response"]["result"]
        elif state["agent_response"]["status"] == "success":
            final_response = state["agent_response"]["final_result"]
        else:
            final_response = "抱歉，处理您的请求时出现了一些问题，请稍后再试。"
        
        return {
            "final_response": final_response
        }
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        运行工作流
        
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
            "agent_response": {},
            "final_response": ""
        }
        
        # 执行工作流
        result = self.workflow.invoke(initial_state)
        
        return result


# 示例用法
if __name__ == "__main__":
    # 创建工作流实例
    cybersecurity_agent = CybersecurityWorkflow()
    
    # 测试查询
    test_queries = [
        "什么是勒索软件？",
        "分析这份CTI报告，判断是不是勒索软件攻击，并告诉我该怎么防御",
        "如何修复CVE-2023-1234漏洞？",
        "帮我写一首诗"
    ]
    
    for query in test_queries:
        print(f"\n--- 处理查询: {query} ---")
        result = cybersecurity_agent.run(query)
        print(f"最终响应: {result['final_response']}")