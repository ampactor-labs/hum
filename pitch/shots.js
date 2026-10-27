// Captures the slide pictures from the bundled session, so every picture shows
// the same run that the hosted copy plays. Run it after record.py.
//   node pitch/shots.js    # writes img/stage-calm.png, img/stage-rush.png,
//                          # img/stage-trip.png, img/card-refused.png and hero.png
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..'), img = path.join(__dirname, 'img');
const SPEED = 4, PORT = 8791;
(async () => {
  const srv = spawn('python3', ['-I', '-m', 'http.server', String(PORT), '--bind', '127.0.0.1', '--directory', root], { stdio: 'ignore' });
  try {
    await new Promise(r => setTimeout(r, 1500));
    const b = await chromium.launch();
    const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
    await p.goto(`http://127.0.0.1:${PORT}/?session=sessions/default.ndjson&speed=${SPEED}`, { waitUntil: 'load' });
    const head = () => p.locator('#stHead').innerText();
    // Waits for a beat of the session, read from the sentence the stage shows.
    const until = async (test, beat) => {
      const t0 = Date.now();
      while (!(await test())) {
        if (Date.now() - t0 > 180000) throw new Error('the session never showed ' + beat);
        await p.waitForTimeout(50);
      }
    };
    // Takes the picture a few seconds of session time after the beat begins.
    const shot = async (name, seconds) => {
      await p.waitForTimeout(seconds * 1000 / SPEED);
      await p.screenshot({ path: path.join(img, name + '.png') });
      console.log(name + ': ' + (await head()));
    };
    await until(async () => / hums /.test(await head()) && /\d/.test(await p.locator('#stHz').innerText()), 'the calm');
    await shot('stage-calm', 6);
    await until(async () => /^Rush hour/.test(await head()), 'the rush hour');
    await shot('stage-rush', 2.5);
    await until(async () => /^Two power plants/.test(await head()), 'the event');
    await shot('stage-trip', 1.2);
    fs.copyFileSync(path.join(img, 'stage-trip.png'), path.join(__dirname, 'hero.png'));
    await p.keyboard.press('r');
    await p.waitForTimeout(400);
    await p.locator('#ovRefused .scard').screenshot({ path: path.join(img, 'card-refused.png') });
    console.log('card-refused');
    await b.close();
  } finally {
    srv.kill();
  }
})().catch(e => { console.error(e); process.exit(1); });
