# Algoritmos-Optimizacion-Grafos

Simulador de algoritmos de optimización en grafos aplicado a un escenario industrial, con implementaciones de:

- **Dijkstra** (camino más corto)
- **Prim** (árbol de expansión mínima, MST)
- **Kruskal** (árbol de expansión mínima, MST)

El repositorio incluye dos enfoques:

1. **Simuladores en Python (terminal interactiva)**
2. **Simulador visual en navegador (HTML/CSS/JavaScript + Canvas)**

---

## Objetivo del proyecto

Modelar una red de estaciones industriales como un grafo ponderado para:

- Encontrar rutas óptimas entre origen y destino,
- Minimizar costos de conexión global mediante MST,
- Visualizar y entender paso a paso la ejecución de algoritmos clásicos de teoría de grafos.

---

## Escenario modelado

El problema usa un grafo no dirigido con:

- **12 nodos** (estaciones como ALMACEN, CNC-1, ENSAMBLE-B, QA, DESPACHO, etc.),
- **22 aristas** con pesos en **metros** (distancias/costos entre estaciones).

El mismo conjunto de nodos y aristas se utiliza tanto en los scripts Python como en la versión web.

---

## Estructura del repositorio

```text
.
├── 001_Simulador_Dijkstra.py
├── 002_Simulador_PRIM.py
├── 003_Simulador_Kruskal.py
├── index.html
├── css/
│   └── styles.css
└── js/
		├── graph-data.js
		├── algorithms.js
		├── canvas.js
		├── utils.js
		└── app.js
```

---

## Algoritmos implementados

### 1) Dijkstra

- **Propósito:** calcular la ruta de menor costo entre un nodo origen y un nodo destino.
- **Estrategia:** cola de prioridad + relajación de aristas.
- **Complejidad:** `O((V+E) log V)`.

### 2) Prim

- **Propósito:** construir un **MST** desde un nodo inicial.
- **Estrategia:** crecimiento incremental del árbol con la arista más barata hacia un nodo fuera del MST.
- **Complejidad:** `O(E log V)`.

### 3) Kruskal

- **Propósito:** construir un **MST** global del grafo.
- **Estrategia:** ordenar aristas por peso y agregar solo las que no forman ciclo.
- **Estructura clave:** Union-Find (con compresión de ruta y unión por rango).
- **Complejidad:** `O(E log E)`.

---

## Ejecución de los simuladores en Python

### Requisitos

- Python 3.8+ (recomendado)
- Sistema Linux, macOS o Windows

No se requieren librerías externas; se usan módulos estándar de Python.

### Ejecutar Dijkstra

```bash
python3 001_Simulador_Dijkstra.py
```

### Ejecutar Prim

```bash
python3 002_Simulador_PRIM.py
```

### Ejecutar Kruskal

```bash
python3 003_Simulador_Kruskal.py
```

Los tres scripts incluyen:

- menú interactivo,
- visualización textual paso a paso,
- métricas y resultados finales,
- opción de ajustar velocidad de simulación.

---

## Simulador web (HTML/CSS/JavaScript)

Además de la versión en terminal, se desarrolló una versión web interactiva donde se reutilizó la lógica de los algoritmos de Python y se implementó en JavaScript para ejecutarse en el navegador.

En esta versión:

- Se mantuvo el mismo grafo de la planta (12 nodos y 22 aristas).
- Se implementaron **Dijkstra, Prim y Kruskal** en `js/algorithms.js`.
- Se separó la arquitectura en módulos:
	- `js/graph-data.js` para datos del grafo,
	- `js/algorithms.js` para la lógica algorítmica,
	- `js/canvas.js` para la visualización en Canvas,
	- `js/app.js` para estado, eventos y simulación,
	- `js/utils.js` para utilidades de UI.

Esto permite comparar fácilmente la versión académica en Python con una versión visual orientada a demostración y publicación web.

---

## Publicación con GitHub Pages

Proceso seguido para publicarlo:

1. Subir al repositorio los archivos estáticos (`index.html`, carpeta `css/` y carpeta `js/`).
2. En GitHub, abrir **Settings → Pages** del repositorio.
3. En **Build and deployment**, seleccionar **Source: Deploy from a branch**.
4. Elegir la rama **main** y la carpeta raíz (`/root`).
5. Guardar cambios y esperar a que GitHub complete el despliegue.
6. Verificar que la URL pública cargue correctamente.

### Enlace de acceso

🔗 https://aad23110162.github.io/Algoritmos-Optimizacion-Grafos/

---

## Funcionalidades de la versión web

- Selección dinámica de algoritmo: **Dijkstra / Prim / Kruskal**.
- Mapa de planta en **Canvas** con nodos, aristas y pesos.
- Animación por pasos del algoritmo con control de velocidad.
- Bitácora de eventos en tiempo real.
- Métricas de ejecución:
  - Pasos,
  - Nodos visitados,
  - Distancia/costo,
  - Aristas del MST.
- Resumen visual del resultado:
  - Ruta óptima (Dijkstra),
  - MST y ruta dentro del MST (Prim/Kruskal).

---

