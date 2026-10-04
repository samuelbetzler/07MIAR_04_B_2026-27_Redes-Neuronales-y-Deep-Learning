# 07MIAR_04_B_2026-27: Redes Neuronales y Deep Learning

Repositorio oficial de actividades académicas para la asignatura **Redes Neuronales y Deep Learning (07MIAR)** en el **Máster Universitario en Inteligencia Artificial** de la **Universidad Internacional de Valencia (VIU)**.

* **Estudiante:** Samuel Segundo Campozano López
* **Grupo:** Grupo B — Convocatoria 2026-27
* **Entrega:** Octubre, 2026

---

## Estructura del Repositorio

```text
07MIAR_04_B_2026-27_Redes-Neuronales-y-Deep-Learning/
├── README.md
├── .gitignore
└── Foro_TF_Playground/
    ├── Foro_TF_Playground_CampozanoLopez_Samuel.pdf    # Informe formal de 4 páginas
    ├── Foro_TF_Playground_CampozanoLopez_Samuel.html   # Fuente HTML imprimible
    ├── build_definitive_document.py                    # Generador automatizado del informe
    ├── definitive_benchmark_results.json               # Mediciones completas en JSON
    ├── definitive_benchmark_results.csv                # Registro de pérdidas y esparsidad
    ├── run_definitive_benchmark.js                     # Script automatizado con Puppeteer
    ├── capturas_playground/                            # 18 capturas reales de la interfaz
    └── anexo/                                          # Anexo auditable de reproducibilidad
        ├── run_playground.js                           # Script ejecutable de los experimentos
        ├── resultados_brutos.csv                       # Registro con URLs y detalles por enlace
        ├── links_isDead_run.json                       # Volcado JSON de la extracción DOM D3.js
        └── capturas/
            ├── circle/                                 # 9 condiciones en Circle
            └── spiral/                                 # 9 condiciones en Spiral
```

---

## Foro Evaluable: TensorFlow Playground

### Título del Estudio
**Estudio Factorial del Tipo de Regularización ($L_1$, $L_2$, None) en Interacción con la Tasa de Aprendizaje ($\alpha$) en Redes MLP**

### Resumen del Diseño Experimental
* **Topología (Norma 3):** Perceptrón multicapa con 3 capas ocultas $[4, 4, 2]$ ($2 \to 4 \to 4 \to 2 \to 1$), sumando exactamente 34 pesos entrenables y 11 sesgos no regularizados.
* **Activación y Datos (Normas 2 y 8):** Activación $\tanh$ intermedia; Datasets **Circle** y **Spiral** con ratio 80% entrenamiento / 20% test ($400/100$ muestras), ruido fijado al 10% y tamaño de minilote $B=10$.
* **Rejilla Factorial (Normas 4 y 5):** Rejilla balanceada $3 \times 3$ evaluada en ambos datasets:
  $$\text{Regularizador} \in \{\text{None}, L_1, L_2\} \quad \times \quad \text{Learning Rate } \alpha \in \{0.003, 0.03, 0.3\}$$
  con tasa de regularización fija $\lambda = 0.003$ durante 500 épocas.
* **Trazabilidad de Normas 6 y 7:** Hilo registrado en Blackboard el 27/09/2026 a las 16:28 sin colisión factorial con otros compañeros.

### Hallazgos Principales
1. **Poda selectiva frente a ruido ($L_1$ con $\alpha=0.03$ en Circle):** Desconecta permanentemente el $62.7\%$ de las conexiones ($21.3/34$ enlaces muertos), manteniendo un error de test competitivo ($0.0837 \pm 0.0006$) gracias a que los enlaces viables sostienen gradientes fuertes $|\partial E/\partial w| > \lambda$.
2. **Estabilidad en regularización continua ($L_2$ con $\alpha=0.03$):** Empata con el mejor desempeño ($0.0820 \pm 0.0017$) preservando la totalidad de la red ($0/34$ muertos).
3. **Inestabilidad estocástica a $\alpha=0.3$:** El sobrepaso de gradiente (*overshooting*) degrada la convergencia en todos los regímenes (None: $0.1163$, $L_2$: $0.1013$, $L_1$: $0.1283$), demostrando que a $\alpha=0.3$ el deterioro en $L_1$ no obedece a un salto sustancial de desconexiones ($22.0$ vs. $21.3$).
4. **Subajuste estructural en Spiral:** Con coordenadas lineales puras ($X_1, X_2$), la arquitectura 4-4-2 carece de capacidad inductiva para envolver las ramas helicoidales ($1.75$ vueltas). Penalizar pesos en regímenes de subajuste severo bloquea la optimización y confina las pérdidas al entorno del clasificador nulo ($\approx 0.45\text{--}0.46$).

---

## Reproducibilidad y Código Abierto

Para auditar o reproducir los 54 experimentos:
1. Instalar dependencias en `Foro_TF_Playground/`:
   ```bash
   npm install puppeteer-core
   ```
2. Ejecutar la batería completa de pruebas:
   ```bash
   node anexo/run_playground.js
   ```
3. Consultar las URLs exactas con estado persistente para cada semilla en `anexo/resultados_brutos.csv`.
