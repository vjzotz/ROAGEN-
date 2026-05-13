# ROAGEN

**by vjzotz**

> Automatic XML generator for Resolume Arena Advanced Output — from SVG to slices in seconds.

---

## 🇬🇧 English

### What is ROAGEN?
ROAGEN is a portable desktop tool that converts SVG files into Resolume Arena Advanced Output XML configurations. It automates the creation of Slices and Polygons from SVG shapes, whether they come from Resolume's own export, Adobe Illustrator, Inkscape, or any other SVG-compatible software.

### Features
- ✅ Reads `<rect>`, `<polygon>` and `<path>` shapes from any SVG
- ✅ Detects rectangular shapes automatically → generates **Slices** with full Warper/BezierWarper/Homography blocks
- ✅ Detects free-form shapes → generates **Polygons** with Input/Output contours
- ✅ Supports separate Input and Output SVGs for advanced mapping
- ✅ Filters Illustrator stroke/border duplicate paths automatically
- ✅ Generates a visual **Grid PNG** of your layout with labels and guides
- ✅ Fully compatible with **Resolume Arena 7.26+**
- ✅ Portable `.exe` — no installation required

### How to use
1. Download `ROAGEN.exe` from the [Releases](../../releases) section
2. Load your **Input SVG** (the composition mapping)
3. Load your **Output SVG** (optional — the physical output mapping)
4. Enter composition and output resolutions
5. Click **GENERAR XML** → load the resulting `.xml` into Resolume Arena Advanced Output
6. Optionally click **GENERAR GRILLA** → get a visual PNG reference of your layout

### Supported SVG sources
| Software | Supported |
|---|---|
| Resolume Arena (export) | ✅ |
| Adobe Illustrator | ✅ |
| Inkscape | ✅ |
| Any SVG 1.1 compliant tool | ✅ |

### Requirements
- Windows 10 / 11
- Resolume Arena 7.26+
- No Python required — just run the `.exe`

---

## 🇦🇷 Español

### ¿Qué es ROAGEN?
ROAGEN es una herramienta de escritorio portable que convierte archivos SVG en configuraciones XML para la Salida Avanzada de Resolume Arena. Automatiza la creación de Slices y Polígonos a partir de formas SVG, ya sean exportadas desde el propio Resolume, Adobe Illustrator, Inkscape o cualquier software compatible con SVG.

### Características
- ✅ Lee formas `<rect>`, `<polygon>` y `<path>` de cualquier SVG
- ✅ Detecta formas rectangulares → genera **Slices** con bloques completos de Warper/BezierWarper/Homography
- ✅ Detecta formas libres → genera **Polygons** con contornos Input/Output
- ✅ Soporta SVGs separados de Input y Output para mapeo avanzado
- ✅ Filtra automáticamente los paths de borde/stroke duplicados de Illustrator
- ✅ Genera una **Grilla PNG** visual del layout con nombres y guías
- ✅ Totalmente compatible con **Resolume Arena 7.26+**
- ✅ `.exe` portable — sin instalación

### Cómo usarlo
1. Descargá `ROAGEN.exe` desde la sección [Releases](../../releases)
2. Cargá tu **SVG Input** (el mapeo de composición)
3. Cargá tu **SVG Output** (opcional — el mapeo de salida física)
4. Ingresá las resoluciones de composición y salida
5. Hacé clic en **GENERAR XML** → cargá el `.xml` resultante en la Salida Avanzada de Resolume Arena
6. Opcionalmente hacé clic en **GENERAR GRILLA** → obtenés un PNG de referencia visual del layout

### Fuentes SVG soportadas
| Software | Soportado |
|---|---|
| Resolume Arena (exportación) | ✅ |
| Adobe Illustrator | ✅ |
| Inkscape | ✅ |
| Cualquier herramienta SVG 1.1 | ✅ |

### Requisitos
- Windows 10 / 11
- Resolume Arena 7.26+
- No requiere Python — solo ejecutá el `.exe`

---

## 🛠️ Build from source

```bash
# Install dependencies
pip install customtkinter beautifulsoup4 svgwrite svglib reportlab

# Run from source
python ROAGEN.py

# Compile to exe
python -m PyInstaller --noconfirm --onefile --windowed --clean --collect-all customtkinter --collect-all svgwrite --collect-all svglib --collect-all reportlab --collect-all bs4 --icon="logo.ico" ROAGEN.py
```

---

## 📄 License
MIT License — free to use, modify and distribute.

---

*Made with ❤️ for the VJ and video mapping community*
