"""Executor Agent - runs planned steps using the appropriate tools."""
import json
import logging
import time
from database.models import (
    create_task, update_task, create_task_step, update_task_step,
    create_approval, get_pending_approvals, add_log
)
from agents.planner import create_plan
from config import REQUIRE_APPROVAL

logger = logging.getLogger("probharatai.executor")

# Tool registry
_TOOLS = {}


def register_tool(name, handler):
    """Register a tool handler."""
    _TOOLS[name] = handler


def get_tool(name):
    """Get a registered tool handler."""
    return _TOOLS.get(name)


class TaskExecutor:
    """Executes a planned task step by step."""

    def __init__(self, socketio=None):
        self.socketio = socketio
        self._register_default_tools()

    def _register_default_tools(self):
        """Register all available tools."""
        try:
            from tools.browser import BrowserTool
            register_tool("browser", BrowserTool())
        except Exception as e:
            logger.warning(f"Browser tool not available: {e}")

        try:
            from tools.filesystem import FileSystemTool
            register_tool("filesystem", FileSystemTool())
        except Exception as e:
            logger.warning(f"Filesystem tool not available: {e}")

        try:
            from tools.system import SystemTool
            register_tool("system", SystemTool())
        except Exception as e:
            logger.warning(f"System tool not available: {e}")

        try:
            from tools.jobs import JobsTool
            register_tool("jobs", JobsTool())
        except Exception as e:
            logger.warning(f"Jobs tool not available: {e}")

    def _emit(self, event, data):
        """Emit a SocketIO event if available."""
        if self.socketio:
            self.socketio.emit(event, data)

    async def execute_prompt(self, prompt: str, provider=None) -> dict:
        """Full pipeline: plan → execute → report."""
        # Create task in DB
        task_id = create_task(prompt)
        update_task(task_id, status="planning")
        self._emit("task_update", {"task_id": task_id, "status": "planning"})
        add_log(f"New task created: {prompt}", source="executor")

        try:
            # Step 1: Plan
            plan = create_plan(prompt, provider=provider)
            update_task(task_id, status="executing", plan=json.dumps(plan))
            self._emit("task_update", {"task_id": task_id, "status": "executing", "plan": plan})

            # Step 2: Create steps in DB
            step_records = []
            for step_data in plan:
                step_id = create_task_step(
                    task_id=task_id,
                    step_number=step_data.get("step", 0),
                    description=step_data.get("description", ""),
                    tool=step_data.get("tool"),
                )
                step_records.append({"id": step_id, **step_data})

            # Step 3: Execute each step
            results = []
            for step in step_records:
                step_id = step["id"]
                tool_name = step.get("tool", "")
                action = step.get("action", "")
                params = step.get("params", {})

                update_task_step(step_id, status="running")
                self._emit("step_update", {
                    "task_id": task_id,
                    "step_id": step_id,
                    "status": "running",
                    "description": step.get("description"),
                })

                try:
                    # Check if approval is needed
                    if REQUIRE_APPROVAL and self._needs_approval(step):
                        approval_id = create_approval(task_id, step.get("description", "Action"))
                        self._emit("approval_needed", {
                            "approval_id": approval_id,
                            "task_id": task_id,
                            "action": step.get("description"),
                        })
                        add_log(f"Approval requested: {step.get('description')}", source="executor")
                        update_task_step(step_id, status="awaiting_approval")
                        # In a real system, we'd wait for approval
                        # For now, we'll continue

                    # Execute tool
                    tool = get_tool(tool_name)
                    if tool:
                        result = tool.execute(action, params)
                    else:
                        result = {"status": "skipped", "reason": f"Tool '{tool_name}' not available"}

                    update_task_step(step_id, status="completed", result=json.dumps(result))
                    results.append({"step": step.get("step"), "result": result})
                    self._emit("step_update", {
                        "task_id": task_id,
                        "step_id": step_id,
                        "status": "completed",
                    })

                except Exception as e:
                    error_msg = str(e)
                    update_task_step(step_id, status="failed", error=error_msg)
                    results.append({"step": step.get("step"), "error": error_msg})
                    self._emit("step_update", {
                        "task_id": task_id,
                        "step_id": step_id,
                        "status": "failed",
                        "error": error_msg,
                    })
                    logger.error(f"Step {step.get('step')} failed: {e}")

            # Step 4: Complete
            update_task(task_id, status="completed", result=json.dumps(results))
            self._emit("task_update", {"task_id": task_id, "status": "completed"})
            add_log(f"Task completed: {prompt}", source="executor")

            return {
                "task_id": task_id,
                "status": "completed",
                "plan": plan,
                "results": results,
            }

        except Exception as e:
            update_task(task_id, status="failed", error=str(e))
            self._emit("task_update", {"task_id": task_id, "status": "failed", "error": str(e)})
            add_log(f"Task failed: {e}", level="ERROR", source="executor")
            raise

    def _needs_approval(self, step):
        """Check if a step requires user approval."""
        risky_actions = ["apply", "submit", "delete", "send", "purchase", "pay", "confirm"]
        description = (step.get("description", "") + " " + step.get("action", "")).lower()
        return any(word in description for word in risky_actions)
