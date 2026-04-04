# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx"]
# ///
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document

doc = Document("TP_Local_File_TEMPLATE.docx")

# Find the position of tables in the body and get preceding paragraphs
print("=== Document structure: Tables and preceding paragraphs ===\n")

table_indices = []
body_elems = list(doc.element.body)

# First, find all table positions
for i, elem in enumerate(body_elems):
    if 'tbl' in elem.tag.lower():
        table_indices.append(i)

print(f"Total tables found: {len(table_indices)}")
print(f"Table 19-25 are at body element indices: {table_indices[19:26]}\n")

# Now for tables 19-25, get preceding paragraphs
from docx.oxml.ns import qn

for table_num in range(19, 26):
    elem_idx = table_indices[table_num]
    print(f"\n=== TABLE {table_num} (body element {elem_idx}) ===")
    print("Preceding 3 paragraphs:")
    
    # Go back and find paragraphs
    para_found = 0
    for check_idx in range(elem_idx - 1, -1, -1):
        elem = body_elems[check_idx]
        if 'tbl' not in elem.tag.lower():
            # Extract text
            text_parts = []
            for t in elem.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    text_parts.append(t.text)
            text = "".join(text_parts).strip()
            if text:
                print(f"  [{para_found}] {text[:100]}")
                para_found += 1
                if para_found >= 3:
                    break
    
    # Show first few rows of the table
    table = doc.tables[table_num]
    print(f"Table content: {len(table.rows)} rows x {len(table.columns)} cols")
    if len(table.rows) > 0:
        first_row = table.rows[0]
        tcs = first_row._tr.findall(qn("w:tc"))
        cells = []
        for tc in tcs:
            text = "".join(
                t.text or "" for p in tc.findall(qn("w:p")) for r in p.findall(qn("w:r")) for t in r.findall(qn("w:t"))
            )
            cells.append(text.strip()[:30])
        print(f"  First row: {cells}")
