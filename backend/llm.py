import json

import httpx
from pydantic import ValidationError

from .config import Settings
from .prompts import build_messages
from .schemas import ModelOutput, TaskRequest


class ModelError(Exception):
    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def parse_output(content: str) -> ModelOutput:
    content = content.strip()
    if content.startswith("```") and content.endswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return ModelOutput.model_validate(json.loads(content))
    except (ValueError, ValidationError) as exc:
        raise ModelError("模型返回格式无效，请重试或更换支持 JSON 输出的模型") from exc


class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, req: TaskRequest) -> tuple[ModelOutput, dict[str, int]]:
        s = self.settings
        if not s.api_key or not s.model or s.api_base == "https://your-provider.example/v1":
            raise ModelError("请在 .env 配置 CODEPILOT_API_BASE、CODEPILOT_API_KEY 和 CODEPILOT_MODEL", 503)
        try:
            async with httpx.AsyncClient(timeout=s.model_timeout) as client:
                response = await client.post(
                    s.api_base.rstrip("/") + "/chat/completions",
                    headers={"Authorization": f"Bearer {s.api_key}"},
                    json={"model": s.model, "messages": build_messages(req), "temperature": 0.2},
                )
        except httpx.TimeoutException as exc:
            raise ModelError("模型请求超时，请稍后重试", 504) from exc
        except httpx.RequestError as exc:
            raise ModelError("无法连接模型服务，请检查服务地址与网络", 502) from exc
        if response.status_code == 429:
            raise ModelError("模型额度不足或请求过于频繁，请检查账户额度", 429)
        if response.status_code in (401, 403):
            raise ModelError("模型服务认证失败，请检查 API 密钥", 502)
        if response.is_error:
            raise ModelError(f"模型服务返回 HTTP {response.status_code}", 502)
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            output = parse_output(content)
            usage = {k: v for k, v in body.get("usage", {}).items() if isinstance(v, int)}
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
            raise ModelError("模型服务响应结构无效", 502) from exc
        required = {"generate": output.code, "complete": output.code, "tests": output.code,
                    "fix": output.code, "docs": output.documentation, "explain": output.explanation}
        if req.task.value in required and not required[req.task.value].strip():
            raise ModelError("模型返回内容为空，请重试", 502)
        return output, usage
