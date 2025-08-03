"""
Modern Streaming Response Handler for AI Helper Agent
Uses OpenAI client for real-time LLM response streaming with Rich UI
"""

import asyncio
import sys
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from ..core.llm_client import UnifiedLLMClient

console = Console()

class ModernStreamingHandler:
    """Modern streaming handler with Rich UI integration"""
    
    def __init__(self, llm_client: UnifiedLLMClient):
        self.llm_client = llm_client
        self.response_buffer = ""
        self.total_tokens = 0
        self.start_time = None
        
    async def stream_response(self, query: str, system_prompt: str = None,
                             show_stats: bool = True) -> str:
        """Stream response with beautiful Rich formatting"""
        try:
            self.start_time = time.time()
            self.response_buffer = ""
            self.total_tokens = 0
            
            # Show AI indicator with Rich formatting
            console.print()
            console.print(Panel.fit(
                f"[bold blue]🤖 AI Assistant[/bold blue]\n[dim]Thinking...[/dim]",
                border_style="blue",
                padding=(0, 1)
            ))
            console.print()
            
            # Create a Live display for streaming
            display_text = ""
            
            # Stream the response with Rich Live updating and Markdown rendering
            with Live(refresh_per_second=10, console=console) as live:
                async for chunk in self.llm_client.stream_completion(query, system_prompt):
                    if chunk:
                        display_text += chunk
                        self.response_buffer += chunk
                        self.total_tokens += len(chunk.split())
                        
                        # Try to render as Markdown, fall back to Text if it fails
                        try:
                            # Render as Rich Markdown for proper formatting
                            response_content = Markdown(display_text)
                        except:
                            # Fallback to styled text
                            response_content = Text(display_text)
                            response_content.stylize("white")
                        
                        # Update the live display with properly formatted content
                        live.update(Panel(
                            response_content,
                            title="[bold green]🤖 AI Response[/bold green]",
                            border_style="green",
                            padding=(1, 2)
                        ))
            
            # Show completion stats with Rich formatting
            if show_stats:
                elapsed_time = time.time() - self.start_time
                tokens_per_second = self.total_tokens / elapsed_time if elapsed_time > 0 else 0
                
                stats_table = Table(show_header=False, box=None, padding=(0, 1))
                stats_table.add_column(style="green")
                stats_table.add_column(style="cyan") 
                stats_table.add_column(style="yellow")
                
                stats_table.add_row(
                    f"📊 {self.total_tokens} tokens",
                    f"⏱️ {elapsed_time:.2f}s", 
                    f"🚀 {tokens_per_second:.1f} tok/s"
                )
                
                console.print()
                console.print(Panel.fit(
                    stats_table,
                    title="[dim]Performance Stats[/dim]",
                    border_style="dim"
                ))
            
            console.print()
            return self.response_buffer
            
        except Exception as e:
            error_panel = Panel.fit(
                f"[red]❌ Streaming error: {str(e)}[/red]",
                title="[red]Error[/red]",
                border_style="red"
            )
            console.print(error_panel)
            return f"❌ Streaming error: {e}"
    
    async def quick_response(self, query: str, system_prompt: str = None) -> str:
        """Quick response without streaming UI"""
        return await self.stream_response(query, system_prompt)
    
    async def stream_conversation(self, messages: List[Dict[str, str]], 
                                show_stats: bool = True) -> str:
        """Stream response for conversation messages with Rich UI"""
        try:
            self.start_time = time.time()
            self.response_buffer = ""
            self.total_tokens = 0
            
            # Show AI indicator with Rich formatting
            console.print()
            console.print(Panel.fit(
                f"[bold blue]🤖 AI Assistant[/bold blue]\n[dim]Processing your request...[/dim]",
                border_style="blue",
                padding=(0, 1)
            ))
            console.print()
            
            # Create a Live display for streaming
            display_text = ""
            
            # Stream the response with Rich Live updating and Markdown rendering
            with Live(refresh_per_second=10, console=console) as live:
                async for chunk in self.llm_client.stream_chat_completion(messages):
                    if chunk:
                        display_text += chunk
                        self.response_buffer += chunk
                        self.total_tokens += len(chunk.split())
                        
                        # Try to render as Markdown, fall back to Text if it fails
                        try:
                            # Render as Rich Markdown for proper formatting
                            response_content = Markdown(display_text)
                        except:
                            # Fallback to styled text
                            response_content = Text(display_text)
                            response_content.stylize("white")
                        
                        # Update the live display with properly formatted content
                        live.update(Panel(
                            response_content,
                            title="[bold green]🤖 AI Response[/bold green]",
                            border_style="green",
                            padding=(1, 2)
                        ))
            
            # Show completion stats with Rich formatting
            if show_stats:
                elapsed_time = time.time() - self.start_time
                tokens_per_second = self.total_tokens / elapsed_time if elapsed_time > 0 else 0
                
                stats_table = Table(show_header=False, box=None, padding=(0, 1))
                stats_table.add_column(style="green")
                stats_table.add_column(style="cyan") 
                stats_table.add_column(style="yellow")
                
                stats_table.add_row(
                    f"📊 {self.total_tokens} tokens",
                    f"⏱️ {elapsed_time:.2f}s", 
                    f"🚀 {tokens_per_second:.1f} tok/s"
                )
                
                console.print()
                console.print(Panel.fit(
                    stats_table,
                    title="[dim]Performance Stats[/dim]",
                    border_style="dim"
                ))
            
            console.print()
            return self.response_buffer
            
        except Exception as e:
            error_panel = Panel.fit(
                f"[red]❌ Streaming error: {str(e)}[/red]",
                title="[red]Error[/red]",
                border_style="red"
            )
            console.print(error_panel)
            return f"❌ Streaming error: {e}"


