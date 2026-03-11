"""Tests for the Job Application feature in ProBharatAI.

Covers:
  1. Database CRUD  – create_job_application, get_job_applications
  2. API endpoint   – GET /api/jobs
  3. JobsTool class  – search, apply, track, export, match (all mocked)
"""
import json
import os
import csv
import pytest
from unittest.mock import patch, MagicMock

# ── 1. Database Model Tests ─────────────────────────────────────────────────


class TestJobApplicationModels:
    """Test database CRUD for job_applications table."""

    def test_create_and_retrieve(self):
        from database.models import create_job_application, get_job_applications

        create_job_application(
            platform="linkedin",
            title="Python Dev",
            company="TestCo",
            url="https://example.com/job/1",
            status="found",
        )
        jobs = get_job_applications()
        assert len(jobs) == 1
        assert jobs[0]["platform"] == "linkedin"
        assert jobs[0]["title"] == "Python Dev"
        assert jobs[0]["company"] == "TestCo"
        assert jobs[0]["status"] == "found"

    def test_filter_by_task_id(self):
        from database.models import (
            create_job_application,
            get_job_applications,
            create_task,
        )

        task_id = create_task("test prompt")
        create_job_application(task_id=task_id, platform="naukri", title="Data Engineer")
        create_job_application(platform="indeed", title="ML Engineer")

        all_jobs = get_job_applications()
        assert len(all_jobs) == 2

        filtered = get_job_applications(task_id=task_id)
        assert len(filtered) == 1
        assert filtered[0]["platform"] == "naukri"

    def test_limit(self):
        from database.models import create_job_application, get_job_applications

        for i in range(5):
            create_job_application(platform="linkedin", title=f"Job {i}")

        jobs = get_job_applications(limit=3)
        assert len(jobs) == 3

    def test_empty_table(self):
        from database.models import get_job_applications

        jobs = get_job_applications()
        assert jobs == []


# ── 2. API Route Tests ───────────────────────────────────────────────────────


