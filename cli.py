"""ProBharatAI CLI - Command line interface for controlling the platform."""
import click
import subprocess
import sys
import os
import signal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


@click.group()
@click.version_option(version="1.0.0", prog_name="ProBharatAI")
def cli():
    """🤖 ProBharatAI - Open-Source AI Desktop Automation Platform"""
    pass


@cli.command()
def install():
    """Install all dependencies for ProBharatAI."""
    click.echo("🚀 Installing ProBharatAI...")

    # Backend dependencies
    click.echo("\n📦 Installing Python dependencies...")
    backend_dir = PROJECT_ROOT / "backend"
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(backend_dir / "requirements.txt")],
        check=True,
    )

    # Install Playwright browsers
    click.echo("\n🌐 Installing browser automation...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

    # Frontend dependencies
    click.echo("\n⚛️  Installing frontend dependencies...")
    frontend_dir = PROJECT_ROOT / "frontend"
    subprocess.run(["npm", "install"], cwd=str(frontend_dir), shell=True, check=True)

    # Copy env template
    env_file = backend_dir / ".env"
    if not env_file.exists():
        import shutil
        shutil.copy(str(backend_dir / ".env.example"), str(env_file))
        click.echo("📝 Created .env file from template")

    click.echo("\n✅ ProBharatAI installed successfully!")
    click.echo("   Run 'probharatai start' to launch the platform.")


@cli.command()
@click.option("--backend-only", is_flag=True, help="Start only the backend server")
@click.option("--frontend-only", is_flag=True, help="Start only the frontend")
def start(backend_only, frontend_only):
    """Start ProBharatAI services."""
    processes = []

    try:
        if not frontend_only:
            click.echo("🖥️  Starting backend server...")
            backend_dir = PROJECT_ROOT / "backend"
            backend_proc = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=str(backend_dir),
            )
            processes.append(backend_proc)
            click.echo("   Backend running on http://localhost:8000")

        if not backend_only:
            click.echo("⚛️  Starting frontend...")
            frontend_dir = PROJECT_ROOT / "frontend"
            frontend_proc = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                shell=True,
            )
            processes.append(frontend_proc)
            click.echo("   Dashboard running on http://localhost:3000")

        click.echo("\n🤖 ProBharatAI is running! Press Ctrl+C to stop.")

        # Wait for processes
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        click.echo("\n🛑 Stopping ProBharatAI...")
        for proc in processes:
            proc.terminate()
        click.echo("   Stopped.")


@cli.command()
def stop():
    """Stop ProBharatAI services."""
    click.echo("🛑 Stopping ProBharatAI...")
    # Kill processes on port 8000 and 3000
    if sys.platform == "win32":
        os.system("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq probharatai*\" 2>nul")
        os.system("taskkill /F /IM node.exe /FI \"WINDOWTITLE eq probharatai*\" 2>nul")
    else:
        os.system("pkill -f 'probharatai' 2>/dev/null")
    click.echo("✅ ProBharatAI stopped.")


@cli.command()
def status():
    """Check ProBharatAI service status."""
    import requests

    click.echo("🔍 Checking ProBharatAI status...\n")

    try:
        response = requests.get("http://localhost:8000/api/health", timeout=3)
        data = response.json()
        click.echo(f"   Backend:  ✅ Running (v{data.get('version', '?')})")
    except Exception:
        click.echo("   Backend:  ❌ Not running")

    try:
        response = requests.get("http://localhost:3000", timeout=3)
        click.echo("   Frontend: ✅ Running")
    except Exception:
        click.echo("   Frontend: ❌ Not running")


@cli.command()
@click.argument("prompt")
def run(prompt):
    """Execute a prompt from the command line."""
    import requests

    click.echo(f"🤖 Executing: {prompt}\n")
    try:
        response = requests.post(
            "http://localhost:8000/api/prompt",
            json={"prompt": prompt},
            timeout=120,
        )
        data = response.json()
        if "error" in data:
            click.echo(f"❌ Error: {data['error']}")
        else:
            click.echo(f"✅ Task #{data.get('task_id')} completed!")
            for step in data.get("plan", []):
                click.echo(f"   Step {step['step']}: {step['description']}")
    except requests.ConnectionError:
        click.echo("❌ Backend not running. Start with: probharatai start")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


if __name__ == "__main__":
    cli()
