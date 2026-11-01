"""Only Docker executes submitted code. No host-Python fallback."""
import ast
import asyncio
import hashlib
import json
import shutil
import time
import uuid

from .config import Settings
from .schemas import ValidationResult


def tests_present(source: str) -> bool:
    tree = ast.parse(source)
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
               for n in ast.walk(tree))


async def limited_output(stream, max_bytes=65536):
    chunks, total = [], 0
    while True:
        chunk = await stream.read(4096)
        if not chunk:
            break
        if total < max_bytes:
            chunks.append(chunk[:max_bytes - total])
        total += len(chunk)
    return b"".join(chunks).decode("utf-8", errors="replace")


class DockerSandbox:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.slots = asyncio.Semaphore(2)

    def command(self, name: str) -> list[str]:
        return ["docker", "run", "--rm", "--name", name, "--pull=never", "-i",
                "--network=none", "--memory=256m", "--memory-swap=256m", "--cpus=1", "--pids-limit=64",
                "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--user=65534:65534",
                "--tmpfs=/work:rw,nosuid,nodev,noexec,size=16m,mode=1777", self.settings.sandbox_image]

    async def verify(self, code: str, tests: str) -> ValidationResult:
        started = time.perf_counter()
        digest = hashlib.sha256(tests.encode()).hexdigest()

        def result(status, output="", exit_code=None):
            return ValidationResult(status=status, output=output, exit_code=exit_code,
                                    duration_ms=int((time.perf_counter() - started) * 1000), tests_sha256=digest)
        try:
            ast.parse(code, filename="solution.py")
            ast.parse(tests, filename="test_solution.py")
        except SyntaxError as exc:
            return result("syntax_error", f"{exc.filename}:{exc.lineno}: {exc.msg}\n{exc.text or ''}")
        if not tests.strip() or not tests_present(tests):
            return result("no_tests", "请提供含 test_ 函数的 pytest 测试；语法检查成功不代表功能正确")
        if not shutil.which("docker"):
            return result("unavailable", "未找到 Docker。请安装 Docker Desktop 并构建 sandbox 镜像。代码未执行。")
        async with self.slots:
            name = "codepilot-" + uuid.uuid4().hex
            proc = None
            try:
                proc = await asyncio.create_subprocess_exec(*self.command(name), stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
                reader = asyncio.create_task(limited_output(proc.stdout))
                async def run():
                    proc.stdin.write(json.dumps({"code": code, "tests": tests}).encode())
                    await proc.stdin.drain()
                    proc.stdin.close()
                    await proc.wait()
                    return await reader
                try:
                    output = await asyncio.wait_for(run(), timeout=self.settings.execution_timeout)
                except asyncio.TimeoutError:
                    return result("timeout", "测试执行超时，容器已请求清理")
                if proc.returncode == 125:
                    return result("unavailable", output, proc.returncode)
                # pytest exit 5 means no tests collected, not a successful validation.
                status = "passed" if proc.returncode == 0 else "no_tests" if proc.returncode == 5 else "failed"
                return result(status, output, proc.returncode)
            except (OSError, BrokenPipeError, ConnectionResetError) as exc:
                return result("error", f"容器执行失败：{type(exc).__name__}")
            finally:
                # A canceled HTTP request must not leave an executing container behind.
                try:
                    cleanup = await asyncio.create_subprocess_exec("docker", "rm", "-f", name,
                        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                    await asyncio.wait_for(cleanup.wait(), 5)
                except (OSError, asyncio.TimeoutError):
                    pass
                if proc and proc.returncode is None:
                    proc.kill()
                    await proc.wait()
                if 'reader' in locals() and not reader.done():
                    reader.cancel()
