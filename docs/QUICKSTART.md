# 本机下一步操作

本目录已经生成 VSIX、报告草稿、PPT、工程讲解视频和源码包。

1. 编辑工程根目录的 .env（可从 .env.example 复制）。填写模型服务的 API_BASE、API_KEY 和 MODEL。
2. PowerShell 运行 `powershell -ExecutionPolicy Bypass -File scripts/start.ps1`。
3. VS Code 选择“从 VSIX 安装”，打开 artifacts/course-codepilot-0.1.0.vsix。
4. 保存一个 Python 文件，在活动栏打开 CodePilot，输入需求或选中代码运行任务。
5. 需要执行测试时，安装并启动 Docker Desktop，再运行 scripts/build-sandbox.ps1。
6. 用 docs/ACCEPTANCE.md 逐项验收；真实模型实验运行 evaluation.run，并将结果补入报告。

当前模型密钥未配置，Docker 未安装。工程测试使用模拟依赖，不能当作模型准确率。
报告仍需本人填写姓名学号、实践时间和个人体会，讲解视频仍需配合真实操作录屏。
