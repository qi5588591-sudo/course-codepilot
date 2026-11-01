# 交接时的复核

日期：2026-11-01（Asia/Shanghai）。本次仅整理 GitHub 备份和交接，不增加功能。

| 命令或检查 | 本次实际结果 |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | 121 passed、3 skipped；3 项为真实 Docker 集成检查 |
| `node extension/node_modules/typescript/bin/tsc -p extension` | 编译通过 |
| `node --test extension/test/core.test.cjs` | 4 项通过 |
| `.env` 是否存在 | 不存在；未读取任何模型密钥 |
| GitHub 目标 | qi5588591-sudo/course-codepilot，公开，由用户明确选择 |
| Git 忽略规则 | 本地环境、缓存、数据库、ZIP、密钥和原始课程文件不上传 |

本次未重新执行原生 VS Code、浏览器和多语言工具链检查；历史记录仍见 artifacts。
CI 工作流增加了后端检查、插件编译/核心检查及 VSIX 打包。远端状态以 GitHub Actions 页面为准。
本次没有云模型调用，没有新增模型准确率或修复效果数据，也没有声称完成真实 Docker 验证。

## 远端复核

- 公开仓库：https://github.com/qi5588591-sudo/course-codepilot
- 基线标签：`v0.1.0-handoff`，对应提交 `b2c881a`。
- 从 GitHub 重新克隆后，使用现有 Python 依赖运行检查，仍为 121 passed、3 skipped。
- 基线首次 GitHub Actions 成功，包含全新安装依赖、后端检查、插件编译/检查与 VSIX 打包：
  https://github.com/qi5588591-sudo/course-codepilot/actions/runs/41302060647
- 默认分支 `main` 用于继续开发。标签保留本次最初基线，不随后续提交移动。
