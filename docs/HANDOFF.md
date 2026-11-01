# CodePilot 项目交接

交接日期：2026-11-01（Asia/Shanghai）。本阶段暂停功能开发，保存可继续工作的工程基线。

## 1 当前目标和实现边界

课程设计题目 32，面向开发者的智能代码生成与辅助工具。个人完成，学生熟悉 Python，前端经验较少，允许使用云端模型和开源参考。
产品入口是 VS Code 插件；后端为 Python FastAPI，SQLite 存储历史。支持 Python、Java、JavaScript、C++ 的代码辅助；首版只自动执行 Python。

已实现：生成、补全、解释、审查优化、测试生成、API 文档、错误修复、命名建议、函数建议。
插件包含侧栏、右键/命令、上下文选择、差异预览、原文档版本保护、结果保存、历史和取消。
Python 测试反馈流程已经编写，最多修复两轮，保留固定测试和哈希。Docker 不可用时返回未验证。

明确未完成：真实云模型效果测试、真实 Docker 验证、正式 45 题模型实验，以及真实模型操作录屏。
当前无项目 `.env`，不包含模型密钥；未检测到本机 Docker。下一次继续时需重新确认这些环境事实。

## 2 先读什么

1. `AGENTS.md`：AI 修改约束及检查命令。
2. `README.md` / `docs/QUICKSTART.md`：启动和使用。
3. `docs/ROADMAP.md`：下一阶段任务及完成标准。
4. `artifacts/VERIFICATION.md`：工程证据与未验证项。
5. `docs/ACCEPTANCE.md`：逐项功能验收。
6. `docs/REPORT.md` 和 `docs/DEMO_SCRIPT.md`：报告正文、演示讲稿。

## 3 代码地图

| 模块 | 入口 | 责任 |
|---|---|---|
| HTTP 服务 | backend/main.py | 应用生命周期、任务/验证/修复/历史接口、认证与断连取消 |
| 数据结构 | backend/schemas.py | 四语言、九类任务、结果和修复轮次 |
| 模型适配 | backend/llm.py | chat/completions 协议、JSON 解析、错误映射 |
| 上下文与提示 | backend/prompts.py | 任务模板、Python AST 符号摘要、上下文开关 |
| 修复编排 | backend/service.py | 验证、固定测试、最多两轮修复、保存结果 |
| 执行隔离 | backend/sandbox.py / sandbox/ | Docker 禁网、资源/超时/输出限制、清理 |
| 存储 | backend/storage.py | SQLite 任务与轮次结果 |
| 插件宿主 | extension/src/extension.ts | 编辑器、后端通信、差异/应用、取消、补全 |
| 插件界面 | extension/src/webview.ts / extension/media/ | 侧栏、消息、文本展示和样式 |
| 评估 | evaluation/build_dataset.py / run.py / summarize.py | 固定题目、真实模型对比、指标导出 |

## 4 换一台机器继续

以下在仓库根目录执行，先安装 Python 3.12、Node 22+、pnpm 11.25.0 和 VS Code。

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env   # 仅在 .env 不存在时执行
# 本地编辑 .env，填 CODEPILOT_API_BASE、CODEPILOT_API_KEY、CODEPILOT_MODEL
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
```

API_BASE 是供应商基础路径，例如止于 /v1，不包含 /chat/completions。
本地健康检查 /health，交互文档 /docs。没有模型配置也能启动，生成请求返回明确的 503。
安装仓库 `artifacts/course-codepilot-0.1.0.vsix`，或在 extension 目录安装依赖并编译后 F5 调试。
生产运行插件不依赖 pnpm 和 Node 开发工具。

需要自动验证时，启动 Docker Desktop 的 Linux containers，运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-sandbox.ps1
$env:CODEPILOT_DOCKER_TESTS='1'
.venv\Scripts\python.exe -m pytest tests/test_sandbox.py -q
```

完成后移除该环境变量，避免其他不带 Docker 的检查意外失败。

## 5 验证证据和含义

2026-10-29 工程基线：pytest 121 通过、3 个 Docker 集成测试跳过；插件核心 4 项；浏览器 Webview 5 项；原生 VS Code 宿主 6 场景；Java/JS/C++ 参考示例 9 项。
模型 HTTP 与修复编排测试使用模拟依赖。45 题包括 30 生成题、15 修复题，人工参考实现满足独立断言，缺陷实现确实失败。
上述数字均不是模型正确率。宿主测试使用本地模拟 HTTP 服务；多语言示例是手工参考代码。

仓库保留 artifacts 下的 XML/JSON 原始记录。交接时重新运行的核心检查见 `docs/HANDOFF_CHECKS.md`。
CI 仅执行不需要密钥、Docker、桌面的核心检查；CI 通过同样不代表真实模型功能验收通过。

## 6 已知限制和后续注意

- 只有 Python 自动执行，默认镜像仅标准库和 pytest；待测实现需可以独立导入为 solution。
- AST 摘要与长度截断尚不是大型代码仓库检索。上下文评估目前只有项目约定文件，不能声称跨文件理解提升。
- 模型 JSON 格式仍可能失败；真实供应商协议和效果尚需验收。
- 修改原代码后必须重新生成；不得为方便而移除旧结果保护。
- 原生 VS Code 测试、浏览器测试和材料生成脚本不适合作为无桌面的默认 CI。
- `scripts/ui-check.cjs`、`scripts/build-deck.mjs` 的默认工具路径来自原开发机，跨机器需配置相应环境变量和运行时。
- 报告依赖 docs/report-template.docx；PPT 使用 Codex artifact-tool，视频使用 Windows System.Speech 和 imageio-ffmpeg。
- 报告和 PPT 包含历史测试数量；改变功能和测试后需统一更新文字，不能只重生成文件。
- 提交包打包器与 Git 跟踪规则不同，更新交接文件后如需新的 ZIP，应重新运行脚本检查清单。

## 7 现有课程材料

deliverables 中有原模板填充的报告草稿、10 页可编辑 PPT、约 5 分钟中文合成配音工程讲解视频。
报告尚需本人填写身份信息、实践日期、个人体会和真实模型实验。视频是工程讲解，不是实机模型操作录屏。
原课程 PDF 与旧版 .doc 在原本机目录保留，未上传公开仓库；必要时向学生索取，不要凭空补写要求。

## 8 下一次可直接复制的提示

```text
请继续这个仓库的 CodePilot 课程设计。先阅读 AGENTS.md、docs/HANDOFF.md、
docs/ROADMAP.md 和 docs/HANDOFF_CHECKS.md，检查当前 Git 状态，再简要说明项目完成度。
本次先处理 ROADMAP 的 P0：重新检查环境，协助配置一个云模型，在 Docker 中验证
Python 执行与最多两轮固定测试修复，然后按 ACCEPTANCE 验收。不要重写架构，
不要将模拟测试当作模型效果，不要读取或输出密钥。真实付费实验先限定在两道题，
记录实际结果、失败原因和用量；更新交接文档。
```
