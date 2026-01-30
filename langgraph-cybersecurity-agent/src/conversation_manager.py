"""
对话管理模块
使用LangGraph Checkpointer + Redis维护完整会话历史
"""
from typing import Dict, Any, Optional
import redis
from langgraph.checkpoint.redis import RedisSaver
from .config import config


class ConversationManager:
    """对话管理类"""
    
    def __init__(self):
        # Redis连接
        self.redis_client = redis.Redis.from_url(config.REDIS_URL)
        
        # 检查点管理器 (预留位置，暂不启用)
        # self.checkpointer = RedisSaver(self.redis_client) if config.CHECKPOINTER_ENABLED else None
        
        # 会话数据存储
        self.sessions = {}
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """
        创建新会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话初始化信息
        """
        self.sessions[session_id] = {
            "history": [],
            "created_at": __import__('datetime').datetime.now().isoformat(),
            "last_accessed": __import__('datetime').datetime.now().isoformat()
        }
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "会话创建成功"
        }
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话历史数据
        """
        session = self.sessions.get(session_id)
        if session:
            session["last_accessed"] = __import__('datetime').datetime.now().isoformat()
            return session
        return None
    
    def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """
        向会话添加消息
        
        Args:
            session_id: 会话ID
            role: 消息角色 (user, assistant等)
            content: 消息内容
            
        Returns:
            添加是否成功
        """
        session = self.sessions.get(session_id)
        if not session:
            self.create_session(session_id)
            session = self.sessions[session_id]
        
        session["history"].append({
            "role": role,
            "content": content,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        session["last_accessed"] = __import__('datetime').datetime.now().isoformat()
        
        return True
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            清空是否成功
        """
        if session_id in self.sessions:
            self.sessions[session_id]["history"] = []
            self.sessions[session_id]["last_accessed"] = __import__('datetime').datetime.now().isoformat()
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除是否成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> list:
        """
        列出所有会话ID
        
        Returns:
            会话ID列表
        """
        return list(self.sessions.keys())


# 注意：在当前实现中，我们暂时不启用Redis持久化存储
# 因为用户要求暂时关闭对话管理功能，但保留合适的位置
class DummyConversationManager:
    """虚拟对话管理类 - 当前使用的版本"""
    
    def __init__(self):
        """初始化虚拟对话管理器"""
        pass
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """创建虚拟会话"""
        return {
            "session_id": session_id,
            "status": "disabled",  # 表示功能被禁用
            "message": "对话管理功能当前已禁用，会话不会持久化"
        }
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取虚拟会话历史"""
        return {
            "history": [],
            "session_id": session_id,
            "status": "disabled"
        }
    
    def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """添加消息到虚拟会话"""
        # 什么都不做，因为功能被禁用
        return True
    
    def clear_session(self, session_id: str) -> bool:
        """清空虚拟会话"""
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """删除虚拟会话"""
        return True
    
    def list_sessions(self) -> list:
        """列出虚拟会话"""
        return []


# 使用虚拟版本作为当前实现
conversation_manager = DummyConversationManager()