#!/usr/bin/env python3
"""
Memory Management for Conversation History
Manages conversation history with limits, cleanup, and optimization
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque
from pathlib import Path

from rich.console import Console

console = Console()


@dataclass
class ConversationMessage:
    """Single conversation message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = field(default_factory=time.time)
    tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Conversation session with metadata"""
    session_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    total_tokens: int = 0
    provider: str = ""
    model: str = ""


@dataclass
class MemoryConfig:
    """Memory management configuration"""
    max_messages_per_session: int = 100
    max_total_messages: int = 1000
    max_session_age_hours: int = 24
    max_inactive_hours: int = 2
    max_tokens_per_session: int = 50000
    max_total_tokens: int = 500000
    cleanup_interval_minutes: int = 30
    persist_to_disk: bool = True
    storage_path: str = ""


class ConversationMemoryManager:
    """Manages conversation history with automatic cleanup and optimization"""
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.sessions: Dict[str, ConversationSession] = {}
        self.last_cleanup = time.time()
        
        # Setup storage
        if self.config.persist_to_disk and self.config.storage_path:
            self.storage_path = Path(self.config.storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
    
    def create_session(self, session_id: str, provider: str = "", model: str = "") -> ConversationSession:
        """Create a new conversation session"""
        if session_id in self.sessions:
            console.print(f"[yellow]⚠ Session {session_id} already exists, returning existing session[/yellow]")
            return self.sessions[session_id]
        
        session = ConversationSession(
            session_id=session_id,
            provider=provider,
            model=model
        )
        
        self.sessions[session_id] = session
        self._maybe_cleanup()
        
        console.print(f"[green]✅ Created conversation session: {session_id}[/green]")
        return session
    
    def add_message(self, session_id: str, role: str, content: str, tokens: int = 0, **metadata) -> bool:
        """Add a message to a conversation session"""
        if session_id not in self.sessions:
            console.print(f"[red]❌ Session {session_id} not found[/red]")
            return False
        
        session = self.sessions[session_id]
        
        # Check limits
        if len(session.messages) >= self.config.max_messages_per_session:
            self._trim_session_messages(session)
        
        if session.total_tokens + tokens > self.config.max_tokens_per_session:
            self._trim_session_tokens(session, tokens)
        
        # Create message
        message = ConversationMessage(
            role=role,
            content=content,
            tokens=tokens,
            metadata=metadata
        )
        
        # Add to session
        session.messages.append(message)
        session.total_tokens += tokens
        session.last_activity = time.time()
        
        self._maybe_cleanup()
        self._maybe_persist()
        
        return True
    
    def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get messages from a session"""
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id].messages
        if limit:
            return messages[-limit:]
        return messages
    
    def get_session_context(self, session_id: str, max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
        """Get session context formatted for LLM API"""
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        context = []
        total_tokens = 0
        
        # Start from the most recent messages and work backwards
        for message in reversed(session.messages):
            if max_tokens and total_tokens + message.tokens > max_tokens:
                break
            
            context.insert(0, {
                "role": message.role,
                "content": message.content
            })
            total_tokens += message.tokens
        
        return context
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._maybe_persist()
            console.print(f"[green]✅ Deleted session: {session_id}[/green]")
            return True
        return False
    
    def clear_all_sessions(self) -> None:
        """Clear all conversation sessions"""
        self.sessions.clear()
        self._maybe_persist()
        console.print("[green]✅ Cleared all conversation sessions[/green]")
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "total_tokens": session.total_tokens,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "age_hours": (time.time() - session.created_at) / 3600,
            "inactive_hours": (time.time() - session.last_activity) / 3600,
            "provider": session.provider,
            "model": session.model
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global memory statistics"""
        total_messages = sum(len(session.messages) for session in self.sessions.values())
        total_tokens = sum(session.total_tokens for session in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "memory_usage_percent": {
                "sessions": len(self.sessions) / max(1, self.config.max_total_messages) * 100,
                "messages": total_messages / max(1, self.config.max_total_messages) * 100,
                "tokens": total_tokens / max(1, self.config.max_total_tokens) * 100
            },
            "oldest_session": min((s.created_at for s in self.sessions.values()), default=0),
            "newest_session": max((s.created_at for s in self.sessions.values()), default=0)
        }
    
    def _trim_session_messages(self, session: ConversationSession) -> None:
        """Trim messages from a session to stay within limits"""
        target_count = int(self.config.max_messages_per_session * 0.8)  # Keep 80% of limit
        
        if len(session.messages) > target_count:
            # Keep system messages and recent messages
            system_messages = [msg for msg in session.messages if msg.role == 'system']
            other_messages = [msg for msg in session.messages if msg.role != 'system']
            
            # Keep the most recent messages
            recent_messages = other_messages[-target_count + len(system_messages):]
            
            # Update session
            session.messages = system_messages + recent_messages
            session.total_tokens = sum(msg.tokens for msg in session.messages)
            
            console.print(f"[yellow]⚠ Trimmed session {session.session_id} to {len(session.messages)} messages[/yellow]")
    
    def _trim_session_tokens(self, session: ConversationSession, new_tokens: int) -> None:
        """Trim session to make room for new tokens"""
        target_tokens = int(self.config.max_tokens_per_session * 0.8)  # Keep 80% of limit
        
        while session.total_tokens + new_tokens > target_tokens and session.messages:
            # Remove oldest non-system message
            for i, msg in enumerate(session.messages):
                if msg.role != 'system':
                    removed_msg = session.messages.pop(i)
                    session.total_tokens -= removed_msg.tokens
                    break
            else:
                # No non-system messages to remove
                break
        
        console.print(f"[yellow]⚠ Trimmed session {session.session_id} to {session.total_tokens} tokens[/yellow]")
    
    def _maybe_cleanup(self) -> None:
        """Perform cleanup if needed"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.config.cleanup_interval_minutes * 60:
            self._cleanup_old_sessions()
            self.last_cleanup = current_time
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old and inactive sessions"""
        current_time = time.time()
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            # Check age
            age_hours = (current_time - session.created_at) / 3600
            if age_hours > self.config.max_session_age_hours:
                sessions_to_remove.append(session_id)
                continue
            
            # Check inactivity
            inactive_hours = (current_time - session.last_activity) / 3600
            if inactive_hours > self.config.max_inactive_hours:
                sessions_to_remove.append(session_id)
                continue
        
        # Remove old sessions
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            console.print(f"[yellow]🧹 Cleaned up {len(sessions_to_remove)} old sessions[/yellow]")
        
        # Check global limits
        self._enforce_global_limits()
    
    def _enforce_global_limits(self) -> None:
        """Enforce global memory limits"""
        total_messages = sum(len(session.messages) for session in self.sessions.values())
        total_tokens = sum(session.total_tokens for session in self.sessions.values())
        
        # Remove oldest sessions if over limits
        if (len(self.sessions) > self.config.max_total_messages or 
            total_messages > self.config.max_total_messages or 
            total_tokens > self.config.max_total_tokens):
            
            # Sort sessions by last activity (oldest first)
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1].last_activity
            )
            
            removed_count = 0
            for session_id, session in sorted_sessions:
                if (len(self.sessions) <= self.config.max_total_messages * 0.8 and
                    total_messages <= self.config.max_total_messages * 0.8 and
                    total_tokens <= self.config.max_total_tokens * 0.8):
                    break
                
                total_messages -= len(session.messages)
                total_tokens -= session.total_tokens
                del self.sessions[session_id]
                removed_count += 1
            
            if removed_count > 0:
                console.print(f"[yellow]🧹 Removed {removed_count} sessions to enforce global limits[/yellow]")
    
    def _maybe_persist(self) -> None:
        """Persist to disk if configured"""
        if self.config.persist_to_disk and self.config.storage_path:
            self._save_to_disk()
    
    def _save_to_disk(self) -> None:
        """Save sessions to disk"""
        try:
            storage_file = self.storage_path / "conversations.json"
            
            # Convert sessions to serializable format
            data = {
                "sessions": {
                    session_id: asdict(session)
                    for session_id, session in self.sessions.items()
                },
                "last_cleanup": self.last_cleanup
            }
            
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            console.print(f"[red]❌ Error saving conversations: {e}[/red]")
    
    def _load_from_disk(self) -> None:
        """Load sessions from disk"""
        try:
            storage_file = self.storage_path / "conversations.json"
            
            if not storage_file.exists():
                return
            
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore sessions
            for session_id, session_data in data.get("sessions", {}).items():
                # Convert messages back to ConversationMessage objects
                messages = [
                    ConversationMessage(**msg_data)
                    for msg_data in session_data.get("messages", [])
                ]
                
                session = ConversationSession(
                    session_id=session_data["session_id"],
                    messages=messages,
                    created_at=session_data["created_at"],
                    last_activity=session_data["last_activity"],
                    total_tokens=session_data["total_tokens"],
                    provider=session_data.get("provider", ""),
                    model=session_data.get("model", "")
                )
                
                self.sessions[session_id] = session
            
            self.last_cleanup = data.get("last_cleanup", time.time())
            
            console.print(f"[green]✅ Loaded {len(self.sessions)} conversation sessions from disk[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error loading conversations: {e}[/red]")


# Global memory manager
memory_manager = ConversationMemoryManager()
