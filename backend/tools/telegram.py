"""Telegram Integration - notifications, approvals, monitoring."""
import logging
import os
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger("probharatai.tools.telegram")


class TelegramBot:
    """Send notifications and receive approvals via Telegram."""

    def __init__(self, token=None, chat_id=None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def is_configured(self):
        return bool(self.token and self.chat_id)

    def send_message(self, text, parse_mode="Markdown"):
        """Send a message to the configured chat."""
        if not self.is_configured():
            logger.warning("Telegram not configured. Skipping notification.")
            return {"status": "skipped", "reason": "Telegram not configured"}

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
                timeout=10,
            )
            response.raise_for_status()
            return {"status": "success", "message_id": response.json().get("result", {}).get("message_id")}
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return {"status": "error", "message": str(e)}

    def send_task_update(self, task_name, status, details=""):
        """Send a formatted task update."""
        text = f"""🤖 *ProBharatAI Update*

📋 *Task:* {task_name}
📊 *Status:* {status}
{f'📝 *Details:* {details}' if details else ''}
"""
        return self.send_message(text)

    def send_job_summary(self, applied_count, top_company="", role=""):
        """Send a job application summary."""
        text = f"""🤖 *ProBharatAI Update*

✅ Applied to *{applied_count}* jobs today
🏢 Top company: *{top_company}*
💼 Role: *{role}*
"""
        return self.send_message(text)

    def send_approval_request(self, action_description, approval_id):
        """Send an approval request to Telegram."""
        text = f"""🔐 *ProBharatAI Approval Required*

Action: {action_description}

Reply with:
✅ `/approve {approval_id}`
❌ `/reject {approval_id}`
"""
        return self.send_message(text)

    def execute(self, action: str, params: dict) -> dict:
        """Tool interface for the executor."""
        action_map = {
            "notify": lambda p: self.send_message(p.get("message", "")),
            "task_update": lambda p: self.send_task_update(
                p.get("task_name", ""), p.get("status", ""), p.get("details", "")
            ),
            "job_summary": lambda p: self.send_job_summary(
                p.get("count", 0), p.get("company", ""), p.get("role", "")
            ),
            "approval": lambda p: self.send_approval_request(
                p.get("action", ""), p.get("approval_id", "")
            ),
        }
        handler = action_map.get(action)
        if handler:
            return handler(params)
        return {"status": "error", "message": f"Unknown telegram action: {action}"}


# Global instance
telegram = TelegramBot()
