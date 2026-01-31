"""
安全分析智能体模块
负责威胁分析、漏洞评估、防护策略生成等核心安全任务
"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from .llm_factory import create_llm
from ..tools.rag_tools import RAGTools
from ..tools.graph_tools import GraphTools
from ..tools.web_tools import WebTools
from ..config import config


class SecurityAnalysisAgent:
    """安全分析智能体类"""
    
    def __init__(self):
        self.llm = create_llm(temperature=0.3)
        
        # 初始化相关工具
        self.rag_tools = RAGTools()
        self.graph_tools = GraphTools()
        self.web_tools = WebTools()
        
        # 威胁分析提示词模板
        self.threat_analysis_template = PromptTemplate(
            input_variables=["query", "context"],
            template="""
你是网络安全专家，专门负责威胁分析和安全评估。请分析以下安全相关查询：

查询内容：{query}

相关上下文信息：{context}

请按以下方面进行分析：
1. 威胁识别：识别潜在威胁和风险点
2. 影响评估：评估威胁可能造成的影响
3. 攻击向量：分析可能的攻击路径
4. 防护建议：提供具体的防护措施
5. 应急响应：如适用，提供应急响应建议

请提供详细且专业的分析结果。
"""
        )
        
        # 漏洞评估提示词模板
        self.vulnerability_assessment_template = PromptTemplate(
            input_variables=["query", "context"],
            template="""
你是网络安全漏洞评估专家。请对以下漏洞相关信息进行专业评估：

查询内容：{query}

相关上下文信息：{context}

请按以下方面进行评估：
1. 漏洞分类：确定漏洞类型(CVE、配置错误等)
2. 严重程度：评估漏洞的严重性(CVSS评分)
3. 影响范围：分析漏洞影响的系统和数据
4. 利用可能性：评估被利用的可能性
5. 修复建议：提供具体的修复方案
6. 临时缓解措施：如无法立即修复，提供临时缓解措施

请提供详细且实用的评估结果。
"""
        )
        
        # 防护策略生成提示词模板
        self.protection_strategy_template = PromptTemplate(
            input_variables=["query", "context"],
            template="""
你是网络安全防护策略专家。请为以下场景生成全面的防护策略：

查询内容：{query}

相关上下文信息：{context}

请提供一个全面的防护策略，包括但不限于：
1. 预防措施：如何预防此类安全问题
2. 检测机制：如何及时发现此类威胁
3. 响应流程：发现问题后的应对流程
4. 验证方法：如何验证防护措施的有效性
5. 持续改进：如何持续优化防护策略

请提供实用且可操作的防护策略。
"""
        )
    
    def analyze_threat(self, query: str) -> Dict[str, Any]:
        """
        分析威胁
        
        Args:
            query: 查询内容
            
        Returns:
            威胁分析结果
        """
        try:
            # 检索相关上下文
            context_results = self.rag_tools.retrieve_context(query)
            context = " ".join([item["content"] for item in context_results])
            
            # 构建分析链
            chain = self.threat_analysis_template | self.llm
            result = chain.invoke({"query": query, "context": context})
            
            return {
                "status": "success",
                "analysis_type": "threat_analysis",
                "result": result.content,
                "context_used": len(context_results)
            }
        except Exception as e:
            return {
                "status": "error",
                "analysis_type": "threat_analysis",
                "message": f"威胁分析过程中出现错误: {str(e)}"
            }
    
    def assess_vulnerability(self, query: str) -> Dict[str, Any]:
        """
        评估漏洞
        
        Args:
            query: 查询内容
            
        Returns:
            漏洞评估结果
        """
        try:
            # 检索相关上下文
            context_results = self.rag_tools.retrieve_context(query)
            context = " ".join([item["content"] for item in context_results])
            
            # 构建评估链
            chain = self.vulnerability_assessment_template | self.llm
            result = chain.invoke({"query": query, "context": context})
            
            return {
                "status": "success",
                "analysis_type": "vulnerability_assessment",
                "result": result.content,
                "context_used": len(context_results)
            }
        except Exception as e:
            return {
                "status": "error",
                "analysis_type": "vulnerability_assessment",
                "message": f"漏洞评估过程中出现错误: {str(e)}"
            }
    
    def generate_protection_strategy(self, query: str) -> Dict[str, Any]:
        """
        生成防护策略
        
        Args:
            query: 查询内容
            
        Returns:
            防护策略结果
        """
        try:
            # 检索相关上下文
            context_results = self.rag_tools.retrieve_context(query)
            context = " ".join([item["content"] for item in context_results])
            
            # 构建策略生成链
            chain = self.protection_strategy_template | self.llm
            result = chain.invoke({"query": query, "context": context})
            
            return {
                "status": "success",
                "analysis_type": "protection_strategy",
                "result": result.content,
                "context_used": len(context_results)
            }
        except Exception as e:
            return {
                "status": "error",
                "analysis_type": "protection_strategy",
                "message": f"防护策略生成过程中出现错误: {str(e)}"
            }
    
    def process(self, query: str) -> Dict[str, Any]:
        """
        处理安全分析请求
        
        Args:
            query: 用户查询
            
        Returns:
            处理结果
        """
        # 简单判断用户查询类型，并选择相应的分析方法
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["威胁", "攻击", "风险", "恶意", "病毒", "木马", "勒索", "入侵"]):
            return self.analyze_threat(query)
        elif any(keyword in query_lower for keyword in ["漏洞", "cve", "缺陷", "弱点", "安全补丁", "修复"]):
            return self.assess_vulnerability(query)
        elif any(keyword in query_lower for keyword in ["防护", "防御", "安全策略", "安全措施", "加固", "策略"]):
            return self.generate_protection_strategy(query)
        else:
            # 默认进行综合威胁分析
            return self.analyze_threat(query)