import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(path.join(root,'build/author.mjs'));
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const skill=process.env.CODEPILOT_PRESENTATION_SKILL || 'C:/Users/35123/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';
const python=process.env.CODEPILOT_ARTIFACT_PYTHON || 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1025-760-0_26.1025.760.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe';
const font='Microsoft YaHei';
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const slides=[];
function text(slide,value,x,y,w,h,size=28,color='#334155',bold=false){
 const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 s.text=value;s.text.style={typeface:font,fontSize:size,color,bold};s.text.insets=0;return s;
}
function page(title,notes){
 const s=deck.slides.add();s.background.fill='#FFFFFF';
 text(s,title,76,58,1128,80,44,'#12233D',true);
 text(s,String(deck.slides.items.length).padStart(2,'0')+' / 10',1095,660,110,30,18,'#64748B');
 s.speakerNotes.text=notes;slides.push({title,notes});return s;
}
function lines(s,items,y=188,width=1100){items.forEach((v,i)=>text(s,v,80,y+i*83,width,70,28));}

let s=page('CodePilot 智能编程助手','本课程设计选择第三十二题，面向开发者的智能代码生成与辅助工具。工程采用 VS Code 插件和 Python 后端，重点实现上下文代码辅助与测试反馈修复。本讲解展示工程结构和已完成的检查，真实云模型效果仍需配置后测量。');
text(s,'面向开发者的智能代码生成与辅助工具',80,226,1100,94,47,'#12233D',true);
text(s,'VS Code 插件与 Python 服务',80,353,1100,60,31);
text(s,'课程设计第 32 题\n2026 年 10 月 29 日工程版本',80,495,1100,90,25,'#64748B');

s=page('题目要求与功能覆盖','题目要求覆盖自然语言生成、多语言、补全、审查、测试、文档、修复和 IDE 集成。工程以插件为统一入口，增加解释、命名与函数建议。Python 自动测试和修复是首版深入实现的部分，其他语言的编译执行在外部工具链中完成。来源：课程题目 PDF 第 27 页。');
const left=['自然语言生成与四语言支持','光标补全与命名建议','代码审查与优化','VS Code 插件集成'];
const right=['单元测试生成','API 文档与使用示例','错误诊断与修复','Python 测试反馈验证'];
left.forEach((v,i)=>text(s,v,80,190+i*105,550,70,29));right.forEach((v,i)=>text(s,v,700,190+i*105,500,70,29));

s=page('系统架构','插件使用 TypeScript，负责收集选区、光标上下文和主动添加的文件。Python 后端使用 FastAPI，按任务组织提示词并解析 JSON。SQLite 保存任务和修复轮次。验证服务将 Python 代码送入 Docker，缺少执行环境时返回未验证。参考：https://code.visualstudio.com/api/references/vscode-api 和 https://fastapi.tiangolo.com/ 。');
lines(s,['VS Code 插件    侧栏、命令、原生补全、差异预览','FastAPI 服务    任务路由、上下文、模型调用与解析','SQLite 记录    任务历史、模型用量与修复轮次','Docker 验证    Python 语法检查与 pytest 执行']);

s=page('插件交互','右侧图片为本工程真实 Webview 资源的离线界面预览，模型尚未配置，并非云模型运行结果。开发者选择任务和语言，输入需求或选中代码。处理结果可以预览差异，再应用到原位置。应用前核对文档版本和内容，避免旧结果覆盖新编辑。');
lines(s,['任务、语言和需求在侧栏集中操作','相关文件由用户主动选择','代码修改提供差异预览','原文件变化后拒绝应用旧结果'],190,760);
s.images.add({blob:new Uint8Array(await fs.readFile(path.join(root,'docs/images/assistant-preview.png'))),contentType:'image/png',alt:'离线界面预览，模型尚未配置',fit:'contain',position:{left:944,top:155,width:220,height:490}});

s=page('上下文与结构化输出','系统默认使用选区和有限长度的前后代码。Python 通过 AST 提取顶层导入、函数签名和类名。每种任务有独立提示词，输出代码、解释、文档、问题和建议。后端校验结构，前端用纯文本呈现模型内容。首版没有自动扫描整个工作区，也没有实现大型仓库语义检索。');
lines(s,['选区与光标附近代码形成直接上下文','AST 摘要补充导入、函数签名和类名','分任务提示词约束输出目标和格式','JSON 校验后分别展示代码、文档和问题']);