class ConversationManager:
    """Manages conversation history with Rich UI streaming support"""
    
    def __init__(self, llm_client: UnifiedLLMClient, session_id: str = "default"):
        self.llm_client = llm_client
        self.session_id = session_id
        self.conversation_history = []
        self.streaming_handler = ModernStreamingHandler(llm_client)
        self.message_count = 0
        self.session_start_time = datetime.now()
        
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.message_count += 1
        
    async def chat(self, user_input: str, system_prompt: str = None) -> str:
        """Chat with AI using Rich UI streaming"""
        
        # Show user message with Rich formatting
        user_panel = Panel.fit(
            f"[bold cyan]{user_input}[/bold cyan]",
            title="[bold cyan]You[/bold cyan]",
            border_style="cyan",
            padding=(0, 1)
        )
        console.print(user_panel)
        
        # Add user message to history
        self.add_message("user", user_input)
        
        # Prepare messages for API
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Get AI response with streaming
        ai_response = await self.streaming_handler.stream_conversation(messages)
        
        # Add AI response to history
        self.add_message("assistant", ai_response)
        
        return ai_response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.message_count = 0
        
        console.print(Panel.fit(
            "[yellow]✨ Conversation history cleared[/yellow]",
            title="[dim]Reset[/dim]",
            border_style="yellow"
        ))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        user_messages = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.conversation_history if msg["role"] == "assistant")
        
        return {
            "session_id": self.session_id,
            "total_messages": len(self.conversation_history),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "session_duration": (datetime.now() - self.session_start_time).total_seconds()
        }
    
    def show_history(self, limit: int = 5):
        """Show conversation history with Rich formatting"""
        if not self.conversation_history:
            console.print(Panel.fit(
                "[dim]No conversation history yet[/dim]",
                title="History",
                border_style="dim"
            ))
            return
        
        # Show recent messages
        recent_messages = self.conversation_history[-limit:]
        
        history_table = Table(title="📚 Recent Conversation History", show_header=True)
        history_table.add_column("Role", style="cyan", width=12)
        history_table.add_column("Message", style="white", width=60)
        history_table.add_column("Time", style="dim", width=20)
        
        for msg in recent_messages:
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            role_display = f"{role_emoji} {msg['role'].title()}"
            message_preview = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
            
            history_table.add_row(role_display, message_preview, timestamp)
        
        console.print(history_table)


# Factory functions
def create_streaming_handler(llm_client: UnifiedLLMClient) -> ModernStreamingHandler:
    """Create a streaming handler instance"""
    return ModernStreamingHandler(llm_client)

def create_conversation_manager(llm_client: UnifiedLLMClient, session_id: str = "default") -> ConversationManager:
    """Create a conversation manager instance"""
    return ConversationManager(llm_client, session_id)
