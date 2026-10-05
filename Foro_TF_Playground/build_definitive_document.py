import os
import sys
import base64
import json
import math
import subprocess
import fitz

base_dir = r"D:\VIU\07MIAR_Redes_Neuronales\Foro_TF_Playground"
logo_path = os.path.join(base_dir, "logo-viu-frame.png")
shot_circle = os.path.join(base_dir, "scratch", "circle_full_crop.png")
shot_spiral = os.path.join(base_dir, "scratch", "spiral_full_crop.png")

with open(logo_path, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode("utf-8")

with open(shot_circle, "rb") as f:
    shot_circle_b64 = base64.b64encode(f.read()).decode("utf-8")

with open(shot_spiral, "rb") as f:
    shot_spiral_b64 = base64.b64encode(f.read()).decode("utf-8")

# Única fuente canónica de datos
json_canonical = os.path.join(base_dir, "resultados_brutos.json")
with open(json_canonical, encoding="utf-8") as f:
    bench_data = json.load(f)

def generate_table_rows(dataset_name):
    rows_html = []
    items = [x for x in bench_data if x["dataset"] == dataset_name]
    for exp in items:
        reg = exp["reg"]
        lr = exp["lr"]
        tr = [s["trainLoss"] for s in exp["seedDetails"]]
        te = [s["testLoss"] for s in exp["seedDetails"]]
        dead = [s["deadCount"] for s in exp["seedDetails"]]

        tr_m = sum(tr) / 3.0
        te_m = sum(te) / 3.0
        tr_std = math.sqrt(sum((x - tr_m) ** 2 for x in tr) / 2.0)
        te_std = math.sqrt(sum((x - te_m) ** 2 for x in te) / 2.0)
        dead_m = sum(dead) / 3.0
        dead_pct = (dead_m / 34.0) * 100.0

        tr_readings = f"[{tr[0]:.3f}, {tr[1]:.3f}, {tr[2]:.3f}]"
        te_readings = f"[{te[0]:.3f}, {te[1]:.3f}, {te[2]:.3f}]"
        dead_readings = f"[{dead[0]}, {dead[1]}, {dead[2]}] / 34"

        reg_label = "<b>None</b>" if reg == "none" else (f"<b>L<sub>1</sub></b> (&lambda;=0.003)" if reg == "L1" else f"<b>L<sub>2</sub></b> (&lambda;=0.003)")
        highlight = ""
        if dataset_name == "circle":
            if (reg == "L1" and lr == 0.003) or (reg == "L2" and lr == 0.03):
                highlight = ' class="highlight-row"'
            sparsity_str = f"{dead_m:.1f} / 34 ({dead_pct:.1f}%)" if dead_m > 0 else "0 / 34 (0.0%)"
            row = f"""      <tr{highlight}>
        <td>{reg_label}</td>
        <td>{lr}</td>
        <td>{tr_readings}</td>
        <td>{tr_m:.4f} &plusmn; {tr_std:.4f}</td>
        <td>{te_readings}</td>
        <td>{te_m:.4f} &plusmn; {te_std:.4f}</td>
        <td>{dead_readings}</td>
        <td>{sparsity_str}</td>
      </tr>"""
        else:
            behavior = ""
            if reg == "none" and lr == 0.003:
                behavior = "Estancado en meseta inicial."
            elif reg == "none" and lr == 0.03:
                behavior = "Bimodal: s<sub>1</sub> falla (0.445); s<sub>2</sub> y s<sub>3</sub> trazan corte oblicuo."
            elif reg == "none" and lr == 0.3:
                behavior = "s<sub>1</sub> desciende (0.327); s<sub>2</sub>, s<sub>3</sub> inestables en meseta."
            elif reg == "L1" and lr == 0.003:
                behavior = "Pérdida cercana al límite trivial (&asymp;0.46)."
            elif reg == "L1" and lr == 0.03:
                behavior = "Poda severa (79.4%); red bloqueada en meseta."
            elif reg == "L1" and lr == 0.3:
                behavior = "88.2% enlaces muertos; salida fija."
            elif reg == "L2" and lr == 0.003:
                behavior = "Contracción homogénea; sin convergencia."
            elif reg == "L2" and lr == 0.03:
                behavior = "Estancado en meseta; sin resolución no lineal."
            elif reg == "L2" and lr == 0.3:
                behavior = "Pesos contraídos; sin resolución geométrica."
            
            row = f"""      <tr>
        <td>{reg_label}</td>
        <td>{lr}</td>
        <td>{tr_readings}</td>
        <td>{tr_m:.4f} &plusmn; {tr_std:.4f}</td>
        <td>{te_readings}</td>
        <td>{te_m:.4f} &plusmn; {te_std:.4f}</td>
        <td>{dead_readings}</td>
        <td>{behavior}</td>
      </tr>"""
        rows_html.append(row)
    return "\n".join(rows_html)

circle_rows = generate_table_rows("circle")
spiral_rows = generate_table_rows("spiral")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Estudio Experimental: Tipo de Regularización y Tasa de Aprendizaje</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Montserrat:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  @page {{
    size: A4;
    margin: 1.18cm 1.35cm 1.18cm 1.35cm;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: 'Lora', 'Georgia', serif;
    font-variant-ligatures: none;
    color: #2c3e50;
    line-height: 1.31;
    font-size: 8.2pt;
    max-width: 820px;
    margin: 0 auto;
    padding: 0;
    background-color: #ffffff;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }}

  /* Portada Oficial VIU Simplificada (Mismo diseño de referencia del estudiante) */
  .cover {{
    display: block;
    position: relative;
    height: 25.8cm;
    page-break-after: always;
    page-break-inside: avoid;
    break-after: page;
    box-sizing: border-box;
    padding: 0;
    margin: 0;
  }}
  .cover-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #E24E1B;
    padding-bottom: 12px;
    margin: 0 0 4.2cm 0;
  }}
  .cover-header-left .univ {{
    font-family: 'Montserrat', sans-serif;
    font-size: 11pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #E24E1B;
    text-transform: uppercase;
  }}
  .cover-header-left .master {{
    font-family: 'Montserrat', sans-serif;
    font-size: 9.8pt;
    font-weight: 500;
    color: #7f8c8d;
    margin-top: 4px;
  }}
  .cover-header-right img {{
    height: 48px;
    width: auto;
    display: block;
  }}
  .cover-body {{
    margin: 0 0 7.8cm 0;
    padding: 0;
  }}
  .cover-body .subject {{
    font-family: 'Montserrat', sans-serif;
    font-size: 10.5pt;
    font-weight: 700;
    color: #E24E1B;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 14px;
  }}
  .cover-body h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 20pt;
    font-weight: 800;
    line-height: 1.25;
    color: #1a252f;
    margin: 0 0 16px 0;
    letter-spacing: -0.4px;
  }}
  .cover-body .subtitle {{
    font-family: 'Lora', serif;
    font-size: 10pt;
    font-style: italic;
    color: #555555;
    line-height: 1.45;
    margin: 0;
  }}
  .cover-footer {{
    border-top: 1px solid #dcdde1;
    padding-top: 18px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    row-gap: 16px;
    column-gap: 32px;
    font-family: 'Montserrat', sans-serif;
    font-size: 8.5pt;
  }}
  .cover-footer .meta-item {{
    display: flex;
    flex-direction: column;
  }}
  .cover-footer .meta-label {{
    text-transform: uppercase;
    font-size: 7.2pt;
    font-weight: 700;
    letter-spacing: 1px;
    color: #7f8c8d;
    margin-bottom: 3px;
  }}
  .cover-footer .meta-value {{
    font-weight: 600;
    color: #2c3e50;
    font-size: 9pt;
  }}

  /* Contenido académico */
  .academic-page {{
    page-break-after: always;
    page-break-inside: avoid;
    break-after: page;
    height: 25.8cm;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    box-sizing: border-box;
  }}
  .academic-page:last-child {{
    page-break-after: avoid;
    break-after: avoid;
  }}

  h2 {{
    page-break-before: avoid;
    break-before: avoid;
    page-break-after: avoid;
    break-after: avoid;
    font-family: 'Montserrat', sans-serif;
    font-size: 10.0pt;
    font-weight: 700;
    color: #1a252f;
    border-bottom: 1.5px solid #E24E1B;
    padding-bottom: 2px;
    margin-top: 4px;
    margin-bottom: 3px;
    letter-spacing: -0.2px;
  }}
  .academic-page > h2:first-child {{
    margin-top: 0;
  }}
  p {{
    text-align: justify;
    margin-top: 0;
    margin-bottom: 3px;
  }}

  /* Tablas booktabs */
  table.booktabs {{
    width: 100%;
    border-collapse: collapse;
    margin: 3px 0 4px 0;
    font-size: 7.05pt;
    line-height: 1.18;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  table.booktabs th, table.booktabs td {{
    padding: 1.8px 2.8px;
    text-align: left;
  }}
  table.booktabs thead tr:first-child th {{
    border-top: 1.6px solid #1a252f;
    border-bottom: 1.1px solid #1a252f;
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    color: #1a252f;
  }}
  table.booktabs tbody tr:last-child td {{
    border-bottom: 1.6px solid #1a252f;
  }}
  table.booktabs tbody tr:hover {{
    background-color: #fafbfc;
  }}
  .highlight-row {{
    background-color: #fdf5f2;
    font-weight: 600;
  }}
  .caption {{
    font-family: 'Montserrat', sans-serif;
    font-size: 6.8pt;
    font-weight: 600;
    color: #7f8c8d;
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  /* Cajas y capturas */
  .formula-box {{
    background-color: #f8f9fa;
    border-left: 3px solid #E24E1B;
    padding: 3px 7px;
    margin: 3px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.1pt;
    color: #1a252f;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  .figure-box {{
    display: flex;
    gap: 10px;
    align-items: center;
    background-color: #fafbfc;
    border: 1px solid #e1e8ed;
    padding: 4px;
    margin: 3px 0;
    border-radius: 4px;
  }}
  .figure-box img {{
    width: 53%;
    height: auto;
    border: 1px solid #dcdde1;
    border-radius: 2px;
  }}
  .figure-caption {{
    font-size: 6.8pt;
    font-family: 'Montserrat', sans-serif;
    color: #555;
    line-height: 1.23;
  }}

  /* Referencias */
  .references {{
    font-size: 6.8pt;
    line-height: 1.23;
    margin-top: 2px;
  }}
  .references p {{
    margin-bottom: 2px;
    text-indent: -1.3em;
    padding-left: 1.3em;
  }}
</style>
</head>
<body>

<!-- PÁGINA 1: PORTADA OFICIAL VIU -->
<div class="cover">
  <div class="cover-header">
    <div class="cover-header-left">
      <div class="univ">Universidad Internacional de Valencia</div>
      <div class="master">Máster Universitario en Inteligencia Artificial</div>
    </div>
    <div class="cover-header-right">
      <img src="data:image/png;base64,{logo_b64}" alt="VIU Logo">
    </div>
  </div>
  <div class="cover-body">
    <div class="subject">07MIAR_04_B_2026-27_REDES NEURONALES Y DEEP LEARNING</div>
    <h1>Foro Evaluable: Estudio Factorial de la Regularización (L<sub>1</sub>, L<sub>2</sub>, None) y la Tasa de Aprendizaje (&alpha;) en TensorFlow Playground</h1>
    <div class="subtitle">Evaluación empírica en TensorFlow Playground: trazabilidad de pérdidas en interfaz web, medición de enlaces muertos k/34 e interacción entre contracción estocástica y capacidad representacional</div>
  </div>
  <div class="cover-footer">
    <div class="meta-item">
      <span class="meta-label">Autor</span>
      <span class="meta-value">Samuel Segundo Campozano López</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Fecha de Entrega</span>
      <span class="meta-value">4 de octubre de 2026 (Límite: 18 de octubre de 2026)</span>
    </div>
    <div class="meta-item" style="grid-column: span 2;">
      <span class="meta-label">Registro Oficial en Foro Blackboard (Normas 6 y 7)</span>
      <span class="meta-value">Hilo publicado el 27/09/2026 a las 16:28 &mdash; Combinación factorial verificada sin colisión</span>
    </div>
  </div>
</div>

<!-- PÁGINA 2: METODOLOGÍA Y RESULTADOS EN CIRCLE -->
<div class="academic-page">
  <h2>1. Fundamentación Teórica y Mecánica de Desconexión en Playground</h2>
  <p>
    En el entrenamiento de perceptrones multicapa (MLP), el riesgo empírico se combina con términos de penalización funcional [1, 3]. En el entorno interactivo de TensorFlow Playground [2] y su motor subyacente (<code>src/nn.ts</code>) [4], la optimización se ejecuta mediante descenso de gradiente estocástico (SGD sin momento) sobre minilotes de tamaño <i>B</i> = 10:
  </p>
  <div class="formula-box">
    w &larr; w &minus; (&alpha; / B) &sum; &part;E/&part;w ; &nbsp;&nbsp;&nbsp;&nbsp; w<sub>nuevo</sub> &larr; w &minus; (&alpha; &middot; &lambda;) &middot; &Omega;'(w)
  </div>
  <p>
    donde &Omega;'(w) = sgn(w) en L<sub>1</sub> y &Omega;'(w) = w en L<sub>2</sub>. En <code>nn.ts</code> se implementa un umbral con congelación permanente para L<sub>1</sub>: si la actualización hace que el peso cruce el origen (<code>w &middot; w<sub>nuevo</sub> &lt; 0</code>), el peso se fija a 0 y el enlace se marca como muerto (<code>link.isDead = true</code>), omitiéndose en posteriores propagaciones [4].
  </p>
  <p>
    Con 400 muestras de entrenamiento y <i>B</i> = 10, cada época consta de 40 pasos; en 500 épocas se ejecutan <i>T</i> = 20.000 actualizaciones por enlace. Si un peso carece de gradiente útil sostenido, la contracción acumulada potencial es &Delta;w &asymp; &alpha;&lambda;T. Como los pesos inician en <i>U</i>[&minus;0.5, 0.5]: a &alpha; = 0.003 (&lambda; = 0.003), &alpha;&lambda;T = 0.18 &lt; 0.50 (la contracción potencial no domina sobre la dispersión inicial; se preserva la conectividad básica); a &alpha; = 0.03, &alpha;&lambda;T = 1.80 &gt; 0.50 (la contracción acumulada supera el rango inicial, permitiendo que las conexiones sin gradiente suficiente alcancen el cruce de cero dentro del presupuesto de <i>T</i> actualizaciones); y a &alpha; = 0.3, con independencia del regularizador, el elevado paso de aprendizaje &alpha; induce inestabilidad de optimización y sobrepaso estocástico (<i>overshooting</i>) en el entorno del mínimo.
  </p>

  <h2>2. Protocolo Experimental y Rejilla 3&times;3 en Dataset Circle</h2>
  <p>
    Conforme a la <b>Norma 3</b>, se fija una red de 3 capas ocultas <b>[4, 4, 2]</b> (topología <code>2 &rarr; 4 &rarr; 4 &rarr; 2 &rarr; 1</code>), con <b>34 pesos entrenables</b> y 11 sesgos no regularizados. Entradas: coordenadas (<i>X</i><sub>1</sub>, <i>X</i><sub>2</sub>); Activación: Tanh; Ruido: 10%; Split: 80% train / 20% test (400/100 muestras, <b>Norma 2</b>); &lambda; = 0.003. Se evalúan 3 semillas pseudoaleatorias controladas (<i>s</i> &isin; {{0.42, 0.101, 0.2024}}). Para garantizar reproducibilidad y auditoría estricta de la <b>Norma 1</b>, la aplicación web oficial (<code>playground.tensorflow.org</code>) fue ejecutada mediante Puppeteer en Chromium sin modificar el código de la plataforma. El entrenamiento se ejecuta controlando exactamente 500 épocas (500 pulsaciones secuenciales del botón <code>#next-step-button</code> tras cargar los hiperparámetros en la URL), extrayéndose las lecturas de los elementos <code>#loss-train</code> y <code>#loss-test</code> a 3 decimales, reportando la media muestral &mu; y la desviación estándar muestral &sigma; (<i>n</i> &minus; 1 grados de libertad). La esparsidad se midió inspeccionando la propiedad <code>__data__</code> asociada por D3.js a cada trazado SVG (<code>&lt;path id^="link"&gt;</code>) para acceder al atributo nativo <code>link.isDead === true</code> (ver volcado JSON en el repositorio público). En configuraciones saturadas se observan coincidencias entre semillas (e.g., train 0.035 en L<sub>1</sub> o <i>k</i> = [22, 22, 22]), compatibles con la resolución nativa de 3 decimales y convergencia hacia niveles equivalentes de esparsidad en la muestra evaluada.
  </p>

  <div class="caption">Tabla 1. Mediciones directas en interfaz de TensorFlow Playground &mdash; Dataset Circle (Ruido 10%, 500 épocas, n=3 semillas)</div>
  <table class="booktabs">
    <thead>
      <tr>
        <th>Regularizador</th>
        <th>Learning Rate (&alpha;)</th>
        <th>Lecturas Train [s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>]</th>
        <th>Train Loss (&mu; &plusmn; &sigma;)</th>
        <th>Lecturas Test [s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>]</th>
        <th>Test Loss (&mu; &plusmn; &sigma;)</th>
        <th>Enlaces Muertos [s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>]</th>
        <th>Esparsidad Media</th>
      </tr>
    </thead>
    <tbody>
{circle_rows}
    </tbody>
  </table>

  <div class="figure-box">
    <img src="data:image/png;base64,{shot_circle_b64}" alt="Circle L2 Playground">
    <div class="figure-caption">
      <b>Figura 1. Captura de ejecución en TensorFlow Playground (Circle, L<sub>2</sub>, &alpha;=0.03, semilla 0.42, 500 épocas).</b><br>
      Parámetros fijados en el panel DATA (split 80/20, ruido 10%, batch 10, red [4, 4, 2] con tanh) y superficie de separación concéntrica regular frente al ruido (test loss visible: 0.084, train loss: 0.032, 0/34 enlaces muertos).
    </div>
  </div>
</div>

<!-- PÁGINA 3: RESULTADOS EN SPIRAL Y DISCUSIÓN CRÍTICA -->
<div class="academic-page">
  <h2>3. Evaluación en Dataset Spiral y Límite de Capacidad Representacional</h2>
  <p>
    Se somete la misma arquitectura factorial al dataset <b>Spiral</b> (Norma 8), caracterizado por dos ramas helicoidales entrelazadas de 1.75 vueltas:
  </p>

  <div class="caption">Tabla 2. Mediciones directas en interfaz de TensorFlow Playground &mdash; Dataset Spiral (Ruido 10%, 500 épocas, n=3 semillas)</div>
  <table class="booktabs">
    <thead>
      <tr>
        <th>Regularizador</th>
        <th>Learning Rate (&alpha;)</th>
        <th>Lecturas Train [s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>]</th>
        <th>Train Loss (&mu; &plusmn; &sigma;)</th>
        <th>Lecturas Test [s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>]</th>
        <th>Test Loss (&mu; &plusmn; &sigma;)</th>
        <th>Enlaces Muertos [s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>]</th>
        <th>Comportamiento Estructural</th>
      </tr>
    </thead>
    <tbody>
{spiral_rows}
    </tbody>
  </table>

  <div class="figure-box">
    <img src="data:image/png;base64,{shot_spiral_b64}" alt="Spiral None Playground">
    <div class="figure-caption">
      <b>Figura 2. Captura de ejecución en TensorFlow Playground (Spiral, None, &alpha;=0.03, semilla s<sub>1</sub>=0.42, 500 épocas).</b><br>
      Muestra la semilla s<sub>1</sub>, estancada casi sin separación efectiva entre clases (test loss: 0.445, train loss: 0.473). Con 34 pesos y coordenadas puras (<i>X</i><sub>1</sub>, <i>X</i><sub>2</sub>), la red carece de capacidad inductiva para resolver las espirales.
    </div>
  </div>

  <h2>4. Discusión Crítica: Dinámica de Poda y Límites de Capacidad</h2>
  <p>
    <b>1. Dinámica de Poda y Línea Base L<sub>1</sub>:</b> Sin gradiente, un enlace muere si |<i>w</i><sub>0</sub>| &lt; &alpha;&lambda;T; al inicializar en <i>w</i><sub>0</sub> &sim; <i>U</i>[&minus;0.5, 0.5], esto ocurre con probabilidad teórica base &alpha;&lambda;T / 0.5 = 36% (&asymp;12 de 34 enlaces). Esta estimación sirve como línea base teórica ante ausencia de señal, no como cota estricta: en Spiral, donde la red queda atascada en meseta sin gradientes útiles sostenidos, se observan [9, 16, 21] enlaces muertos (media 45%), del mismo orden de magnitud ante <i>n</i> = 3; mientras que en Circle el gradiente activo protege la conectividad, reduciendo los muertos a solo 5.7 (16.7%). A &alpha; = 0.03, la desconexión selectiva consolida una subred esparsa viable (21.3 muertos, test 0.0837 &plusmn; 0.0006). A &alpha; = 0.3, la cifra de enlaces muertos se mantiene similar (22.0 vs. 21.3); por tanto, el número agregado de enlaces muertos no explica por sí solo la degradación del error a 0.1283, la cual es coherente, sobre todo, con el sobrepaso de gradiente (<i>overshooting</i>) propio de un paso agresivo con <i>B</i> = 10, patente también en None (0.1163) y L<sub>2</sub> (0.1013) [1, 3].
  </p>
  <p>
    <b>2. L<sub>2</sub> Continuo y Diagnóstico de la Brecha Train-Test:</b> L<sub>2</sub> (&alpha;=0.03, test 0.0820 &plusmn; 0.0017) empata en generalización con L<sub>1</sub> conservador (0.0763 &plusmn; 0.0074), superando a None (0.0997 &plusmn; 0.0045) y preservando todos los enlaces (0/34 muertos). Resulta revelador analizar la <i>brecha de generalización</i> (test &minus; train): en un modelo de 45 parámetros entrenables (34 pesos, 11 sesgos), la red sin regularizar sobreajusta el ruido ambiental del 10%, exhibiendo una brecha de 0.068&ndash;0.077 donde la pérdida de test supera entre 3 y 4 veces a la de train. Ambos regularizadores tienden a comprimir dicha brecha (L<sub>1</sub>: 0.039&ndash;0.055; L<sub>2</sub>: 0.050&ndash;0.064), resultado coherente con la mitigación de varianza: la brecha baja en 17 de 18 comparaciones por semilla (excepción: L<sub>2</sub>, &alpha;=0.3, s<sub>1</sub>). La esparsidad no estructurada de L<sub>1</sub> requiere librerías dispersas para aceleración real, y ante <i>n</i> = 3 la dispersión de L<sub>2</sub> es un indicador muestral [3].
  </p>
  <p>
    <b>3. Subajuste Estructural en Spiral:</b> En Spiral, un clasificador constante en 0 rinde una pérdida cuadrática de 0.500. En este montaje experimental (entradas <i>X</i><sub>1</sub>, <i>X</i><sub>2</sub> puras y red 4-4-2), las variantes con regularización (L<sub>1</sub>, L<sub>2</sub>) quedan atrapadas en valores próximos a dicho límite (0.453&ndash;0.461). A &alpha; = 0.003, todas las arquitecturas (incluida None con 0.4497) permanecen en meseta. En cambio, sin regularizar, semillas con pasos más ágiles escapan a la simetría nula trazando planos de corte que reducen la pérdida (None &alpha;=0.03 en s<sub>2</sub>, s<sub>3</sub> con 0.305 y 0.310; y None &alpha;=0.3 en s<sub>1</sub> con 0.327). Esto <b>sugiere</b> que en este montaje, la penalización de pesos agrava el subajuste cuando el modelo carece de la capacidad inductiva necesaria para resolver la geometría [3].
  </p>
</div>

<!-- PÁGINA 4: CONCLUSIONES, RECOMENDACIONES NORMATIVAS Y REFERENCIAS -->
<div class="academic-page">
  <h2>5. Conclusiones y Recomendaciones Normativas (Norma 9)</h2>
  <p>
    Basándose estrictamente en las mediciones empíricas registradas en TensorFlow Playground, se emiten las siguientes conclusiones y recomendaciones:
  </p>

  <div class="caption">Tabla 3. Matriz Normativa de Selección de Hiperparámetros basada en Evidencia Experimental</div>
  <table class="booktabs">
    <thead>
      <tr>
        <th>Topología / Diagnóstico</th>
        <th>Régimen Recomendado</th>
        <th>Configuración Evaluada</th>
        <th>Justificación Basada Estrictamente en Datos</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Fronteras radiales convexas con ruido moderado (Circle)</b></td>
        <td>L<sub>2</sub> continuo o L<sub>1</sub> conservador</td>
        <td>L<sub>2</sub> (&alpha;=0.03, &lambda;=0.003) &middot; L<sub>1</sub> (&alpha;=0.003, &lambda;=0.003)</td>
        <td>Desempeño equivalente (test 0.076&ndash;0.082 frente a 0.0997 en None). L<sub>1</sub> poda el 16.7% de enlaces; L<sub>2</sub> preserva conectividad completa sin desconexiones.</td>
      </tr>
      <tr>
        <td><b>Poda estructural deliberada / Compresión de red (Circle)</b></td>
        <td>L<sub>1</sub> con &alpha; moderado</td>
        <td>L<sub>1</sub> (&alpha;=0.03, &lambda;=0.003)</td>
        <td>Poda 21.3/34 enlaces (62.7% de esparsidad no estructurada) con test competitivo (0.0837 &plusmn; 0.0006); consistente con enlaces activos de gradiente fuerte. Requiere kernels dispersos para acelerar cómputo.</td>
      </tr>
      <tr>
        <td><b>Tasas de aprendizaje agresivas (&alpha; = 0.3)</b></td>
        <td>Evitar &alpha; = 0.3 en Circle (no se probó &alpha; &gt; 0.3)</td>
        <td>Evaluado a &alpha;=0.3 en todas las variantes</td>
        <td>Empeora el test en L<sub>1</sub> (0.0837&rarr;0.1283; +0.027 a +0.058 en las 3 semillas), en L<sub>2</sub> (0.0820&rarr;0.1013; +0.026 y +0.031 en 2 de 3 semillas) y en None solo por s<sub>3</sub> (0.0997&rarr;0.1163; +0.051). Coherente con sobrepaso de gradiente; en L<sub>1</sub> la poda es similar (22.0 vs 21.3).</td>
      </tr>
      <tr>
        <td><b>Variedades entrelazadas de alta curvatura (Spiral)</b></td>
        <td>None (&alpha;=0.03) como base; ampliar capacidad = hipótesis</td>
        <td>None (&alpha;=0.03) evaluado</td>
        <td>En este montaje (4-4-2, entradas <i>X</i><sub>1</sub>, <i>X</i><sub>2</sub>), L<sub>1</sub>/L<sub>2</sub> quedan en ~0.45&ndash;0.46 y regularizar parece reforzar el subajuste. Sin regularizar, 2 de 3 semillas bajan a &asymp;0.31; sin&middot;cos y más capacidad no se probaron.</td>
      </tr>
    </tbody>
  </table>

  <div class="formula-box" style="font-size: 7.0pt; margin: 3px 0;">
    <b>Hipótesis Metodológica sobre Dinámica de Poda:</b> La tasa &alpha; modula la rapidez con que las conexiones con gradiente débil derivan hacia el cero en <i>T</i> pasos (&Delta;w &asymp; &alpha;&lambda;T), mientras que teóricamente &lambda; actuaría discriminando los enlaces con gradiente insuficiente (|&part;E/&part;w| &le; &lambda;). En Circle, el recuento medio de enlaces muertos es similar entre &alpha;=0.03 (21.3) y &alpha;=0.3 (22.0).
  </div>

  <h2>6. Reproducibilidad y Código Abierto</h2>
  <p style="font-size: 7.1pt; margin-bottom: 3px;">
    Todas las evaluaciones fueron ejecutadas y capturadas sobre la aplicación web oficial de TensorFlow Playground (https://playground.tensorflow.org) en el motor Chromium mediante automatización en Puppeteer, registrando las lecturas directas del panel (#loss-train y #loss-test) e inspeccionando el estado interno de los enlaces (<code>isDead</code> y <code>weight</code>) mediante el enlace de datos de D3.js. El código ejecutor (<code>run_playground.js</code>), el registro bruto de las 54 ejecuciones (<code>resultados_brutos.csv</code> con enlaces muertos, marcas temporales y URLs directas), el volcado JSON (<code>links_isDead_run.json</code>) y las capturas íntegras se encuentran depositados en:
    <br><code style="font-family: 'JetBrains Mono', monospace; font-size: 6.8pt; color: #2980b9; word-break: break-all;">https://github.com/samuelbetzler/07MIAR_04_B_2026-27_Redes-Neuronales-y-Deep-Learning</code>
    <br>Estado base verificable para la semilla 0.42:
    <br><code style="font-family: 'JetBrains Mono', monospace; font-size: 6.1pt; color: #7f8c8d; word-break: break-all;">https://playground.tensorflow.org/#activation=tanh&amp;regularization=L2&amp;batchSize=10&amp;dataset=circle&amp;learningRate=0.03&amp;regularizationRate=0.003&amp;noise=10&amp;networkShape=4,4,2&amp;seed=0.42&amp;percTrainData=80&amp;x=true&amp;y=true</code>
  </p>

  <h2>Referencias Bibliográficas</h2>
  <div class="references">
    <p>[1] Tibshirani, R. (1996). <i>Regression shrinkage and selection via the lasso</i>. Journal of the Royal Statistical Society: Series B (Methodological), 58(1), 267&ndash;288.</p>
    <p>[2] Smilkov, D., Carter, S., Sculley, D., Vi&eacute;gas, F. B., &amp; Wattenberg, M. (2017). <i>Direct-manipulation visualization of deep networks</i>. arXiv preprint arXiv:1708.03788 (presentado en ICML Workshop on Visualization for Deep Learning).</p>
    <p>[3] Goodfellow, I., Bengio, Y., &amp; Courville, A. (2016). <i>Deep Learning</i>. MIT Press. Capítulo 7: Regularization for Deep Learning (pp. 224&ndash;270).</p>
    <p>[4] TensorFlow Playground. (2016). <i>Repositorio oficial de código abierto</i>. Google Inc. Disponible en: https://github.com/tensorflow/playground. Regla de desconexión y cruce por cero implementada en <code>src/nn.ts</code> (commit <code>bd89e3a</code>, 8 de marzo de 2017). Consulta: 4 de octubre de 2026.</p>
  </div>
</div>

</body>
</html>
"""

html_file = os.path.join(base_dir, "Foro_TF_Playground_CampozanoLopez_Samuel.html")
pdf_file = os.path.join(base_dir, "Foro_TF_Playground_CampozanoLopez_Samuel.pdf")

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML generado exitosamente en: {html_file}")

# Chrome headless shell
chrome_path = r"C:\Users\samue\.cache\puppeteer\chrome-headless-shell\win64-131.0.6778.204\chrome-headless-shell-win64\chrome-headless-shell.exe"

cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_file}",
    html_file
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Chrome salida:", res.stdout, res.stderr)

doc = fitz.open(pdf_file)
print(f"==================================================")
print(f"PDF GENERADO: {pdf_file}")
print(f"NÚMERO TOTAL DE PÁGINAS: {len(doc)}")
print(f"==================================================")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    img_name = f"scratch/page_definitive_{i+1}.png"
    img_path = os.path.join(base_dir, img_name)
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    pix.save(img_path)
    print(f"Página {i+1} exportada a: {img_path}")
