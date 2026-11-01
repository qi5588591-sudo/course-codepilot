"""Populate a converted copy of the supplied Word template, preserving the original."""
import hashlib
from pathlib import Path
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

root=Path(__file__).resolve().parents[1]
reference=root/'docs/report-template.docx'
doc=Document(reference)
text=(root/'docs/REPORT.md').read_text(encoding='utf-8')
sections=re.split(r'^## ',text,flags=re.M)[1:]
main=doc.tables[1]
for row in main.rows:
    row.height=None
    for cell in row.cells:
        for p in cell.paragraphs[1:]:p._element.getparent().remove(p._element)
for i,section in enumerate(sections,1):
    title,body=section.split('\n',1)
    cell=main.cell(i,0)
    cell.paragraphs[0].text=title
    cell.paragraphs[0].paragraph_format.keep_with_next=False
    for run in cell.paragraphs[0].runs:
        run.bold=True
    for content in body.strip().split('\n\n'):
        p=cell.add_paragraph(content.strip())
        p.paragraph_format.space_after=Pt(6)
        p.paragraph_format.line_spacing=1.35
        p.paragraph_format.keep_together=False
        p.paragraph_format.keep_with_next=False
        p.paragraph_format.page_break_before=False
        for run in p.runs:
            run.font.name='Times New Roman';run.font.size=Pt(10.5);run.font.color.rgb=RGBColor(0,0,0)
            run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体')

# Add the actual core algorithm excerpt to the appendix in the original table slot.
appendix=main.cell(9,0)
source=(root/'backend/service.py').read_text(encoding='utf-8')
snippet=source[source.index('    async def repair'):]
for index,line in enumerate(snippet.splitlines()):
    p=appendix.add_paragraph(line)
    p.paragraph_format.line_spacing=Pt(12);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.keep_with_next=index == 0
    p.paragraph_format.keep_together=False
    for run in p.runs:
        run.font.name='Times New Roman';run.font.size=Pt(9)
        run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体')

for i in range(4):doc.tables[0].cell(i,1).paragraphs[0].text='待本人填写'
doc.paragraphs[19].text='题目序号 32    任务名称：智能代码生成与辅助工具'
doc.paragraphs[20].text='实践开展时间：待本人填写       报告状态：工程草稿'
for style_name in ['Title','Heading 1','Heading 2']:
    if style_name in doc.styles: doc.styles[style_name].font.color.rgb=RGBColor(0,0,0)
target=root/'deliverables/课程设计报告草稿.docx'
target.parent.mkdir(exist_ok=True)
doc.save(target)
(root/'build/artifact.md').write_text(f'''# Report template contract
Reference: {reference}
SHA256: {hashlib.sha256(reference.read_bytes()).hexdigest()}
Original retained source: 智能应用系统课程设计报告-2025模版.doc (unchanged)
Reference render: build/template-1.png through template-3.png, 3 pages.
Keep the source cover, school logo, metadata table, instruction page and one-column report table.
Fill report sections in their existing cells; allow cell/page expansion as the source permits.
Use 宋体 for Chinese and Times New Roman for English, black body text 10.5 pt.
Appendix code: 9 pt, exactly 12 pt line spacing, as requested by template.
Personal fields and reflection remain explicitly pending; no invented personal information or model scores.
''',encoding='utf-8')
print(target)
