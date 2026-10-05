const fs = require('fs');
const path = require('path');

const puppeteer = require('puppeteer');

// Auto-resolve Chrome/Chromium executable
function resolveChromePath() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH && fs.existsSync(process.env.PUPPETEER_EXECUTABLE_PATH)) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }
  try {
    if (puppeteer.executablePath && typeof puppeteer.executablePath === 'function') {
      const p = puppeteer.executablePath();
      if (p && fs.existsSync(p)) return p;
    }
  } catch (err) {}

  const candidates = [
    'C:\\Users\\samue\\.cache\\puppeteer\\chrome-headless-shell\\win64-131.0.6778.204\\chrome-headless-shell-win64\\chrome-headless-shell.exe',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  ];

  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  throw new Error("No se encontró ningún binario de Chrome/Chromium. Ejecute 'npm install puppeteer' o defina PUPPETEER_EXECUTABLE_PATH.");
}

const chromePath = resolveChromePath();
console.log('Utilizando ejecutable de Chrome:', chromePath);

const datasets = ['circle', 'spiral'];
const regularizers = ['none', 'L1', 'L2'];
const learningRates = [0.003, 0.03, 0.3];
const seeds = ['0.42', '0.101', '0.2024'];

const experiments = [];
for (const ds of datasets) {
  for (const reg of regularizers) {
    for (const lr of learningRates) {
      experiments.push({
        dataset: ds,
        reg: reg,
        lr: lr,
        regRate: 0.003
      });
    }
  }
}

const baseDir = __dirname;
const imgDir = path.join(baseDir, 'capturas_playground');
if (!fs.existsSync(imgDir)) fs.mkdirSync(imgDir, { recursive: true });

async function runSingle(browser, exp) {
  const expKey = `${exp.dataset}_${exp.reg}_lr${exp.lr}`;
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  const seedResults = [];

  for (let sIdx = 0; sIdx < seeds.length; sIdx++) {
    const seed = seeds[sIdx];
    const hash = `#activation=tanh&regularization=${exp.reg}&batchSize=10&dataset=${exp.dataset}&learningRate=${exp.lr}&regularizationRate=${exp.regRate}&noise=10&networkShape=4,4,2&seed=${seed}&percTrainData=80&x=true&y=true`;
    const url = 'https://playground.tensorflow.org/' + hash;

    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.waitForSelector('#next-step-button');

    // Control estricto de 500 épocas en la interfaz
    const data = await page.evaluate(() => {
      const btn = document.querySelector('#next-step-button');
      for (let i = 0; i < 500; i++) {
        btn.click();
      }

      const trStr = document.querySelector('#loss-train') ? document.querySelector('#loss-train').innerText.trim() : '0.000';
      const teStr = document.querySelector('#loss-test') ? document.querySelector('#loss-test').innerText.trim() : '0.000';

      const paths = Array.from(document.querySelectorAll('path')).filter(p => p.id && p.id.startsWith('link'));
      let deadCount = 0;
      let deadIds = [];
      paths.forEach(p => {
        const d = p.__data__;
        if (d && (d.isDead || d.weight === 0)) {
          deadCount++;
          deadIds.push(p.id);
        }
      });

      return {
        trainStr: trStr,
        testStr: teStr,
        trainLoss: parseFloat(trStr),
        testLoss: parseFloat(teStr),
        deadCount: deadCount,
        deadIds: deadIds,
        totalWeights: paths.length
      };
    });

    seedResults.push({ seed, timestamp: new Date().toISOString(), url, ...data });

    if (sIdx === 0) {
      const shotPath = path.join(imgDir, `${expKey}.png`);
      await page.screenshot({ path: shotPath });
    }
  }

  await page.close();
  console.log(`[DONE] ${expKey} -> Tr: [${seedResults.map(r=>r.trainStr).join(',')}] | Te: [${seedResults.map(r=>r.testStr).join(',')}] | Dead: [${seedResults.map(r=>r.deadCount).join(',')}]/34`);

  return {
    dataset: exp.dataset,
    reg: exp.reg,
    lr: exp.lr,
    regRate: exp.regRate,
    seedDetails: seedResults
  };
}

async function runBenchmark() {
  console.log(`Iniciando ejecución automatizada de 54 experimentos sobre TensorFlow Playground...`);
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const allResults = [];
  for (const exp of experiments) {
    const res = await runSingle(browser, exp);
    allResults.push(res);
  }

  await browser.close();

  // Exportar resultados unificados
  fs.writeFileSync(path.join(baseDir, 'resultados_brutos.json'), JSON.stringify(allResults, null, 2));

  // Generar CSV plano
  const csvLines = ['timestamp,dataset,regularizer,learning_rate,regularization_rate,seed,train_loss,test_loss,dead_links_k_34,sparsity_pct,playground_url'];
  for (const exp of allResults) {
    for (const s of exp.seedDetails) {
      csvLines.push(`${s.timestamp},${exp.dataset},${exp.reg},${exp.lr},${exp.regRate},${s.seed},${s.trainLoss},${s.testLoss},${s.deadCount},${((s.deadCount/34)*100).toFixed(2)},"${s.url}"`);
    }
  }
  fs.writeFileSync(path.join(baseDir, 'resultados_brutos.csv'), csvLines.join('\n'));
  console.log('Todos los experimentos finalizados con éxito. Archivos guardados: resultados_brutos.json y resultados_brutos.csv.');
}

if (require.main === module) {
  runBenchmark().catch(console.error);
}
