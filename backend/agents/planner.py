"""AI Planner Agent - breaks user prompts into executable task steps."""
import json
import logging
from llm.router import chat

logger = logging.getLogger("probharatai.planner")

PLANNER_SYSTEM_PROMPT = """You are ProBharatAI Planner, an AI that breaks down user requests into executable steps.

Available tools:
- browser: Open browser, navigate, click, type, scrape, fill forms, submit
- filesystem: Create/read/write/delete/rename/copy files and directories
- system: Open applications, run commands, control desktop
- jobs: Search jobs on LinkedIn/Naukri/Indeed, check resume match, auto-apply
- telegram: Send notifications, get approvals
- data: Save to CSV, SQLite, Google Sheets

For each step, output a JSON array of objects with:
- step: step number
- description: what this step does
- tool: which tool to use
- action: specific action within the tool
- params: parameters for the action

IMPORTANT:
- Break complex tasks into small, atomic steps
- If a task requires user credentials, add a step to check/request them
- For destructive actions, add an approval step
- Be thorough but efficient

Respond ONLY with valid JSON array, no markdown or explanation."""


def create_plan(prompt: str, provider=None) -> list:
    """Create an execution plan from a user prompt."""
    logger.info(f"Creating plan for: {prompt}")

    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Create a step-by-step plan for: {prompt}"},
    ]

    try:
        response = chat(messages, provider=provider, temperature=0.3)
        # Parse JSON from response
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0]
        plan = json.loads(response)
        logger.info(f"Plan created with {len(plan)} steps")
        return plan
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse plan JSON: {e}")
        # Fallback: single step
        return [
            {
                "step": 1,
                "description": prompt,
                "tool": "browser",
                "action": "execute",
                "params": {"prompt": prompt},
            }
        ]
    except Exception as e:
        logger.error(f"Planner error: {e}")
        raise
