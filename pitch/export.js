// Exports the show and both decks (one page per slide, 1920 by 1080) and the one-pager
// (Letter) to PDF through Playwright's Chromium, then the one file to upload:
// HUM-Morgan-Espitia.pdf, the hosted tour as pages in its own order. The slides
// stay text, so their links work; each live screen and card is a picture of the
// page as the tour leaves it; the backup pages follow at the end.
//   node export.js            # writes the PDFs beside the sources
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const PORT = 8799;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const deck of ['show', 'torus', 'nucleus']) {
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

  // The tour, step by step, from the page as the hosted copy serves it.
  const root = path.join(__dirname, '..');
  const srv = spawn('python3', ['-I', '-m', 'http.server', String(PORT), '--bind', '127.0.0.1', '--directory', root], { stdio: 'ignore' });
  try {
    await new Promise(r => setTimeout(r, 800));
    const tour = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1.5 });
    await tour.goto(`http://127.0.0.1:${PORT}/index.html?capture&speed=4`, { waitUntil: 'load' });
    await tour.waitForTimeout(1500);
    const steps = [];
    for (let k = 0; ; k++) {
      if (k > 0) { await tour.keyboard.press('ArrowRight'); }
      const at = await tour.evaluate(() => ({ text: document.getElementById('tourText').textContent, deck: document.getElementById('ovDeck').classList.contains('show'), again: !document.getElementById('tourAgain').hidden }));
      if (k > 0 && at.text.startsWith('Start')) break;
      if (at.deck) {
        await tour.waitForTimeout(300);
        steps.push({ slide: await tour.evaluate(() => parseInt(document.getElementById('deckFrame').contentWindow.location.hash.slice(1), 10) || 0) });
      } else {
        // A live screen plays its stretch of the recording at four times speed and holds; a card shows at once.
        await tour.waitForTimeout(at.again ? 6000 : 600);
        steps.push({ picture: 'data:image/jpeg;base64,' + (await tour.screenshot({ type: 'jpeg', quality: 88 })).toString('base64') });
      }
    }
    // One document: the show's slides and the pictures in the tour's order, then the backup pages.
    const one = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await one.goto(`http://127.0.0.1:${PORT}/pitch/show.html`, { waitUntil: 'load' });
    await one.evaluate(async (steps) => {
      const deck = document.querySelector('.deck'), slides = Array.from(deck.querySelectorAll('.slide'));
      const nucleus = new DOMParser().parseFromString(await (await fetch('nucleus.html')).text(), 'text/html');
      const backups = Array.from(nucleus.querySelectorAll('.slide')).filter(s => s.querySelector('.tag'));
      const pages = steps.map(s => {
        if (s.slide != null) return slides[s.slide].cloneNode(true);
        const sec = document.createElement('section'); sec.className = 'slide'; sec.style.padding = '0';
        const img = document.createElement('img'); img.src = s.picture; img.style.cssText = 'width:1920px;height:1080px;display:block';
        sec.appendChild(img); return sec;
      });
      const used = new Set(steps.filter(s => s.slide != null).map(s => s.slide));
      slides.forEach((s, k) => { if (!used.has(k)) pages.push(s.cloneNode(true)); });
      backups.forEach(s => pages.push(document.importNode(s, true)));
      deck.replaceChildren(...pages);
      await Promise.all(Array.from(document.images).map(i => i.complete ? null : new Promise(r => { i.onload = i.onerror = r; })));
    }, steps);
    await one.emulateMedia({ media: 'print' });
    await one.waitForTimeout(800);
    await one.pdf({ path: path.join(__dirname, 'HUM-Morgan-Espitia.pdf'), width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
    console.log('HUM-Morgan-Espitia.pdf: ' + steps.length + ' steps, then the backup pages');
  } finally {
    srv.kill();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
