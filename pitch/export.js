// Exports both decks (one page per slide, 1920 by 1080) and the one-pager
// (Letter) to PDF through Playwright's Chromium.
//   node export.js            # writes torus.pdf, nucleus.pdf, nucleus-one-pager.pdf beside the sources
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const deck of ['torus', 'nucleus']) {
    await page.goto('file://' + path.join(__dirname, deck + '.html'), { waitUntil: 'load' });
    await page.emulateMedia({ media: 'print' });
    await page.waitForTimeout(800);
    await page.pdf({ path: path.join(__dirname, deck + '.pdf'), width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
    console.log(deck + '.pdf');
  }
  await page.goto('file://' + path.join(__dirname, 'nucleus-one-pager.html'), { waitUntil: 'load' });
  await page.emulateMedia({ media: 'print' });
  await page.waitForTimeout(500);
  await page.pdf({ path: path.join(__dirname, 'nucleus-one-pager.pdf'), format: 'Letter', printBackground: true, preferCSSPageSize: true });
  console.log('nucleus-one-pager.pdf');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
