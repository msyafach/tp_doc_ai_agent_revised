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

  // A3 landscape: 420mm × 297mm → at 96 dpi ≈ 1587 × 1123 px
  await page.setViewport({ width: 1587, height: 1123, deviceScaleFactor: 1 });

  // Use file:// URL so Puppeteer can access _files/ assets (CSS, images, fonts)
  const fileUrl = pathToFileURL(HTML_PATH).href;
  console.log(`🌐  Loading: ${HTML_PATH}`);
  await page.goto(fileUrl, { waitUntil: "networkidle0", timeout: 60_000 });

  // Let any deferred rendering (fonts, lazy images) settle
  await new Promise((r) => setTimeout(r, 1500));

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
    format: "A3",
    landscape: true,
    printBackground: true,
    margin: { top: "16mm", right: "18mm", bottom: "16mm", left: "18mm" },
  });

  await browser.close();
  console.log(`✅  Done! → ${OUTPUT_PATH}`);
})();
