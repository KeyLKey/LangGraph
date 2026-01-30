"""
RAG工具模块
提供向量存储和检索功能
"""
from typing import Dict, Any, List
import uuid


class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(self):
        # 模拟向量存储，实际应用中应替换为真正的向量数据库
        self.documents = {}
        self.metadata = {}
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加文档到向量存储
        
        Args:
            content: 文档内容
            metadata: 元数据
            
        Returns:
            添加结果
        """
        doc_id = str(uuid.uuid4())
        self.documents[doc_id] = content
        self.metadata[doc_id] = metadata or {}
        
        return {
            "status": "success",
            "document_id": doc_id,
            "message": "文档已成功添加到向量存储"
        }
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query: 查询内容
            top_k: 返回结果数量
            
        Returns:
            相似文档列表
        """
        # 简单的关键词匹配模拟向量搜索
        results = []
        query_lower = query.lower()
        
        for doc_id, content in self.documents.items():
            score = 0
            content_lower = content.lower()
            
            # 简单计算匹配分数
            for word in query_lower.split():
                if word in content_lower:
                    score += 1
            
            if score > 0:
                results.append({
                    "id": doc_id,
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "score": score,
                    "metadata": self.metadata[doc_id]
                })
        
        # 按分数排序并返回top_k个结果
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def clear_store(self):
        """清空向量存储"""
        self.documents.clear()
        self.metadata.clear()


class RAGTools:
    """RAG工具类"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        检索上下文信息
        
        Args:
            query: 查询内容
            top_k: 返回结果数量
            
        Returns:
            上下文信息列表
        """
        return self.vector_store.search_similar(query, top_k)
    
    def add_content_for_retrieval(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加内容以供后续检索
        
        Args:
            content: 要添加的内容
            metadata: 元数据信息
            
        Returns:
            添加结果
        """
        return self.vector_store.add_document(content, metadata)
    
    def clear_session_data(self):
        """清空会话相关的RAG数据"""
        # 在实际实现中，这里应该只清空当前会话的数据
        # 但现在我们简化为清空整个存储
        self.vector_store.clear_store()