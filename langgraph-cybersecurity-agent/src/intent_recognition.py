"""
意图识别模块
识别用户查询的意图类型，支持复合意图
"""
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from .config import config


class IntentRecognizer:
    """意图识别类"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        
        # 意图识别提示词模板
        self.intent_template = PromptTemplate(
            input_variables=["query"],
            template="""
你是网络安全助手的意图识别系统。请分析用户查询并识别其意图类型。

意图类型包括：
1. SecurityAnalysis - 威胁分析、漏洞评估、防护策略生成等
2. KnowledgeQuery - 查询定义、事实、图谱等知识
3. FileUnderstanding - 基于文件的任务
4. Fallback - 兜底意图，引导用户到网络安全内容

用户可能同时有多个意图，比如："分析这份CTI报告，判断是不是勒索软件攻击，并告诉我该怎么防御，用通俗的话解释。"

用户查询：{query}

请严格按照以下JSON格式回复，支持多种意图：
{{"intents": ["intent1", "intent2", ...], "confidence": "高/中/低", "explanation": "意图识别说明"}}
"""
        )
    
    def recognize_intent(self, query: str) -> Dict[str, Any]:
        """
        识别查询意图
        
        Args:
            query: 用户查询字符串
            
        Returns:
            包含意图列表、置信度和说明的字典
        """
        try:
            chain = self.intent_template | self.llm
            result = chain.invoke({"query": query})
            
            # 解析LLM返回的结果
            response_text = result.content.strip()
            
            # 尝试解析JSON格式的响应
            if response_text.startswith('{') and response_text.endswith('}'):
                import json
                try:
                    parsed_result = json.loads(response_text)
                    return parsed_result
                except json.JSONDecodeError:
                    pass
            
            # 如果无法解析JSON，返回默认值
            return {
                "intents": ["Fallback"],
                "confidence": "低",
                "explanation": "未能正确解析意图，使用兜底意图"
            }
            
        except Exception as e:
            return {
                "intents": ["Fallback"],
                "confidence": "低",
                "explanation": f"意图识别异常：{str(e)}"
            }
    
    def get_primary_intent(self, query: str) -> str:
        """
        获取主要意图
        
        Args:
            query: 用户查询字符串
            
        Returns:
            主要意图字符串
        """
        result = self.recognize_intent(query)
        intents = result.get("intents", [])
        return intents[0] if intents else "Fallback"
    
    def has_security_analysis_intent(self, query: str) -> bool:
        """
        检查是否包含安全分析意图
        
        Args:
            query: 用户查询字符串
            
        Returns:
            是否包含安全分析意图的布尔值
        """
        result = self.recognize_intent(query)
        return "SecurityAnalysis" in result.get("intents", [])
    
    def has_knowledge_query_intent(self, query: str) -> bool:
        """
        检查是否包含知识查询意图
        
        Args:
            query: 用户查询字符串
            
        Returns:
            是否包含知识查询意图的布尔值
        """
        result = self.recognize_intent(query)
        return "KnowledgeQuery" in result.get("intents", [])
    
    def has_file_understanding_intent(self, query: str) -> bool:
        """
        检查是否包含文件理解意图
        
        Args:
            query: 用户查询字符串
            
        Returns:
            是否包含文件理解意图的布尔值
        """
        result = self.recognize_intent(query)
        return "FileUnderstanding" in result.get("intents", [])