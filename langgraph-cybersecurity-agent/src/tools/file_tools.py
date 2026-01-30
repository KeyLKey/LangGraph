"""
文件工具模块
提供文件读取、格式转换等功能
"""
from typing import Dict, Any, List
import os
from pathlib import Path
from .rag_tools import VectorStoreManager


class FileTools:
    """文件处理工具类"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.pdf', '.docx', '.json', '.csv', '.xml']
        self.vector_store = VectorStoreManager()
    
    def read_file(self, file_path: str) -> str:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串
        """
        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            if not path.exists():
                return f"错误：文件 {file_path} 不存在"
                
            if extension not in self.supported_extensions:
                return f"错误：不支持的文件格式 {extension}"
            
            # 根据文件类型读取内容
            if extension == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif extension == '.pdf':
                # 模拟PDF读取
                return f"[已读取PDF文件: {file_path}] PDF内容模拟：这是来自PDF文件的内容，实际实现中应使用PyPDF2或其他库来读取真实PDF内容。"
            elif extension == '.docx':
                # 模拟DOCX读取
                return f"[已读取DOCX文件: {file_path}] DOCX内容模拟：这是来自Word文档的内容，实际实现中应使用python-docx库来读取真实DOCX内容。"
            elif extension == '.json':
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return str(data)
            elif extension == '.csv':
                # 模拟CSV读取
                return f"[已读取CSV文件: {file_path}] CSV内容模拟：这是来自CSV文件的内容，实际实现中应使用pandas或csv库来读取真实CSV内容。"
            elif extension == '.xml':
                # 模拟XML读取
                return f"[已读取XML文件: {file_path}] XML内容模拟：这是来自XML文件的内容，实际实现中应使用xml库来读取真实XML内容。"
            else:
                return f"错误：无法处理的文件类型 {extension}"
                
        except Exception as e:
            return f"读取文件时发生错误：{str(e)}"
    
    def save_to_vector_store(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        将内容保存到向量存储中
        
        Args:
            content: 要保存的内容
            metadata: 元数据信息
            
        Returns:
            保存结果
        """
        # 这里调用RAG工具进行向量化和存储
        return self.vector_store.add_document(content, metadata)
    
    def validate_file_type(self, file_path: str) -> bool:
        """
        验证文件类型是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否支持该文件类型的布尔值
        """
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"文件不存在: {file_path}"}
            
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "extension": path.suffix,
                "modified_time": stat.st_mtime,
                "is_supported": self.validate_file_type(file_path)
            }
        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}