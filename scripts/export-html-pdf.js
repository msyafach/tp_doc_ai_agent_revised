/**
 * export-html-pdf.js
 *
 * Converts "TP Local File Generator — README.html" → PDF by:
 *   1. Loading the HTML in screen mode (preserves exact visual styling)
 *   2. Screenshotting every .page element individually (no print CSS, no clipping)
 *   3. Stitching screenshots into a multi-page PDF with pdf-lib
 *
 * Usage:
 *   node scripts/export-html-pdf.js
 */

const puppeteer = require("puppeteer");
const { PDFDocument } = require("pdf-lib");
const { pathToFileURL } = require("url");
const path = require("path");
const fs   = require("fs");

const HTML_PATH   = path.resolve(__dirname, "../TP Local File Generator — README.html");
const OUTPUT_PATH = path.resolve(__dirname, "../TP Local File Generator — README.pdf");

(async () => {
  console.log("🚀  Launching headless browser …");
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();

  // Screen mode — keeps the beautiful HTML styling, no @media print overrides
  await page.emulateMediaType("screen");

  // 2× device scale for sharp text in the PDF screenshots
  await page.setViewport({ width: 1200, height: 900, deviceScaleFactor: 2 });

  const fileUrl = pathToFileURL(HTML_PATH).href;
  console.log(`🌐  Loading: ${HTML_PATH}`);
  await page.goto(fileUrl, { waitUntil: "networkidle0", timeout: 60_000 });

  // Let fonts and lazy assets settle
  await new Promise((r) => setTimeout(r, 2000));

  // Base CSS has overflow:hidden on .page — remove it so full content is visible
  await page.evaluate(() => {
    document.querySelectorAll(".page").forEach((el) => {
      el.style.setProperty("overflow", "visible", "important");
      el.style.setProperty("height", "auto", "important");
      el.style.setProperty("min-height", "0", "important");
    });
  });

  // Screenshot every .page element exactly as rendered on screen
  console.log("📸  Screenshotting each .page …");
  const pageElements = await page.$$(".page");
  if (pageElements.length === 0) {
    console.error("❌  No .page elements found — check the HTML structure.");
    await browser.close();
    process.exit(1);
  }

  const screenshots = [];
  for (let i = 0; i < pageElements.length; i++) {
    const shot = await pageElements[i].screenshot({ type: "png" });
    screenshots.push(shot);
    console.log(`   page ${i + 1} / ${pageElements.length}`);
  }

  await browser.close();

  // Stitch screenshots into a PDF — one image per page
  console.log("📄  Assembling PDF …");
  const pdfDoc = await PDFDocument.create();
  for (const shot of screenshots) {
    const img     = await pdfDoc.embedPng(shot);
    const pdfPage = pdfDoc.addPage([img.width, img.height]);
    pdfPage.drawImage(img, { x: 0, y: 0, width: img.width, height: img.height });
  }

  const bytes = await pdfDoc.save();
  fs.writeFileSync(OUTPUT_PATH, bytes);
  console.log(`✅  Done! → ${OUTPUT_PATH}  (${pageElements.length} pages)`);
})();
