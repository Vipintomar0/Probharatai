"""Job Automation Tool - LinkedIn, Naukri, Indeed automation."""
import logging
import json
import csv
from pathlib import Path
from database.models import create_job_application, get_job_applications

logger = logging.getLogger("probharatai.tools.jobs")


class JobsTool:
    """Automated job search and application across platforms."""

    def __init__(self):
        self.browser_tool = None

    def _get_browser(self):
        if not self.browser_tool:
            from tools.browser import BrowserTool
            self.browser_tool = BrowserTool()
        return self.browser_tool

    def execute(self, action: str, params: dict) -> dict:
        action_map = {
            "search": self.search_jobs,
            "apply": self.apply_to_job,
            "track": self.track_applications,
            "export": self.export_applications,
            "match": self.check_resume_match,
        }
        handler = action_map.get(action)
        if handler:
            return handler(params)
        return {"status": "error", "message": f"Unknown jobs action: {action}"}

    def search_jobs(self, params):
        """Search for jobs on the specified platform."""
        platform = params.get("platform", "linkedin").lower()
        query = params.get("query", "")
        location = params.get("location", "India")
        limit = params.get("limit", 20)

        browser = self._get_browser()

        if platform == "linkedin":
            url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"
        elif platform == "naukri":
            url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs"
        elif platform == "indeed":
            url = f"https://www.indeed.com/jobs?q={query}&l={location}"
        else:
            return {"status": "error", "message": f"Unsupported platform: {platform}"}

        try:
            result = browser.open_url({"url": url})
            # Scrape job listings
            jobs = browser.scrape({"selector": params.get("selector", ".job-card-container"), "limit": limit})

            # Store found jobs
            for job_data in jobs.get("data", [])[:limit]:
                create_job_application(
                    task_id=params.get("task_id"),
                    platform=platform,
                    title=job_data.get("text", "")[:200],
                    url=job_data.get("href", ""),
                    status="found",
                )

            return {
                "status": "success",
                "platform": platform,
                "query": query,
                "jobs_found": len(jobs.get("data", [])),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def apply_to_job(self, params):
        """Apply to a specific job."""
        url = params.get("url", "")
        platform = params.get("platform", "linkedin")

        browser = self._get_browser()

        try:
            browser.open_url({"url": url})

            # Platform-specific apply logic
            if platform == "linkedin":
                # Click Easy Apply
                browser.click({"text": "Easy Apply"})
                browser.wait({"timeout": 2000})

            return {
                "status": "success",
                "message": "Application initiated",
                "url": url,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def track_applications(self, params):
        """Get tracking data for all applications."""
        task_id = params.get("task_id")
        applications = get_job_applications(task_id=task_id)
        summary = {
            "total": len(applications),
            "found": sum(1 for a in applications if a["status"] == "found"),
            "applied": sum(1 for a in applications if a["status"] == "applied"),
            "rejected": sum(1 for a in applications if a["status"] == "rejected"),
        }
        return {"status": "success", "summary": summary, "applications": applications[:20]}

    def export_applications(self, params):
        """Export applications to CSV."""
        path = params.get("path", "job_applications.csv")
        task_id = params.get("task_id")
        applications = get_job_applications(task_id=task_id)

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if applications:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=applications[0].keys())
                writer.writeheader()
                writer.writerows(applications)

        return {"status": "success", "path": path, "count": len(applications)}

    def check_resume_match(self, params):
        """Use AI to check resume compatibility with job description."""
        from llm.router import chat

        resume = params.get("resume", "")
        job_description = params.get("job_description", "")

        messages = [
            {
                "role": "system",
                "content": "You are a resume matcher. Analyze the resume against the job description and return a JSON with: match_score (0-100), strengths (list), gaps (list), recommendation (string).",
            },
            {
                "role": "user",
                "content": f"Resume:\n{resume}\n\nJob Description:\n{job_description}",
            },
        ]

        try:
            response = chat(messages, temperature=0.3)
            return {"status": "success", "analysis": response}
        except Exception as e:
            return {"status": "error", "message": str(e)}
