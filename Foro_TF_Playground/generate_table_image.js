const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1100, height: 600, deviceScaleFactor: 2 });

  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    padding: 20px;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
  }
  .card {
    background: #ffffff;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid #cbd5e1;
    padding: 22px 26px;
    box-sizing: border-box;
  }
  .header {
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }
  .title {
    font-size: 15pt;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
  }
  .subtitle {
    font-size: 8.8pt;
    color: #64748b;
    margin-top: 4px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9.2pt;
    line-height: 1.42;
  }
  th {
    background-color: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 11px 13px;
    font-weight: 600;
    font-size: 8.8pt;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  th:first-child { border-top-left-radius: 6px; }
  th:last-child { border-top-right-radius: 6px; }
  td {
    padding: 12px 13px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) td {
    background-color: #f8fafc;
  }
  .badge-blue {
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8.5pt;
  }
  .badge-purple {
    display: inline-block;
    background: #f3e8ff;
    color: #7e22ce;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8.5pt;
  }
  .badge-amber {
    display: inline-block;
    background: #fef3c7;
    color: #b45309;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8.5pt;
  }
  .badge-slate {
    display: inline-block;
    background: #f1f5f9;
    color: #475569;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8.5pt;
  }
  .code {
    font-family: Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8.8pt;
    color: #334155;
    background: #f1f5f9;
    padding: 2px 5px;
    border-radius: 3px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 3px;
  }
  .footer {
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid #e2e8f0;
    font-size: 8pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
  }
</style>
</head>
<body>
<div class="card" id="target-card">
  <div class="header">
    <div class="title">Tabla 3. Matriz Normativa de Selección de Hiperparámetros</div>
    <div class="subtitle">07MIAR &mdash; Redes Neuronales y Deep Learning | Samuel Segundo Campozano López</div>
  </div>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Topología / Diagnóstico</th>
        <th style="width: 24%;">Régimen Recomendado</th>
        <th style="width: 21%;">Configuración Evaluada</th>
        <th style="width: 30%;">Justificación Basada en Datos</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Fronteras radiales convexas con ruido moderado (Circle)</b></td>
        <td><span class="badge-blue">L₂ continuo o L₁ conservador</span></td>
        <td><span class="code">L₂ (α=0.03, λ=0.003)</span><br><span class="code">L₁ (α=0.003, λ=0.003)</span></td>
        <td>Desempeño equivalente (test 0.076–0.082 vs 0.0997 en None). L₁ poda el 16.7% de enlaces; L₂ preserva conectividad completa sin desconexiones.</td>
      </tr>
      <tr>
        <td><b>Poda estructural deliberada / Compresión de red (Circle)</b></td>
        <td><span class="badge-purple">L₁ con α moderado</span></td>
        <td><span class="code">L₁ (α=0.03, λ=0.003)</span></td>
        <td>Poda 21.3/34 enlaces (62.7% de esparsidad no estructurada) con test competitivo (0.0837 ± 0.0006); consistente con enlaces activos de gradiente fuerte. Requiere kernels dispersos para acelerar cómputo.</td>
      </tr>
      <tr>
        <td><b>Tasas de aprendizaje agresivas (α = 0.3)</b></td>
        <td><span class="badge-amber">Evitar α = 0.3 en Circle (no se probó α &gt; 0.3)</span></td>
        <td>Evaluado a α=0.3 en todas las variantes</td>
        <td>Empeora el test en L₁ (0.0837&rarr;0.1283, 3/3 semillas), en L₂ (0.0820&rarr;0.1013, 2/3) y de forma inconsistente en None (0.0997&rarr;0.1163, solo s₃). Coherente con sobrepaso de gradiente; en L₁ la poda es similar (22.0 vs 21.3).</td>
      </tr>
      <tr>
        <td><b>Variedades entrelazadas de alta curvatura (Spiral)</b></td>
        <td><span class="badge-slate">None (α=0.03) como base; ampliar capacidad = hipótesis</span></td>
        <td><span class="code">None (α=0.03)</span> evaluado</td>
        <td>En este montaje (4-4-2, entradas X₁, X₂), L₁/L₂ quedan en ~0.45–0.46 y regularizar parece reforzar el subajuste. Sin regularizar, 2 de 3 semillas bajan a ≈0.31; sin&middot;cos y más capacidad no se probaron.</td>
      </tr>
    </tbody>
  </table>
  <div class="footer">
    <span><b>Fuente:</b> 54 corridas experimentales en TensorFlow Playground (split 80/20, ruido 10%, batch 10, 500 épocas).</span>
    <span><b>Universidad Internacional de Valencia (VIU)</b></span>
  </div>
</div>
</body>
</html>`;

  await page.setContent(html, { waitUntil: 'networkidle0' });
  const card = await page.$('#target-card');
  const outPath = path.join(__dirname, 'Tabla_3_Matriz_Normativa.png');
  await card.screenshot({ path: outPath });
  console.log('Imagen de tabla generada con éxito en:', outPath);
  await browser.close();
})();
