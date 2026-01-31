"""
知识查询智能体模块
负责从Neo4j、ATT&CK/CVE/TTP、论文/网页等来源查询网络安全知识
"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from .llm_factory import create_llm
from ..tools.graph_tools import GraphTools
from ..tools.web_tools import WebTools
from ..tools.paper_tools import PaperTools
from ..config import config


class KnowledgeAgent:
    """知识查询智能体类"""
    
    def __init__(self):
        self.llm = create_llm(temperature=0.1)
        
        # 初始化相关工具
        self.graph_tools = GraphTools()
        self.web_tools = WebTools()
        self.paper_tools = PaperTools()
        
        # 知识查询提示词模板
        self.query_template = PromptTemplate(
            input_variables=["query", "knowledge_base_results"],
            template="""
你是网络安全知识专家，负责解释和总结从各种知识源检索到的信息。

用户查询：{query}

从知识库检索到的信息：
{knowledge_base_results}

请结合这些信息，以清晰、准确的方式回答用户的查询。
如果信息不足，请明确指出需要哪些额外信息。
"""
        )
    
    def query_threat_intelligence(self, threat_name: str) -> Dict[str, Any]:
        """
        查询威胁情报
        
        Args:
            threat_name: 威胁名称
            
        Returns:
            威胁情报查询结果
        """
        try:
            # 使用图数据库查询威胁情报
            results = self.graph_tools.query_threat_intelligence(threat_name)
            
            return {
                "status": "success",
                "query_type": "threat_intelligence",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "query_type": "threat_intelligence",
                "message": f"查询威胁情报时出现错误: {str(e)}"
            }
    
    def query_vulnerability_info(self, cve_id: str) -> Dict[str, Any]:
        """
        查询漏洞信息
        
        Args:
            cve_id: CVE编号
            
        Returns:
            漏洞信息查询结果
        """
        try:
            # 使用图数据库查询漏洞信息
            results = self.graph_tools.query_vulnerability_info(cve_id)
            
            return {
                "status": "success",
                "query_type": "vulnerability_info",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "query_type": "vulnerability_info",
                "message": f"查询漏洞信息时出现错误: {str(e)}"
            }
    
    def query_attack_patterns(self, technique_id: str) -> Dict[str, Any]:
        """
        查询攻击模式(ATT&CK技术)
        
        Args:
            technique_id: ATT&CK技术ID
            
        Returns:
            攻击模式查询结果
        """
        try:
            # 使用图数据库查询ATT&CK技术
            results = self.graph_tools.query_attack_patterns(technique_id)
            
            return {
                "status": "success",
                "query_type": "attack_patterns",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "query_type": "attack_patterns",
                "message": f"查询攻击模式时出现错误: {str(e)}"
            }
    
    def query_malware_info(self, malware_name: str) -> Dict[str, Any]:
        """
        查询恶意软件信息
        
        Args:
            malware_name: 恶意软件名称
            
        Returns:
            恶意软件信息查询结果
        """
        try:
            # 使用图数据库查询恶意软件信息
            results = self.graph_tools.query_malware_info(malware_name)
            
            return {
                "status": "success",
                "query_type": "malware_info",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "query_type": "malware_info",
                "message": f"查询恶意软件信息时出现错误: {str(e)}"
            }
    
    def search_web_knowledge(self, query: str) -> Dict[str, Any]:
        """
        搜索网络知识
        
        Args:
            query: 查询内容
            
        Returns:
            网络知识搜索结果
        """
        try:
            # 使用网络搜索工具
            results = self.web_tools.search_general_query(query)
            
            return {
                "status": "success",
                "query_type": "web_search",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "query_type": "web_search",
                "message": f"网络搜索时出现错误: {str(e)}"
            }
    
    def search_academic_knowledge(self, query: str) -> Dict[str, Any]:
        """
        搜索学术知识
        
        Args:
            query: 查询内容
            
        Returns:
            学术知识搜索结果
        """
        try:
            # 使用论文搜索工具
            results = self.paper_tools.search_general_query(query)
            
            return {
                "status": "success",
                "query_type": "academic_search",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "query_type": "academic_search",
                "message": f"学术搜索时出现错误: {str(e)}"
            }
    
    def process(self, query: str) -> Dict[str, Any]:
        """
        处理知识查询请求
        
        Args:
            query: 用户查询
            
        Returns:
            处理结果
        """
        try:
            # 根据查询内容决定使用哪种查询方式
            query_lower = query.lower()
            
            # 尝试识别查询类型
            if "cve" in query_lower or any(cve_format in query_lower for cve_format in ["cve-", "cve-20"]):
                # 提取CVE ID
                import re
                cve_match = re.search(r'CVE-\d{4}-\d{4,7}', query, re.IGNORECASE)
                if cve_match:
                    cve_id = cve_match.group(0).upper()
                    cve_result = self.query_vulnerability_info(cve_id)
                    
                    # 通过LLM整理结果
                    chain = self.query_template | self.llm
                    formatted_result = chain.invoke({
                        "query": query,
                        "knowledge_base_results": str(cve_result.get("results", []))
                    })
                    
                    return {
                        "status": "success",
                        "result": formatted_result.content,
                        "raw_data": cve_result
                    }
            
            elif any(keyword in query_lower for keyword in ["威胁", "threat", "attack", "malware", "trojan", "virus", "ransomware"]):
                # 识别威胁名称
                threat_name = query.replace("威胁", "").replace("是什么", "").strip()
                if not threat_name:
                    threat_name = query
                threat_result = self.query_threat_intelligence(threat_name)
                
                # 通过LLM整理结果
                chain = self.query_template | self.llm
                formatted_result = chain.invoke({
                    "query": query,
                    "knowledge_base_results": str(threat_result.get("results", []))
                })
                
                return {
                    "status": "success",
                    "result": formatted_result.content,
                    "raw_data": threat_result
                }
            
            elif any(keyword in query_lower for keyword in ["att&ck", "attack technique", "tactic", "technique"]):
                # 识别ATT&CK技术ID
                import re
                tech_match = re.search(r'T\d{4}', query, re.IGNORECASE)
                if tech_match:
                    tech_id = tech_match.group(0).upper()
                    tech_result = self.query_attack_patterns(tech_id)
                    
                    # 通过LLM整理结果
                    chain = self.query_template | self.llm
                    formatted_result = chain.invoke({
                        "query": query,
                        "knowledge_base_results": str(tech_result.get("results", []))
                    })
                    
                    return {
                        "status": "success",
                        "result": formatted_result.content,
                        "raw_data": tech_result
                    }
            
            elif any(keyword in query_lower for keyword in ["恶意软件", "malware", "病毒", "木马", "勒索软件"]):
                # 识别恶意软件名称
                malware_name = query.replace("恶意软件", "").replace("是什么", "").strip()
                if not malware_name:
                    malware_name = query
                malware_result = self.query_malware_info(malware_name)
                
                # 通过LLM整理结果
                chain = self.query_template | self.llm
                formatted_result = chain.invoke({
                    "query": query,
                    "knowledge_base_results": str(malware_result.get("results", []))
                })
                
                return {
                    "status": "success",
                    "result": formatted_result.content,
                    "raw_data": malware_result
                }
            
            else:
                # 默认进行网络搜索
                web_result = self.search_web_knowledge(query)
                
                # 通过LLM整理结果
                chain = self.query_template | self.llm
                formatted_result = chain.invoke({
                    "query": query,
                    "knowledge_base_results": str(web_result.get("results", []))
                })
                
                return {
                    "status": "success",
                    "result": formatted_result.content,
                    "raw_data": web_result
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"处理知识查询时出现错误: {str(e)}"
            }