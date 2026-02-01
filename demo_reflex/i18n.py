"""
Internationalization Module
Provides EN/ES translations for the CAPA Demo.
"""

from typing import Dict

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Navigation
    "nav.home": {"en": "Home", "es": "Inicio"},
    "nav.docs": {"en": "Documentation", "es": "Documentacion"},
    "nav.api": {"en": "API Reference", "es": "Referencia API"},
    "nav.simple": {"en": "Simple Analysis", "es": "Analisis Simple"},
    "nav.multi": {"en": "Multi-Angle", "es": "Multi-Angulo"},
    "nav.modules": {"en": "Modules", "es": "Modulos"},
    "nav.canons": {"en": "Canons", "es": "Canones"},
    "nav.capture": {"en": "Capture", "es": "Capturar"},

    # Home Page
    "home.title": {"en": "CAPA", "es": "CAPA"},
    "home.subtitle": {"en": "Craniofacial Analysis & Prediction Architecture", "es": "Arquitectura de Analisis y Prediccion Craneofacial"},
    "home.description": {"en": "Advanced craniofacial analysis system based on 15+ peer-reviewed scientific papers", "es": "Sistema avanzado de analisis craneofacial basado en 15+ articulos cientificos revisados por pares"},
    "home.get_started": {"en": "Get Started", "es": "Comenzar"},
    "home.view_docs": {"en": "View Documentation", "es": "Ver Documentacion"},

    # Stats
    "stats.papers": {"en": "Scientific Papers", "es": "Articulos Cientificos"},
    "stats.modules": {"en": "Analysis Modules", "es": "Modulos de Analisis"},
    "stats.modes": {"en": "Analysis Modes", "es": "Modos de Analisis"},
    "stats.precision": {"en": "Precision Rate", "es": "Tasa de Precision"},

    # Features
    "features.title": {"en": "Features", "es": "Caracteristicas"},
    "features.wd.title": {"en": "WD Analysis", "es": "Analisis WD"},
    "features.wd.desc": {"en": "Bizygomatic width measurement and personality trait correlation", "es": "Medicion del ancho bicigomatico y correlacion de rasgos de personalidad"},
    "features.forehead.title": {"en": "Forehead Analysis", "es": "Analisis de Frente"},
    "features.forehead.desc": {"en": "Frontal inclination measurement and impulsiveness assessment", "es": "Medicion de inclinacion frontal y evaluacion de impulsividad"},
    "features.morphology.title": {"en": "Morphology Analysis", "es": "Analisis de Morfologia"},
    "features.morphology.desc": {"en": "Face shape classification and facial proportions", "es": "Clasificacion de forma facial y proporciones faciales"},
    "features.canons.title": {"en": "Neoclassical Canons", "es": "Canones Neoclasicos"},
    "features.canons.desc": {"en": "Classical facial proportion analysis based on Farkas principles", "es": "Analisis de proporciones faciales clasicas basado en principios de Farkas"},

    # Analysis Modes
    "modes.title": {"en": "Analysis Modes", "es": "Modos de Analisis"},
    "modes.fast": {"en": "Quick analysis for preview", "es": "Analisis rapido para previsualizacion"},
    "modes.standard": {"en": "Balanced speed and precision", "es": "Balance entre velocidad y precision"},
    "modes.thorough": {"en": "Exhaustive detailed analysis", "es": "Analisis exhaustivo detallado"},
    "modes.scientific": {"en": "Maximum scientific accuracy", "es": "Maxima precision cientifica"},

    # Documentation Page
    "docs.title": {"en": "Documentation", "es": "Documentacion"},
    "docs.intro": {"en": "Introduction", "es": "Introduccion"},
    "docs.scientific": {"en": "Scientific Foundation", "es": "Fundamento Cientifico"},
    "docs.papers": {"en": "Research Papers", "es": "Articulos de Investigacion"},
    "docs.limitations": {"en": "Limitations", "es": "Limitaciones"},

    # API Reference Page
    "api.title": {"en": "API Reference", "es": "Referencia de API"},
    "api.core_classes": {"en": "Core Classes", "es": "Clases Principales"},
    "api.modules": {"en": "Scientific Modules", "es": "Modulos Cientificos"},
    "api.configuration": {"en": "Configuration", "es": "Configuracion"},
    "api.result_types": {"en": "Result Types", "es": "Tipos de Resultado"},

    # Simple Analysis Page
    "simple.title": {"en": "Simple Analysis", "es": "Analisis Simple"},
    "simple.subtitle": {"en": "Upload an image and perform a complete analysis", "es": "Carga una imagen y realiza un analisis completo"},
    "simple.upload": {"en": "Upload Image", "es": "Cargar Imagen"},
    "simple.select": {"en": "Select Image", "es": "Seleccionar Imagen"},
    "simple.drag": {"en": "or drag and drop here", "es": "o arrastra aqui"},
    "simple.config": {"en": "Configuration", "es": "Configuracion"},
    "simple.mode": {"en": "Analysis Mode", "es": "Modo de Analisis"},
    "simple.analyze": {"en": "Analyze", "es": "Analizar"},
    "simple.analyzing": {"en": "Analyzing image...", "es": "Analizando imagen..."},

    # Multi-Angle Page
    "multi.title": {"en": "Multi-Angle Analysis", "es": "Analisis Multi-Angulo"},
    "multi.subtitle": {"en": "Upload multiple images from different angles", "es": "Carga multiples imagenes desde diferentes angulos"},
    "multi.upload": {"en": "Upload Images", "es": "Cargar Imagenes"},
    "multi.select": {"en": "Select Images", "es": "Seleccionar Imagenes"},
    "multi.max_files": {"en": "You can upload up to 5 images", "es": "Puedes cargar hasta 5 imagenes"},
    "multi.config": {"en": "Angle Configuration", "es": "Configuracion de Angulos"},
    "multi.subject_id": {"en": "Subject ID", "es": "ID del Sujeto"},
    "multi.analyze": {"en": "Analyze Multi-Angle", "es": "Analizar Multi-Angulo"},
    "multi.analyzing": {"en": "Analyzing multi-angle images...", "es": "Analizando imagenes multi-angulo..."},

    # Capture Analysis Page
    "capture.title": {"en": "Capture Analysis", "es": "Analisis de Captura"},
    "capture.subtitle": {"en": "Take a frontal photo or upload from gallery", "es": "Toma una foto frontal o sube desde la galeria"},
    "capture.mode_badge": {"en": "THOROUGH Mode", "es": "Modo EXHAUSTIVO"},
    "capture.camera": {"en": "Camera", "es": "Camara"},
    "capture.gallery": {"en": "Gallery", "es": "Galeria"},
    "capture.tap_capture": {"en": "Tap to capture", "es": "Toca para capturar"},
    "capture.select_gallery": {"en": "Select from Gallery", "es": "Seleccionar de Galeria"},
    "capture.frontal_tip": {"en": "Choose a frontal photo for best results", "es": "Elige una foto frontal para mejores resultados"},
    "capture.browse_files": {"en": "Browse Files", "es": "Buscar Archivos"},
    "capture.drag_drop": {"en": "or drag and drop here", "es": "o arrastra y suelta aqui"},
    "capture.retake": {"en": "Retake", "es": "Repetir"},
    "capture.analyze": {"en": "Analyze", "es": "Analizar"},
    "capture.analyzing": {"en": "Analyzing with THOROUGH mode...", "es": "Analizando con modo EXHAUSTIVO..."},
    "capture.analyzing_note": {"en": "This may take a moment for comprehensive analysis", "es": "Esto puede tomar un momento para un analisis completo"},
    "capture.new_capture": {"en": "New Capture", "es": "Nueva Captura"},
    "capture.face_scanning": {"en": "Looking for face...", "es": "Buscando rostro..."},
    "capture.face_detected": {"en": "Face detected - center in oval", "es": "Rostro detectado - centra en el ovalo"},
    "capture.face_centered": {"en": "Hold still...", "es": "Mantente quieto..."},
    "capture.face_ready": {"en": "Capturing in", "es": "Capturando en"},
    "capture.face_capturing": {"en": "Capturing...", "es": "Capturando..."},
    "capture.center_guide": {"en": "Center your face in the oval guide", "es": "Centra tu rostro en la guia ovalada"},

    # Modules Page
    "modules.title": {"en": "Individual Modules", "es": "Modulos Individuales"},
    "modules.subtitle": {"en": "Test each analysis module separately", "es": "Prueba cada modulo de analisis por separado"},
    "modules.wd.title": {"en": "WD (Bizygomatic Width) Analyzer", "es": "Analizador WD (Ancho Bicigomatico)"},
    "modules.wd.desc": {"en": "Analyzes bizygomatic width and social personality classification", "es": "Analiza el ancho bicigomatico y clasificacion de personalidad social"},
    "modules.forehead.title": {"en": "Forehead Inclination Analyzer", "es": "Analizador de Inclinacion Frontal"},
    "modules.forehead.desc": {"en": "Analyzes frontal inclination and impulsiveness level", "es": "Analiza la inclinacion frontal y nivel de impulsividad"},
    "modules.morphology.title": {"en": "Morphology Analyzer", "es": "Analizador de Morfologia"},
    "modules.morphology.desc": {"en": "Analyzes face shape and facial proportions", "es": "Analiza forma facial y proporciones faciales"},

    # Canons Page
    "canons.title": {"en": "Neoclassical Canons", "es": "Canones Neoclasicos"},
    "canons.subtitle": {"en": "Classical facial proportion analysis", "es": "Analisis de proporciones faciales clasicas"},
    "canons.ethnic": {"en": "Ethnic Group", "es": "Grupo Etnico"},
    "canons.analyze": {"en": "Analyze Canons", "es": "Analizar Canones"},
    "canons.analyzing": {"en": "Analyzing neoclassical canons...", "es": "Analizando canones neoclasicos..."},
    "canons.harmony": {"en": "Overall Harmony Score", "es": "Puntuacion de Armonia General"},
    "canons.measurements": {"en": "Canon Measurements", "es": "Mediciones de Canones"},
    "canons.deviation_note": {"en": "Values show deviation from ideal (0 = perfect)", "es": "Los valores muestran desviacion del ideal (0 = perfecto)"},

    # Results
    "results.title": {"en": "Results", "es": "Resultados"},
    "results.success": {"en": "Analysis completed successfully", "es": "Analisis completado exitosamente"},
    "results.confidence": {"en": "Overall Confidence", "es": "Confianza General"},
    "results.processing_time": {"en": "Processing Time", "es": "Tiempo de Procesamiento"},
    "results.export_json": {"en": "Export Results (JSON)", "es": "Exportar Resultados (JSON)"},
    "results.export": {"en": "Export Results", "es": "Exportar Resultados"},

    # WD Results
    "results.wd.title": {"en": "WD Analysis", "es": "Analisis WD"},
    "results.wd.value": {"en": "WD Value", "es": "Valor WD"},
    "results.wd.classification": {"en": "Classification", "es": "Clasificacion"},
    "results.wd.bizygomatic": {"en": "Bizygomatic Width", "es": "Ancho Bicigomatico"},
    "results.wd.bigonial": {"en": "Bigonial Width", "es": "Ancho Bigonial"},
    "results.wd.confidence": {"en": "Confidence", "es": "Confianza"},
    "results.wd.personality": {"en": "Personality Profile", "es": "Perfil de Personalidad"},

    # Forehead Results
    "results.forehead.title": {"en": "Forehead Analysis", "es": "Analisis de Frente"},
    "results.forehead.angle": {"en": "Slant Angle", "es": "Angulo de Inclinacion"},
    "results.forehead.impulsiveness": {"en": "Impulsiveness Level", "es": "Nivel de Impulsividad"},
    "results.forehead.height": {"en": "Forehead Height", "es": "Altura de Frente"},
    "results.forehead.confidence": {"en": "Confidence", "es": "Confianza"},
    "results.forehead.geometry": {"en": "Forehead Geometry", "es": "Geometria de Frente"},
    "results.forehead.neuro": {"en": "Neuroscience Correlations", "es": "Correlaciones Neurocientificas"},

    # Morphology Results
    "results.morphology.title": {"en": "Morphology Analysis", "es": "Analisis de Morfologia"},
    "results.morphology.shape": {"en": "Face Shape", "es": "Forma Facial"},
    "results.morphology.index": {"en": "Facial Index", "es": "Indice Facial"},
    "results.morphology.ratio": {"en": "W/H Ratio", "es": "Proporcion A/A"},
    "results.morphology.confidence": {"en": "Confidence", "es": "Confianza"},
    "results.morphology.proportions": {"en": "Facial Proportions", "es": "Proporciones Faciales"},

    # Multi-Angle Results
    "results.multi.combined": {"en": "Combined Results", "es": "Resultados Combinados"},
    "results.multi.angles_processed": {"en": "Angles Processed", "es": "Angulos Procesados"},
    "results.multi.combined_wd": {"en": "Combined WD", "es": "WD Combinado"},
    "results.multi.combined_shape": {"en": "Face Shape", "es": "Forma Facial"},
    "results.multi.combined_confidence": {"en": "Confidence", "es": "Confianza"},

    # Canons Results
    "results.canons.name": {"en": "Canon", "es": "Canon"},
    "results.canons.measured": {"en": "Measured", "es": "Medido"},
    "results.canons.ideal": {"en": "Ideal", "es": "Ideal"},
    "results.canons.deviation": {"en": "Deviation", "es": "Desviacion"},
    "results.canons.status": {"en": "Status", "es": "Estado"},
    "results.canons.in_range": {"en": "In Range", "es": "En Rango"},
    "results.canons.out_of_range": {"en": "Out of Range", "es": "Fuera de Rango"},

    # Canon Names
    "canon.equal_thirds": {"en": "Equal Thirds", "es": "Tercios Iguales"},
    "canon.eye_width": {"en": "Eye Width", "es": "Ancho de Ojo"},
    "canon.nose_width": {"en": "Nose Width", "es": "Ancho de Nariz"},
    "canon.mouth_width": {"en": "Mouth Width", "es": "Ancho de Boca"},
    "canon.nose_length": {"en": "Nose Length", "es": "Longitud de Nariz"},
    "canon.interocular": {"en": "Interocular Distance", "es": "Distancia Interocular"},
    "canon.face_width": {"en": "Face Width", "es": "Ancho Facial"},
    "canon.lower_face": {"en": "Lower Face", "es": "Tercio Inferior"},

    # Errors
    "error.no_image": {"en": "Please upload an image", "es": "Por favor carga una imagen"},
    "error.processing": {"en": "Error processing", "es": "Error al procesar"},
    "error.unknown": {"en": "Unknown error", "es": "Error desconocido"},
    "error.no_face": {"en": "No face detected or image unreadable", "es": "No se detecto rostro o imagen ilegible"},

    # Common
    "common.loading": {"en": "Loading...", "es": "Cargando..."},
    "common.processing": {"en": "Processing...", "es": "Procesando..."},
    "common.upload": {"en": "Upload", "es": "Cargar"},
    "common.analyze": {"en": "Analyze", "es": "Analizar"},
    "common.export": {"en": "Export", "es": "Exportar"},
    "common.close": {"en": "Close", "es": "Cerrar"},
    "common.language": {"en": "Language", "es": "Idioma"},

    # Personality Traits
    "trait.social_orientation": {"en": "Social Orientation", "es": "Orientacion Social"},
    "trait.relational_field": {"en": "Relational Field", "es": "Campo Relacional"},
    "trait.communication_style": {"en": "Communication Style", "es": "Estilo de Comunicacion"},
    "trait.leadership": {"en": "Leadership", "es": "Liderazgo"},
    "trait.interpersonal_effectiveness": {"en": "Interpersonal Effectiveness", "es": "Efectividad Interpersonal"},
    "trait.emotional_expressiveness": {"en": "Emotional Expressiveness", "es": "Expresividad Emocional"},
    "trait.social_energy_level": {"en": "Social Energy Level", "es": "Nivel de Energia Social"},
    "trait.conflict_resolution_style": {"en": "Conflict Resolution Style", "es": "Estilo de Resolucion de Conflictos"},

    # Classifications
    "class.highly_social": {"en": "Highly Social", "es": "Altamente Social"},
    "class.moderately_social": {"en": "Moderately Social", "es": "Moderadamente Social"},
    "class.balanced_social": {"en": "Balanced", "es": "Equilibrado"},
    "class.reserved": {"en": "Reserved", "es": "Reservado"},
    "class.highly_reserved": {"en": "Highly Reserved", "es": "Altamente Reservado"},

    # Impulsiveness Levels
    "impulse.very_low": {"en": "Very Low", "es": "Muy Bajo"},
    "impulse.low": {"en": "Low", "es": "Bajo"},
    "impulse.moderate_low": {"en": "Moderately Low", "es": "Moderadamente Bajo"},
    "impulse.moderate": {"en": "Moderate", "es": "Moderado"},
    "impulse.moderate_high": {"en": "Moderately High", "es": "Moderadamente Alto"},
    "impulse.high": {"en": "High", "es": "Alto"},
    "impulse.very_high": {"en": "Very High", "es": "Muy Alto"},

    # Face Shapes
    "shape.oval": {"en": "Oval", "es": "Ovalado"},
    "shape.round": {"en": "Round", "es": "Redondo"},
    "shape.square": {"en": "Square", "es": "Cuadrado"},
    "shape.rectangular": {"en": "Rectangular", "es": "Rectangular"},
    "shape.heart": {"en": "Heart", "es": "Corazon"},
    "shape.diamond": {"en": "Diamond", "es": "Diamante"},
    "shape.triangular": {"en": "Triangular", "es": "Triangular"},
    "shape.oblong": {"en": "Oblong", "es": "Oblongo"},
}


def t(key: str, lang: str = "en") -> str:
    """
    Get translation for a key in the specified language.

    Args:
        key: Translation key (e.g., "nav.home")
        lang: Language code ("en" or "es")

    Returns:
        Translated string, or key if not found
    """
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("en", key))
    return key


def get_all_translations(lang: str = "en") -> Dict[str, str]:
    """
    Get all translations for a language as a flat dictionary.

    Args:
        lang: Language code ("en" or "es")

    Returns:
        Dictionary with all translations
    """
    return {key: t(key, lang) for key in TRANSLATIONS}
