const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT_DIR = 'C:\\Users\\info\\Dropbox\\Projects\\component-catalog\\previews';

const items = [
  {key: 'Buttons #20', url: 'https://www.smoothui.dev/docs/components/clip-corners-button', lib: 'smoothui'},
  {key: 'Buttons #21', url: 'https://www.smoothui.dev/docs/components/dot-morph-button', lib: 'smoothui'},
  {key: 'Buttons #22', url: 'https://www.smoothui.dev/docs/components/smooth-button', lib: 'smoothui'},
  {key: 'Cards #39', url: 'https://www.smoothui.dev/docs/components/app-download-stack', lib: 'smoothui'},
  {key: 'Cards #40', url: 'https://www.smoothui.dev/docs/components/apple-invites', lib: 'smoothui'},
  {key: 'Cards #41', url: 'https://www.smoothui.dev/docs/components/book', lib: 'smoothui'},
  {key: 'Cards #42', url: 'https://www.smoothui.dev/docs/components/glow-hover-card', lib: 'smoothui'},
  {key: 'Cards #43', url: 'https://www.smoothui.dev/docs/components/image-metadata-preview', lib: 'smoothui'},
  {key: 'Cards #44', url: 'https://www.smoothui.dev/docs/components/product-card', lib: 'smoothui'},
  {key: 'Cards #45', url: 'https://www.smoothui.dev/docs/components/scrollable-card-stack', lib: 'smoothui'},
  {key: 'Cards #46', url: 'https://www.smoothui.dev/docs/components/tweet-card', lib: 'smoothui'},
  {key: 'Hero Animations #39', url: 'https://seraui.com/docs/hero', lib: 'seraui'},
  {key: 'Buttons #23', url: 'https://seraui.com/docs/glow-button', lib: 'seraui'},
  {key: 'Buttons #24', url: 'https://seraui.com/docs/modern-button', lib: 'seraui'},
];

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, {recursive: true});
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({viewport: {width: 1280, height: 800}, deviceScaleFactor: 2});
  const results = [];

  for (const item of items) {
    const page = await context.newPage();
    const filename = item.key.replace(/[# ]/g, '-').toLowerCase() + '.png';
    const filepath = path.join(OUT_DIR, filename);
    let status = 'unknown';

    try {
      await page.goto(item.url, {waitUntil: 'domcontentloaded', timeout: 30000});
      await page.waitForTimeout(5000);

      if (item.lib === 'smoothui') {
        // Hide site chrome
        await page.evaluate(() => {
          document.querySelectorAll('header, nav, aside, footer, [class*="float"], [class*="toolbar"], [role="tablist"], [class*="tab-list"]').forEach(el => el.style.display = 'none');
        });
        await page.waitForTimeout(500);
        
        const selectors = ['.not-prose[class*="bg"]', '.frame-box', '[class*="not-prose"]'];
        for (const sel of selectors) {
          const el = await page.$(sel);
          if (el) {
            const box = await el.boundingBox();
            if (box && box.width > 100 && box.height > 50) {
              await el.screenshot({path: filepath, timeout: 15000});
              status = 'ok:' + sel;
              break;
            }
          }
        }
        if (status === 'unknown') {
          const main = await page.$('main');
          if (main) {
            const box = await main.boundingBox();
            if (box) {
              await page.screenshot({path: filepath, clip: {x: box.x + 20, y: box.y + 200, width: box.width - 40, height: 350}});
              status = 'clip-main';
            }
          }
        }
      } else if (item.lib === 'seraui') {
        // Click Preview tab
        await page.evaluate(() => {
          for (const b of document.querySelectorAll('button')) {
            if (b.textContent.trim() === 'Preview') { b.click(); break; }
          }
        });
        await page.waitForTimeout(1500);
        
        // Hide site chrome
        await page.evaluate(() => {
          document.querySelectorAll('header, nav, aside, footer, [class*="sidebar"], [class*="Sidebar"], [role="tablist"], [class*="inline-flex"][class*="rounded-full"]').forEach(el => el.style.display = 'none');
        });
        await page.waitForTimeout(500);
        
        const selectors = ['div[class*="not-prose"][class*="rounded"]', 'div[class*="not-prose"][class*="grid"]', 'div[class*="not-prose"]'];
        for (const sel of selectors) {
          const el = await page.$(sel);
          if (el) {
            const box = await el.boundingBox();
            if (box && box.width > 200 && box.height > 100) {
              await el.screenshot({path: filepath, timeout: 15000});
              status = 'ok:' + sel;
              break;
            }
          }
        }
        if (status === 'unknown') {
          const rect = await page.evaluate(() => {
            for (const el of document.querySelectorAll('div')) {
              const r = el.getBoundingClientRect();
              if (r.top > 500 && r.width > 400 && r.height > 100 && r.height < 500) {
                return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(Math.min(r.height, 400))};
              }
            }
            return null;
          });
          if (rect) {
            await page.screenshot({path: filepath, clip: {x: rect.x, y: rect.y, width: rect.w, height: rect.h}});
            status = 'clip';
          } else {
            status = 'no-shot';
          }
        }
      } else {
        status = 'no-match';
      }
    } catch (e) {
      status = 'error:' + e.message.substring(0, 60);
    }

    results.push({key: item.key, status, file: filename});
    await page.close();
    console.log(`${item.key}: ${status}`);
  }

  await browser.close();
  console.log('\n=== RESULTS ===');
  for (const r of results) console.log(`${r.key}: ${r.status}`);
  fs.writeFileSync(path.join(OUT_DIR, 'pilot-results-v4.json'), JSON.stringify(results, null, 2));
})();