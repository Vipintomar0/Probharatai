"""Memory Manager - maintains conversation and task context."""
import json
import logging
from datetime import datetime
from typing import Optional
from database.models import get_all_tasks, get_task_steps, get_logs

logger = logging.getLogger("probharatai.memory")


class MemoryManager:
    """Manages conversation history and task context for the AI agent."""

    def __init__(self, max_history=20):
        self.max_history = max_history
        self.conversation_history = []
        self.context = {}

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        # Trim if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_messages(self) -> list:
        """Get conversation history in LLM-compatible format."""
        return [{"role": m["role"], "content": m["content"]} for m in self.conversation_history]

    def set_context(self, key: str, value):
        """Store contextual information."""
        self.context[key] = value

    def get_context(self, key: str, default=None):
        """Retrieve contextual information."""
        return self.context.get(key, default)

    def get_recent_tasks_summary(self, limit=5) -> str:
        """Get a summary of recent tasks for context."""
        tasks = get_all_tasks(limit=limit)
        if not tasks:
            return "No previous tasks."

        summary_parts = []
        for task in tasks:
            steps = get_task_steps(task["id"])
            step_summary = ", ".join(s["description"][:50] for s in steps[:3])
            summary_parts.append(
                f"- Task #{task['id']}: {task['prompt'][:80]} "
                f"[{task['status']}] Steps: {step_summary}"
            )
        return "\n".join(summary_parts)

    def build_system_context(self) -> str:
        """Build contextual system message for the AI."""
        parts = [
            "You are ProBharatAI, an AI desktop automation assistant.",
            "You can control the browser, file system, and desktop.",
            "",
            "Recent task history:",
            self.get_recent_tasks_summary(),
        ]

        if self.context:
            parts.append("\nCurrent context:")
            for k, v in self.context.items():
                parts.append(f"  {k}: {v}")

        return "\n".join(parts)

    def clear(self):
        """Clear conversation history and context."""
        self.conversation_history.clear()
        self.context.clear()


# Global memory instance
memory = MemoryManager()
