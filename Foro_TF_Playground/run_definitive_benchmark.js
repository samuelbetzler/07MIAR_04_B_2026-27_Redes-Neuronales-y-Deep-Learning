const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const chromePath = 'C:\\Users\\samue\\.cache\\puppeteer\\chrome-headless-shell\\win64-131.0.6778.204\\chrome-headless-shell-win64\\chrome-headless-shell.exe';
const baseDir = 'D:\\VIU\\07MIAR_Redes_Neuronales\\Foro_TF_Playground';
const imgDir = path.join(baseDir, 'capturas_playground');

if (!fs.existsSync(imgDir)) {
  fs.mkdirSync(imgDir, { recursive: true });
}

const experiments = [
  // CIRCLE (9 conditions)
  { dataset: 'circle', reg: 'none', lr: 0.003, regRate: 0.003 },
  { dataset: 'circle', reg: 'none', lr: 0.03,  regRate: 0.003 },
  { dataset: 'circle', reg: 'none', lr: 0.3,   regRate: 0.003 },
  { dataset: 'circle', reg: 'L1',   lr: 0.003, regRate: 0.003 },
  { dataset: 'circle', reg: 'L1',   lr: 0.03,  regRate: 0.003 },
  { dataset: 'circle', reg: 'L1',   lr: 0.3,   regRate: 0.003 },
  { dataset: 'circle', reg: 'L2',   lr: 0.003, regRate: 0.003 },
  { dataset: 'circle', reg: 'L2',   lr: 0.03,  regRate: 0.003 },
  { dataset: 'circle', reg: 'L2',   lr: 0.3,   regRate: 0.003 },
  // SPIRAL (9 conditions)
  { dataset: 'spiral', reg: 'none', lr: 0.003, regRate: 0.003 },
  { dataset: 'spiral', reg: 'none', lr: 0.03,  regRate: 0.003 },
  { dataset: 'spiral', reg: 'none', lr: 0.3,   regRate: 0.003 },
  { dataset: 'spiral', reg: 'L1',   lr: 0.003, regRate: 0.003 },
  { dataset: 'spiral', reg: 'L1',   lr: 0.03,  regRate: 0.003 },
  { dataset: 'spiral', reg: 'L1',   lr: 0.3,   regRate: 0.003 },
  { dataset: 'spiral', reg: 'L2',   lr: 0.003, regRate: 0.003 },
  { dataset: 'spiral', reg: 'L2',   lr: 0.03,  regRate: 0.003 },
  { dataset: 'spiral', reg: 'L2',   lr: 0.3,   regRate: 0.003 },
];

const seeds = ['0.42', '0.101', '0.2024'];

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

    // Run 500 epochs and inspect both UI losses and link objects
    const data = await page.evaluate(() => {
      const btn = document.querySelector('#next-step-button');
      for (let i = 0; i < 500; i++) {
        btn.click();
      }

      const trStr = document.querySelector('#loss-train') ? document.querySelector('#loss-train').innerText.trim() : '0.000';
      const teStr = document.querySelector('#loss-test') ? document.querySelector('#loss-test').innerText.trim() : '0.000';

      // Inspect link DOM elements and their __data__
      const paths = Array.from(document.querySelectorAll('path')).filter(p => p.id && p.id.startsWith('link'));
      let deadCount = 0;
      let totalWeights = paths.length;
      paths.forEach(p => {
        const d = p.__data__;
        if (d && (d.isDead || d.weight === 0)) {
          deadCount++;
        }
      });

      return {
        trainStr: trStr,
        testStr: teStr,
        trainLoss: parseFloat(trStr),
        testLoss: parseFloat(teStr),
        deadCount: deadCount,
        totalWeights: totalWeights
      };
    });

    seedResults.push({ seed, ...data });

    // Save screenshot for seed 0.42
    if (sIdx === 0) {
      const shotPath = path.join(imgDir, `${expKey}.png`);
      await page.screenshot({ path: shotPath });
    }
  }

  await page.close();

  const trVals = seedResults.map(r => r.trainLoss);
  const teVals = seedResults.map(r => r.testLoss);
  const deadVals = seedResults.map(r => r.deadCount);

  const trMean = trVals.reduce((a, b) => a + b, 0) / trVals.length;
  const teMean = teVals.reduce((a, b) => a + b, 0) / teVals.length;
  const deadMean = deadVals.reduce((a, b) => a + b, 0) / deadVals.length;

  const trStd = Math.sqrt(trVals.reduce((acc, v) => acc + Math.pow(v - trMean, 2), 0) / (trVals.length - 1));
  const teStd = Math.sqrt(teVals.reduce((acc, v) => acc + Math.pow(v - teMean, 2), 0) / (teVals.length - 1));

  console.log(`[DONE] ${expKey} -> Tr: [${seedResults.map(r=>r.trainStr).join(',')}] | Te: [${seedResults.map(r=>r.testStr).join(',')}] | Dead: [${seedResults.map(r=>r.deadCount).join(',')}]/34`);

  return {
    dataset: exp.dataset,
    reg: exp.reg,
    lr: exp.lr,
    regRate: exp.regRate,
    seedDetails: seedResults,
    trainReadings: seedResults.map(r => r.trainStr),
    testReadings: seedResults.map(r => r.testStr),
    deadReadings: seedResults.map(r => r.deadCount),
    trMean: Number(trMean.toFixed(4)),
    trStd: Number(trStd.toFixed(4)),
    teMean: Number(teMean.toFixed(4)),
    teStd: Number(teStd.toFixed(4)),
    deadMean: Math.round(deadMean),
    deadPct: Number(((Math.round(deadMean) / 34) * 100).toFixed(1))
  };
}

async function runBenchmark() {
  console.log("Running comprehensive live benchmark measuring UI losses + exact isDead link counts...");
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const concurrency = 3;
  const allResults = [];

  for (let i = 0; i < experiments.length; i += concurrency) {
    const batch = experiments.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(exp => runSingle(browser, exp)));
    allResults.push(...batchResults);
  }

  await browser.close();

  const outJson = path.join(baseDir, 'definitive_benchmark_results.json');
  fs.writeFileSync(outJson, JSON.stringify(allResults, null, 2));
  console.log(`\nSaved definitive benchmark to ${outJson}`);
}

runBenchmark().catch(err => {
  console.error(err);
  process.exit(1);
});
