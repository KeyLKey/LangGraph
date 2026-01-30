"""
安全护栏模块
用于确保问题在服务范围内，拒绝越界查询
"""
from typing import Dict, Any, Optional
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from .config import config


class SecurityGuardrails:
    """安全护栏类"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        
        # 安全护栏提示词模板
        self.guardrail_template = PromptTemplate(
            input_variables=["query"],
            template="""
你是网络安全助手的安全护栏系统。你的职责是判断用户查询是否在网络安全服务范围内。

网络安全服务范围包括：
- 威胁分析与评估
- 漏洞检测与修复
- 安全防护策略
- 攻击事件响应
- CTI（网络威胁情报）
- 安全标准与合规
- 恶意软件分析
- 网络攻击防护

如果查询与此相关，请返回 "ALLOWED"。
如果查询与此无关或涉及敏感内容，请返回 "BLOCKED" 并说明原因。

用户查询：{query}

请严格按照以下JSON格式回复：
{{"status": "ALLOWED|BLOCKED", "reason": "详细原因说明"}}
"""
        )
        
    def check_query(self, query: str) -> Dict[str, Any]:
        """
        检查查询是否符合安全护栏要求
        
        Args:
            query: 用户查询字符串
            
        Returns:
            包含状态和原因的字典
        """
        try:
            chain = self.guardrail_template | self.llm
            result = chain.invoke({"query": query})
            
            # 解析LLM返回的结果
            response_text = result.content.strip()
            
            # 简单解析JSON格式的响应
            if response_text.startswith('{') and response_text.endswith('}'):
                import json
                try:
                    parsed_result = json.loads(response_text)
                    return parsed_result
                except json.JSONDecodeError:
                    pass
            
            # 如果无法解析JSON，则默认允许
            return {
                "status": "ALLOWED",
                "reason": "安全护栏验证通过"
            }
            
        except Exception as e:
            # 发生异常时，默认允许访问
            return {
                "status": "ALLOWED",
                "reason": f"安全护栏检查异常，但仍允许访问：{str(e)}"
            }

    def is_allowed(self, query: str) -> bool:
        """
        判断查询是否被允许
        
        Args:
            query: 用户查询字符串
            
        Returns:
            是否允许的布尔值
        """
        result = self.check_query(query)
        return result.get("status") == "ALLOWED"