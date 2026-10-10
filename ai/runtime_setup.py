from __future__ import annotations

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

import requests
from utils.stop_control import StopRequested, interruptible_sleep, stop_requested

if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(os.path.dirname(sys.executable))
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

ASSETS_OLLAMA = PROJECT_ROOT / "ai" / "ollama"

OLLAMA_MODELS_PATH = ASSETS_OLLAMA / "models"

OLLAMA_INSTALLER = ASSETS_OLLAMA / "OllamaSetup.exe"
OLLAMA_BUNDLED_EXE = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"

OLLAMA_API = "http://127.0.0.1:11434"

DEFAULT_MODEL = "qwen3.5:latest"

def _api_ready() -> bool:
    try:
        r = requests.get(f"{OLLAMA_API}/api/tags", timeout=2)
        return r.ok
    except requests.RequestException:
        return False

def _find_ollama_exe() -> str | None:
    path_ollama = shutil.which("ollama")
    if path_ollama:
        return path_ollama

    if OLLAMA_BUNDLED_EXE.exists():
        return str(OLLAMA_BUNDLED_EXE)

    return None

def _run_ollama_command(command: list[str], *, capture_output: bool = False,
                        check: bool = False) -> subprocess.CompletedProcess:
    """Run an Ollama CLI command while keeping the bot cancellable."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
        text=True if capture_output else None,
    )
    while process.poll() is None:
        if stop_requested():
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise StopRequested("Bot stopped during an Ollama command")
        time.sleep(0.2)

    stdout, stderr = process.communicate()
    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check and result.returncode:
        raise subprocess.CalledProcessError(
            result.returncode, command, output=stdout, stderr=stderr
        )
    return result

def ensure_ollama_ready(timeout_seconds: int = 180) -> str:
    if stop_requested():
        raise StopRequested("Bot stop requested")
    ollama_exe = _find_ollama_exe()

    if not _api_ready():
        if ollama_exe is None:
            if not OLLAMA_INSTALLER.exists():
                raise FileNotFoundError(
                    f"Ollama installer not found: {OLLAMA_INSTALLER}"
                )
            print("📦 در حال نصب Ollama...")
            subprocess.Popen([str(OLLAMA_INSTALLER)], cwd=str(OLLAMA_INSTALLER.parent))

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if stop_requested():
                raise StopRequested("Bot stopped while waiting for Ollama")
            if _api_ready():
                break
            interruptible_sleep(2)

    if not _api_ready():
        raise TimeoutError("Ollama is not ready yet.")

    return ollama_exe or "ollama"

def ensure_model(model_name: str = DEFAULT_MODEL) -> None:
    if stop_requested():
        raise StopRequested("Bot stop requested")
    ollama = ensure_ollama_ready()

    os.environ["OLLAMA_MODELS"] = str(OLLAMA_MODELS_PATH)

    result = _run_ollama_command([ollama, "list"], capture_output=True)

    if model_name in result.stdout:
        print(f"✅ مدل {model_name} از قبل موجود است.")
        return

    print(f"📥 در حال دانلود مدل {model_name}...")
    _run_ollama_command([ollama, "pull", model_name], check=True)
    print(f"✅ مدل {model_name} دانلود شد.")
