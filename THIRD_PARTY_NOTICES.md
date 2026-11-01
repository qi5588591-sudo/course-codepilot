# 开源参考与原创实现记录

本工程自行编写插件和后端。没有复制 Tabby、Continue 或 VS Code Samples 的源文件。
VS Code Webview、补全、命令、文档编辑的用法依据官方文档和示例组织；因此不存在把完整开源产品改名后提交的情况。

| 参考 | 版本记录 | 用途 | 直接复制代码 |
|---|---|---|---|
| https://github.com/microsoft/vscode-extension-samples | 2026-10-29 阅读仓库与官方 API 文档，未 vendor 特定提交 | Webview、补全、命令、编辑结构 | 无 |
| https://github.com/TabbyML/tabby | 2026-10-29 阅读 README / LICENSE，未引入依赖 | 客户端/服务端分层与代码补全设计参考 | 无 |
| https://github.com/continuedev/continue | 2026-10-29 阅读 README，未引入依赖 | 代码助手交互形态参考 | 无 |

VS Code Samples 为 MIT，Continue 为 Apache-2.0。Tabby 在 ee/ 目录另行规定许可证。
项目未复制这些项目源码，今后若引入具体文件，需在此记录提交号、文件、修改点及保留的声明。

原创部分：分任务提示词、Python 符号摘要、上下文选择、模型结果解析、原位置版本检查、
测试验证编排、固定测试反馈修复、SQLite 历史、45 道项目评估题与评估脚本。

实际第三方依赖版本由 requirements.lock.txt 与 extension/pnpm-lock.yaml 固定。
其许可证仍归各依赖作者所有。pytest 位于独立验证镜像中。
