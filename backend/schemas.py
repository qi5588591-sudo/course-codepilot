from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskType(str, Enum):
    generate = "generate"
    complete = "complete"
    explain = "explain"
    review = "review"
    tests = "tests"
    docs = "docs"
    fix = "fix"
    naming = "naming"
    suggest = "suggest"


Language = Literal["python", "java", "javascript", "cpp"]


class ContextFile(BaseModel):
    path: str = Field(max_length=300)
    content: str = Field(max_length=12000)


class TaskRequest(BaseModel):
    task: TaskType
    language: Language = "python"
    requirement: str = Field(default="", max_length=8000)
    code: str = Field(default="", max_length=60000)
    prefix: str = Field(default="", max_length=16000)
    suffix: str = Field(default="", max_length=8000)
    context_files: list[ContextFile] = Field(default_factory=list, max_length=4)
    error_log: str = Field(default="", max_length=16000)
    use_context: bool = True

    @model_validator(mode="after")
    def meaningful(self):
        if not any([self.requirement.strip(), self.code.strip(), self.prefix.strip()]):
            raise ValueError("请输入需求或提供代码")
        return self


class Issue(BaseModel):
    line: int | None = Field(default=None, ge=1)
    severity: Literal["info", "warning", "error"] = "info"
    message: str
    suggestion: str = ""


class ModelOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: str = Field(default="", max_length=100000)
    explanation: str = Field(default="", max_length=50000)
    documentation: str = Field(default="", max_length=80000)
    issues: list[Issue] = Field(default_factory=list, max_length=100)
    suggestions: list[str] = Field(default_factory=list, max_length=100)


class ValidationResult(BaseModel):
    status: Literal["passed", "failed", "syntax_error", "timeout", "unavailable", "no_tests", "error"]
    output: str = ""
    exit_code: int | None = None
    duration_ms: int = 0
    tests_sha256: str = ""


class TaskResponse(ModelOutput):
    id: str
    task: TaskType
    language: Language
    duration_ms: int
    usage: dict[str, int] = Field(default_factory=dict)
    verification: str = "未验证"
    model: str


class VerifyRequest(BaseModel):
    code: str = Field(min_length=1, max_length=60000)
    tests: str = Field(default="", max_length=60000)


class RepairRequest(VerifyRequest):
    requirement: str = Field(default="", max_length=8000)
    max_repairs: int = Field(default=2, ge=0, le=2)


class RepairRound(BaseModel):
    round: int
    code: str
    validation: ValidationResult
    explanation: str = ""


class RepairResponse(BaseModel):
    id: str
    rounds: list[RepairRound]
    final_code: str
    status: str
    usage: dict[str, int] = Field(default_factory=dict)
    model: str
    repair_error: str | None = None
