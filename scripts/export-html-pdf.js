/**
 * export-html-pdf.js
 *
 * Converts the pre-rendered HTML export of the README to PDF (A3 landscape).
 * Unlike export-pdf.js (which builds HTML from Markdown + renders Mermaid),
 * this script loads the existing HTML file directly — diagrams are already
 * embedded as SVGs so no rendering step is needed.
 *
 * Usage:
 *   node scripts/export-html-pdf.js
 *
 * Input:  "TP Local File Generator — README.html"  (+ _files/ assets folder)
 * Output: "TP Local File Generator — README.pdf"
 */

const puppeteer = require("puppeteer");
const path = require("path");
const { pathToFileURL } = require("url");

const HTML_PATH   = path.resolve(__dirname, "../TP Local File Generator — README.html");
const OUTPUT_PATH = path.resolve(__dirname, "../TP Local File Generator — README.pdf");

(async () => {
  console.log("🚀  Launching headless browser …");
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();

  // A4 portrait: 210mm × 297mm → at 96 dpi ≈ 794 × 1123 px
  await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 1 });

  // Keep screen styles — without this Puppeteer switches to @media print
  // which strips colours, backgrounds and layout from the Typora theme.
  await page.emulateMediaType("screen");

  // Use file:// URL so Puppeteer can access _files/ assets (CSS, images, fonts)
  const fileUrl = pathToFileURL(HTML_PATH).href;
  console.log(`🌐  Loading: ${HTML_PATH}`);
  await page.goto(fileUrl, { waitUntil: "networkidle0", timeout: 60_000 });

  // Let any deferred rendering (fonts, lazy images) settle
  await new Promise((r) => setTimeout(r, 1500));

  // Inject CSS to:
  // 1. Collapse slide/section fixed heights so content flows naturally
  // 2. Prevent orphaned headings and broken blocks
  await page.addStyleTag({ content: `
    /* Remove slide/presentation fixed sizing — make sections flow */
    section, .slide, [class*="slide"], [class*="page"] {
      height: auto !important;
      min-height: 0 !important;
      max-height: none !important;
      overflow: visible !important;
      display: block !important;
      page-break-inside: auto !important;
      break-inside: auto !important;
    }

    /* Keep headings with following content */
    h1, h2, h3, h4, h5, h6 {
      page-break-after: avoid !important;
      break-after:      avoid !important;
    }

    /* Keep blocks intact */
    pre, table, figure, blockquote {
      page-break-inside: avoid !important;
      break-inside:      avoid !important;
    }

    p, li { orphans: 3; widows: 3; }
  ` });

  // Scale down any SVG taller than one usable page height
  await page.evaluate(() => {
    const MAX_H = 680;
    document.querySelectorAll("svg").forEach((svg) => {
      const { width, height } = svg.getBoundingClientRect();
      if (height > MAX_H) {
        const scale = MAX_H / height;
        svg.style.setProperty("width",  Math.round(width * scale) + "px", "important");
        svg.style.setProperty("height", MAX_H + "px", "important");
      }
    });
  });

  console.log("📄  Exporting PDF …");
  await page.pdf({
    path: OUTPUT_PATH,
    format: "A4",
    landscape: false,
    printBackground: true,
    margin: { top: "14mm", right: "14mm", bottom: "14mm", left: "14mm" },
  });

  await browser.close();
  console.log(`✅  Done! → ${OUTPUT_PATH}`);
})();
