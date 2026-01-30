"""
文件理解智能体模块
负责将原始文件转换为结构化、可被其他智能体消费的中间语义表示
"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from ..tools.file_tools import FileTools
from ..tools.rag_tools import RAGTools
from ..config import config


class FileUnderstandingAgent:
    """文件理解智能体类"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=0.2,
            api_key=config.OPENAI_API_KEY
        )
        
        # 初始化相关工具
        self.file_tools = FileTools()
        self.rag_tools = RAGTools()
        
        # 文件内容分析提示词模板
        self.analysis_template = PromptTemplate(
            input_variables=["file_content", "query"],
            template="""
你是网络安全文件分析专家。请分析以下文件内容并提取关键信息：

文件内容：
{file_content}

分析目标：{query}

请提取以下信息：
1. 文件类型和基本信息
2. 关键安全指标和数据
3. 识别的安全事件或威胁
4. 重要实体（IP地址、域名、哈希值等）
5. 时间线和行为模式
6. 结论和建议

请提供结构化的分析结果。
"""
        )
        
        # 文件总结提示词模板
        self.summary_template = PromptTemplate(
            input_variables=["file_content"],
            template="""
你是网络安全文档总结专家。请对以下文件内容进行简洁准确的总结：

文件内容：
{file_content}

请提供一个简明扼要的总结，包括：
1. 文件主要内容概述
2. 关键发现或结论
3. 重要数据点
4. 需要注意的安全事项

总结应控制在200字以内。
"""
        )
    
    def analyze_file_content(self, file_path: str, query: str = "") -> Dict[str, Any]:
        """
        分析文件内容
        
        Args:
            file_path: 文件路径
            query: 分析目标查询
            
        Returns:
            文件分析结果
        """
        try:
            # 读取文件内容
            file_content = self.file_tools.read_file(file_path)
            
            if file_content.startswith("错误：") or file_content.startswith("错误："):
                return {
                    "status": "error",
                    "message": f"读取文件失败: {file_content}"
                }
            
            # 使用LLM分析文件内容
            if query:
                chain = self.analysis_template | self.llm
                result = chain.invoke({"file_content": file_content, "query": query})
            else:
                chain = self.summary_template | self.llm
                result = chain.invoke({"file_content": file_content})
            
            # 将分析结果添加到向量存储中，便于后续检索
            metadata = {
                "file_path": file_path,
                "analysis_type": "file_analysis",
                "timestamp": str(__import__('datetime').datetime.now())
            }
            self.rag_tools.add_content_for_retrieval(result.content, metadata)
            
            return {
                "status": "success",
                "file_path": file_path,
                "analysis_result": result.content,
                "content_length": len(file_content),
                "metadata": metadata
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"分析文件时出现错误: {str(e)}"
            }
    
    def extract_security_indicators(self, file_path: str) -> Dict[str, Any]:
        """
        从文件中提取安全指标
        
        Args:
            file_path: 文件路径
            
        Returns:
            安全指标提取结果
        """
        try:
            # 读取文件内容
            file_content = self.file_tools.read_file(file_path)
            
            if file_content.startswith("错误：") or file_content.startswith("错误："):
                return {
                    "status": "error",
                    "message": f"读取文件失败: {file_content}"
                }
            
            # 提取安全相关指标的提示词
            indicator_extraction_prompt = PromptTemplate(
                input_variables=["file_content"],
                template="""
请从以下文件内容中提取所有安全相关指标和实体：

文件内容：
{file_content}

请提取并分类以下类型的信息：
1. IP地址 (IPv4/IPv6)
2. 域名
3. 文件哈希 (MD5, SHA1, SHA256)
4. URL链接
5. 注册表项
6. 进程名
7. 服务名
8. 端口号
9. CVE编号
10. 其他可疑实体

请以JSON格式返回提取的指标，格式如下：
{{
  "ips": ["ip1", "ip2", ...],
  "domains": ["domain1", "domain2", ...],
  "hashes": ["hash1", "hash2", ...],
  "urls": ["url1", "url2", ...],
  "registry_keys": ["key1", "key2", ...],
  "processes": ["process1", "process2", ...],
  "services": ["service1", "service2", ...],
  "ports": ["port1", "port2", ...],
  "cves": ["cve1", "cve2", ...],
  "other_indicators": ["indicator1", "indicator2", ...]
}}
"""
            )
            
            chain = indicator_extraction_prompt | self.llm
            result = chain.invoke({"file_content": file_content})
            
            # 尝试解析LLM返回的JSON
            import json
            extracted_indicators = {}
            try:
                # 提取JSON部分
                content = result.content.strip()
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = content[json_start:json_end]
                    extracted_indicators = json.loads(json_str)
                else:
                    extracted_indicators = {"raw_response": content}
            except json.JSONDecodeError:
                extracted_indicators = {"raw_response": result.content}
            
            return {
                "status": "success",
                "file_path": file_path,
                "extracted_indicators": extracted_indicators,
                "content_length": len(file_content)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"提取安全指标时出现错误: {str(e)}"
            }
    
    def convert_to_structured_format(self, file_path: str) -> Dict[str, Any]:
        """
        将文件转换为结构化格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            结构化格式转换结果
        """
        try:
            # 读取文件内容
            file_content = self.file_tools.read_file(file_path)
            
            if file_content.startswith("错误：") or file_content.startswith("错误："):
                return {
                    "status": "error",
                    "message": f"读取文件失败: {file_content}"
                }
            
            # 转换为结构化格式的提示词
            structuring_prompt = PromptTemplate(
                input_variables=["file_content"],
                template="""
请将以下文件内容转换为结构化的JSON格式，便于其他系统处理：

文件内容：
{file_content}

请转换为以下JSON格式：
{{
  "original_type": "原文件类型",
  "summary": "内容摘要",
  "entities": {{
    "people": ["人名列表"],
    "organizations": ["组织名列表"],
    "locations": ["地点列表"],
    "dates": ["日期列表"],
    "technical_terms": ["技术术语列表"]
  }},
  "security_elements": {{
    "threats_identified": ["识别的威胁"],
    "vulnerabilities_mentioned": ["提及的漏洞"],
    "recommendations": ["建议"],
    "indicators_of_compromise": ["妥协指标"]
  }},
  "metadata": {{
    "word_count": 数字,
    "language": "语言",
    "confidence_level": "high/medium/low"
  }}
}}
"""
            )
            
            chain = structuring_prompt | self.llm
            result = chain.invoke({"file_content": file_content})
            
            # 尝试解析LLM返回的JSON
            import json
            structured_data = {}
            try:
                # 提取JSON部分
                content = result.content.strip()
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = content[json_start:json_end]
                    structured_data = json.loads(json_str)
                else:
                    structured_data = {"raw_content": content}
            except json.JSONDecodeError:
                structured_data = {"raw_content": result.content}
            
            return {
                "status": "success",
                "file_path": file_path,
                "structured_data": structured_data,
                "content_length": len(file_content)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"转换为结构化格式时出现错误: {str(e)}"
            }
    
    def process(self, file_path_or_content: str, query: str = "") -> Dict[str, Any]:
        """
        处理文件理解请求
        
        Args:
            file_path_or_content: 文件路径或直接的内容
            query: 分析目标查询
            
        Returns:
            处理结果
        """
        # 检查输入是文件路径还是直接内容
        if file_path_or_content.startswith('/') or '.' in file_path_or_content.split('/')[-1]:
            # 看起来像是文件路径
            return self.analyze_file_content(file_path_or_content, query)
        else:
            # 直接是内容，我们模拟将其保存到临时位置然后处理
            # 在实际实现中，这将需要更复杂的逻辑来处理直接传入的内容
            return {
                "status": "success",
                "analysis_result": f"已接收直接内容进行分析，内容长度: {len(file_path_or_content)} 字符",
                "query": query,
                "content_length": len(file_path_or_content)
            }