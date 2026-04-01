"""
Wraps tp_app DOCX export functions.
"""
from __future__ import annotations
import os
import tempfile
from typing import Literal


def export_docx(
    state: dict,
    export_type: Literal["builder", "template"] = "builder",
) -> bytes:
    """
    Generate a DOCX file and return raw bytes.
    export_type:
      "builder"  — uses python-docx generate_tp_document()
      "template" — uses docxtpl render_tp_document()
    """
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        output_path = tmp.name

    try:
        if export_type == "builder":
            from export.docx_export import generate_tp_document
            generate_tp_document(state, output_path)
        else:
            from export.docx_template_export import render_tp_document
            render_tp_document(state, output_path)

        with open(output_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass
