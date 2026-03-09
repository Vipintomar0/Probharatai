"""System Control Tool - OS-level automation."""
import logging
import subprocess
import platform
import os

logger = logging.getLogger("probharatai.tools.system")


class SystemTool:
    """System-level automation using OS APIs and PyAutoGUI."""

    def __init__(self):
        self.os_type = platform.system().lower()

    def execute(self, action: str, params: dict) -> dict:
        action_map = {
            "open_app": self.open_application,
            "run_command": self.run_command,
            "screenshot": self.take_screenshot,
            "notify": self.system_notify,
            "get_info": self.get_system_info,
            "keypress": self.keypress,
            "mouse_click": self.mouse_click,
        }
        handler = action_map.get(action)
        if handler:
            return handler(params)
        return {"status": "error", "message": f"Unknown system action: {action}"}

    def open_application(self, params):
        app = params.get("application", "")
        try:
            if self.os_type == "windows":
                os.startfile(app)
            elif self.os_type == "darwin":
                subprocess.Popen(["open", "-a", app])
            else:
                subprocess.Popen([app])
            return {"status": "success", "application": app}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_command(self, params):
        command = params.get("command", "")
        timeout = params.get("timeout", 30)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return {
                "status": "success",
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def take_screenshot(self, params):
        try:
            import pyautogui
            path = params.get("path", "desktop_screenshot.png")
            pyautogui.screenshot(path)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def system_notify(self, params):
        title = params.get("title", "ProBharatAI")
        message = params.get("message", "")
        try:
            if self.os_type == "windows":
                from ctypes import windll
                windll.user32.MessageBoxW(0, message, title, 0x40)
            elif self.os_type == "darwin":
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
            else:
                subprocess.run(["notify-send", title, message])
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_system_info(self, params):
        import psutil
        return {
            "status": "success",
            "os": platform.system(),
            "os_version": platform.version(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent if self.os_type != "windows" else psutil.disk_usage("C:\\").percent,
        }

    def keypress(self, params):
        try:
            import pyautogui
            keys = params.get("keys", [])
            if isinstance(keys, list):
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(keys)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def mouse_click(self, params):
        try:
            import pyautogui
            x = params.get("x", 0)
            y = params.get("y", 0)
            pyautogui.click(x, y)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
