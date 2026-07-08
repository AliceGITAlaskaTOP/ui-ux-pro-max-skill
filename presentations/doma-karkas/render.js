const { chromium } = require('playwright-core');
const fs = require('fs');

(async () => {
  const [htmlPath, outPdf, shotDir] = process.argv.slice(2);
  fs.mkdirSync(shotDir, { recursive: true });
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    ignoreDefaultArgs: ['--headless=old', '--headless'],
    args: ['--headless=new', '--no-sandbox', '--disable-gpu', '--font-render-hinting=none'],
  });
  const page = await browser.newPage({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1.5,
  });
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  // Per-slide screenshots (screen media) for visual QA
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: `${shotDir}/slide-${String(i + 1).padStart(2, '0')}.png` });
  }

  // PDF (print media, one slide per page via CSS @page + page-break)
  await page.pdf({
    path: outPdf,
    width: '1280px',
    height: '720px',
    printBackground: true,
    preferCSSPageSize: true,
  });

  // Report which fonts actually loaded
  const loaded = await page.evaluate(() =>
    Array.from(document.fonts).map(f => `${f.family} ${f.weight} ${f.status}`)
  );
  console.log('SLIDES:', slides.length);
  console.log('FONTS:', JSON.stringify([...new Set(loaded)]));
  await browser.close();
})().catch(e => { console.error('RENDER ERROR:', e.message); process.exit(1); });
