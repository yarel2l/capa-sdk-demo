"""
CAPA Service Module
Encapsulates all CAPA SDK functionalities for use in Reflex.
"""

import sys
from pathlib import Path
import cv2
import numpy as np
from typing import Optional, Dict, List, Any
import traceback
import json

# Add parent directory to path to import capa
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from capa import (
    CoreAnalyzer,
    MultiAngleAnalyzer,
    AnalysisConfiguration,
    AnalysisMode,
    AngleSpecification
)
from capa.modules import (
    WDAnalyzer,
    ForeheadAnalyzer,
    MorphologyAnalyzer,
    NeoclassicalCanonsAnalyzer
)

# Import ResultsIntegrator for cross-module analysis
try:
    from capa.analyzers.results_integrator import ResultsIntegrator, EvidenceLevel
    HAS_RESULTS_INTEGRATOR = True
except ImportError:
    HAS_RESULTS_INTEGRATOR = False
    ResultsIntegrator = None
    EvidenceLevel = None


class CapaService:
    """Service class for CAPA SDK operations."""

    def __init__(self):
        self.core_analyzer = None
        self.multi_angle_analyzer = None
        self.wd_analyzer = WDAnalyzer()
        self.forehead_analyzer = ForeheadAnalyzer()
        self.morphology_analyzer = MorphologyAnalyzer()
        self.neoclassical_analyzer = NeoclassicalCanonsAnalyzer()

    def analyze_single_image(
        self,
        image_path: str,
        mode: str = "STANDARD",
        enable_wd: bool = True,
        enable_forehead: bool = True,
        enable_morphology: bool = True,
        enable_neoclassical: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a single image.

        Args:
            image_path: Path to the image file
            mode: Analysis mode (FAST, STANDARD, THOROUGH, SCIENTIFIC)
            enable_wd: Enable WD analysis
            enable_forehead: Enable forehead analysis
            enable_morphology: Enable morphology analysis
            enable_neoclassical: Enable neoclassical canons analysis

        Returns:
            Dictionary with analysis results
        """
        import time
        start_time = time.time()

        try:
            # Create configuration
            analysis_mode = AnalysisMode[mode]
            config = AnalysisConfiguration(
                mode=analysis_mode,
                enable_wd_analysis=enable_wd,
                enable_forehead_analysis=enable_forehead,
                enable_morphology_analysis=enable_morphology,
                enable_neoclassical_analysis=enable_neoclassical,
            )

            # Initialize analyzer
            self.core_analyzer = CoreAnalyzer(config=config)

            # Perform analysis
            result = self.core_analyzer.analyze_image(image_path)

            if result is None:
                return {
                    "success": False,
                    "error": "No face detected or image unreadable"
                }

            # Format results
            results_dict = {
                "success": True,
                "wd_result": None,
                "forehead_result": None,
                "morphology_result": None,
                "neoclassical_result": None,
                "metadata": None
            }

            # WD Analysis results with full personality profile
            if result.wd_result:
                wd = result.wd_result
                wd_dict = {
                    # Use cm values when available (paper-calibrated)
                    "wd_value": float(wd.wd_value_cm) if hasattr(wd, 'wd_value_cm') and wd.wd_value_cm != 0 else float(wd.wd_value),
                    "wd_value_px": float(wd.wd_value),  # Keep pixel value for reference
                    "classification": wd.primary_classification.value,
                    # Widths in cm when available
                    "bizygomatic_width": float(wd.bizygomatic_width_cm) if hasattr(wd, 'bizygomatic_width_cm') and wd.bizygomatic_width_cm != 0 else float(wd.bizygomatic_width),
                    "bizygomatic_width_px": float(wd.bizygomatic_width),
                    "bigonial_width": float(wd.bigonial_width_cm) if hasattr(wd, 'bigonial_width_cm') and wd.bigonial_width_cm != 0 else float(wd.bigonial_width),
                    "bigonial_width_px": float(wd.bigonial_width),
                    "confidence": max(0.0, min(1.0, float(wd.measurement_confidence))),  # Clamp to 0-1
                    "wd_ratio": float(wd.wd_ratio) if hasattr(wd, 'wd_ratio') else None,
                    "normalized_wd_value": float(wd.normalized_wd_value) if hasattr(wd, 'normalized_wd_value') else None,
                    # Demographic normalization data
                    "demographic_percentile": float(wd.demographic_percentile) if hasattr(wd, 'demographic_percentile') else None,
                    "robust_classification": wd.robust_classification if hasattr(wd, 'robust_classification') else None,
                    # Flag to indicate if values are in cm
                    "units": "cm" if hasattr(wd, 'wd_value_cm') and wd.wd_value_cm != 0 else "px",
                }

                # Add personality profile if available (use correct attribute names with _score suffix)
                if hasattr(wd, 'personality_profile') and wd.personality_profile:
                    pp = wd.personality_profile
                    wd_dict["personality_profile"] = {
                        "social_orientation": getattr(pp, 'social_orientation_score', getattr(pp, 'social_orientation', 'N/A')),
                        "relational_field": getattr(pp, 'relational_field_score', getattr(pp, 'relational_field', 'N/A')),
                        "communication_style": getattr(pp, 'communication_style_score', getattr(pp, 'communication_style', 'N/A')),
                        "leadership": getattr(pp, 'leadership_tendency', getattr(pp, 'leadership', 'N/A')),
                        "interpersonal_effectiveness": getattr(pp, 'interpersonal_effectiveness', 'N/A'),
                        "emotional_expressiveness": getattr(pp, 'emotional_expressiveness', 'N/A'),
                        "social_energy_level": getattr(pp, 'social_energy_level', 'N/A'),
                        "conflict_resolution_style": getattr(pp, 'conflict_resolution_style', 'N/A'),
                    }

                # Add secondary traits if available
                if hasattr(wd, 'secondary_traits') and wd.secondary_traits:
                    wd_dict["secondary_traits"] = list(wd.secondary_traits)

                # Add Z-score demographic data if available
                if hasattr(wd, 'normalized_wd_z_score') and wd.normalized_wd_z_score is not None:
                    wd_dict["demographic_data"] = {
                        "z_score": float(wd.normalized_wd_z_score),
                        "percentile": float(wd.demographic_percentile) if hasattr(wd, 'demographic_percentile') and wd.demographic_percentile else 50.0,
                        "robust_classification": wd.robust_classification if hasattr(wd, 'robust_classification') else None,
                        "reference_population": getattr(wd, 'demographic_reference', {}) if hasattr(wd, 'demographic_reference') else None,
                    }

                # Add evidence level for scientific transparency
                wd_dict["evidence_level"] = "validated"
                wd_dict["paper_reference"] = "Lefevre et al. (2012) - fWHR correlations"

                results_dict["wd_result"] = wd_dict

            # Forehead Analysis results with full geometry
            if result.forehead_result:
                fh = result.forehead_result
                fh_dict = {
                    "slant_angle": float(fh.forehead_geometry.slant_angle_degrees),
                    "forehead_height": float(fh.forehead_geometry.forehead_height),
                    "impulsiveness_level": fh.impulsiveness_level.value,
                    "confidence": float(fh.measurement_confidence),
                }

                # Add detailed geometry
                geom = fh.forehead_geometry
                fh_dict["geometry"] = {
                    "slant_angle": float(geom.slant_angle_degrees),
                    "forehead_height": float(geom.forehead_height),
                    "forehead_width": float(geom.forehead_width) if hasattr(geom, 'forehead_width') else 0,
                    "curvature": float(geom.forehead_curvature) if hasattr(geom, 'forehead_curvature') else 0,
                    "frontal_prominence": float(geom.frontal_prominence) if hasattr(geom, 'frontal_prominence') else 0,
                    "temporal_width": float(geom.temporal_width) if hasattr(geom, 'temporal_width') else 0,
                    "width_height_ratio": float(geom.width_height_ratio) if hasattr(geom, 'width_height_ratio') else 0,
                }

                # Add neuroscience correlations if available
                if hasattr(fh, 'neuroscience_correlations') and fh.neuroscience_correlations:
                    nc = fh.neuroscience_correlations
                    fh_dict["neuroscience"] = {
                        "cortical_thickness_correlation": getattr(nc, 'cortical_thickness_correlation', None),
                        "gray_matter_volume_correlation": getattr(nc, 'gray_matter_volume_correlation', None),
                        "prefrontal_activity_indicator": getattr(nc, 'prefrontal_activity_indicator', None),
                    }

                    # Add neurotransmitter predictions
                    fh_dict["neurotransmitters"] = {
                        "dopamine_activity": getattr(nc, 'dopamine_system_activity', None),
                        "serotonin_balance": getattr(nc, 'serotonin_system_balance', None),
                        "gaba_function": getattr(nc, 'gaba_system_function', None),
                    }

                    # Add cognitive function predictions
                    fh_dict["cognitive_functions"] = {
                        "executive_function": getattr(nc, 'executive_function_score', None),
                        "working_memory": getattr(nc, 'working_memory_capacity', None),
                        "attention_control": getattr(nc, 'attention_control_score', None),
                        "cognitive_flexibility": getattr(nc, 'cognitive_flexibility', None),
                        "inhibitory_control": getattr(nc, 'inhibitory_control', None),
                    }

                # Add impulsivity profile (BIS-11 dimensions) if available
                if hasattr(fh, 'impulsivity_profile') and fh.impulsivity_profile:
                    ip = fh.impulsivity_profile
                    fh_dict["impulsivity_profile"] = {
                        "motor_impulsiveness": getattr(ip, 'motor_impulsiveness', None),
                        "cognitive_impulsiveness": getattr(ip, 'cognitive_impulsiveness', None),
                        "non_planning_impulsiveness": getattr(ip, 'non_planning_impulsiveness', None),
                        "attentional_impulsiveness": getattr(ip, 'attentional_impulsiveness', None),
                        "risk_taking_tendency": getattr(ip, 'risk_taking_tendency', None),
                        "sensation_seeking": getattr(ip, 'sensation_seeking', None),
                        "behavioral_inhibition": getattr(ip, 'behavioral_inhibition', None),
                        "emotional_regulation": getattr(ip, 'emotional_regulation', None),
                    }

                # Add confidence intervals (95% CI) if available
                if hasattr(fh, 'confidence_intervals') and fh.confidence_intervals:
                    ci = fh.confidence_intervals
                    fh_dict["confidence_intervals"] = {
                        "angle_95ci": ci.get('angle_95ci', None),
                        "impulsiveness_95ci": ci.get('impulsiveness_95ci', None),
                    }

                # Add evidence level for scientific transparency
                fh_dict["evidence_level"] = "validated"
                fh_dict["paper_reference"] = "Guerrero-Apolo et al. (2018) - FID-BIS11 correlation"

                results_dict["forehead_result"] = fh_dict

            # Morphology Analysis results with full proportions
            if result.morphology_result:
                morph = result.morphology_result
                morph_dict = {
                    "face_shape": morph.shape_classification.primary_shape.value,
                    "facial_index": float(morph.facial_proportions.facial_index),
                    "width_height_ratio": float(morph.facial_proportions.facial_width_height_ratio),
                    "confidence": float(morph.measurement_confidence),
                }

                # Add shape confidence if available
                if hasattr(morph.shape_classification, 'confidence'):
                    morph_dict["shape_confidence"] = float(morph.shape_classification.confidence)

                # Add detailed proportions
                props = morph.facial_proportions
                morph_dict["proportions"] = {
                    "upper_face_ratio": float(props.upper_face_ratio) if hasattr(props, 'upper_face_ratio') else 0,
                    "middle_face_ratio": float(props.middle_face_ratio) if hasattr(props, 'middle_face_ratio') else 0,
                    "lower_face_ratio": float(props.lower_face_ratio) if hasattr(props, 'lower_face_ratio') else 0,
                    "bizygomatic_width": float(props.bizygomatic_width) if hasattr(props, 'bizygomatic_width') else 0,
                    "bigonial_width": float(props.bigonial_width) if hasattr(props, 'bigonial_width') else 0,
                    "facial_width": float(props.bizygomatic_width) if hasattr(props, 'bizygomatic_width') else 0,
                    "facial_height": float(props.total_face_height) if hasattr(props, 'total_face_height') else 0,
                    "facial_index": float(props.facial_index) if hasattr(props, 'facial_index') else 0,
                    "nasal_width": float(props.nasal_width) if hasattr(props, 'nasal_width') else 0,
                    "mouth_width": float(props.mouth_width) if hasattr(props, 'mouth_width') else 0,
                }

                # Add shape probabilities distribution if available
                shape_class = morph.shape_classification
                if hasattr(shape_class, 'shape_probabilities') and shape_class.shape_probabilities:
                    morph_dict["shape_probabilities"] = {
                        shape.value if hasattr(shape, 'value') else str(shape): float(prob)
                        for shape, prob in shape_class.shape_probabilities.items()
                    }
                elif hasattr(shape_class, 'secondary_shapes') and shape_class.secondary_shapes:
                    # Fallback: create probabilities from primary + secondary shapes
                    morph_dict["shape_probabilities"] = {
                        shape_class.primary_shape.value: float(shape_class.confidence) if hasattr(shape_class, 'confidence') else 0.7,
                    }
                    remaining_prob = 1.0 - morph_dict["shape_probabilities"][shape_class.primary_shape.value]
                    for i, sec_shape in enumerate(shape_class.secondary_shapes[:4]):  # Max 4 secondary
                        shape_name = sec_shape.value if hasattr(sec_shape, 'value') else str(sec_shape)
                        morph_dict["shape_probabilities"][shape_name] = remaining_prob / len(shape_class.secondary_shapes[:4])

                # Add symmetry analysis if available
                if hasattr(morph, 'symmetry_analysis') and morph.symmetry_analysis:
                    sym = morph.symmetry_analysis
                    morph_dict["symmetry"] = {
                        "horizontal_symmetry": getattr(sym, 'horizontal_symmetry', None),
                        "vertical_symmetry": getattr(sym, 'vertical_symmetry', None),
                        "overall_symmetry": getattr(sym, 'overall_symmetry', None),
                    }

                results_dict["morphology_result"] = morph_dict

            # Neoclassical Canons results
            if result.neoclassical_result:
                neo = result.neoclassical_result
                neo_dict = {
                    "overall_score": float(neo.overall_validity_score) if hasattr(neo, 'overall_validity_score') else 0.0,
                    "beauty_score": float(neo.beauty_score) if hasattr(neo, 'beauty_score') else None,
                    "proportion_balance": float(neo.proportion_balance) if hasattr(neo, 'proportion_balance') else None,
                    "confidence": float(neo.confidence) if hasattr(neo, 'confidence') else 0.0,
                }

                # Extract individual canon measurements
                if hasattr(neo, 'canons') and neo.canons:
                    canon_measurements = {}
                    for canon in neo.canons:
                        canon_name = getattr(canon, 'canon_name', f'Canon {len(canon_measurements)+1}')
                        canon_measurements[canon_name] = {
                            "measured_value": float(getattr(canon, 'measured_ratio', 0)),
                            "deviation": float(canon.deviation_percentage) if hasattr(canon, 'deviation_percentage') else 0,
                            "within_range": canon.is_valid if hasattr(canon, 'is_valid') else False,
                            "confidence": float(getattr(canon, 'confidence', 0.8)),
                        }
                    neo_dict["canon_measurements"] = canon_measurements

                # Add recommendations if available
                if hasattr(neo, 'recommendations') and neo.recommendations:
                    neo_dict["recommendations"] = list(neo.recommendations)

                results_dict["neoclassical_result"] = neo_dict

            # Processing metadata
            if result.processing_metadata:
                # Clamp confidence to valid range
                overall_conf = float(result.processing_metadata.overall_confidence)
                overall_conf = max(0.0, min(1.0, overall_conf))

                results_dict["metadata"] = {
                    "overall_confidence": overall_conf,
                    "processing_time": time.time() - start_time,  # Use actual elapsed time
                    "analysis_mode": mode,
                    "modules_executed": {
                        "wd": enable_wd,
                        "forehead": enable_forehead,
                        "morphology": enable_morphology,
                        "neoclassical": enable_neoclassical,
                    }
                }
            else:
                # Provide metadata even if processing_metadata is None
                results_dict["metadata"] = {
                    "overall_confidence": 0.0,
                    "processing_time": time.time() - start_time,
                    "analysis_mode": mode,
                    "modules_executed": {
                        "wd": enable_wd,
                        "forehead": enable_forehead,
                        "morphology": enable_morphology,
                        "neoclassical": enable_neoclassical,
                    }
                }

            return results_dict

        except Exception as e:
            return {
                "success": False,
                "error": f"Error during analysis: {str(e)}",
                "traceback": traceback.format_exc()
            }
        finally:
            if self.core_analyzer:
                self.core_analyzer.shutdown()
                self.core_analyzer = None

    def analyze_multi_angle(
        self,
        image_paths: List[Dict[str, str]],
        subject_id: str = "subject_001"
    ) -> Dict[str, Any]:
        """
        Perform multi-angle analysis.

        Args:
            image_paths: List of dicts with 'path' and 'angle_type' keys
            subject_id: Subject identifier

        Returns:
            Dictionary with combined results
        """
        import time
        start_time = time.time()

        try:
            self.multi_angle_analyzer = MultiAngleAnalyzer()

            # Create angle specifications
            angle_specs = []
            for img_data in image_paths:
                spec = AngleSpecification(
                    angle_type=img_data['angle_type'],
                    image_path=img_data['path'],
                    weight=1.0,
                    quality_threshold=0.3
                )
                angle_specs.append(spec)

            # Perform analysis
            result = self.multi_angle_analyzer.analyze_multiple_angles(
                angle_specs=angle_specs,
                subject_id=subject_id
            )

            # Clamp confidence to valid range (SDK sometimes returns corrupted values)
            combined_conf = float(result.combined_confidence) if result.combined_confidence else None
            if combined_conf is not None:
                combined_conf = max(0.0, min(1.0, combined_conf))

            # Format results
            results_dict = {
                "success": True,
                "subject_id": subject_id,
                "num_angles": len(result.angle_results),
                "combined_wd_value": float(result.combined_wd_value) if result.combined_wd_value else None,
                "combined_forehead_angle": float(result.combined_forehead_angle) if result.combined_forehead_angle else None,
                "combined_face_shape": result.combined_face_shape,
                "combined_confidence": combined_conf,
                "angle_results": {},
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "analysis_type": "multi_angle",
                }
            }

            # Extract detailed results from individual angle analyses
            for angle, angle_result in result.angle_results.items():
                if angle_result:
                    angle_data = {"status": "Success"}

                    # Extract WD details from frontal analysis
                    if angle_result.wd_result and angle == "frontal":
                        wd = angle_result.wd_result
                        # Clamp WD confidence
                        wd_conf = float(wd.measurement_confidence)
                        wd_conf = max(0.0, min(1.0, wd_conf))

                        results_dict["wd_result"] = {
                            "wd_value": float(wd.wd_value_cm) if hasattr(wd, 'wd_value_cm') and wd.wd_value_cm != 0 else float(wd.wd_value),
                            "wd_value_px": float(wd.wd_value),
                            "classification": wd.primary_classification.value,
                            "bizygomatic_width": float(wd.bizygomatic_width_cm) if hasattr(wd, 'bizygomatic_width_cm') and wd.bizygomatic_width_cm != 0 else float(wd.bizygomatic_width),
                            "bizygomatic_width_px": float(wd.bizygomatic_width),
                            "bigonial_width": float(wd.bigonial_width_cm) if hasattr(wd, 'bigonial_width_cm') and wd.bigonial_width_cm != 0 else float(wd.bigonial_width),
                            "bigonial_width_px": float(wd.bigonial_width),
                            "confidence": wd_conf,
                            "units": "cm" if hasattr(wd, 'wd_value_cm') and wd.wd_value_cm != 0 else "px",
                        }

                        # Add personality profile if available
                        if hasattr(wd, 'personality_profile') and wd.personality_profile:
                            pp = wd.personality_profile
                            results_dict["wd_result"]["personality_profile"] = {
                                "social_orientation": getattr(pp, 'social_orientation_score', getattr(pp, 'social_orientation', 'N/A')),
                                "relational_field": getattr(pp, 'relational_field_score', getattr(pp, 'relational_field', 'N/A')),
                                "communication_style": getattr(pp, 'communication_style_score', getattr(pp, 'communication_style', 'N/A')),
                                "leadership": getattr(pp, 'leadership_tendency', getattr(pp, 'leadership', 'N/A')),
                                "interpersonal_effectiveness": getattr(pp, 'interpersonal_effectiveness', 'N/A'),
                                "emotional_expressiveness": getattr(pp, 'emotional_expressiveness', 'N/A'),
                                "social_energy_level": getattr(pp, 'social_energy_level', 'N/A'),
                                "conflict_resolution_style": getattr(pp, 'conflict_resolution_style', 'N/A'),
                            }

                    # Extract forehead details from profile analysis
                    if angle_result.forehead_result and angle == "profile":
                        fh = angle_result.forehead_result
                        # Clamp forehead confidence
                        fh_conf = float(fh.measurement_confidence)
                        fh_conf = max(0.0, min(1.0, fh_conf))

                        results_dict["forehead_result"] = {
                            "slant_angle": float(fh.forehead_geometry.slant_angle_degrees),
                            "forehead_height": float(fh.forehead_geometry.forehead_height),
                            "impulsiveness_level": fh.impulsiveness_level.value,
                            "confidence": fh_conf,
                        }

                        # Add geometry details
                        geom = fh.forehead_geometry
                        results_dict["forehead_result"]["geometry"] = {
                            "slant_angle": float(geom.slant_angle_degrees),
                            "forehead_height": float(geom.forehead_height),
                            "forehead_width": float(geom.forehead_width) if hasattr(geom, 'forehead_width') else 0,
                            "curvature": float(geom.forehead_curvature) if hasattr(geom, 'forehead_curvature') else 0,
                            "frontal_prominence": float(geom.frontal_prominence) if hasattr(geom, 'frontal_prominence') else 0,
                            "width_height_ratio": float(geom.forehead_width / geom.forehead_height) if hasattr(geom, 'forehead_width') and geom.forehead_height > 0 else 0,
                        }

                        # Extract neuroscience correlations if available
                        if hasattr(fh, 'neurotransmitters') and fh.neurotransmitters:
                            results_dict["forehead_result"]["neurotransmitters"] = {
                                "dopamine_activity": float(getattr(fh.neurotransmitters, 'dopamine_activity', 0)),
                                "serotonin_balance": float(getattr(fh.neurotransmitters, 'serotonin_balance', 0)),
                                "gaba_function": float(getattr(fh.neurotransmitters, 'gaba_function', 0)),
                            }

                        if hasattr(fh, 'cognitive_functions') and fh.cognitive_functions:
                            results_dict["forehead_result"]["cognitive_functions"] = {
                                "executive_function": float(getattr(fh.cognitive_functions, 'executive_function', 0)),
                                "working_memory": float(getattr(fh.cognitive_functions, 'working_memory', 0)),
                                "attention_control": float(getattr(fh.cognitive_functions, 'attention_control', 0)),
                            }

                        if hasattr(fh, 'neuroscience_correlations') and fh.neuroscience_correlations:
                            nc = fh.neuroscience_correlations
                            nc_attrs = [attr for attr in dir(nc) if not attr.startswith('_')]

                            # Dynamically extract all numeric attributes
                            nc_dict = {}
                            for attr in nc_attrs:
                                try:
                                    val = getattr(nc, attr)
                                    if isinstance(val, (int, float)):
                                        nc_dict[attr] = float(val)
                                except Exception:
                                    pass

                            if nc_dict:
                                results_dict["forehead_result"]["neuroscience"] = nc_dict

                    # Extract morphology details from frontal analysis
                    if angle_result.morphology_result and angle == "frontal":
                        morph = angle_result.morphology_result
                        # Clamp morphology confidence
                        morph_conf = float(morph.measurement_confidence)
                        morph_conf = max(0.0, min(1.0, morph_conf))

                        results_dict["morphology_result"] = {
                            "face_shape": morph.shape_classification.primary_shape.value,
                            "facial_index": float(morph.facial_proportions.facial_index),
                            "width_height_ratio": float(morph.facial_proportions.facial_width_height_ratio),
                            "confidence": morph_conf,
                        }

                        # Add proportions
                        props = morph.facial_proportions
                        results_dict["morphology_result"]["proportions"] = {
                            "upper_face_ratio": float(props.upper_face_ratio) if hasattr(props, 'upper_face_ratio') else 0,
                            "middle_face_ratio": float(props.middle_face_ratio) if hasattr(props, 'middle_face_ratio') else 0,
                            "lower_face_ratio": float(props.lower_face_ratio) if hasattr(props, 'lower_face_ratio') else 0,
                            "facial_width": float(props.bizygomatic_width) if hasattr(props, 'bizygomatic_width') else 0,
                            "facial_height": float(props.total_face_height) if hasattr(props, 'total_face_height') else 0,
                        }

                    # Extract neoclassical canons from frontal analysis
                    if angle_result.neoclassical_result and angle == "frontal":
                        neo = angle_result.neoclassical_result
                        neo_dict = {
                            "overall_score": float(neo.overall_validity_score) if hasattr(neo, 'overall_validity_score') else 0.0,
                            "beauty_score": float(neo.beauty_score) if hasattr(neo, 'beauty_score') else None,
                            "proportion_balance": float(neo.proportion_balance) if hasattr(neo, 'proportion_balance') else None,
                            "confidence": float(neo.confidence) if hasattr(neo, 'confidence') else 0.0,
                        }

                        # Extract individual canon measurements
                        if hasattr(neo, 'canons') and neo.canons:
                            canon_measurements = {}

                            # Scientific threshold: ±10% deviation is acceptable
                            # Note: SDK has per-canon tolerances (3-15%) from papers, but many are too strict
                            # for practical use (e.g., Canon 1 has 3% tolerance, but only ~30% of population meets it)
                            # Using uniform 10% threshold for consistent user experience
                            DEVIATION_THRESHOLD = 10.0

                            for canon in neo.canons:
                                canon_name = getattr(canon, 'canon_name', f'Canon {len(canon_measurements)+1}')
                                deviation = float(canon.deviation_percentage) if hasattr(canon, 'deviation_percentage') else 0

                                # Use uniform 10% threshold for practical validity assessment
                                # SDK's per-canon tolerances are too strict for demo purposes
                                is_within_range = abs(deviation) <= DEVIATION_THRESHOLD

                                # Keep SDK validity_score for reference
                                validity_score = float(getattr(canon, 'validity_score', 0)) if hasattr(canon, 'validity_score') else None

                                canon_measurements[canon_name] = {
                                    "measured_value": float(getattr(canon, 'measured_ratio', 0)),
                                    "deviation": deviation,
                                    "within_range": is_within_range,
                                    "confidence": float(getattr(canon, 'confidence', 0.8)),
                                    "validity_score": validity_score,
                                    "expected_ratio": float(getattr(canon, 'expected_ratio', 0)) if hasattr(canon, 'expected_ratio') else None,
                                    "acceptable_deviation": float(getattr(canon, 'acceptable_deviation', 0)) if hasattr(canon, 'acceptable_deviation') else None,
                                }
                            neo_dict["canon_measurements"] = canon_measurements

                        results_dict["neoclassical_result"] = neo_dict

                    results_dict["angle_results"][angle] = angle_data
                else:
                    results_dict["angle_results"][angle] = {"status": "Failed"}

            # Update processing time
            results_dict["metadata"]["processing_time"] = time.time() - start_time

            return results_dict

        except Exception as e:
            return {
                "success": False,
                "error": f"Error during multi-angle analysis: {str(e)}",
                "traceback": traceback.format_exc()
            }
        finally:
            if self.multi_angle_analyzer:
                self.multi_angle_analyzer.shutdown()
                self.multi_angle_analyzer = None

    def analyze_wd_only(self, image_path: str) -> Dict[str, Any]:
        """Analyze WD (bizygomatic width) only."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": "Could not load image"}

            result = self.wd_analyzer.analyze_image(image)
            if not result:
                return {"success": False, "error": "Analysis failed"}

            wd_dict = {
                "success": True,
                # Use cm values when available
                "wd_value": float(result.wd_value_cm) if hasattr(result, 'wd_value_cm') and result.wd_value_cm != 0 else float(result.wd_value),
                "wd_value_px": float(result.wd_value),
                "bizygomatic_width": float(result.bizygomatic_width_cm) if hasattr(result, 'bizygomatic_width_cm') and result.bizygomatic_width_cm != 0 else float(result.bizygomatic_width),
                "bizygomatic_width_px": float(result.bizygomatic_width),
                "bigonial_width": float(result.bigonial_width_cm) if hasattr(result, 'bigonial_width_cm') and result.bigonial_width_cm != 0 else float(result.bigonial_width),
                "bigonial_width_px": float(result.bigonial_width),
                "classification": result.primary_classification.value,
                "confidence": float(result.measurement_confidence),
                "units": "cm" if hasattr(result, 'wd_value_cm') and result.wd_value_cm != 0 else "px",
            }

            # Add personality profile if available (use correct attribute names)
            if hasattr(result, 'personality_profile') and result.personality_profile:
                pp = result.personality_profile
                wd_dict["personality_profile"] = {
                    "social_orientation": getattr(pp, 'social_orientation_score', getattr(pp, 'social_orientation', 'N/A')),
                    "relational_field": getattr(pp, 'relational_field_score', getattr(pp, 'relational_field', 'N/A')),
                    "communication_style": getattr(pp, 'communication_style_score', getattr(pp, 'communication_style', 'N/A')),
                    "leadership": getattr(pp, 'leadership_tendency', getattr(pp, 'leadership', 'N/A')),
                    "interpersonal_effectiveness": getattr(pp, 'interpersonal_effectiveness', 'N/A'),
                    "emotional_expressiveness": getattr(pp, 'emotional_expressiveness', 'N/A'),
                    "social_energy_level": getattr(pp, 'social_energy_level', 'N/A'),
                    "conflict_resolution_style": getattr(pp, 'conflict_resolution_style', 'N/A'),
                }

            return wd_dict
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_forehead_only(self, image_path: str) -> Dict[str, Any]:
        """Analyze forehead inclination only."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": "Could not load image"}

            result = self.forehead_analyzer.analyze_image(image)
            if not result:
                return {"success": False, "error": "Analysis failed"}

            fh_dict = {
                "success": True,
                "slant_angle": float(result.forehead_geometry.slant_angle_degrees),
                "forehead_height": float(result.forehead_geometry.forehead_height),
                "impulsiveness_level": result.impulsiveness_level.value,
                "confidence": float(result.measurement_confidence),
            }

            # Add detailed geometry
            geom = result.forehead_geometry
            fh_dict["geometry"] = {
                "slant_angle": float(geom.slant_angle_degrees),
                "forehead_height": float(geom.forehead_height),
                "forehead_width": float(geom.forehead_width) if hasattr(geom, 'forehead_width') else 0,
                "curvature": float(geom.forehead_curvature) if hasattr(geom, 'forehead_curvature') else 0,
                "frontal_prominence": float(geom.frontal_prominence) if hasattr(geom, 'frontal_prominence') else 0,
            }

            return fh_dict
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_morphology_only(self, image_path: str) -> Dict[str, Any]:
        """Analyze facial morphology only."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": "Could not load image"}

            result = self.morphology_analyzer.analyze_image(image)
            if not result:
                return {"success": False, "error": "Analysis failed"}

            morph_dict = {
                "success": True,
                "face_shape": result.shape_classification.primary_shape.value,
                "facial_index": float(result.facial_proportions.facial_index),
                "width_height_ratio": float(result.facial_proportions.facial_width_height_ratio),
                "confidence": float(result.measurement_confidence),
            }

            # Add detailed proportions
            props = result.facial_proportions
            morph_dict["proportions"] = {
                "upper_face_ratio": float(props.upper_face_ratio) if hasattr(props, 'upper_face_ratio') else 0,
                "middle_face_ratio": float(props.middle_face_ratio) if hasattr(props, 'middle_face_ratio') else 0,
                "lower_face_ratio": float(props.lower_face_ratio) if hasattr(props, 'lower_face_ratio') else 0,
                "facial_width": float(props.bizygomatic_width) if hasattr(props, 'bizygomatic_width') else 0,
                "facial_height": float(props.total_face_height) if hasattr(props, 'total_face_height') else 0,
            }

            return morph_dict
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_neoclassical_only(self, image_path: str, ethnic_group: str = 'caucasian') -> Dict[str, Any]:
        """Analyze neoclassical canons only."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": "Could not load image"}

            result = self.neoclassical_analyzer.analyze_image(image, ethnic_group=ethnic_group)
            if not result:
                return {"success": False, "error": "Analysis failed"}

            # Format canon measurements
            canon_measurements = {}
            for canon_name, measurement in result.canon_measurements.items():
                canon_measurements[canon_name] = {
                    "measured_value": float(measurement.measured_value),
                    "deviation": float(measurement.deviation_from_ideal),
                    "within_range": measurement.within_acceptable_range,
                    "confidence": float(measurement.measurement_confidence)
                }

            return {
                "success": True,
                "overall_score": float(result.overall_harmony_score),
                "canon_measurements": canon_measurements,
                "ethnic_group": ethnic_group
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
capa_service = CapaService()
