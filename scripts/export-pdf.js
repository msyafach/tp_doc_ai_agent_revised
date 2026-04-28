/**
 * export-pdf.js
 *
 * One-time script to export README.md → README.pdf (A3 landscape).
 * Renders Mermaid diagrams via Puppeteer (headless Chrome).
 *
 * Usage:
 *   node scripts/export-pdf.js
 *
 * First run (install deps):
 *   npm install --prefix scripts puppeteer marked
 */

const puppeteer = require("puppeteer");
const { marked } = require("marked");
const fs = require("fs");
const path = require("path");

const README_PATH = path.resolve(__dirname, "../README.md");
const OUTPUT_PATH = path.resolve(__dirname, "../README.pdf");

// ── HTML template ─────────────────────────────────────────────────────────────

function buildHtml(markdownContent) {
  const body = marked.parse(markdownContent);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>TP Local File Generator — README</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <style>
    /* ── Page setup (A3 landscape) ─────────────────────────────────── */
    @page {
      size: A3 landscape;
      margin: 16mm 18mm;
    }

    * { box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   "Helvetica Neue", Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.65;
      color: #111;
      max-width: 100%;
      margin: 0;
      padding: 0;
    }

    /* ── Headings ──────────────────────────────────────────────────── */
    h1 {
      font-size: 22pt;
      border-bottom: 3px solid #000;
      padding-bottom: 6px;
      margin-top: 0;
      page-break-before: avoid;
    }
    h2 {
      font-size: 16pt;
      border-bottom: 2px solid #333;
      padding-bottom: 4px;
      margin-top: 28px;
      page-break-after: avoid;
    }
    h3 {
      font-size: 13pt;
      border-bottom: 1px solid #aaa;
      padding-bottom: 2px;
      margin-top: 20px;
      page-break-after: avoid;
    }
    h4 {
      font-size: 11.5pt;
      margin-top: 16px;
      page-break-after: avoid;
    }

    /* ── Mermaid diagrams — fit to page width ──────────────────────── */
    .mermaid {
      display: block;
      width: 100%;
      max-width: 100%;
      overflow: visible;
      margin: 16px 0;
      page-break-inside: avoid;
    }
    .mermaid svg {
      display: block;
      width: 100% !important;
      max-width: 100% !important;
      height: auto !important;
    }

    /* ── Tables ────────────────────────────────────────────────────── */
    table {
      border-collapse: collapse;
      width: 100%;
      font-size: 9.5pt;
      margin: 12px 0;
      page-break-inside: avoid;
    }
    th {
      background: #e8e8e8;
      font-weight: 600;
      text-align: left;
      padding: 6px 10px;
      border: 1px solid #bbb;
    }
    td {
      padding: 5px 10px;
      border: 1px solid #bbb;
      vertical-align: top;
    }
    tr:nth-child(even) td { background: #f7f7f7; }

    /* ── Code blocks ───────────────────────────────────────────────── */
    pre {
      background: #f4f4f4;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 10px 14px;
      font-size: 8.5pt;
      line-height: 1.5;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
      page-break-inside: avoid;
    }
    code {
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 8.5pt;
      background: #f0f0f0;
      padding: 1px 4px;
      border-radius: 3px;
    }
    pre code {
      background: none;
      padding: 0;
      font-size: inherit;
    }

    /* ── Blockquotes ───────────────────────────────────────────────── */
    blockquote {
      border-left: 4px solid #999;
      margin: 10px 0;
      padding: 4px 14px;
      color: #444;
      background: #fafafa;
    }

    /* ── Lists ─────────────────────────────────────────────────────── */
    ul, ol { padding-left: 22px; }
    li { margin: 3px 0; }

    /* ── Horizontal rule ───────────────────────────────────────────── */
    hr {
      border: none;
      border-top: 1px solid #ccc;
      margin: 20px 0;
    }

    /* ── Links ─────────────────────────────────────────────────────── */
    a { color: #222; text-decoration: underline; }

    /* ── Page break hints ──────────────────────────────────────────── */
    h2 { page-break-before: auto; }
    p, li { orphans: 3; widows: 3; }
  </style>
</head>
<body>
  ${body}

  <script>
    // Convert <code class="language-mermaid"> blocks to <div class="mermaid">
    document.querySelectorAll("pre > code.language-mermaid").forEach((el) => {
      const div = document.createElement("div");
      div.className = "mermaid";
      div.textContent = el.textContent;
      el.closest("pre").replaceWith(div);
    });

    // Initialise Mermaid — useMaxWidth ensures diagrams scale to container
    mermaid.initialize({
      startOnLoad: true,
      theme: "neutral",
      flowchart:   { useMaxWidth: true, htmlLabels: true },
      sequence:    { useMaxWidth: true },
      gantt:       { useMaxWidth: true },
      journey:     { useMaxWidth: true },
    });
  </script>
</body>
</html>`;
}

// ── Main ──────────────────────────────────────────────────────────────────────

(async () => {
  console.log("📖  Reading README.md …");
  const markdown = fs.readFileSync(README_PATH, "utf-8");
  const html = buildHtml(markdown);

  console.log("🚀  Launching headless browser …");
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();

  // Set viewport to A3 landscape width in px (420mm @ 96dpi ≈ 1587px)
  await page.setViewport({ width: 1587, height: 1123, deviceScaleFactor: 1 });

  console.log("🎨  Rendering HTML + Mermaid diagrams …");
  await page.setContent(html, { waitUntil: "networkidle0" });

  // Wait until every .mermaid div has an <svg> child (all diagrams rendered)
  try {
    await page.waitForFunction(
      () => {
        const divs = [...document.querySelectorAll(".mermaid")];
        return divs.length === 0 || divs.every((d) => d.querySelector("svg"));
      },
      { timeout: 30_000 }
    );
  } catch {
    console.warn("⚠️  Some diagrams may not have fully rendered — continuing.");
  }

  // Extra settle time for SVG layout
  await new Promise((r) => setTimeout(r, 1500));

  // Scale down any SVG taller than one usable page height so it doesn't split across pages.
  // A3 landscape usable height ≈ 297mm − 32mm margins ≈ 265mm → ~1003px at 96dpi.
  // We cap at 680px to leave room for the section heading and paragraph above the diagram.
  await page.evaluate(() => {
    const MAX_H = 680;
    document.querySelectorAll(".mermaid svg").forEach((svg) => {
      const { width, height } = svg.getBoundingClientRect();
      if (height > MAX_H) {
        const scale = MAX_H / height;
        svg.style.width  = Math.round(width * scale) + "px";
        svg.style.height = MAX_H + "px";
      }
    });
  });

  console.log("📄  Exporting PDF …");
  await page.pdf({
    path: OUTPUT_PATH,
    format: "A3",
    landscape: true,
    printBackground: true,
    margin: { top: "16mm", right: "18mm", bottom: "16mm", left: "18mm" },
  });

  await browser.close();
  console.log(`✅  Done! → ${OUTPUT_PATH}`);
})();
