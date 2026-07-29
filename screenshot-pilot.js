const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT_DIR = 'C:\\Users\\info\\Dropbox\\Projects\\component-catalog\\previews';

// Pilot components: [{key, name, url, library}]
const pilot = [
  // Aceternity Buttons
  {key: 'Buttons #03', url: 'https://ui.aceternity.com/components/magnetic-button', lib: 'aceternity'},
  {key: 'Buttons #02', url: 'https://ui.aceternity.com/components/hover-border-gradient', lib: 'aceternity'},
  {key: 'Buttons #06', url: 'https://ui.aceternity.com/components/tailwindcss-buttons', lib: 'aceternity'},
  
  // Aceternity Hero
  {key: 'Hero Animations #33', url: 'https://ui.aceternity.com/components/spotlight', lib: 'aceternity'},
  {key: 'Hero Animations #31', url: 'https://ui.aceternity.com/components/lamp-effect', lib: 'aceternity'},
  {key: 'Hero Animations #29', url: 'https://ui.aceternity.com/components/hero-parallax', lib: 'aceternity'},
  {key: 'Hero Animations #28', url: 'https://ui.aceternity.com/components/hero-highlight', lib: 'aceternity'},
  {key: 'Hero Animations #27', url: 'https://ui.aceternity.com/components/card-spotlight', lib: 'aceternity'},
  {key: 'Hero Animations #32', url: 'https://ui.aceternity.com/components/spotlight-new', lib: 'aceternity'},
  
  // Aceternity Cards
  {key: 'Cards #15', url: 'https://ui.aceternity.com/components/github-profile', lib: 'aceternity'},
  
  // SmoothUI Buttons
  {key: 'Buttons #20', url: 'https://www.smoothui.dev/docs/components/clip-corners-button', lib: 'smoothui'},
  {key: 'Buttons #21', url: 'https://www.smoothui.dev/docs/components/dot-morph-button', lib: 'smoothui'},
  {key: 'Buttons #22', url: 'https://www.smoothui.dev/docs/components/smooth-button', lib: 'smoothui'},
  
  // SmoothUI Cards
  {key: 'Cards #39', url: 'https://www.smoothui.dev/docs/components/app-download-stack', lib: 'smoothui'},
  {key: 'Cards #40', url: 'https://www.smoothui.dev/docs/components/apple-invites', lib: 'smoothui'},
  {key: 'Cards #41', url: 'https://www.smoothui.dev/docs/components/book', lib: 'smoothui'},
  {key: 'Cards #42', url: 'https://www.smoothui.dev/docs/components/glow-hover-card', lib: 'smoothui'},
  {key: 'Cards #43', url: 'https://www.smoothui.dev/docs/components/image-metadata-preview', lib: 'smoothui'},
  {key: 'Cards #44', url: 'https://www.smoothui.dev/docs/components/product-card', lib: 'smoothui'},
  {key: 'Cards #45', url: 'https://www.smoothui.dev/docs/components/scrollable-card-stack', lib: 'smoothui'},
  {key: 'Cards #46', url: 'https://www.smoothui.dev/docs/components/tweet-card', lib: 'smoothui'},
  
  // SeraUI
  {key: 'Hero Animations #39', url: 'https://seraui.com/docs/hero', lib: 'seraui'},
  {key: 'Buttons #23', url: 'https://seraui.com/docs/glow-button', lib: 'seraui'},
  {key: 'Buttons #24', url: 'https://seraui.com/docs/modern-button', lib: 'seraui'},
];

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, {recursive: true});
  
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({
    viewport: {width: 1280, height: 800},
    deviceScaleFactor: 1,
  });
  
  const results = [];
  
  for (const item of pilot) {
    const page = await context.newPage();
    const filename = item.key.replace(/[# ]/g, '-').toLowerCase() + '.png';
    const filepath = path.join(OUT_DIR, filename);
    
    try {
      await page.goto(item.url, {waitUntil: 'networkidle', timeout: 30000});
      await page.waitForTimeout(3000); // let animations settle
      
      let selector = '.preview'; // Aceternity
      if (item.lib === 'smoothui') {
        // SmoothUI uses different selectors
        const previewEl = await page.$('[data-preview], .preview, [class*="preview"], main > div > div');
        if (previewEl) {
          await previewEl.screenshot({path: filepath});
          results.push({key: item.key, status: 'ok', file: filename});
          await page.close();
          continue;
        }
      }
      if (item.lib === 'seraui') {
        // SeraUI — screenshot the main content area
        const main = await page.$('main, [class*="content"], [class*="preview"]');
        if (main) {
          await main.screenshot({path: filepath});
          results.push({key: item.key, status: 'ok', file: filename});
          await page.close();
          continue;
        }
      }
      
      // Aceternity default
      const el = await page.$(selector);
      if (el) {
        await el.screenshot({path: filepath});
        results.push({key: item.key, status: 'ok', file: filename});
      } else {
        // Fallback: screenshot the page
        await page.screenshot({path: filepath, clip: {x: 0, y: 0, width: 1280, height: 600}});
        results.push({key: item.key, status: 'fallback', file: filename});
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
    console.log(`${r.key}: ${r.status}${r.file ? ' -> ' + r.file : ''}${r.error ? ' ERROR: ' + r.error : ''}`);
  }
  
  // Save results JSON
  fs.writeFileSync(path.join(OUT_DIR, 'pilot-results.json'), JSON.stringify(results, null, 2));
})();