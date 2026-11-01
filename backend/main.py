import asyncio
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .llm import ModelError
from .schemas import RepairRequest, RepairResponse, TaskRequest, TaskResponse, ValidationResult, VerifyRequest
from .service import AssistantService


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app):
        app.state.service = AssistantService(config)
        yield

    app = FastAPI(title="CodePilot 课程智能编程助手", version="0.1.0", lifespan=lifespan)

    async def authorize(request: Request, authorization: str = Header(default="")):
        # Browser pages must not trigger local model calls. VS Code uses Node fetch (no Origin).
        if request.headers.get("origin") and request.headers['origin'].rstrip('/') != str(request.base_url).rstrip('/'):
            raise HTTPException(403, "不接受浏览器跨域请求")
        if config.backend_token and not secrets.compare_digest(authorization, "Bearer " + config.backend_token):
            raise HTTPException(401, "本地后端令牌无效")

    @app.exception_handler(ModelError)
    async def model_error(request, exc):
        return JSONResponse(status_code=exc.status, content={"detail": str(exc)})

    @app.get("/health")
    async def health():
        return {"status": "ok", "model_configured": bool(config.api_key and config.model and config.api_base != 'https://your-provider.example/v1'),
                "model": config.model, "version": "0.1.0", "execution": "docker-only"}

    async def until_disconnected(request: Request, operation):
        job = asyncio.create_task(operation)
        try:
            while not job.done():
                await asyncio.wait({job}, timeout=0.1)
                if await request.is_disconnected():
                    job.cancel()
                    raise HTTPException(499, "请求已取消")
            return await job
        finally:
            if not job.done():
                job.cancel()
            if job.cancelled() or not job.done():
                try:
                    await job
                except asyncio.CancelledError:
                    pass

    @app.post("/api/tasks", response_model=TaskResponse, dependencies=[Depends(authorize)])
    async def task(body: TaskRequest, request: Request):
        return await until_disconnected(request, request.app.state.service.task(body))

    @app.post("/api/verify", response_model=ValidationResult, dependencies=[Depends(authorize)])
    async def verify(body: VerifyRequest, request: Request):
        return await until_disconnected(request, request.app.state.service.sandbox.verify(body.code, body.tests))

    @app.post("/api/repair", response_model=RepairResponse, dependencies=[Depends(authorize)])
    async def repair(body: RepairRequest, request: Request):
        return await until_disconnected(request, request.app.state.service.repair(body))

    @app.get("/api/history", dependencies=[Depends(authorize)])
    async def history(request: Request, limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0)):
        return request.app.state.service.store.list(limit, offset)

    @app.get("/api/history/{task_id}", dependencies=[Depends(authorize)])
    async def detail(task_id: str, request: Request):
        result = request.app.state.service.store.get(task_id)
        if result is None:
            raise HTTPException(404, "记录不存在")
        return result

    return app


app = create_app()
