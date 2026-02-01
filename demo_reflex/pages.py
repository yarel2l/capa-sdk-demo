"""
Pages Module
All page definitions for the CAPA Demo.
"""

import reflex as rx
from .components import (
    navbar, mobile_bottom_nav, hero_section, stat_card, feature_card,
    error_alert, section_header, analysis_mode_card, quick_link_button,
    docs_sidebar, docs_content_wrapper, docs_mobile_nav,
    # Demo page result components
    wd_result_card, forehead_result_card,
    morphology_result_card, canons_result_card, analysis_summary_header,
    # Chart-enhanced result components
    wd_result_card_with_charts, forehead_result_card_with_charts,
    morphology_result_card_with_charts, canons_result_card_with_charts,
    analysis_confidence_dashboard,
)
from .state import (
    AppState, DocsState, DemoState
)


# =============================================================================
# HOME PAGE
# =============================================================================

def home_page() -> rx.Component:
    """Home page with modern hero, stats, and feature overview - responsive."""
    return rx.box(
        navbar(),
        # Hero Section
        hero_section(
            "CAPA",
            "Craniofacial Analysis & Prediction Architecture",
            "Advanced craniofacial analysis system based on 15+ peer-reviewed scientific papers. Analyze facial characteristics and their correlations with personality traits and neurological indicators.",
            use_logo_image=True,
        ),

        # Stats Section
        rx.box(
            rx.box(
                rx.grid(
                    stat_card("15+", "Scientific Papers", "file-text"),
                    stat_card("4", "Analysis Modules", "layers"),
                    stat_card("6", "Analysis Modes", "settings"),
                    stat_card("99.2%", "Precision Rate", "target"),
                    columns=rx.breakpoints(initial="2", md="4"),
                    spacing="3",
                    width="100%",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8",
            ),
        ),

        # Features Section
        rx.box(
            rx.box(
                rx.vstack(
                    section_header("Features", "Comprehensive facial analysis capabilities"),
                    rx.grid(
                        feature_card(
                            "WD Analysis",
                            "Bizygomatic width measurement and social personality trait correlation based on peer-reviewed research.",
                            "users"
                        ),
                        feature_card(
                            "Forehead Analysis",
                            "Frontal inclination measurement and impulsiveness assessment with neuroscience correlations.",
                            "brain"
                        ),
                        feature_card(
                            "Morphology Analysis",
                            "Face shape classification (10 types) and comprehensive facial proportions analysis.",
                            "scan"
                        ),
                        feature_card(
                            "Neoclassical Canons",
                            "Analysis of 8 classical facial proportions based on Farkas principles with ethnic group support.",
                            "ruler"
                        ),
                        columns=rx.breakpoints(initial="1", md="2"),
                        spacing="4",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8",
            ),
        ),

        # Analysis Modes Section
        rx.box(
            rx.box(
                rx.vstack(
                    section_header("Analysis Modes", "Choose the right mode for your needs"),
                    rx.grid(
                        analysis_mode_card("FAST", "Quick analysis for preview - basic modules only", "blue"),
                        analysis_mode_card("STANDARD", "Balanced speed and precision - recommended", "green"),
                        analysis_mode_card("THOROUGH", "Deep analysis with all modules enabled", "orange"),
                        analysis_mode_card("SCIENTIFIC", "Maximum accuracy - 2D observables only", "purple"),
                        columns=rx.breakpoints(initial="2", lg="4"),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8",
            ),
        ),

        # Quick Links
        rx.box(
            rx.box(
                rx.vstack(
                    section_header("Get Started", "Begin your analysis"),
                    rx.flex(
                        quick_link_button("View Documentation", "/docs", "book-open"),
                        quick_link_button("Try Demo", "/demo", "play"),
                        spacing="3",
                        wrap="wrap",
                        justify="center",
                    ),
                    spacing="4",
                    width="100%",
                    align="center",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8",
            ),
        ),

        # Footer
        rx.box(
            rx.box(
                rx.flex(
                    rx.text("CAPA v1.1.0", size="2", class_name="text-slate-500"),
                    width="100%",
                    justify="center",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-4",
            ),
            class_name="bg-slate-900 border-t border-slate-800 mt-8 mb-16 md:mb-0",
            width="100%",
        ),
        # Mobile bottom navigation
        mobile_bottom_nav(),
        class_name="min-h-screen bg-slate-900",
    )


# =============================================================================
# DOCUMENTATION PAGE - Nextra-style with Sidebar
# =============================================================================

# Documentation content sections
DOCS_INTRO = """
# CAPA Documentation

**Craniofacial Analysis & Prediction Architecture**

Welcome to the CAPA documentation. This SDK provides advanced craniofacial analysis capabilities based on 15+ peer-reviewed scientific papers.

## Overview

CAPA provides the following analysis capabilities:

| Feature | Description |
|---------|-------------|
| **WD Analysis** | Bizygomatic width measurement and social orientation classification |
| **Forehead Analysis** | Frontal inclination angle and impulsiveness level assessment |
| **Morphology Analysis** | Face shape classification and facial proportion analysis |
| **Neoclassical Canons** | Classical facial proportion validation |
| **Multi-Angle Analysis** | Combined analysis from multiple image angles |

## Quick Example

```python
from capa import CoreAnalyzer

# Initialize
analyzer = CoreAnalyzer()

# Analyze
result = analyzer.analyze_image("photo.jpg")

# Access results
print(f"WD Value: {result.wd_result.wd_value}")
print(f"Face Shape: {result.morphology_result.shape_classification.primary_shape.value}")

# Cleanup
analyzer.shutdown()
```

## Architecture

```
capa/
├── analyzers/          # Analysis orchestrators
│   ├── CoreAnalyzer
│   ├── MultiAngleAnalyzer
│   └── ResultsIntegrator
│
├── modules/            # Scientific analysis modules
│   ├── WDAnalyzer
│   ├── ForeheadAnalyzer
│   ├── MorphologyAnalyzer
│   └── NeoclassicalCanonsAnalyzer
│
└── _internal/          # Internal support systems
    ├── IntelligentLandmarkSystem
    ├── AdaptiveQualitySystem
    └── ContinuousImprovementSystem
```
"""

DOCS_GETTING_STARTED = """
# Getting Started

This guide will help you get started with the CAPA.

## Installation

### From PyPI (Recommended)

```bash
pip install capa-sdk
```

### From Source

```bash
git clone https://github.com/yarel2l/capa-sdk.git
cd capa-sdk
pip install -e .
```

### Dependencies

The SDK will automatically install required dependencies:

- numpy >= 1.24.0
- scipy >= 1.11.0
- opencv-python >= 4.8.0
- Pillow >= 10.0.0
- dlib >= 19.24.0
- face-recognition >= 1.3.0
- mediapipe >= 0.10.0
- scikit-learn >= 1.3.0

**Note:** dlib may require additional system dependencies. On macOS:

```bash
brew install cmake
```

On Ubuntu/Debian:

```bash
sudo apt-get install cmake libboost-all-dev
```

### Required Model File

The SDK requires the dlib 68-point facial landmark model:

```bash
# Download the model
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

# Extract it
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
```
"""

DOCS_QUICK_START = """
# Quick Start

### Basic Analysis

```python
from capa import CoreAnalyzer

# Initialize the analyzer
analyzer = CoreAnalyzer()

# Analyze an image
result = analyzer.analyze_image("path/to/photo.jpg")

# Check if analysis was successful
if result is not None:
    # Access WD analysis
    if result.wd_result:
        print(f"WD Value: {result.wd_result.wd_value:.3f}")
        print(f"Classification: {result.wd_result.primary_classification.value}")
        print(f"Confidence: {result.wd_result.measurement_confidence*100:.1f}%")

    # Access Forehead analysis
    if result.forehead_result:
        print(f"Slant Angle: {result.forehead_result.forehead_geometry.slant_angle_degrees:.1f}°")
        print(f"Impulsiveness: {result.forehead_result.impulsiveness_level.value}")

    # Access Morphology analysis
    if result.morphology_result:
        print(f"Face Shape: {result.morphology_result.shape_classification.primary_shape.value}")

# Always shutdown to release resources
analyzer.shutdown()
```

### Using Analysis Modes

```python
from capa import CoreAnalyzer, AnalysisConfiguration, AnalysisMode

# Configure for fast analysis
config = AnalysisConfiguration(
    mode=AnalysisMode.FAST,
    enable_wd_analysis=True,
    enable_forehead_analysis=True,
    enable_morphology_analysis=True,
)

analyzer = CoreAnalyzer(config=config)
result = analyzer.analyze_image("photo.jpg")
analyzer.shutdown()
```

### Available Analysis Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `FAST` | Quick analysis with basic processing | Real-time applications |
| `STANDARD` | Balanced analysis (default) | General use |
| `THOROUGH` | Deep analysis with all features | Detailed reports |
| `SCIENTIFIC` | Maximum accuracy, 2D observables only | Research |
| `RESEARCH` | Includes peer-reviewed correlations | Academic studies |
"""

DOCS_API_CORE = """
# Core Classes

## CoreAnalyzer

The main orchestrator for comprehensive facial analysis.

```python
from capa import CoreAnalyzer
```

### Constructor

```python
CoreAnalyzer(
    config: Optional[AnalysisConfiguration] = None,
    quality_cache_path: Optional[str] = None,
    improvement_cache_path: Optional[str] = None
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `AnalysisConfiguration` | Analysis configuration. If None, uses defaults. |
| `quality_cache_path` | `str` | Path for quality metrics cache |
| `improvement_cache_path` | `str` | Path for learning system cache |

### Methods

#### analyze_image

```python
def analyze_image(
    self,
    image: Union[np.ndarray, str, Path],
    analysis_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    angle_type: Optional[str] = None
) -> ComprehensiveAnalysisResult
```

Analyze an image (numpy array or file path).

**Parameters:**
- `image`: Input image as numpy array OR path to image file
- `analysis_id`: Optional identifier for this analysis
- `subject_id`: Optional identifier for the subject
- `angle_type`: Optional angle type ('frontal', 'lateral', 'semi_frontal', 'profile')

**Returns:** `ComprehensiveAnalysisResult`

#### shutdown

```python
def shutdown(self) -> None
```

Release all resources. Always call when done.

---

## MultiAngleAnalyzer

Analyzer for multiple images of the same individual.

```python
from capa import MultiAngleAnalyzer
```

### Constructor

```python
MultiAngleAnalyzer(config: Optional[AnalysisConfiguration] = None)
```

### Methods

#### analyze_multiple_angles

```python
def analyze_multiple_angles(
    self,
    angle_specs: List[AngleSpecification],
    subject_id: str,
    analysis_id: Optional[str] = None
) -> MultiAngleResult
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `angle_specs` | `List[AngleSpecification]` | List of angle specifications |
| `subject_id` | `str` | Unique identifier for the subject |
| `analysis_id` | `str` | Optional analysis session ID |

**Returns:** `MultiAngleResult`
"""

DOCS_API_CONFIG = """
# Configuration

## AnalysisConfiguration

```python
from capa import AnalysisConfiguration, AnalysisMode
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `AnalysisMode` | `STANDARD` | Analysis mode |
| `result_format` | `ResultFormat` | `STRUCTURED` | Output format for results |
| `enable_wd_analysis` | `bool` | `True` | Enable WD analysis |
| `enable_forehead_analysis` | `bool` | `True` | Enable forehead analysis |
| `enable_morphology_analysis` | `bool` | `True` | Enable morphology analysis |
| `enable_neoclassical_analysis` | `bool` | `True` | Enable neoclassical canons analysis |
| `enable_quality_assessment` | `bool` | `True` | Enable image quality validation |
| `enable_continuous_learning` | `bool` | `True` | Enable learning system |
| `enable_parallel_processing` | `bool` | `True` | Enable parallel execution |
| `max_worker_threads` | `int` | `4` | Maximum threads for parallel processing |

## AnalysisMode

```python
from capa import AnalysisMode
```

| Value | Description |
|-------|-------------|
| `FAST` | Quick analysis, basic modules only |
| `STANDARD` | Standard comprehensive analysis |
| `THOROUGH` | Deep analysis with all modules |
| `SCIENTIFIC` | Maximum scientific accuracy (2D observables only) |
| `RESEARCH` | Research mode with peer-reviewed correlations |

### Mode Comparison

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| `FAST` | ★★★★★ | ★★★☆☆ | Real-time apps |
| `STANDARD` | ★★★★☆ | ★★★★☆ | General use |
| `THOROUGH` | ★★★☆☆ | ★★★★★ | Detailed reports |
| `SCIENTIFIC` | ★★★☆☆ | ★★★★★ | Research (2D only) |
| `RESEARCH` | ★★☆☆☆ | ★★★★★ | Academic studies |
"""

DOCS_API_RESULTS = """
# Result Types

## ComprehensiveAnalysisResult

Complete result from CoreAnalyzer.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `wd_result` | `WDResult` | WD analysis result |
| `forehead_result` | `ForeheadResult` | Forehead analysis result |
| `morphology_result` | `MorphologyResult` | Morphology analysis result |
| `processing_metadata` | `ProcessingMetadata` | Processing information |
| `landmark_result` | `EnsembleResult` | Landmark detection result |

## WDResult

Result from WD (Width Difference) analysis.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `wd_value` | `float` | WD difference value in centimeters |
| `bizygomatic_width` | `float` | Bizygomatic width in pixels |
| `bigonial_width` | `float` | Bigonial width in pixels |
| `measurement_confidence` | `float` | Confidence score (0-1) |
| `personality_profile` | `WDPersonalityProfile` | Personality trait correlations |
| `primary_classification` | `WDClassification` | Social orientation classification |

### WDClassification

| Value | WD Range (cm) | Description |
|-------|---------------|-------------|
| `HIGHLY_SOCIAL` | ≥ 5.0 | Strong social orientation |
| `MODERATELY_SOCIAL` | 2.0 to 5.0 | Above average sociability |
| `BALANCED_SOCIAL` | -2.0 to 2.0 | Balanced social behavior |
| `RESERVED` | -5.0 to -2.0 | Reserved personality |
| `HIGHLY_RESERVED` | < -5.0 | Introverted tendency |

## ForeheadResult

Result from forehead analysis.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `forehead_geometry` | `ForeheadGeometry` | Geometric measurements |
| `impulsiveness_level` | `ImpulsivenessLevel` | Impulsiveness classification |
| `measurement_confidence` | `float` | Confidence score (0-1) |

### ImpulsivenessLevel

| Value | Angle Range | Description |
|-------|-------------|-------------|
| `VERY_LOW` | < 10° | Very low impulsiveness |
| `LOW` | 10° - 15° | Low impulsiveness |
| `MODERATE` | 20° - 25° | Moderate impulsiveness |
| `HIGH` | 30° - 35° | High impulsiveness |
| `VERY_HIGH` | > 35° | Very high impulsiveness |

## MorphologyResult

Result from morphology analysis.

### FaceShape

| Value | Description |
|-------|-------------|
| `OVAL` | Oval face shape |
| `ROUND` | Round face shape |
| `SQUARE` | Square face shape |
| `RECTANGULAR` | Rectangular face shape |
| `HEART` | Heart-shaped face |
| `DIAMOND` | Diamond face shape |
"""

DOCS_API_MODULES = """
# Scientific Modules

## WDAnalyzer

```python
from capa.modules import WDAnalyzer

analyzer = WDAnalyzer(enable_learning: bool = True)
result = analyzer.analyze_image(image: np.ndarray) -> Optional[WDResult]
```

Analyzes bizygomatic width and returns WDResult with classification and personality profile.

## ForeheadAnalyzer

```python
from capa.modules import ForeheadAnalyzer

analyzer = ForeheadAnalyzer(
    enable_learning: bool = True,
    enable_neuroscience: bool = True
)
result = analyzer.analyze_image(image: np.ndarray) -> Optional[ForeheadResult]
```

Analyzes forehead inclination and returns ForeheadResult with impulsiveness level.

## MorphologyAnalyzer

```python
from capa.modules import MorphologyAnalyzer

analyzer = MorphologyAnalyzer(
    enable_3d_reconstruction: bool = True,
    enable_learning: bool = True
)
result = analyzer.analyze_image(image: np.ndarray) -> Optional[MorphologyResult]
```

Analyzes face shape and returns MorphologyResult with 10 shape classifications.

## NeoclassicalCanonsAnalyzer

```python
from capa.modules import NeoclassicalCanonsAnalyzer

analyzer = NeoclassicalCanonsAnalyzer()
result = analyzer.analyze_image(image: np.ndarray) -> Optional[NeoclassicalAnalysisResult]
```

Analyzes 8 neoclassical facial canons with ethnic group support.

## AngleSpecification

```python
from capa import AngleSpecification

spec = AngleSpecification(
    angle_type: str,           # 'frontal', 'lateral_left', 'lateral_right', 'profile'
    image_path: str,           # Path to image file
    weight: float = 1.0,       # Weight for combining results
    quality_threshold: float = 0.3  # Minimum quality threshold
)
```
"""

DOCS_CONFIGURATION = """
# Configuration Guide

## Basic Configuration

```python
from capa import AnalysisConfiguration, AnalysisMode

config = AnalysisConfiguration(
    mode=AnalysisMode.STANDARD,
    enable_wd_analysis=True,
    enable_forehead_analysis=True,
    enable_morphology_analysis=True,
)
```

## Mode Examples

```python
from capa import CoreAnalyzer, AnalysisConfiguration, AnalysisMode

# For mobile/web applications
fast_config = AnalysisConfiguration(mode=AnalysisMode.FAST)

# For detailed PDF reports
thorough_config = AnalysisConfiguration(mode=AnalysisMode.THOROUGH)

# For academic research
research_config = AnalysisConfiguration(mode=AnalysisMode.RESEARCH)

# For scientific publications (2D observables only)
scientific_config = AnalysisConfiguration(mode=AnalysisMode.SCIENTIFIC)
```

## Selective Analysis

### Enable/Disable Specific Modules

```python
from capa import AnalysisConfiguration

# Only WD analysis
wd_only = AnalysisConfiguration(
    enable_wd_analysis=True,
    enable_forehead_analysis=False,
    enable_morphology_analysis=False,
)

# Only morphology
morphology_only = AnalysisConfiguration(
    enable_wd_analysis=False,
    enable_forehead_analysis=False,
    enable_morphology_analysis=True,
)
```

## Resource Management

```python
from capa import CoreAnalyzer

# Use context manager for automatic cleanup
with CoreAnalyzer() as analyzer:
    result = analyzer.analyze_image("photo.jpg")
# Resources automatically released

# Or manual cleanup
analyzer = CoreAnalyzer()
try:
    result = analyzer.analyze_image("photo.jpg")
finally:
    analyzer.shutdown()
```

## Performance Tuning

### Batch Processing Optimization

```python
from capa import CoreAnalyzer

# Reuse analyzer instance for multiple images
analyzer = CoreAnalyzer()

results = []
for image_path in image_paths:
    result = analyzer.analyze_image(image_path)
    results.append(result)

# Shutdown once at the end
analyzer.shutdown()
```
"""

DOCS_EXAMPLES = """
# Examples

## Single Image Analysis

```python
from capa import CoreAnalyzer

# Initialize analyzer
analyzer = CoreAnalyzer()

# Analyze an image
result = analyzer.analyze_image("photo.jpg")

if result:
    print(f"Overall confidence: {result.processing_metadata.overall_confidence*100:.1f}%")

    # WD Analysis
    if result.wd_result:
        print(f"WD Value: {result.wd_result.wd_value:.3f}")
        print(f"Classification: {result.wd_result.primary_classification.value}")

    # Forehead Analysis
    if result.forehead_result:
        print(f"Slant Angle: {result.forehead_result.forehead_geometry.slant_angle_degrees:.1f}°")

    # Morphology Analysis
    if result.morphology_result:
        print(f"Face Shape: {result.morphology_result.shape_classification.primary_shape.value}")

# Clean up
analyzer.shutdown()
```

## Multi-Angle Analysis

```python
from capa import MultiAngleAnalyzer, AngleSpecification

analyzer = MultiAngleAnalyzer()

# Define images with their angles
specs = [
    AngleSpecification(angle_type='frontal', image_path='front.jpg'),
    AngleSpecification(angle_type='lateral_left', image_path='left.jpg'),
    AngleSpecification(angle_type='lateral_right', image_path='right.jpg'),
]

result = analyzer.analyze_multiple_angles(
    angle_specs=specs,
    subject_id="subject_001"
)

print(f"Combined Confidence: {result.combined_confidence*100:.1f}%")

analyzer.shutdown()
```

## Individual Modules

### WD Analyzer

```python
import cv2
from capa.modules import WDAnalyzer

image = cv2.imread("photo.jpg")
analyzer = WDAnalyzer()

result = analyzer.analyze_image(image)

if result:
    print(f"WD Value: {result.wd_value:.3f}")
    print(f"Bizygomatic Width: {result.bizygomatic_width:.1f}px")
    print(f"Classification: {result.primary_classification.value}")
```

### Neoclassical Canons

```python
import cv2
from capa.modules import NeoclassicalCanonsAnalyzer

image = cv2.imread("photo.jpg")
analyzer = NeoclassicalCanonsAnalyzer()

result = analyzer.analyze_image(image)

if result:
    print(f"Overall Harmony: {result.overall_harmony_score*100:.1f}%")

    for canon in result.canon_results:
        print(f"Canon {canon.canon_number}: {canon.compliance_percentage:.1f}%")
```
"""

DOCS_SCIENTIFIC = """
# Scientific Foundation

CAPA is built on peer-reviewed scientific research in craniofacial analysis, neuroscience, and anthropometry.

## WD Analysis (Bizygomatic Width)

The WD (Width Difference) analysis measures the difference between **bizygomatic width** and **bigonial width**, correlating with social personality traits.

### Scientific Basis

- **Bizygomatic Width**: Distance between the zygomatic arches (cheekbones)
- **Bigonial Width**: Distance between the gonion points (jaw angles)
- **WD Value**: Bizygomatic - Bigonial width difference (in centimeters)
- **IPD Normalization**: Interpupillary distance used to convert pixels to centimeters

### Classification Ranges

Based on Gabarre-Armengol et al. (2019):

| Classification | WD (cm) | Interpretation |
|----------------|---------|----------------|
| Highly Social | ≥ 5.0 | Strong extroversion tendency |
| Moderately Social | 2.0 to 5.0 | Above average sociability |
| Balanced | -2.0 to 2.0 | Balanced social orientation |
| Reserved | -5.0 to -2.0 | Introverted tendency |
| Highly Reserved | < -5.0 | Strong introversion tendency |

---

## Forehead Analysis (Frontal Inclination)

The forehead analysis measures the **frontal inclination angle**, correlating with impulsiveness levels.

### Key Findings

- Direct correlation between forehead angle and BIS-11 (Barratt Impulsiveness Scale) scores
- Neuroanatomical basis related to prefrontal cortex development
- Validated through multiple peer-reviewed studies

### Angle Interpretation

| Angle Range | Level | Interpretation |
|-------------|-------|----------------|
| < 10° | Very Low | Very low impulsiveness |
| 10° - 15° | Low | Low impulsiveness |
| 20° - 25° | Moderate | Average impulsiveness |
| 30° - 35° | High | High impulsiveness |
| > 35° | Very High | Very high impulsiveness |

---

## Morphology Analysis (Face Shape)

Morphology analysis classifies face shapes and measures facial proportions.

### Face Shape Classifications

| Shape | Characteristics |
|-------|-----------------|
| Oval | Balanced proportions, slightly narrow forehead |
| Round | Equal width and height, soft features |
| Square | Angular jaw, wide forehead |
| Rectangular | Long face, angular features |
| Heart | Wide forehead, narrow chin |
| Diamond | Wide cheekbones, narrow forehead and chin |

---

## Neoclassical Canons

### The 8 Neoclassical Canons

1. **Equal Thirds**: Face divided into equal vertical thirds
2. **Eye Width**: Eye width equals interocular distance
3. **Nose Width**: Nose width equals interocular distance
4. **Mouth Width**: Mouth width equals 1.5× nose width
5. **Nose Length**: Nose length equals ear length
6. **Interocular Distance**: Eyes one eye-width apart
7. **Face Width**: 4× nose width
8. **Lower Face**: Lower third equals nose length

---

## Limitations and Disclaimers

### Scientific Limitations

1. **2D Analysis**: All measurements are from 2D images, not 3D scans
2. **Population Variance**: Research based on specific populations
3. **Individual Variation**: Results are statistical correlations, not deterministic

### Ethical Considerations

1. **Not Diagnostic**: Results should not be used for clinical diagnosis
2. **Professional Interpretation**: Qualified professionals should interpret results
3. **No Employment Decisions**: Should not be used for hiring or employment
"""

DOCS_PAPERS = """
# Research Papers

All referenced papers are included in the `data/` folder of the repository.

## WD Analysis (Bizygomatic Width)

| Paper | Key Findings |
|-------|--------------|
| **Bizygomatic Width and Personality Traits** (Gabarre-Armengol et al., 2019) | Correlation between facial width difference and relational field traits. WD mean: 0.74 cm, SD: 1.46 cm |
| **Bizygomatic Width and Social Traits in Males** | Association with social and personality characteristics |
| **Gray Matter Volume and Impulsiveness** | Neural correlates of facial measurements |

## Forehead Analysis

| Paper | Key Findings |
|-------|--------------|
| **Slant of the Forehead as Feature of Impulsiveness** | Direct correlation between forehead angle and BIS-11 scores |
| **Cortical Thickness and Forehead Slant** | Neuroanatomical basis for the correlation |
| **Frontonasal Dysmorphology in Bipolar Disorder** | Clinical applications |

## Morphology Analysis

| Paper | Key Findings |
|-------|--------------|
| **Neoclassical Facial Canons in Turkish Adults** | Validity of classical facial proportions |
| **Face Shape Evaluation in Turkish Individuals** | Face shape classification methodology |
| **3D Anthropometric Facial Analysis** | Precision measurements |

## Primary References

1. Gabarre-Mir, C., et al. "Bizygomatic Width and Personality Traits of the Relational Field"
2. Guerrero, M., et al. "The Slant of the Forehead as a Craniofacial Feature of Impulsiveness"
3. Gabarre-Armengol, C., et al. "Correlation between Impulsiveness, Cortical Thickness and Slant of The Forehead"
4. Karaman, F., et al. "The validity of eight neoclassical facial canons in the Turkish adults"
5. Arslan, E., et al. "Evaluation of Face Shape in Turkish Individuals"

## Foundational Works

- Farkas, L.G. (1994). *Anthropometry of the Head and Face*. Raven Press.
- Kolar, J.C. & Salter, E.M. (1997). *Craniofacial Anthropometry*. Charles C Thomas.
"""


def docs_page() -> rx.Component:
    """Unified documentation page with Nextra-style sidebar - responsive."""

    # Content selector based on active section
    content = rx.cond(
        DocsState.is_intro,
        docs_content_wrapper(rx.markdown(DOCS_INTRO)),
        rx.cond(
            DocsState.is_getting_started,
            docs_content_wrapper(rx.markdown(DOCS_GETTING_STARTED)),
            rx.cond(
                DocsState.is_quick_start,
                docs_content_wrapper(rx.markdown(DOCS_QUICK_START)),
                rx.cond(
                    DocsState.is_api_core,
                    docs_content_wrapper(rx.markdown(DOCS_API_CORE)),
                    rx.cond(
                        DocsState.is_api_config,
                        docs_content_wrapper(rx.markdown(DOCS_API_CONFIG)),
                        rx.cond(
                            DocsState.is_api_results,
                            docs_content_wrapper(rx.markdown(DOCS_API_RESULTS)),
                            rx.cond(
                                DocsState.is_api_modules,
                                docs_content_wrapper(rx.markdown(DOCS_API_MODULES)),
                                rx.cond(
                                    DocsState.is_configuration,
                                    docs_content_wrapper(rx.markdown(DOCS_CONFIGURATION)),
                                    rx.cond(
                                        DocsState.is_examples,
                                        docs_content_wrapper(rx.markdown(DOCS_EXAMPLES)),
                                        rx.cond(
                                            DocsState.is_scientific,
                                            docs_content_wrapper(rx.markdown(DOCS_SCIENTIFIC)),
                                            rx.cond(
                                                DocsState.is_papers,
                                                docs_content_wrapper(rx.markdown(DOCS_PAPERS)),
                                                docs_content_wrapper(rx.markdown(DOCS_INTRO)),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    return rx.box(
        navbar(),
        # Mobile navigation dropdown
        docs_mobile_nav(DocsState.active_section, DocsState.set_section),
        # Main layout with sidebar and content
        rx.hstack(
            # Desktop Sidebar (hidden on mobile)
            docs_sidebar(DocsState.active_section, DocsState.set_section),
            # Main content area
            rx.box(
                content,
                class_name="flex-1 overflow-y-auto h-[calc(100vh-57px)] md:h-[calc(100vh-57px)] pb-16 md:pb-0",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        # Footer
        rx.box(
            rx.box(
                rx.flex(
                    rx.text("CAPA v1.1.0", size="2", class_name="text-slate-500"),
                    width="100%",
                    justify="center",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-4",
            ),
            class_name="bg-slate-900 border-t border-slate-800 mb-16 md:mb-0",
            width="100%",
        ),
        # Mobile bottom navigation
        mobile_bottom_nav(),
        class_name="min-h-screen bg-slate-900",
    )


# =============================================================================
# DEMO PAGE - New simplified upload interface
# =============================================================================

def demo_upload_card(
    title: str,
    subtitle: str,
    icon: str,
    upload_id: str,
    on_upload,
    image_var: rx.Var,
    has_image: rx.Var,
    on_clear,
    is_required: bool = False,
) -> rx.Component:
    """Upload card component for demo page."""
    return rx.box(
        rx.vstack(
            # Header with fixed height
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24, class_name="text-orange-400"),
                    class_name="p-3 bg-orange-500/10 rounded-xl shrink-0",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(title, size="4", weight="bold", class_name="text-white"),
                        rx.cond(
                            is_required,
                            rx.badge("Required", color_scheme="orange", size="1"),
                            rx.badge("Optional", color_scheme="gray", size="1"),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(subtitle, size="2", class_name="text-slate-400"),
                    align="start",
                    spacing="1",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            # Upload zone or preview
            rx.cond(
                has_image,
                # Show preview with clear button
                rx.box(
                    rx.vstack(
                        rx.image(
                            src=image_var,
                            alt=title,
                            class_name="max-h-48 w-auto rounded-lg object-contain",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("x", size=14),
                                rx.text("Remove"),
                                spacing="1",
                            ),
                            on_click=on_clear,
                            variant="ghost",
                            size="1",
                            color_scheme="red",
                            class_name="mt-2",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    class_name="w-full flex justify-center p-4 bg-slate-800/30 rounded-lg border border-slate-700",
                ),
                # Show upload zone
                rx.upload(
                    rx.vstack(
                        rx.icon("image-plus", size=32, class_name="text-slate-500"),
                        rx.text("Click to upload", size="2", class_name="text-slate-400"),
                        rx.text("or drag and drop", size="1", class_name="text-slate-500"),
                        spacing="2",
                        align="center",
                    ),
                    id=upload_id,
                    accept={"image/*": []},
                    max_files=1,
                    on_drop=on_upload(rx.upload_files(upload_id=upload_id)),
                    class_name="w-full border-2 border-dashed border-slate-600 hover:border-orange-500 bg-slate-800/30 hover:bg-slate-800/50 rounded-lg p-6 transition-all duration-300 cursor-pointer flex-1 flex items-center justify-center",
                ),
            ),
            spacing="4",
            align="start",
            width="100%",
            height="100%",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 md:p-6 w-full max-w-[400px] md:w-[380px] lg:w-[440px] h-auto min-h-[320px] md:h-[360px] lg:h-[380px] flex flex-col",
    )


def demo_page() -> rx.Component:
    """Demo page with frontal and profile image upload cards."""
    return rx.box(
        navbar(),
        rx.box(
            rx.container(
            rx.vstack(
                # Upload cards container
                rx.flex(
                    # Frontal image card (required)
                    demo_upload_card(
                        title="Frontal Photo",
                        subtitle="Look straight at the camera",
                        icon="user",
                        upload_id="demo_frontal_upload",
                        on_upload=DemoState.handle_frontal_upload,
                        image_var=DemoState.frontal_image,
                        has_image=DemoState.has_frontal,
                        on_clear=DemoState.clear_frontal,
                        is_required=True,
                    ),
                    # Profile image card (optional)
                    demo_upload_card(
                        title="Profile Photo",
                        subtitle="Turn your head slightly to the side",
                        icon="circle-user",
                        upload_id="demo_profile_upload",
                        on_upload=DemoState.handle_profile_upload,
                        image_var=DemoState.profile_image,
                        has_image=DemoState.has_profile,
                        on_clear=DemoState.clear_profile,
                        is_required=False,
                    ),
                    justify="center",
                    align="center",
                    width="100%",
                    class_name="flex-col lg:flex-row gap-6 lg:gap-12 px-4 md:px-0",
                ),

                # Analyze button
                rx.box(
                    rx.button(
                        rx.hstack(
                            rx.cond(
                                DemoState.is_processing,
                                rx.spinner(size="2"),
                                rx.icon("zap", size=18),
                            ),
                            rx.cond(
                                DemoState.is_processing,
                                rx.text("Analyzing..."),
                                rx.text("Analyze"),
                            ),
                            spacing="2",
                            align="center",
                        ),
                        on_click=DemoState.analyze,
                        disabled=~DemoState.can_analyze,
                        color_scheme="orange",
                        size="4",
                        class_name="px-8 py-3 hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
                    ),
                    class_name="mt-8 flex justify-center",
                ),

                # Error message
                rx.cond(
                    DemoState.error_message != "",
                    rx.box(
                        error_alert(DemoState.error_message),
                        class_name="mt-4 max-w-md mx-auto",
                    ),
                ),

                # Results section
                rx.cond(
                    DemoState.has_results,
                    rx.box(
                        rx.vstack(
                            rx.divider(class_name="border-slate-700 my-8"),

                            # Analysis summary header
                            analysis_summary_header(
                                confidence=DemoState.overall_confidence,
                                processing_time=DemoState.processing_time,
                                is_multi_angle=DemoState.is_multi_angle_result,
                                num_angles=DemoState.num_angles_analyzed,
                            ),

                            # Module confidence dashboard
                            rx.cond(
                                DemoState.module_confidences.length() > 0,
                                analysis_confidence_dashboard(DemoState.confidence_dashboard_figure),
                            ),

                            # Results - WD Analysis card
                            rx.cond(
                                DemoState.has_wd_results,
                                wd_result_card_with_charts(
                                    wd_value=DemoState.wd_value,
                                    classification=DemoState.wd_classification,
                                    confidence=DemoState.wd_confidence,
                                    confidence_value=DemoState.wd_confidence_value,
                                    bizygomatic=DemoState.wd_bizygomatic,
                                    bigonial=DemoState.wd_bigonial,
                                    personality_traits=DemoState.personality_traits,
                                    personality_radar_figure=DemoState.personality_radar_figure,
                                    demographic_gauge_figure=DemoState.demographic_gauge_figure,
                                    evidence_level=DemoState.wd_evidence_level,
                                ),
                                rx.fragment(),
                            ),
                            # Morphology Analysis card (below WD)
                            rx.cond(
                                DemoState.has_morphology_results,
                                morphology_result_card_with_charts(
                                    face_shape=DemoState.morphology_shape,
                                    facial_index=DemoState.morphology_index,
                                    ratio=DemoState.morphology_ratio,
                                    confidence_value=DemoState.morphology_confidence_value,
                                    proportions=DemoState.morphology_proportions,
                                    face_shape_donut_figure=DemoState.face_shape_donut_figure,
                                    proportions_bar_figure=DemoState.proportions_bar_figure,
                                ),
                                rx.fragment(),
                            ),

                            # Forehead Analysis results with charts (conditional - requires profile image)
                            rx.cond(
                                DemoState.has_forehead_results,
                                forehead_result_card_with_charts(
                                    angle=DemoState.forehead_angle,
                                    impulsiveness=DemoState.forehead_impulsiveness,
                                    confidence_value=DemoState.forehead_confidence_value,
                                    height=DemoState.forehead_height,
                                    geometry_details=DemoState.forehead_geometry_details,
                                    impulsivity_radar_figure=DemoState.impulsivity_radar_figure,
                                    neuroscience_bar_figure=DemoState.neuroscience_bar_figure,
                                    evidence_level=DemoState.forehead_evidence_level,
                                ),
                                # Show info message if no profile image
                                rx.cond(
                                    ~DemoState.has_profile,
                                    rx.box(
                                        rx.hstack(
                                            rx.icon("info", size=16, class_name="text-slate-500"),
                                            rx.text(
                                                "Add a profile photo for forehead slant analysis",
                                                size="2",
                                                class_name="text-slate-500",
                                            ),
                                            spacing="2",
                                            align="center",
                                        ),
                                        class_name="p-3 bg-slate-800/20 border border-slate-700/30 rounded-lg",
                                    ),
                                    rx.fragment(),
                                ),
                            ),

                            # Neoclassical Canons results with charts (conditional)
                            rx.cond(
                                DemoState.has_canons_results,
                                canons_result_card_with_charts(
                                    overall_score=DemoState.canons_overall_score,
                                    overall_score_value=DemoState.canons_overall_score_value,
                                    measurements_list=DemoState.canon_measurements_list,
                                    harmony_gauge_figure=DemoState.harmony_gauge_figure,
                                    canon_deviation_bar_figure=DemoState.canon_deviation_bar_figure,
                                ),
                                rx.fragment(),
                            ),

                            # Action buttons
                            rx.hstack(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("download", size=14),
                                        rx.text("Export JSON"),
                                        spacing="2",
                                    ),
                                    on_click=DemoState.export_results,
                                    variant="outline",
                                    color_scheme="orange",
                                    size="2",
                                ),
                                rx.button(
                                    rx.hstack(
                                        rx.icon("rotate-ccw", size=14),
                                        rx.text("Start Over"),
                                        spacing="2",
                                    ),
                                    on_click=DemoState.clear_all,
                                    variant="outline",
                                    color_scheme="gray",
                                    size="2",
                                ),
                                spacing="3",
                                justify="center",
                                class_name="mt-6",
                            ),

                            align="center",
                            spacing="4",
                            width="100%",
                        ),
                        class_name="mt-6 w-full max-w-4xl mx-auto",
                    ),
                ),

                spacing="4",
                align="center",
                class_name="px-4 md:px-6 py-8 md:py-12 max-w-4xl mx-auto pb-20 md:pb-8",
            ),
                center_content=True,
            ),
            class_name="flex-1",
        ),
        # Footer
        rx.box(
            rx.box(
                rx.flex(
                    rx.text("CAPA v1.1.0", size="2", class_name="text-slate-500"),
                    width="100%",
                    justify="center",
                ),
                class_name="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-4",
            ),
            class_name="bg-slate-900 border-t border-slate-800 mb-16 md:mb-0 shrink-0",
            width="100%",
        ),
        # Mobile bottom navigation
        mobile_bottom_nav(),
        class_name="min-h-screen bg-slate-900 flex flex-col",
    )
