# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
generate_diagrams.py
====================
Converts all PlantUML source files in docs/diagrams/*.puml to PNG images by
calling the public PlantUML rendering server, saving results to docs/images/.

Usage:
    uv run python generate_diagrams.py

Source files:   docs/diagrams/<DiagramName>.puml
Output images:  docs/images/<DiagramName>.png

Edit .puml files directly in any text editor or VS Code (PlantUML extension),
then re-run this script to regenerate the PNGs.
"""
import sys
import zlib
from pathlib import Path

import requests

# ─── PlantUML URL encoding ─────────────────────────────────────────────────────
# PlantUML server requires: zlib deflate (no headers) + custom base64 alphabet.

_PLANTUML_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
)


def _append3bytes(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return (
        _PLANTUML_ALPHABET[c1]
        + _PLANTUML_ALPHABET[c2]
        + _PLANTUML_ALPHABET[c3]
        + _PLANTUML_ALPHABET[c4]
    )


def _plantuml_base64(data: bytes) -> str:
    result = []
    for i in range(0, len(data), 3):
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0
        result.append(_append3bytes(b1, b2, b3))
    return "".join(result)


def encode_plantuml(uml_text: str) -> str:
    """Encode a PlantUML diagram string to its URL-safe token."""
    compressed = zlib.compress(uml_text.encode("utf-8"))
    deflated = compressed[2:-4]  # strip zlib header (2 bytes) + checksum (4 bytes)
    return _plantuml_base64(deflated)


# ─── Fetch PNG from PlantUML server ───────────────────────────────────────────

PLANTUML_SERVER = "https://www.plantuml.com/plantuml/png"


def fetch_png(uml_text: str) -> bytes:
    token = encode_plantuml(uml_text)
    url = f"{PLANTUML_SERVER}/{token}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise RuntimeError(
            f"PlantUML server returned non-image response ({content_type}).\n"
            f"URL: {url}\nBody (first 300 chars): {response.text[:300]}"
        )
    return response.content


# ─── Main ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
DIAGRAMS_DIR = ROOT / "docs" / "diagrams"
IMAGES_DIR = ROOT / "docs" / "images"


def main():
    if not DIAGRAMS_DIR.exists():
        print(f"ERROR: {DIAGRAMS_DIR} not found.", file=sys.stderr)
        sys.exit(1)

    puml_files = sorted(DIAGRAMS_DIR.glob("*.puml"))
    if not puml_files:
        print(f"No .puml files found in {DIAGRAMS_DIR}.")
        return

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(puml_files)} diagram(s) in {DIAGRAMS_DIR.relative_to(ROOT)}/\n")
    errors = []

    for puml_file in puml_files:
        name = puml_file.stem
        png_path = IMAGES_DIR / f"{name}.png"
        rel_png = png_path.relative_to(ROOT).as_posix()

        print(f"  Rendering '{name}' ...", end=" ", flush=True)
        try:
            uml_text = puml_file.read_text(encoding="utf-8")
            png_data = fetch_png(uml_text)
            png_path.write_bytes(png_data)
            print(f"saved ({len(png_data):,} bytes)  ->  {rel_png}")
        except Exception as exc:
            print(f"FAILED")
            errors.append((name, exc))

    print()
    if errors:
        for name, exc in errors:
            print(f"ERROR [{name}]: {exc}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"All {len(puml_files)} diagram(s) rendered successfully.")
        print(f"Images saved to: {IMAGES_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
