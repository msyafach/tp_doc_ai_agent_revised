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

// ── Brand palette ─────────────────────────────────────────────────────────────
const BRAND = {
  green:       "#13A538",
  greenLight:  "#d6f0de",  // pastel tint
  blue:        "#0095D6",
  blueLight:   "#cce9f6",  // pastel tint
  grey:        "#757574",
  greyLight:   "#efefef",  // pastel tint
  white:       "#ffffff",
  text:        "#2d2d2d",
};

// ── HTML template ─────────────────────────────────────────────────────────────

function buildHtml(markdownContent) {
  // Strip per-diagram %%{init:...}%% overrides so the global mermaid.initialize()
  // brand theme applies uniformly to every diagram.
  const cleaned = markdownContent.replace(/^%%\{init:.*\}%%\n?/gm, "");
  const body = marked.parse(cleaned);

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
      color: ${BRAND.text};
      background: ${BRAND.white};
      max-width: 100%;
      margin: 0;
      padding: 0;
    }

    /* ── Headings ──────────────────────────────────────────────────── */
    h1 {
      font-size: 22pt;
      color: ${BRAND.green};
      border-bottom: 3px solid ${BRAND.green};
      padding-bottom: 6px;
      margin-top: 0;
      page-break-before: avoid;
    }
    h2 {
      font-size: 16pt;
      color: ${BRAND.blue};
      border-bottom: 2px solid ${BRAND.blue};
      padding-bottom: 4px;
      margin-top: 28px;
      page-break-after: avoid;
    }
    h3 {
      font-size: 13pt;
      color: ${BRAND.grey};
      border-bottom: 1px solid #c8c8c8;
      padding-bottom: 2px;
      margin-top: 20px;
      page-break-after: avoid;
    }
    h4 {
      font-size: 11.5pt;
      color: ${BRAND.green};
      margin-top: 16px;
      page-break-after: avoid;
    }

    /* ── Mermaid diagrams ──────────────────────────────────────────── */
    /* Let Mermaid's own useMaxWidth control SVG width.                */
    /* Forcing width:100% on sequence diagrams makes them very tall.  */
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
      max-width: 100%;
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
      background: ${BRAND.green};
      color: ${BRAND.white};
      font-weight: 600;
      text-align: left;
      padding: 6px 10px;
      border: 1px solid #0e8a2e;
    }
    td {
      padding: 5px 10px;
      border: 1px solid #d0d0d0;
      vertical-align: top;
    }
    tr:nth-child(even) td { background: ${BRAND.greenLight}; }

    /* ── Code blocks ───────────────────────────────────────────────── */
    pre {
      background: ${BRAND.blueLight};
      border: 1px solid #a8d8f0;
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
      background: ${BRAND.blueLight};
      color: #006fa3;
      padding: 1px 4px;
      border-radius: 3px;
    }
    pre code {
      background: none;
      color: inherit;
      padding: 0;
      font-size: inherit;
    }

    /* ── Blockquotes ───────────────────────────────────────────────── */
    blockquote {
      border-left: 4px solid ${BRAND.blue};
      margin: 10px 0;
      padding: 4px 14px;
      color: #555;
      background: ${BRAND.blueLight};
    }

    /* ── Lists ─────────────────────────────────────────────────────── */
    ul, ol { padding-left: 22px; }
    li { margin: 3px 0; }

    /* ── Horizontal rule ───────────────────────────────────────────── */
    hr {
      border: none;
      border-top: 2px solid ${BRAND.greenLight};
      margin: 20px 0;
    }

    /* ── Links ─────────────────────────────────────────────────────── */
    a { color: ${BRAND.blue}; text-decoration: underline; }

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

    // Initialise Mermaid with brand palette (base theme + custom variables)
    mermaid.initialize({
      startOnLoad: true,
      theme: "base",
      themeVariables: {
        fontSize:             "11px",
        primaryColor:         "${BRAND.greenLight}",
        primaryBorderColor:   "${BRAND.green}",
        primaryTextColor:     "${BRAND.text}",
        secondaryColor:       "${BRAND.blueLight}",
        secondaryBorderColor: "${BRAND.blue}",
        tertiaryColor:        "${BRAND.greyLight}",
        tertiaryBorderColor:  "${BRAND.grey}",
        lineColor:            "${BRAND.grey}",
        edgeLabelBackground:  "${BRAND.white}",
        clusterBkg:           "${BRAND.blueLight}",
        clusterBorder:        "${BRAND.blue}",
        // Sequence diagram actors
        actorBkg:             "${BRAND.greenLight}",
        actorBorder:          "${BRAND.green}",
        actorTextColor:       "${BRAND.text}",
        actorLineColor:       "${BRAND.grey}",
        // Sequence notes
        noteBkgColor:         "${BRAND.blueLight}",
        noteTextColor:        "${BRAND.text}",
        noteBorderColor:      "${BRAND.blue}",
        // Sequence activations
        activationBkgColor:   "${BRAND.greenLight}",
        activationBorderColor:"${BRAND.green}",
        // Section labels
        labelBoxBkgColor:     "${BRAND.greenLight}",
        labelBoxBorderColor:  "${BRAND.green}",
        labelTextColor:       "${BRAND.text}",
        // Loop / alt boxes
        loopTextColor:        "${BRAND.text}",
        signalColor:          "${BRAND.grey}",
        signalTextColor:      "${BRAND.text}",
      },
      flowchart: { useMaxWidth: true, htmlLabels: true,
                   nodeSpacing: 35, rankSpacing: 50 },
      sequence:  { useMaxWidth: true, mirrorActors: false,
                   messageMargin: 20, width: 120, height: 28 },
      gantt:     { useMaxWidth: true },
      journey:   { useMaxWidth: true },
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
        // Use setProperty with 'important' so it overrides any !important CSS rules
        svg.style.setProperty("width",  Math.round(width * scale) + "px", "important");
        svg.style.setProperty("height", MAX_H + "px", "important");
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
