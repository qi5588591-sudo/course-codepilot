import time
import uuid

from .config import Settings
from .llm import LLMClient, ModelError
from .sandbox import DockerSandbox
from .schemas import RepairRequest, RepairResponse, RepairRound, TaskRequest, TaskResponse
from .storage import Store


def add_usage(total, usage):
    for key, value in usage.items():
        total[key] = total.get(key, 0) + value


class AssistantService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = LLMClient(settings)
        self.sandbox = DockerSandbox(settings)
        self.store = Store(settings.database)

    async def task(self, req: TaskRequest):
        started = time.perf_counter()
        output, usage = await self.llm.generate(req)
        response = TaskResponse(**output.model_dump(), id=uuid.uuid4().hex, task=req.task,
            language=req.language, duration_ms=int((time.perf_counter() - started) * 1000),
            usage=usage, model=self.settings.model)
        self.store.save(response.id, req.task.value, req.language, req.requirement, response.model_dump(mode="json"))
        return response

    async def repair(self, req: RepairRequest):
        code, rounds, usage, repair_error = req.code, [], {}, None
        for attempt in range(req.max_repairs + 1):
            validation = await self.sandbox.verify(code, req.tests)
            rounds.append(RepairRound(round=attempt, code=code, validation=validation))
            if validation.status not in ("failed", "syntax_error") or attempt == req.max_repairs:
                break
            # Bad test syntax is not fixed by modifying implementation code.
            if validation.status == "syntax_error" and validation.output.startswith("test_solution.py:"):
                break
            try:
                output, used = await self.llm.generate(TaskRequest(task="fix", language="python",
                    requirement=req.requirement, code=code, error_log=validation.output,
                    context_files=[{"path": "test_solution.py (read-only)", "content": req.tests[:12000]}]))
            except ModelError as exc:
                repair_error = str(exc)
                break
            if not output.code.strip():
                repair_error = "模型未返回修复代码"
                break
            add_usage(usage, used)
            rounds[-1].explanation = output.explanation
            code = output.code
        response = RepairResponse(id=uuid.uuid4().hex, rounds=rounds, final_code=code,
            status=rounds[-1].validation.status, usage=usage, model=self.settings.model, repair_error=repair_error)
        self.store.save(response.id, "repair", "python", req.requirement, response.model_dump(mode="json"))
        return response
