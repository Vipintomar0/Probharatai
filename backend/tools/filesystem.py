"""Filesystem Tool - file and directory operations."""
import logging
import os
import shutil
import csv
import json
from pathlib import Path

logger = logging.getLogger("probharatai.tools.filesystem")


class FileSystemTool:
    """File system operations: create, read, write, delete, copy, rename."""

    def execute(self, action: str, params: dict) -> dict:
        action_map = {
            "read": self.read_file,
            "write": self.write_file,
            "create": self.create_file,
            "delete": self.delete_file,
            "copy": self.copy_file,
            "rename": self.rename_file,
            "list": self.list_directory,
            "mkdir": self.make_directory,
            "save_csv": self.save_csv,
            "save_json": self.save_json,
            "download": self.download_file,
        }
        handler = action_map.get(action)
        if handler:
            return handler(params)
        return {"status": "error", "message": f"Unknown filesystem action: {action}"}

    def read_file(self, params):
        path = params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"status": "success", "content": content[:10000], "size": len(content)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def write_file(self, params):
        path = params.get("path", "")
        content = params.get("content", "")
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "success", "path": path, "size": len(content)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_file(self, params):
        return self.write_file(params)

    def delete_file(self, params):
        path = params.get("path", "")
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return {"status": "success", "deleted": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def copy_file(self, params):
        src = params.get("source", "")
        dst = params.get("destination", "")
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return {"status": "success", "source": src, "destination": dst}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def rename_file(self, params):
        old = params.get("old_name", "")
        new = params.get("new_name", "")
        try:
            os.rename(old, new)
            return {"status": "success", "old": old, "new": new}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_directory(self, params):
        path = params.get("path", ".")
        try:
            entries = []
            for entry in os.scandir(path):
                entries.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if entry.is_file() else 0,
                })
            return {"status": "success", "entries": entries[:100]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def make_directory(self, params):
        path = params.get("path", "")
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def save_csv(self, params):
        path = params.get("path", "output.csv")
        data = params.get("data", [])
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            if data:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            return {"status": "success", "path": path, "rows": len(data)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def save_json(self, params):
        path = params.get("path", "output.json")
        data = params.get("data", {})
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def download_file(self, params):
        url = params.get("url", "")
        path = params.get("path", "download")
        try:
            import requests
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return {"status": "success", "path": path, "size": os.path.getsize(path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
