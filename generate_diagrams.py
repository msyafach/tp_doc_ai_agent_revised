# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
generate_diagrams.py
====================
Converts all ```plantuml ... ``` fenced code blocks in README.md to PNG images
by calling the public PlantUML rendering server, then replaces the code blocks
with Markdown image references.

Usage:
    uv run python generate_diagrams.py

Output:
    docs/images/<DiagramName>.png  — one PNG per diagram
    README.md                      — updated in-place
"""
import re
import zlib
import struct
import sys
from pathlib import Path

import requests

# ─── PlantUML URL encoding ─────────────────────────────────────────────────────
# PlantUML server uses a custom base64 alphabet + zlib deflate (no headers).

_PLANTUML_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
)


def _encode6bit(b: int) -> str:
    return _PLANTUML_ALPHABET[b & 0x3F]


def _append3bytes(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return (
        _encode6bit(c1)
        + _encode6bit(c2)
        + _encode6bit(c3)
        + _encode6bit(c4)
    )


def _plantuml_base64(data: bytes) -> str:
    result = []
    i = 0
    while i < len(data):
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0
        result.append(_append3bytes(b1, b2, b3))
        i += 3
    return "".join(result)


def encode_plantuml(uml_text: str) -> str:
    """Encode a PlantUML diagram string to its URL-safe token."""
    compressed = zlib.compress(uml_text.encode("utf-8"))
    # Strip zlib header (2 bytes) and checksum (4 bytes) → raw deflate
    deflated = compressed[2:-4]
    return _plantuml_base64(deflated)


# ─── Fetch PNG from PlantUML server ───────────────────────────────────────────

PLANTUML_SERVER = "https://www.plantuml.com/plantuml/png"


def fetch_png(uml_text: str) -> bytes:
    token = encode_plantuml(uml_text)
    url = f"{PLANTUML_SERVER}/{token}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    if response.headers.get("Content-Type", "").startswith("text"):
        # Server returned an error page instead of a PNG
        raise RuntimeError(
            f"PlantUML server returned text instead of PNG.\n"
            f"URL: {url}\nResponse: {response.text[:500]}"
        )
    return response.content


# ─── Main ─────────────────────────────────────────────────────────────────────

README_PATH = Path(__file__).parent / "README.md"
IMAGES_DIR = Path(__file__).parent / "docs" / "images"

# Matches a ```plantuml ... ``` block, capturing the diagram name from @startuml
BLOCK_PATTERN = re.compile(
    r"```plantuml\n(@startuml\s+(\S+).*?@enduml)\n```",
    re.DOTALL,
)

# The "Paste the block above..." hint line that follows some diagrams
PASTE_HINT_PATTERN = re.compile(
    r"\n\n> Paste the block above into \[.*?\]\(.*?\)[^\n]*\n"
)


def main():
    if not README_PATH.exists():
        print(f"ERROR: {README_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    readme = README_PATH.read_text(encoding="utf-8")
    matches = list(BLOCK_PATTERN.finditer(readme))

    if not matches:
        print("No ```plantuml blocks found in README.md.")
        return

    print(f"Found {len(matches)} PlantUML diagram(s).")
    replacements: list[tuple[str, str]] = []  # (original_block, markdown_image)

    for match in matches:
        uml_text = match.group(1)
        diagram_name = match.group(2)
        png_path = IMAGES_DIR / f"{diagram_name}.png"
        rel_path = png_path.relative_to(README_PATH.parent).as_posix()

        print(f"  Rendering '{diagram_name}' ... ", end="", flush=True)
        try:
            png_data = fetch_png(uml_text)
            png_path.write_bytes(png_data)
            print(f"saved to {rel_path} ({len(png_data):,} bytes)")
        except Exception as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            sys.exit(1)

        md_image = f"![{diagram_name}]({rel_path})"
        replacements.append((match.group(0), md_image))

    # Apply replacements
    updated = readme
    for original_block, md_image in replacements:
        updated = updated.replace(original_block, md_image, 1)

    # Remove "Paste the block above..." hint lines (no longer needed)
    updated = PASTE_HINT_PATTERN.sub("\n\n", updated)

    README_PATH.write_text(updated, encoding="utf-8")
    print(f"\nREADME.md updated — {len(matches)} diagram(s) replaced with PNG references.")


if __name__ == "__main__":
    main()
