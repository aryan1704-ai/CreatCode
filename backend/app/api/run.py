import os
import shutil
import subprocess
import sys
import tempfile
import time

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/run", tags=["Code Execution"])


# ---------------------------------------------------------
# Limits
# ---------------------------------------------------------
MAX_CODE_CHARS = 20_000
MAX_INPUT_CHARS = 5_000
MAX_OUTPUT_CHARS = 20_000
TIMEOUT_SECONDS = 5


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------
class RunRequest(BaseModel):
    code: str = Field(..., description="Source code to run")
    language: str = "Python"
    stdin: str = ""


# ---------------------------------------------------------
# Language runners: language -> (file name, command builder)
# ---------------------------------------------------------
def _python_command(path: str):
    # -I = isolated mode (ignores PYTHON* env vars and user site-packages)
    return [sys.executable, "-I", path]


def _node_command(path: str):
    node = shutil.which("node")
    return [node, path] if node else None


RUNNERS = {
    "python": ("main.py", _python_command),
    "javascript": ("main.js", _node_command),
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _truncate(text: str) -> str:
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + "\n... [output truncated]"
    return text


def _safe_env() -> dict:
    """Minimal environment so user code cannot read your API keys or DB password."""
    env = {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
    }

    # Windows needs these for Python/Node to start correctly
    for key in ("SYSTEMROOT", "PATH", "TEMP", "TMP"):
        if key in os.environ:
            env[key] = os.environ[key]

    return env


def _response(status, **extra):
    base = {
        "status": status,
        "message": "",
        "output": "",
        "error": "",
        "exit_code": None,
        "execution_time_ms": 0,
    }
    base.update(extra)
    return base


# ---------------------------------------------------------
# Endpoint
# ---------------------------------------------------------
@router.post("/")
def run_code(request: RunRequest):
    # Plain "def" (not async) so FastAPI runs this in a worker thread
    # and a slow program never blocks the whole server.

    language = request.language.strip().lower()

    if not request.code.strip():
        return _response("error", message="There is no code to run.")

    if len(request.code) > MAX_CODE_CHARS:
        return _response(
            "error",
            message=f"Code is too long (max {MAX_CODE_CHARS} characters).",
        )

    if len(request.stdin) > MAX_INPUT_CHARS:
        return _response(
            "error",
            message=f"Input is too long (max {MAX_INPUT_CHARS} characters).",
        )

    runner = RUNNERS.get(language)

    if not runner:
        supported = ", ".join(name.title() for name in RUNNERS)
        return _response(
            "unsupported",
            message=f"{request.language} is not supported yet. Supported: {supported}.",
        )

    file_name, build_command = runner

    with tempfile.TemporaryDirectory(prefix="creatcode_") as workdir:
        file_path = os.path.join(workdir, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(request.code)

        command = build_command(file_path)

        if not command:
            return _response(
                "unsupported",
                message=f"{request.language} runtime is not installed on the server.",
            )

        started = time.perf_counter()

        try:
            result = subprocess.run(
                command,
                input=request.stdin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_SECONDS,
                cwd=workdir,
                env=_safe_env(),
            )

        except subprocess.TimeoutExpired:
            elapsed = int((time.perf_counter() - started) * 1000)
            return _response(
                "timeout",
                message=f"Execution stopped after {TIMEOUT_SECONDS} seconds.",
                execution_time_ms=elapsed,
            )

        except Exception as error:
            return _response(
                "error",
                message=f"Could not run the code: {error}",
            )

        elapsed = int((time.perf_counter() - started) * 1000)

        succeeded = result.returncode == 0

        return _response(
            "success" if succeeded else "error",
            message="Execution finished." if succeeded else "Program exited with an error.",
            output=_truncate(result.stdout or ""),
            error=_truncate(result.stderr or ""),
            exit_code=result.returncode,
            execution_time_ms=elapsed,
        )