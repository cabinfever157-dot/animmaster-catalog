const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT_DIR = 'C:\\Users\\info\\Dropbox\\Projects\\component-catalog\\previews';

const items = [
  // SmoothUI — clip the preview area
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
  // SeraUI
  {key: 'Hero Animations #39', url: 'https://seraui.com/docs/hero', lib: 'seraui'},
  {key: 'Buttons #23', url: 'https://seraui.com/docs/glow-button', lib: 'seraui'},
  {key: 'Buttons #24', url: 'https://seraui.com/docs/modern-button', lib: 'seraui'},
];

async function screenshotSmoothUI(page, filepath) {
  // SmoothUI renders content in a frame-box or similar container
  // Try multiple selectors
  const selectors = ['.frame-box', '[class*="frame"]', '.not-prose[class*="bg"]', '[data-preview]'];
  for (const sel of selectors) {
    const el = await page.$(sel);
    if (el) {
      const box = await el.boundingBox();
      if (box && box.width > 100 && box.height > 50) {
        await el.screenshot({path: filepath, timeout: 15000});
        return 'ok:' + sel;
      }
    }
  }
  
  // Fallback: find the rendered component by looking for buttons/cards below the tabs
  const rect = await page.evaluate(() => {
    // Find the Preview/Example tab area
    const tabs = document.querySelectorAll('[role="tab"], [data-state]');
    let tabBottom = 0;
    for (const t of tabs) {
      const r = t.getBoundingClientRect();
      if (r.top > 350 && r.top < 450 && r.width > 50) {
        tabBottom = Math.max(tabBottom, r.bottom);
      }
    }
    if (tabBottom === 0) tabBottom = 420;
    
    // Find the first rendered component below the tabs
    const allEls = document.querySelectorAll('div, button, a');
    for (const el of allEls) {
      const r = el.getBoundingClientRect();
      if (r.top > tabBottom && r.top < tabBottom + 200 && r.width > 100 && r.width < 800 && r.height > 30 && r.height < 300) {
        // Found a rendered element — now find its container
        let cur = el;
        for (let i = 0; i < 5; i++) {
          if (!cur) break;
          const pr = cur.getBoundingClientRect();
          if (pr.width > 400 && pr.height > 150 && pr.top > tabBottom) {
            return {x: Math.round(pr.x), y: Math.round(pr.y), w: Math.round(pr.width), h: Math.round(Math.min(pr.height, 400))};
          }
          cur = cur.parentElement;
        }
      }
    }
    return null;
  });
  
  if (rect) {
    await page.screenshot({path: filepath, clip: {x: rect.x, y: rect.y, width: rect.w, height: rect.h}});
    return 'clip:' + rect.w + 'x' + rect.h;
  }
  
  return null;
}

async function screenshotSeraUI(page, filepath) {
  // Click Preview tab
  await page.evaluate(() => {
    for (const b of document.querySelectorAll('button')) {
      if (b.textContent.trim() === 'Preview') { b.click(); break; }
    }
  });
  await page.waitForTimeout(1000);
  
  // SeraUI preview container: div with class containing "not-prose" and "grid-b"
  const selectors = ['.not-prose.grid-b', 'div[class*="not-prose"][class*="rounded"]', 'div[class*="not-prose"][class*="items-center"]'];
  for (const sel of selectors) {
    const el = await page.$(sel);
    if (el) {
      const box = await el.boundingBox();
      if (box && box.width > 100 && box.height > 50) {
        await el.screenshot({path: filepath, timeout: 15000});
        return 'ok:' + sel;
      }
    }
  }
  
  // Fallback: clip area below the Preview/Code tabs
  const rect = await page.evaluate(() => {
    let tabBottom = 0;
    for (const b of document.querySelectorAll('button')) {
      if (b.textContent.trim() === 'Preview' || b.textContent.trim() === 'Code') {
        const r = b.getBoundingClientRect();
        tabBottom = Math.max(tabBottom, r.bottom);
      }
    }
    if (tabBottom === 0) return null;
    
    // Find the first container below tabs that's large enough
    for (const el of document.querySelectorAll('div')) {
      const r = el.getBoundingClientRect();
      if (r.top >= tabBottom && r.width > 300 && r.height > 100 && r.height < 500) {
        return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(Math.min(r.height, 400))};
      }
    }
    return null;
  });
  
  if (rect) {
    await page.screenshot({path: filepath, clip: {x: rect.x, y: rect.y, width: rect.w, height: rect.h}});
    return 'clip:' + rect.w + 'x' + rect.h;
  }
  
  return null;
}

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, {recursive: true});
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({viewport: {width: 1280, height: 800}, deviceScaleFactor: 2});
  const results = [];

  for (const item of items) {
    const page = await context.newPage();
    const filename = item.key.replace(/[# ]/g, '-').toLowerCase() + '.png';
    const filepath = path.join(OUT_DIR, filename);

    try {
      await page.goto(item.url, {waitUntil: 'domcontentloaded', timeout: 30000});
      await page.waitForTimeout(5000); // longer wait for JS rendering

      let result = null;
      if (item.lib === 'smoothui') {
        result = await screenshotSmoothUI(page, filepath);
      } else if (item.lib === 'seraui') {
        result = await screenshotSeraUI(page, filepath);
      } else if (item.lib === 'aceternity') {
        const el = await page.$('.preview');
        if (el) {
          await el.screenshot({path: filepath, timeout: 15000});
          result = 'ok:.preview';
        }
      }

      if (!result) {
        // Last resort: clip the main content area
        await page.screenshot({path: filepath, clip: {x: 240, y: 300, width: 800, height: 400}});
        result = 'fallback-clip';
      }
      
      results.push({key: item.key, status: result, file: filename});
    } catch (e) {
      results.push({key: item.key, status: 'error', error: e.message.substring(0, 80)});
    }

    await page.close();
    console.log(`${item.key}: ${results[results.length-1].status}`);
  }

  await browser.close();
  console.log('\n=== RESULTS ===');
  for (const r of results) console.log(`${r.key}: ${r.status} -> ${r.file || r.error || ''}`);
  fs.writeFileSync(path.join(OUT_DIR, 'pilot-results-v3.json'), JSON.stringify(results, null, 2));
})();