class TestJobsAPI:
    """Test the GET /api/jobs endpoint."""

    def test_empty_jobs(self, client):
        resp = client.get("/api/jobs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["jobs"] == []
        assert data["total"] == 0

    def test_list_jobs(self, client):
        from database.models import create_job_application

        create_job_application(platform="linkedin", title="Backend Dev", status="found")
        create_job_application(platform="naukri", title="Frontend Dev", status="applied")

        resp = client.get("/api/jobs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 2
        assert len(data["jobs"]) == 2

    def test_list_jobs_with_limit(self, client):
        from database.models import create_job_application

        for i in range(5):
            create_job_application(platform="indeed", title=f"Job {i}")

        resp = client.get("/api/jobs?limit=2")
        data = resp.get_json()
        assert len(data["jobs"]) == 2

    def test_list_jobs_filter_by_task_id(self, client):
        from database.models import create_job_application, create_task

        tid = create_task("find jobs")
        create_job_application(task_id=tid, platform="linkedin", title="Match")
        create_job_application(platform="indeed", title="No match")

        resp = client.get(f"/api/jobs?task_id={tid}")
        data = resp.get_json()
        assert data["total"] == 1
        assert data["jobs"][0]["title"] == "Match"


# ── 3. JobsTool Unit Tests ───────────────────────────────────────────────────


class TestJobsTool:
    """Test JobsTool methods with mocked browser and LLM."""

    def _tool(self):
        from tools.jobs import JobsTool
        return JobsTool()

    # -- search_jobs --

    def test_search_unsupported_platform(self):
        tool = self._tool()
        result = tool.search_jobs({"platform": "monster", "query": "python"})
        assert result["status"] == "error"
        assert "Unsupported platform" in result["message"]

    @patch("tools.jobs.JobsTool._get_browser")
    def test_search_jobs_linkedin(self, mock_browser_fn):
        mock_browser = MagicMock()
        mock_browser.open_url.return_value = {}
        mock_browser.scrape.return_value = {
            "data": [
                {"text": "Python Developer at Acme", "href": "https://linkedin.com/job/1"},
                {"text": "Django Dev at WidgetCo", "href": "https://linkedin.com/job/2"},
            ]
        }
        mock_browser_fn.return_value = mock_browser

        tool = self._tool()
        result = tool.search_jobs({"platform": "linkedin", "query": "python", "task_id": None})
        assert result["status"] == "success"
        assert result["platform"] == "linkedin"
        assert result["jobs_found"] == 2

    @patch("tools.jobs.JobsTool._get_browser")
    def test_search_jobs_browser_error(self, mock_browser_fn):
        mock_browser = MagicMock()
        mock_browser.open_url.side_effect = Exception("Connection refused")
        mock_browser_fn.return_value = mock_browser

        tool = self._tool()
        result = tool.search_jobs({"platform": "indeed", "query": "ml"})
        assert result["status"] == "error"
        assert "Connection refused" in result["message"]

    # -- apply_to_job --

    @patch("tools.jobs.JobsTool._get_browser")
    def test_apply_to_job_success(self, mock_browser_fn):
        mock_browser = MagicMock()
        mock_browser_fn.return_value = mock_browser

        tool = self._tool()
        result = tool.apply_to_job({"url": "https://linkedin.com/job/1", "platform": "linkedin"})
        assert result["status"] == "success"
        assert result["url"] == "https://linkedin.com/job/1"

    @patch("tools.jobs.JobsTool._get_browser")
    def test_apply_to_job_error(self, mock_browser_fn):
        mock_browser = MagicMock()
        mock_browser.open_url.side_effect = Exception("Timeout")
        mock_browser_fn.return_value = mock_browser

        tool = self._tool()
        result = tool.apply_to_job({"url": "https://example.com/job"})
        assert result["status"] == "error"

    # -- track_applications --

    def test_track_applications_empty(self):
        tool = self._tool()
        result = tool.track_applications({})
        assert result["status"] == "success"
        assert result["summary"]["total"] == 0

    def test_track_applications_with_data(self):
        from database.models import create_job_application, create_task

        tid = create_task("track test")
        create_job_application(task_id=tid, platform="linkedin", title="Job A", status="found")
        create_job_application(task_id=tid, platform="linkedin", title="Job B", status="applied")
        create_job_application(task_id=tid, platform="naukri", title="Job C", status="rejected")

        tool = self._tool()
        result = tool.track_applications({"task_id": tid})
        assert result["status"] == "success"
        assert result["summary"]["total"] == 3
        assert result["summary"]["found"] == 1
        assert result["summary"]["applied"] == 1
        assert result["summary"]["rejected"] == 1

    # -- export_applications --

    def test_export_applications_empty(self, tmp_path):
        csv_path = str(tmp_path / "export.csv")
        tool = self._tool()
        result = tool.export_applications({"path": csv_path})
        assert result["status"] == "success"
        assert result["count"] == 0

    def test_export_applications_creates_csv(self, tmp_path):
        from database.models import create_job_application

        create_job_application(platform="linkedin", title="Exported Job", status="found")
        csv_path = str(tmp_path / "jobs.csv")

        tool = self._tool()
        result = tool.export_applications({"path": csv_path})
        assert result["status"] == "success"
        assert result["count"] == 1
        assert os.path.exists(csv_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["title"] == "Exported Job"

    # -- check_resume_match --

    @patch("llm.router.chat")
    def test_resume_match_success(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "match_score": 85,
            "strengths": ["Python", "Flask"],
            "gaps": ["Kubernetes"],
            "recommendation": "Good fit overall",
        })

        tool = self._tool()
        result = tool.check_resume_match({
            "resume": "Python developer with 3 years experience",
            "job_description": "Looking for Python Flask developer",
        })
        assert result["status"] == "success"
        assert result["analysis"] is not None

    @patch("llm.router.chat")
    def test_resume_match_llm_error(self, mock_chat):
        mock_chat.side_effect = Exception("LLM API down")

        tool = self._tool()
        result = tool.check_resume_match({
            "resume": "test",
            "job_description": "test",
        })
        assert result["status"] == "error"
        assert "LLM API down" in result["message"]

    # -- execute dispatcher --

    def test_execute_unknown_action(self):
        tool = self._tool()
        result = tool.execute("nonexistent", {})
        assert result["status"] == "error"
        assert "Unknown jobs action" in result["message"]

    def test_execute_routes_to_track(self):
        tool = self._tool()
        result = tool.execute("track", {})
        assert result["status"] == "success"
        assert "summary" in result
