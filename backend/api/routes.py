"""ProBharatAI REST API Routes."""
import json
import logging
import asyncio
from flask import Blueprint, request, jsonify
from database.models import (
    get_all_tasks, get_task, get_task_steps, get_job_applications,
    get_logs, get_setting, set_setting, save_api_key, get_api_key,
    get_pending_approvals, resolve_approval, add_log,
)
from agents.executor import TaskExecutor
from agents.memory import memory
from tools.telegram import telegram

logger = logging.getLogger("probharatai.api")
api_bp = Blueprint("api", __name__)


# ── Prompt / Task Execution ──

@api_bp.route("/prompt", methods=["POST"])
def execute_prompt():
    """Execute a natural language prompt."""
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    provider = data.get("provider")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        memory.add_message("user", prompt)
        executor = TaskExecutor()

        # Run async executor in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(executor.execute_prompt(prompt, provider=provider))
        loop.close()

        memory.add_message("assistant", json.dumps(result.get("results", [])))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Prompt execution failed: {e}")
        return jsonify({"error": str(e)}), 500


# ── Tasks ──

@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    limit = request.args.get("limit", 50, type=int)
    tasks = get_all_tasks(limit=limit)
    return jsonify({"tasks": tasks})


@api_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_detail(task_id):
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    steps = get_task_steps(task_id)
    task["steps"] = steps
    return jsonify(task)


# ── Job Applications ──

@api_bp.route("/jobs", methods=["GET"])
def list_jobs():
    task_id = request.args.get("task_id", type=int)
    limit = request.args.get("limit", 100, type=int)
    jobs = get_job_applications(task_id=task_id, limit=limit)
    return jsonify({"jobs": jobs, "total": len(jobs)})


# ── Logs ──

@api_bp.route("/logs", methods=["GET"])
def list_logs():
    limit = request.args.get("limit", 100, type=int)
    level = request.args.get("level")
    logs = get_logs(limit=limit, level=level)
    return jsonify({"logs": logs})


# ── Settings ──

@api_bp.route("/settings", methods=["GET"])
def get_settings():
    keys = ["default_llm_provider", "browser_headless", "require_approval", "telegram_configured"]
    settings = {k: get_setting(k, "") for k in keys}
    return jsonify(settings)


@api_bp.route("/settings", methods=["POST"])
def update_settings():
    data = request.get_json()
    for key, value in data.items():
        set_setting(key, str(value))
    return jsonify({"status": "updated"})


# ── API Keys ──

@api_bp.route("/api-keys", methods=["POST"])
def save_api_key_route():
    data = request.get_json()
    provider = data.get("provider", "")
    key = data.get("api_key", "")
    if not provider or not key:
        return jsonify({"error": "provider and api_key required"}), 400
    save_api_key(provider, key)
    return jsonify({"status": "saved", "provider": provider})


@api_bp.route("/api-keys/<provider>", methods=["GET"])
def check_api_key(provider):
    key = get_api_key(provider)
    return jsonify({"provider": provider, "configured": bool(key)})


# ── Approvals ──

@api_bp.route("/approvals", methods=["GET"])
def list_approvals():
    approvals = get_pending_approvals()
    return jsonify({"approvals": approvals})


@api_bp.route("/approvals/<int:approval_id>", methods=["POST"])
def handle_approval(approval_id):
    data = request.get_json()
    action = data.get("action", "")  # "approve" or "reject"
    if action not in ("approve", "reject"):
        return jsonify({"error": "action must be 'approve' or 'reject'"}), 400
    status = "approved" if action == "approve" else "rejected"
    resolve_approval(approval_id, status, approved_by="ui")
    return jsonify({"status": status, "approval_id": approval_id})


# ── Telegram ──

@api_bp.route("/telegram/test", methods=["POST"])
def test_telegram():
    result = telegram.send_message("✅ ProBharatAI connected! Telegram notifications are working.")
    return jsonify(result)


# ── System ──

@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "name": "ProBharatAI",
    })


@api_bp.route("/chat", methods=["POST"])
def chat_endpoint():
    """Simple chat endpoint for AI conversation."""
    data = request.get_json()
    message = data.get("message", "").strip()
    provider = data.get("provider")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    from llm.router import chat
    memory.add_message("user", message)
    messages = [
        {"role": "system", "content": memory.build_system_context()},
    ] + memory.get_messages()

    try:
        response = chat(messages, provider=provider)
        memory.add_message("assistant", response)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
