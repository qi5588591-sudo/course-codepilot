# 当前验证记录

日期：2026-10-29（Asia/Shanghai）。本文件区分真实工程检查、模拟依赖和未执行的模型实验。

| 检查 | 实际结果 | 说明 |
|---|---|---|
| Python pytest | 121 passed，3 skipped | API、解析、修复编排、存储、固定数据集。云模型与执行器使用模拟依赖 |
| TypeScript 编译 | 通过 | strict 模式 |
| 插件核心检查 | 4 passed | 语言映射、旧结果保护判断、凭据文件过滤、文本格式 |
| Webview 浏览器检查 | 5 passed | 真正的 UI 资源，模拟消息；输入、转义、历史动作和按钮状态 |
| 原生 VS Code 扩展宿主 | 6 场景通过 | 真实编辑 API + 本地模拟 HTTP 模型，原始记录 extension-host-tests.json |
| 多语言参考示例 | 9 passed | Java、JavaScript、C++ 各 3，原始记录 multilingual-smoke.json |
| 评估集 | 30 生成 + 15 修复 | 人工参考通过独立断言，15 个缺陷版本确实失败 |
| 真实云模型生成与评估 | 未执行 | 未提供 API 配置，未使用其他应用的登录凭据 |
| 真实 Docker 执行 | 未执行 | 当前机器未检测到 Docker |
| 实际 Uvicorn HTTP | 通过 | 健康、Swagger、OpenAPI、未配置模型 503 与无 Docker 返回状态 |
| 报告草稿 | 6 页 | 原模板副本填充，Word 导出后逐页检查；本机无 LibreOffice，使用原生 Word 渲染替代 |
| 答辩 PPT | 10 页 | 编辑对象、原生表格、包结构、字体及首方工具重新导入检查通过 |
| 工程讲解视频 | 5 分 09 秒 | 1280×720，中文合成配音，工程介绍，非云模型实机操作录屏 |

121 为工程检查数，不是大模型正确率。不存在预填的实验提升数据。
完整操作验收见 docs/ACCEPTANCE.md。正式提交前应配置模型和 Docker 并补充真实实验与操作录屏。
