const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT_DIR = 'C:\\Users\\info\\Dropbox\\Projects\\component-catalog\\previews';

const items = [
  // SmoothUI — use .frame-box selector
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
  {key: 'Cards #15', url: 'https://ui.aceternity.com/components/github-profile', lib: 'aceternity'},
  // SeraUI — screenshot the div at y~492 (preview container)
  {key: 'Hero Animations #39', url: 'https://seraui.com/docs/hero', lib: 'seraui'},
  {key: 'Buttons #23', url: 'https://seraui.com/docs/glow-button', lib: 'seraui'},
  {key: 'Buttons #24', url: 'https://seraui.com/docs/modern-button', lib: 'seraui'},
];

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, {recursive: true});
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({viewport: {width: 1280, height: 800}, deviceScaleFactor: 1});
  const results = [];

  for (const item of items) {
    const page = await context.newPage();
    const filename = item.key.replace(/[# ]/g, '-').toLowerCase() + '.png';
    const filepath = path.join(OUT_DIR, filename);

    try {
      await page.goto(item.url, {waitUntil: 'networkidle', timeout: 30000});
      await page.waitForTimeout(3000);

      let selector = null;
      if (item.lib === 'smoothui') {
        selector = '.frame-box';
      } else if (item.lib === 'seraui') {
        // SeraUI: the preview tab content is in a div after the Preview/Code tabs
        // Find the div that contains the rendered component
        await page.evaluate(() => {
          // Click the Preview tab if not already active
          const tabs = document.querySelectorAll('button');
          for (const t of tabs) {
            if (t.textContent.trim() === 'Preview') {
              t.click();
              break;
            }
          }
        });
        await page.waitForTimeout(1000);
        // The preview content is in the 3rd div child of the tab container
        selector = 'main > div > div > div:not(.prose)';
      } else if (item.lib === 'aceternity') {
        selector = '.preview';
      }

      if (selector) {
        const el = await page.$(selector);
        if (el) {
          await el.screenshot({path: filepath});
          results.push({key: item.key, status: 'ok', file: filename, selector});
        } else {
          // Fallback: try to find rendered component by position
          const fallback = await page.evaluate(() => {
            // Find any element that looks like a preview container
            const divs = document.querySelectorAll('div');
            for (const d of divs) {
              const r = d.getBoundingClientRect();
              if (r.width > 300 && r.height > 100 && r.top > 400 && r.top < 600 && r.left > 200) {
                return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)};
              }
            }
            return null;
          });
          if (fallback) {
            await page.screenshot({path: filepath, clip: {x: fallback.x, y: fallback.y, width: fallback.w, height: Math.min(fallback.h, 400)}});
            results.push({key: item.key, status: 'fallback-clip', file: filename});
          } else {
            await page.screenshot({path: filepath, clip: {x: 0, y: 0, width: 1280, height: 600}});
            results.push({key: item.key, status: 'fallback-full', file: filename});
          }
        }
      }
    } catch (e) {
      results.push({key: item.key, status: 'error', error: e.message.substring(0, 80)});
    }

    await page.close();
    console.log(`${item.key}: ${results[results.length-1].status}`);
  }

  await browser.close();
  console.log('\n=== RESULTS ===');
  for (const r of results) {
    console.log(`${r.key}: ${r.status} -> ${r.file || r.error || ''}`);
  }
  fs.writeFileSync(path.join(OUT_DIR, 'pilot-results-v2.json'), JSON.stringify(results, null, 2));
})();