s=page('固定测试反馈修复','验证先检查语法，再执行固定的 pytest 测试。失败时将需求、当前实现和实际日志交给模型。模型只更新实现，测试文本保持不变，最多修复两轮。系统保存每轮代码、结果和测试哈希。测试通过只表示满足当前断言，不代表不存在其他缺陷。');
text(s,'原始实现',80,190,300,60,34,'#12233D',true);text(s,'第 1 轮修复',480,190,300,60,34,'#12233D',true);text(s,'第 2 轮修复',880,190,310,60,34,'#12233D',true);
text(s,'语法与测试验证',80,286,300,80,28);text(s,'依据失败日志更新实现',480,286,320,100,28);text(s,'通过或达到上限后停止',880,286,320,100,28);
text(s,'每轮使用相同测试文本，并记录 SHA256',80,455,1100,65,32,'#155E75',true);
text(s,'环境不可用、缺少测试或超时均返回明确状态',80,548,1100,65,27);

s=page('接口与执行边界','后端提供任务、验证、修复和历史接口。模型配置仅存在后端环境变量中。Docker 运行禁网、非 root，限制内存、CPU 和进程数，根文件系统只读，不挂载宿主目录。没有 Docker 时不会回退到宿主执行。实际容器效果尚未在本机验证。参考：https://docs.docker.com/engine/containers/resource_constraints/ 。');
text(s,'POST /api/tasks        九类智能辅助任务\nPOST /api/verify       Python 测试验证\nPOST /api/repair       最多两轮反馈修复\nGET  /api/history      本地任务记录',80,180,1100,270,29);
text(s,'256 MB 内存限制，禁网，非 root，默认 15 秒超时',80,515,1100,65,28,'#155E75',true);

s=page('可复现的评估设计','项目包含三十道 Python 生成任务和十五道错误修复任务。每题有独立断言，人工参考代码已通过检查。正式实验在同一模型上比较基础提示、加入上下文和反馈修复，记录通过率、耗时和 token 用量。当前上下文只包含项目约定文件，不能据此推断大型项目理解能力。');
text(s,'30 道生成题     15 道修复题',80,185,1100,90,43,'#12233D',true);
lines(s,['对照配置：基础提示、上下文、测试反馈修复','独立测试衡量功能正确性，模型测试单独检查','记录首次通过率、最终通过率、耗时和用量'],325);

s=page('已完成的工程检查','当前后端检查为一百二十一项通过，三项需要 Docker 的集成测试跳过。插件核心四项、Webview 浏览器五项、原生 VS Code 扩展宿主六个场景通过。Java、JavaScript 和 C++ 各三个手工参考示例执行通过。这些是工程检查结果，模型服务采用模拟依赖，不是云模型准确率。');
const rows=[['检查对象','通过','边界'],['Python 工程与题目','121','3 项 Docker 检查跳过'],['插件核心逻辑','4','本地单元检查'],['Webview 资源','5','浏览器模拟消息'],['VS Code 扩展宿主','6','本地模拟模型 HTTP'],['多语言参考示例','9','手写参考，非模型结果']];
const table=s.tables.add({rows:rows.length,columns:3,left:80,top:174,width:1120,height:365,columnWidths:[430,120,570],values:rows});
table.borders.assign({style:'solid',fill:'#CBD5E1',width:1});
for(let r=0;r<rows.length;r++)for(let c=0;c<3;c++){const cell=table.getCell(r,c);cell.fill=r===0?'#12233D':r%2?'#F1F5F9':'#FFFFFF';cell.text.style={typeface:font,fontSize:24,color:r===0?'#FFFFFF':'#334155',bold:r===0};}
text(s,'工程通过数不等于大模型代码生成准确率',80,577,1100,60,27,'#155E75',true);

s=page('当前限制与提交准备','工程源代码、插件安装包、报告草稿、PPT 和工程讲解材料已经组织。当前没有提供模型 API 配置，本机也未检测到 Docker，因此真实云模型实验和容器执行尚未实测。提交前应填写个人信息，完成模型和 Docker 验收，补充真实结果和操作录屏，个人体会由本人填写。');
lines(s,['配置 API 与 Docker 后完成真实功能验收','运行固定评估，保留成功和失败记录','填写个人信息、实践日期及个人体会','补充真实模型操作录屏与实验结果']);

await fs.mkdir(path.join(root,'build/slides'),{recursive:true});
for(let i=0;i<deck.slides.items.length;i++){
 const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(root,'build/slides',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
await fs.writeFile(path.join(root,'build/narration.json'),JSON.stringify(slides,null,2));
const draft=path.join(root,'build/deck-draft.pptx');await(await PresentationFile.exportPptx(deck)).save(draft);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
await finalizePresentation({workspaceDir:root,candidatePath:draft,finalPath:path.join(root,'deliverables/工程答辩最终版.pptx'),
 pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','9'],
 requiredNativeTableOwnerSlides:[9],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:[font]},
 verifyArtifactToolImport:true,receiptPath:path.join(root,'build/deck-validation-v2.json')});
console.log('PPTX exported');
