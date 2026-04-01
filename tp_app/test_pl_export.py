"""Quick test: end-to-end template export with pl_overview_text"""
import os, tempfile
from utils.dummy_data import DUMMY_DATA
from docxtpl import DocxTemplate

state = dict(DUMMY_DATA)
state['pl_overview_text'] = (
    "The overview of SMI profit/loss for FY 2024 and FY 2023:\n"
    "- Sales revenue grew from IDR 390B to IDR 420B, a 7.69% increase.\n"
    "- COGS rose to IDR 315B from IDR 296.4B, an increase of 6.27%.\n"
    "- Gross profit margin improved from 24.0% to 25.0%.\n"
    "- Operating profit surged by 18.46% to IDR 46.2B.\n"
    "- Net income rose from IDR 26.6B to IDR 32.4B, a 21.90% increase."
)

tpl = DocxTemplate('TP_Local_File_TEMPLATE_hdrfix.docx')

from export.docx_template_export import build_context
ctx = build_context(state, tpl)
print('[PASS] build_context succeeded')
print('pl_overview_text length:', len(ctx.get('pl_overview_text', '')))

# Render template
tpl.render(ctx, autoescape=True)
print('[PASS] template rendered')

# Run post-processing
from export.docx_template_export import _overwrite_section_bodies
_overwrite_section_bodies(tpl, ctx)
print('[PASS] _overwrite_section_bodies succeeded')

# Save to temp file
out = os.path.join(tempfile.gettempdir(), 'test_pl_overview.docx')
tpl.save(out)
print('[PASS] saved to', out)

# Verify the P/L overview section in output
from docx import Document
doc = Document(out)
paras = doc.paragraphs
for i, p in enumerate(paras):
    if 'overview of profit' in p.text.lower() and p.style.name.startswith('Heading'):
        print()
        print('Found heading [%d]: %s' % (i, p.text[:80]))
        for j in range(i+1, min(i+12, len(paras))):
            pj = paras[j]
            if pj.style.name.startswith('Heading'):
                print('  [%d] HEADING: %s' % (j, pj.text[:80]))
                break
            print('  [%d] %-20s | %s' % (j, pj.style.name, pj.text[:100]))
        break
