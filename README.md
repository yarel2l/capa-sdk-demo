# CAPA SDK Demo - Reflex Application

Demo interactivo del SDK de CAPA usando el framework Reflex, que muestra las capacidades del sistema de análisis craneofacial.

## Descripción

Esta aplicación web demuestra las capacidades del SDK CAPA (Craniofacial Analysis & Prediction Architecture), un sistema avanzado de análisis craneofacial basado en 15+ artículos científicos peer-reviewed.

## Páginas

La aplicación incluye 3 páginas principales:

### 1. **Home** (`/`)
- Página de bienvenida con descripción del sistema
- Estadísticas de capacidades (15+ papers, 4 módulos, 6 modos, 99.2% precisión)
- Descripción de features y módulos de análisis
- Enlaces rápidos a documentación y demo

### 2. **Documentación** (`/docs`)
- Documentación completa del SDK CAPA
- Navegación estilo Nextra con sidebar
- Secciones: Getting Started, Modules, API Reference, Examples, FAQ
- Ejemplos de código y configuración

### 3. **Demo** (`/demo`)
- Análisis interactivo de imágenes faciales
- Configuración de modos de análisis: FAST, STANDARD, THOROUGH, SCIENTIFIC
- Selección de módulos a ejecutar
- Visualización de resultados con gráficos Plotly
- Exportación de resultados a JSON

## Módulos de Análisis

| Módulo | Descripción |
|--------|-------------|
| **WD Analysis** | Medición de ancho bicigomático y correlación con rasgos sociales |
| **Forehead Analysis** | Análisis de inclinación frontal e indicadores de impulsividad |
| **Morphology Analysis** | Clasificación de forma facial (10 tipos) y proporciones |
| **Neoclassical Canons** | Análisis de 8 proporciones faciales clásicas |

## Instalación

### Prerrequisitos

- Python 3.9+
- El SDK de CAPA instalado en el directorio padre

### Instalar dependencias

```bash
cd demo_reflex
pip install -r requirements.txt
```

## Uso

### Iniciar la aplicación

```bash
cd demo_reflex
reflex run
```

La aplicación se abrirá en `http://localhost:3000`

### Uso alternativo con otro puerto

```bash
reflex run --port 8000
```

## Arquitectura del Proyecto

```
demo_reflex/
├── demo_reflex/
│   ├── __init__.py
│   ├── demo_reflex.py      # Aplicación principal y rutas
│   ├── state.py            # Estados de Reflex (AppState, DemoState, DocsState)
│   ├── pages.py            # Definición de páginas y contenido de docs
│   ├── components.py       # Componentes UI reutilizables
│   └── capa_service.py     # Servicio de integración con CAPA SDK
├── assets/                 # Assets estáticos
├── tests/                  # Tests unitarios
├── uploaded_images/        # Imágenes cargadas (temporal)
├── exports/                # Resultados exportados
├── requirements.txt
├── rxconfig.py            # Configuración de Reflex
└── README.md
```

## Tecnologías

- **Reflex 0.8.26**: Framework full-stack en Python
- **CAPA SDK**: Sistema de análisis craneofacial
- **Plotly**: Visualizaciones y gráficos interactivos
- **OpenCV**: Procesamiento de imágenes
- **MediaPipe / dlib**: Detección de landmarks faciales

## Tests

```bash
cd demo_reflex
pytest
```

## Licencia

Este demo sigue la misma licencia que el SDK de CAPA (dual-license: Open Source para uso no comercial, Commercial License para uso comercial).
