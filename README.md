# CodePilot 面向开发者的智能代码生成与辅助工具

智能应用系统课程设计第 32 题。以 VS Code 为入口，Python 后端调用云模型，支持四种语言的代码生成和辅助功能，并对 Python 实现测试验证及最多两轮自动修复。

**项目状态：已保存工程基线，暂停功能开发（2026-11-01）。** 下次 AI 继续请先读
[AGENTS.md](AGENTS.md) 和 [项目交接](docs/HANDOFF.md)，再查看 [待办顺序](docs/ROADMAP.md)。
工程检查已通过；真实模型效果、真实 Docker 执行和正式模型实验仍待完成。

## 快速启动

需要 Python 3.11+、VS Code 1.90+。仅使用已打包插件时无需安装 Node；修改插件需要 Node 22+ 和 pnpm。

1. 将 `.env.example` 复制为 `.env`，填写模型 API 地址、密钥、模型名称。
2. Windows PowerShell 在工程根目录运行：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple -r requirements.lock.txt
Copy-Item .env.example .env   # 已有 .env 时不要重复复制
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
```

也可以使用 `powershell -ExecutionPolicy Bypass -File scripts/start.ps1` 自动准备环境并启动。
模型接口采用常见的 `POST /chat/completions` 协议，API_BASE 填到 `/v1` 等基础路径，不能再包含 `/chat/completions`。
具体供应商需支持文本消息与 JSON 文本输出；本项目不绑定某个付费套餐。

3. VS Code 扩展页右上角菜单选择“从 VSIX 安装”，选取 `artifacts/course-codepilot-0.1.0.vsix`。
4. 在活动栏打开 CodePilot，保存一个 `.py` 文件，选中函数或输入需求并开始处理。
5. API 健康检查：`http://127.0.0.1:8765/health`，交互文档：`http://127.0.0.1:8765/docs`。

**未填写 API 时后端仍能启动，生成请求会明确提示尚未配置。没有内置密钥或模拟的生成结果。**

## 功能与操作

| 功能 | 入口与行为 |
|---|---|
| 自然语言生成 | 侧栏选择生成，选择语言、输入需求，预览或插入结果 |
| 四语言 | Python、Java、JavaScript、C++，语言由侧栏指定 |
| 补全 | 命令面板执行 CodePilot: 请求代码补全；可选开启自动补全 |
| 解释、审查、命名、函数建议 | 选中代码后在侧栏选择任务；无选区则读取当前文件 |
| 单元测试 | Python 使用 pytest，固定从 solution 导入被测函数；其他语言按对应习惯生成 |
| 文档 | 生成 Markdown API 文档，可打开或保存为 .md |
| 错误诊断 | 选中代码，输入错误日志并选择诊断与修复 |
| Python 验证修复 | 在结果区填写 pytest 测试，执行测试或验证并修复 |
| 历史 | 本地 SQLite 保存结果和修复轮次；加载旧记录可打开为新文件 |

代码修改先用“查看修改差异”检查，再点击“应用到原位置”。生成任务在无选区时插入光标位置，审查/修复替换原选区或原文件。
测试与文档请打开为新文件，避免替换源函数。若原文件已变化，禁止应用旧结果，需重新生成。

上下文默认含选区、光标前后代码和 Python 符号摘要。可主动添加最多 4 个相关文件，每个最多 12000 字符。
未选择的工作区文件不会自动上传。关闭“结合上下文”后仍发送任务本身需要的选中代码。

## Python 测试与修复

安装并启动 Docker Desktop 的 Linux containers，然后运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-sandbox.ps1
```

生成测试后可以直接验证原选中函数。也可对生成代码粘贴独立测试后执行。
验证输入应是可独立导入的 Python 代码；仅选中依赖其他模块或类状态的方法时，需要先整理为完整实现。
被测代码位于容器 `solution.py`，测试位于 `test_solution.py`，示例：

```python
from solution import binary_search

def test_last_element():
    assert binary_search([1, 3, 5], 5) == 2
```

容器禁网、限制内存/CPU/进程数，以非 root 身份运行，根文件系统只读；代码通过 stdin 传入，未挂载宿主目录。
默认超时 15 秒，最多并行 2 个执行任务。未安装 Docker 或镜像不存在时返回未验证，不会在宿主 Python 中执行模型代码。
首版支持标准库与镜像中的 pytest，第三方依赖需显式维护专用镜像。

自动修复只替换实现代码，保留提交的测试文本与 SHA256，最多两轮。语法检查通过不能等同于测试通过。

## 开发与检查

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/backend-tests.xml
cd extension
pnpm install --frozen-lockfile
pnpm run compile
pnpm test
cd ..
node scripts/package-extension.cjs
```

插件 F5 配置位于 `extension/.vscode`。也可以打开 extension 目录并执行上面的构建命令。
显式开启真实 Docker 集成测试：设置 `CODEPILOT_DOCKER_TESTS=1` 后运行 `pytest tests/test_sandbox.py`。
安装包的打包过程不依赖发布账户，不会发布到 Marketplace。

## 可复现实验

45 道项目自建题，包含 30 道生成与 15 道缺陷修复。`evaluation/cases.jsonl` 为固定数据集，`build_dataset.py` 记录题目来源与独立断言。

```powershell
.venv\Scripts\python.exe -m evaluation.run --dry-run
.venv\Scripts\python.exe -m evaluation.run --mode all --output artifacts/evaluation-real.jsonl
.venv\Scripts\python.exe -m evaluation.summarize artifacts/evaluation-real.jsonl --csv artifacts/evaluation-summary.csv
```

正式运行会调用付费 API；先用 `--limit 2` 小规模检查。预检要求模型已配置、Docker 实际执行成功。
baseline/context/repair 对比基础提示、项目约定上下文及测试反馈修复。三组分别调用同一模型，模型温度为 0.2，不保证完全确定性。
指标包括首次通过率、最多两轮修复后的通过率、耗时、token 用量。测试断言不发给首次生成模型；修复阶段提供失败日志和固定测试。
当前上下文评估只包含项目约定文件，不能据此声称已经验证大型项目跨文件理解能力。
**本地单元测试通过数是工程检查结果，不是云模型代码生成准确率。**

## 结构与提交

`backend/` 后端，`extension/` 插件，`sandbox/` 隔离执行镜像，`tests/` 工程测试，`evaluation/` 评估，`examples/` 演示，`docs/` 报告正文与答辩材料。

`docs/ACCEPTANCE.md` 提供验收步骤，`docs/REPORT.md` 对应课程报告章节，`docs/DEMO_SCRIPT.md` 提供演示讲稿。
`artifacts/VERIFICATION.md` 记录当前已验证与未验证项目。`THIRD_PARTY_NOTICES.md` 区分开源参考与原创实现。

源代码提交包可用 `.venv\Scripts\python.exe scripts/package-source.py` 重新生成，会排除虚拟环境、node_modules、.env 与 SQLite 数据。
报告中的姓名、学号、班级和个人体会需本人填写。真实云端实验和正式操作录屏需在模型配置完成后补充，不能用模拟测试替代。

附带的报告草稿保留原课程模板，PPT 为可编辑对象，MP4 为中文合成语音的工程讲解。
材料重建脚本位于 scripts：报告需要 python-docx 和模板副本，PPT 使用 Codex 的 @oai/artifact-tool 运行时，
讲解视频使用 Windows System.Speech 与可选的 imageio-ffmpeg。它们不是运行插件的必需依赖。
