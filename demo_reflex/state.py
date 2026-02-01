"""
State Module
Application state management for CAPA Demo.
"""

import reflex as rx
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import asyncio
import plotly.graph_objects as go

from .capa_service import capa_service
from .plotly_charts import (
    create_personality_radar, create_demographic_gauge,
    create_impulsivity_radar, create_neuroscience_bar,
    create_face_shape_donut, create_proportions_bar,
    create_canon_deviation_bar, create_harmony_gauge,
    create_confidence_dashboard,
)


class LanguageState(rx.State):
    """State for language management."""
    language: str = "en"

    @rx.var
    def is_english(self) -> bool:
        """Check if current language is English."""
        return self.language == "en"

    @rx.var
    def is_spanish(self) -> bool:
        """Check if current language is Spanish."""
        return self.language == "es"

    def set_english(self):
        """Set language to English."""
        self.language = "en"

    def set_spanish(self):
        """Set language to Spanish."""
        self.language = "es"


class DocsState(rx.State):
    """State for documentation navigation."""
    active_section: str = "intro"

    def set_section(self, section: str):
        """Set the active documentation section."""
        self.active_section = section

    @rx.var
    def is_intro(self) -> bool:
        return self.active_section == "intro"

    @rx.var
    def is_getting_started(self) -> bool:
        return self.active_section == "getting_started"

    @rx.var
    def is_quick_start(self) -> bool:
        return self.active_section == "quick_start"

    @rx.var
    def is_api_core(self) -> bool:
        return self.active_section == "api_core"

    @rx.var
    def is_api_config(self) -> bool:
        return self.active_section == "api_config"

    @rx.var
    def is_api_results(self) -> bool:
        return self.active_section == "api_results"

    @rx.var
    def is_api_modules(self) -> bool:
        return self.active_section == "api_modules"

    @rx.var
    def is_configuration(self) -> bool:
        return self.active_section == "configuration"

    @rx.var
    def is_examples(self) -> bool:
        return self.active_section == "examples"

    @rx.var
    def is_scientific(self) -> bool:
        return self.active_section == "scientific"

    @rx.var
    def is_papers(self) -> bool:
        return self.active_section == "papers"


class AppState(rx.State):
    """Base application state."""
    pass


class DemoState(rx.State):
    """State for the new demo page with frontal and profile image uploads."""

    # Frontal image (required)
    frontal_image: str = ""  # Base64 data URI for preview
    frontal_image_path: str = ""  # File path for analysis

    # Profile image (optional)
    profile_image: str = ""  # Base64 data URI for preview
    profile_image_path: str = ""  # File path for analysis

    # Processing state
    is_processing: bool = False
    error_message: str = ""
    results: Dict[str, Any] = {}

    # Analysis configuration
    analysis_mode: str = "THOROUGH"

    @rx.var
    def has_frontal(self) -> bool:
        """Check if frontal image has been uploaded."""
        return bool(self.frontal_image)

    @rx.var
    def has_profile(self) -> bool:
        """Check if profile image has been uploaded."""
        return bool(self.profile_image)

    @rx.var
    def can_analyze(self) -> bool:
        """Check if ready to analyze (need frontal image and not processing)."""
        return bool(self.frontal_image_path) and not self.is_processing

    @rx.var
    def has_results(self) -> bool:
        """Check if analysis results are available."""
        return bool(self.results)

    async def handle_frontal_upload(self, files: List[rx.UploadFile]):
        """Handle frontal image upload."""
        if not files:
            return

        try:
            file = files[0]
            upload_data = await file.read()

            # Save to temp location
            temp_dir = Path("./uploaded_images")
            temp_dir.mkdir(exist_ok=True)

            # Create base64 preview
            import base64
            ext = file.filename.split(".")[-1].lower()
            mime_type = "jpeg" if ext in ["jpg", "jpeg"] else ext
            img_data_uri = f"data:image/{mime_type};base64,{base64.b64encode(upload_data).decode()}"

            # Save file
            image_path = temp_dir / f"demo_frontal_{file.filename}"
            with open(image_path, "wb") as f:
                f.write(upload_data)

            self.frontal_image = img_data_uri
            self.frontal_image_path = str(image_path)
            self.error_message = ""

            print(f"[DEBUG] Demo frontal upload saved: {image_path}")

        except Exception as e:
            self.error_message = f"Failed to upload frontal image: {str(e)}"
            print(f"[ERROR] Frontal upload failed: {e}")

    async def handle_profile_upload(self, files: List[rx.UploadFile]):
        """Handle profile image upload."""
        if not files:
            return

        try:
            file = files[0]
            upload_data = await file.read()

            # Save to temp location
            temp_dir = Path("./uploaded_images")
            temp_dir.mkdir(exist_ok=True)

            # Create base64 preview
            import base64
            ext = file.filename.split(".")[-1].lower()
            mime_type = "jpeg" if ext in ["jpg", "jpeg"] else ext
            img_data_uri = f"data:image/{mime_type};base64,{base64.b64encode(upload_data).decode()}"

            # Save file
            image_path = temp_dir / f"demo_profile_{file.filename}"
            with open(image_path, "wb") as f:
                f.write(upload_data)

            self.profile_image = img_data_uri
            self.profile_image_path = str(image_path)
            self.error_message = ""

            print(f"[DEBUG] Demo profile upload saved: {image_path}")

        except Exception as e:
            self.error_message = f"Failed to upload profile image: {str(e)}"
            print(f"[ERROR] Profile upload failed: {e}")

    def clear_frontal(self):
        """Clear frontal image."""
        self.frontal_image = ""
        self.frontal_image_path = ""

    def clear_profile(self):
        """Clear profile image."""
        self.profile_image = ""
        self.profile_image_path = ""

    def clear_all(self):
        """Reset all state."""
        self.frontal_image = ""
        self.frontal_image_path = ""
        self.profile_image = ""
        self.profile_image_path = ""
        self.is_processing = False
        self.error_message = ""
        self.results = {}

    async def analyze(self):
        """Run analysis on uploaded images."""
        if not self.frontal_image_path:
            self.error_message = "Please upload a frontal image first"
            return

        self.is_processing = True
        self.error_message = ""
        self.results = {}
        yield  # Ensure UI updates immediately to show processing state

        try:
            # Use multi-angle if profile is available
            if self.profile_image_path:
                print(f"[DEBUG] Starting multi-angle analysis...")
                # Build image_paths list for multi-angle analysis
                image_paths = [
                    {"path": self.frontal_image_path, "angle_type": "frontal"},
                    {"path": self.profile_image_path, "angle_type": "profile"},
                ]
                # Run in thread to avoid blocking
                result = await asyncio.to_thread(
                    capa_service.analyze_multi_angle,
                    image_paths=image_paths,
                    subject_id="demo_subject",
                )
            else:
                print(f"[DEBUG] Starting single-image analysis...")
                # Single image analysis - run in thread to avoid blocking
                result = await asyncio.to_thread(
                    capa_service.analyze_single_image,
                    image_path=self.frontal_image_path,
                    mode=self.analysis_mode,
                )

            if result:
                self.results = result
                print(f"[DEBUG] Demo analysis complete: success={result.get('success')}")
            else:
                self.error_message = "Analysis returned no results"

        except Exception as e:
            self.error_message = f"Analysis failed: {str(e)}"
            print(f"[ERROR] Demo analysis failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_processing = False
            yield  # Ensure UI updates with final state

    # Result computed vars (reuse patterns from CaptureAnalysisState)
    @rx.var
    def overall_confidence(self) -> str:
        """Get overall confidence as formatted string."""
        if not self.results:
            return "N/A"
        # Check combined_confidence first (multi-angle)
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            # Clamp to valid range
            conf = max(0.0, min(1.0, conf))
            return f"{conf * 100:.1f}%"
        # Check metadata (single-image)
        if "metadata" in self.results:
            conf = self.results["metadata"].get("overall_confidence", 0)
            # Clamp to valid range
            conf = max(0.0, min(1.0, conf))
            return f"{conf * 100:.1f}%"
        return "N/A"

    @rx.var
    def processing_time(self) -> str:
        """Get processing time as formatted string."""
        if not self.results:
            return "N/A"
        # Check metadata for processing time (available in both single and multi-angle)
        if "metadata" in self.results:
            time_val = self.results["metadata"].get("processing_time", 0)
            if time_val:
                return f"{time_val:.2f}s"
        return "N/A"

    @rx.var
    def is_multi_angle_result(self) -> bool:
        """Check if result is from multi-angle analysis."""
        return bool(self.results and "combined_confidence" in self.results)

    # ========== WD Analysis Computed Vars ==========
    @rx.var
    def has_wd_results(self) -> bool:
        """Check if WD results exist."""
        if not self.results:
            return False
        # Check for wd_result first (available in both single and enhanced multi-angle)
        if self.results.get("wd_result"):
            return True
        # Fallback to combined_wd_value for legacy multi-angle
        if "combined_wd_value" in self.results:
            return self.results.get("combined_wd_value") is not None
        return False

    @rx.var
    def wd_value(self) -> str:
        """Get WD value as formatted string with units."""
        if not self.results:
            return "N/A"
        # Check for wd_result first (available in both single and multi-angle)
        if self.results.get("wd_result"):
            val = self.results["wd_result"].get("wd_value", 0)
            units = self.results["wd_result"].get("units", "px")
            return f"{val:.3f} {units}"
        # Fallback to combined_wd_value (legacy multi-angle)
        if "combined_wd_value" in self.results:
            val = self.results.get("combined_wd_value")
            if val is not None:
                return f"{val:.3f} px"
            return "N/A"
        return "N/A"

    @rx.var
    def wd_classification(self) -> str:
        """Get WD classification."""
        if not self.results:
            return "N/A"
        # Use SDK classification from wd_result (most accurate)
        if self.results.get("wd_result"):
            return self.results["wd_result"].get("classification", "N/A")
        # Fallback classification for legacy combined_wd_value (these are pixel values, use ratio-based classification)
        if "combined_wd_value" in self.results:
            # Since combined_wd_value is in pixels, we can't classify by cm thresholds
            # Return a generic classification based on sign
            val = self.results.get("combined_wd_value")
            if val is not None:
                if val > 0:
                    return "wider_jaw"  # bigonial > bizygomatic (unusual)
                else:
                    return "reserved"  # bigonial < bizygomatic (typical)
            return "N/A"
        return "N/A"

    @rx.var
    def wd_confidence(self) -> str:
        """Get WD confidence as formatted string."""
        if not self.results:
            return "N/A"
        # Use wd_result confidence first (most specific)
        if self.results.get("wd_result"):
            conf = self.results["wd_result"].get("confidence", 0)
            conf = max(0.0, min(1.0, conf))  # Clamp to valid range
            return f"{conf * 100:.1f}%"
        # Fallback to combined confidence
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            conf = max(0.0, min(1.0, conf))  # Clamp to valid range
            return f"{conf * 100:.1f}%"
        return "N/A"

    @rx.var
    def wd_confidence_value(self) -> float:
        """Get WD confidence as float (clamped to 0-1 range)."""
        if not self.results:
            return 0.0
        # Use wd_result confidence first (most specific)
        if self.results.get("wd_result"):
            conf = self.results["wd_result"].get("confidence", 0)
            return max(0.0, min(1.0, conf))
        # Fallback to combined confidence
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            return max(0.0, min(1.0, conf))
        return 0.0

    @rx.var
    def wd_bizygomatic(self) -> str:
        """Get bizygomatic width with units."""
        if not self.results:
            return "N/A"
        if self.results.get("wd_result"):
            val = self.results["wd_result"].get("bizygomatic_width", 0)
            units = self.results["wd_result"].get("units", "px")
            if val:
                return f"{val:.2f} {units}"
        return "N/A"

    @rx.var
    def wd_bigonial(self) -> str:
        """Get bigonial width with units."""
        if not self.results:
            return "N/A"
        if self.results.get("wd_result"):
            val = self.results["wd_result"].get("bigonial_width", 0)
            units = self.results["wd_result"].get("units", "px")
            if val:
                return f"{val:.2f} {units}"
        return "N/A"

    def _format_trait_value(self, value) -> str:
        """Format a personality trait value for display."""
        if value is None or value == "N/A":
            return "N/A"
        if isinstance(value, (int, float)):
            if value >= 0.8:
                return "Very High"
            elif value >= 0.6:
                return "High"
            elif value >= 0.4:
                return "Moderate"
            elif value >= 0.2:
                return "Low"
            else:
                return "Very Low"
        return str(value)

    @rx.var
    def personality_traits(self) -> List[Dict[str, Any]]:
        """Get personality traits as list with formatted values."""
        if not self.results:
            return []
        # Check for wd_result with personality_profile (available in both single and enhanced multi-angle)
        if self.results.get("wd_result"):
            profile = self.results["wd_result"].get("personality_profile", {})
            if profile:
                return [
                    {"trait": "Social Orientation", "value": self._format_trait_value(profile.get("social_orientation", "N/A"))},
                    {"trait": "Relational Field", "value": self._format_trait_value(profile.get("relational_field", "N/A"))},
                    {"trait": "Communication Style", "value": self._format_trait_value(profile.get("communication_style", "N/A"))},
                    {"trait": "Leadership", "value": self._format_trait_value(profile.get("leadership", "N/A"))},
                    {"trait": "Interpersonal Effectiveness", "value": self._format_trait_value(profile.get("interpersonal_effectiveness", "N/A"))},
                    {"trait": "Emotional Expressiveness", "value": self._format_trait_value(profile.get("emotional_expressiveness", "N/A"))},
                    {"trait": "Social Energy Level", "value": self._format_trait_value(profile.get("social_energy_level", "N/A"))},
                    {"trait": "Conflict Resolution", "value": self._format_trait_value(profile.get("conflict_resolution_style", "N/A"))},
                ]
            # If no profile, generate basic traits from classification
            classification = self.results["wd_result"].get("classification", "")
            if classification:
                if classification in ["highly_social", "moderately_social"]:
                    orientation = "High"
                elif classification in ["balanced", "balanced_social"]:
                    orientation = "Moderate"
                else:
                    orientation = "Low"
                return [
                    {"trait": "Social Orientation", "value": orientation},
                    {"trait": "Classification", "value": classification.replace("_", " ").title()},
                ]
        return []

    # ========== Forehead Analysis Computed Vars ==========
    @rx.var
    def has_forehead_results(self) -> bool:
        """Check if forehead results exist (requires profile image)."""
        if not self.results:
            return False
        # Check for forehead_result first (available in both single and enhanced multi-angle)
        if self.results.get("forehead_result"):
            return True
        # Fallback to combined_forehead_angle for legacy multi-angle
        if "combined_forehead_angle" in self.results:
            return self.results.get("combined_forehead_angle") is not None
        return False

    @rx.var
    def forehead_angle(self) -> str:
        """Get forehead slant angle."""
        if not self.results:
            return "N/A"
        # Check forehead_result first
        if self.results.get("forehead_result"):
            angle = self.results["forehead_result"].get("slant_angle", 0)
            if angle:
                return f"{angle:.1f}°"
        # Fallback to combined_forehead_angle
        if "combined_forehead_angle" in self.results:
            angle = self.results.get("combined_forehead_angle")
            if angle is not None:
                return f"{angle:.1f}°"
        return "N/A"

    @rx.var
    def forehead_impulsiveness(self) -> str:
        """Get impulsiveness level derived from forehead angle."""
        if not self.results:
            return "N/A"
        # Check forehead_result first (has direct impulsiveness_level)
        if self.results.get("forehead_result"):
            level = self.results["forehead_result"].get("impulsiveness_level")
            if level:
                return level
        # Fallback: derive from combined_forehead_angle
        if "combined_forehead_angle" in self.results:
            angle = self.results.get("combined_forehead_angle")
            if angle is not None:
                if angle < 10:
                    return "very_low"
                elif angle < 15:
                    return "low"
                elif angle < 25:
                    return "moderate"
                elif angle < 35:
                    return "high"
                else:
                    return "very_high"
        return "N/A"

    @rx.var
    def forehead_confidence(self) -> str:
        """Get forehead confidence as formatted string."""
        if not self.results:
            return "N/A"
        # Check forehead_result first (most specific)
        if self.results.get("forehead_result"):
            conf = self.results["forehead_result"].get("confidence", 0)
            conf = max(0.0, min(1.0, conf))  # Clamp to valid range
            return f"{conf * 100:.1f}%"
        # Fallback to combined confidence
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            conf = max(0.0, min(1.0, conf))  # Clamp to valid range
            return f"{conf * 100:.1f}%"
        return "N/A"

    @rx.var
    def forehead_confidence_value(self) -> float:
        """Get forehead confidence as float (clamped to 0-1 range)."""
        if not self.results:
            return 0.0
        # Check forehead_result first (most specific)
        if self.results.get("forehead_result"):
            conf = self.results["forehead_result"].get("confidence", 0)
            return max(0.0, min(1.0, conf))
        # Fallback to combined confidence
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            return max(0.0, min(1.0, conf))
        return 0.0

    @rx.var
    def forehead_height(self) -> str:
        """Get forehead height."""
        if self.results and self.results.get("forehead_result"):
            height = self.results["forehead_result"].get("forehead_height", 0)
            return f"{height:.1f}px"
        return "N/A"

    @rx.var
    def forehead_geometry_details(self) -> List[Dict[str, str]]:
        """Get detailed forehead geometry."""
        if self.results and self.results.get("forehead_result"):
            geom = self.results["forehead_result"].get("geometry", {})
            if geom:
                return [
                    {"metric": "Slant Angle", "value": f"{geom.get('slant_angle', 0):.1f}°"},
                    {"metric": "Forehead Height", "value": f"{geom.get('forehead_height', 0):.1f} px"},
                    {"metric": "Forehead Width", "value": f"{geom.get('forehead_width', 0):.1f} px"},
                    {"metric": "Curvature Index", "value": f"{geom.get('curvature', 0):.3f}"},
                    {"metric": "Frontal Prominence Index", "value": f"{geom.get('frontal_prominence', 0):.3f}"},
                    {"metric": "Width/Height Ratio", "value": f"{geom.get('width_height_ratio', 0):.2f}"},
                ]
        return []

    # ========== Morphology Analysis Computed Vars ==========
    @rx.var
    def has_morphology_results(self) -> bool:
        """Check if morphology results exist."""
        if not self.results:
            return False
        # Check for morphology_result first (available in both single and enhanced multi-angle)
        if self.results.get("morphology_result"):
            return True
        # Fallback to combined_face_shape for legacy multi-angle
        if "combined_face_shape" in self.results:
            return bool(self.results.get("combined_face_shape"))
        return False

    @rx.var
    def morphology_shape(self) -> str:
        """Get face shape."""
        if not self.results:
            return "N/A"
        # Check morphology_result first
        if self.results.get("morphology_result"):
            shape = self.results["morphology_result"].get("face_shape")
            if shape:
                return shape
        # Fallback to combined_face_shape
        if "combined_face_shape" in self.results:
            shape = self.results.get("combined_face_shape")
            return shape if shape else "N/A"
        return "N/A"

    @rx.var
    def morphology_index(self) -> str:
        """Get facial index."""
        if not self.results:
            return "N/A"
        if self.results.get("morphology_result"):
            index = self.results["morphology_result"].get("facial_index", 0)
            if index:
                return f"{index:.1f}"
        return "N/A"

    @rx.var
    def morphology_ratio(self) -> str:
        """Get width/height ratio."""
        if not self.results:
            return "N/A"
        if self.results.get("morphology_result"):
            ratio = self.results["morphology_result"].get("width_height_ratio", 0)
            if ratio:
                return f"{ratio:.3f}"
        return "N/A"

    @rx.var
    def morphology_confidence(self) -> str:
        """Get morphology confidence as formatted string."""
        if not self.results:
            return "N/A"
        # Check morphology_result first (most specific)
        if self.results.get("morphology_result"):
            conf = self.results["morphology_result"].get("confidence", 0)
            conf = max(0.0, min(1.0, conf))  # Clamp to valid range
            return f"{conf * 100:.1f}%"
        # Fallback to combined confidence
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            conf = max(0.0, min(1.0, conf))  # Clamp to valid range
            return f"{conf * 100:.1f}%"
        return "N/A"

    @rx.var
    def morphology_confidence_value(self) -> float:
        """Get morphology confidence as float (clamped to 0-1 range)."""
        if not self.results:
            return 0.0
        # Check morphology_result first (most specific)
        if self.results.get("morphology_result"):
            conf = self.results["morphology_result"].get("confidence", 0)
            return max(0.0, min(1.0, conf))
        # Fallback to combined confidence
        if "combined_confidence" in self.results:
            conf = self.results.get("combined_confidence", 0) or 0
            return max(0.0, min(1.0, conf))
        return 0.0

    @rx.var
    def morphology_proportions(self) -> List[Dict[str, str]]:
        """Get detailed facial proportions."""
        if self.results and self.results.get("morphology_result"):
            props = self.results["morphology_result"].get("proportions", {})
            if props:
                return [
                    {"metric": "Upper Face Ratio", "value": f"{props.get('upper_face_ratio', 0):.3f}"},
                    {"metric": "Middle Face Ratio", "value": f"{props.get('middle_face_ratio', 0):.3f}"},
                    {"metric": "Lower Face Ratio", "value": f"{props.get('lower_face_ratio', 0):.3f}"},
                    {"metric": "Facial Width", "value": f"{props.get('facial_width', 0):.1f}px"},
                    {"metric": "Facial Height", "value": f"{props.get('facial_height', 0):.1f}px"},
                    {"metric": "Facial Index", "value": f"{props.get('facial_index', 0):.1f}"},
                ]
        return []

    # ========== Neoclassical Canons Computed Vars ==========
    @rx.var
    def has_canons_results(self) -> bool:
        """Check if neoclassical canons results exist."""
        if not self.results:
            return False
        # Check for neoclassical_result (new structure) or canons_result (legacy)
        return bool(
            self.results.get("neoclassical_result") or
            self.results.get("canons_result") or
            self.results.get("canon_measurements")
        )

    @rx.var
    def canons_overall_score(self) -> str:
        """Get overall harmony score."""
        if not self.results:
            return "N/A"
        # Check neoclassical_result first (new structure)
        neo = self.results.get("neoclassical_result", {})
        if neo and "overall_score" in neo:
            return f"{neo['overall_score'] * 100:.1f}%"
        # Fallback to canons_result (legacy)
        canons = self.results.get("canons_result", {})
        if canons and "overall_score" in canons:
            return f"{canons['overall_score'] * 100:.1f}%"
        if "overall_score" in self.results:
            return f"{self.results['overall_score'] * 100:.1f}%"
        return "N/A"

    @rx.var
    def canons_overall_score_value(self) -> float:
        """Get overall score as float (clamped to 0-1 range)."""
        if not self.results:
            return 0.0
        # Check neoclassical_result first (new structure)
        neo = self.results.get("neoclassical_result", {})
        if neo and "overall_score" in neo:
            return max(0.0, min(1.0, neo["overall_score"]))
        # Fallback to canons_result (legacy)
        canons = self.results.get("canons_result", {})
        if canons and "overall_score" in canons:
            return max(0.0, min(1.0, canons["overall_score"]))
        if "overall_score" in self.results:
            return max(0.0, min(1.0, self.results["overall_score"]))
        return 0.0

    @rx.var
    def canon_measurements_list(self) -> List[Dict[str, Any]]:
        """Get canon measurements as formatted list."""
        if not self.results:
            return []
        # Check neoclassical_result first (new structure)
        neo = self.results.get("neoclassical_result", {})
        measurements = neo.get("canon_measurements", {}) if neo else {}
        # Fallback to canons_result (legacy)
        if not measurements:
            measurements = self.results.get("canons_result", {}).get("canon_measurements", {})
        if not measurements:
            measurements = self.results.get("canon_measurements", {})
        if measurements:
            result = []
            for canon_name, data in measurements.items():
                result.append({
                    "name": canon_name.replace("_", " ").title(),
                    "measured": f"{data.get('measured_value', 0):.3f}",
                    "deviation": f"{data.get('deviation', 0):.1f}%",
                    "in_range": data.get("within_range", False),
                    "confidence": f"{data.get('confidence', 0) * 100:.1f}%"
                })
            return result
        return []

    # ========== Analysis Status Computed Vars ==========
    @rx.var
    def analysis_success(self) -> bool:
        """Check if analysis was successful."""
        return bool(self.results and self.results.get("success", True))

    @rx.var
    def analysis_error(self) -> str:
        """Get analysis error message if any."""
        if self.results and "error" in self.results:
            return self.results["error"]
        return self.error_message

    @rx.var
    def num_angles_analyzed(self) -> int:
        """Get number of angles analyzed (for multi-angle)."""
        if self.results and "num_angles" in self.results:
            return self.results["num_angles"]
        return 1 if self.results else 0

    # ========== Chart Data Computed Vars for Plotly Visualizations ==========

    def _trait_to_numeric(self, value) -> float:
        """Convert trait text value to numeric 0-1 range."""
        if isinstance(value, (int, float)):
            return min(1.0, max(0.0, float(value)))
        trait_map = {
            "Very High": 0.9, "High": 0.7, "Moderate": 0.5,
            "Low": 0.3, "Very Low": 0.1, "N/A": 0.0
        }
        return trait_map.get(str(value), 0.5)

    @rx.var
    def personality_radar_data(self) -> List[Dict[str, Any]]:
        """Get personality profile data for radar chart (8 dimensions)."""
        if not self.results or not self.results.get("wd_result"):
            return []
        profile = self.results["wd_result"].get("personality_profile", {})
        if not profile:
            return []
        return [
            {"dimension": "Social Orientation", "value": self._trait_to_numeric(profile.get("social_orientation", 0.5))},
            {"dimension": "Relational Field", "value": self._trait_to_numeric(profile.get("relational_field", 0.5))},
            {"dimension": "Communication", "value": self._trait_to_numeric(profile.get("communication_style", 0.5))},
            {"dimension": "Leadership", "value": self._trait_to_numeric(profile.get("leadership", 0.5))},
            {"dimension": "Interpersonal", "value": self._trait_to_numeric(profile.get("interpersonal_effectiveness", 0.5))},
            {"dimension": "Emotional Expr.", "value": self._trait_to_numeric(profile.get("emotional_expressiveness", 0.5))},
            {"dimension": "Social Energy", "value": self._trait_to_numeric(profile.get("social_energy_level", 0.5))},
            {"dimension": "Conflict Res.", "value": self._trait_to_numeric(profile.get("conflict_resolution_style", 0.5))},
        ]

    @rx.var
    def demographic_percentile_value(self) -> float:
        """Get demographic percentile for gauge chart (0-100)."""
        if not self.results or not self.results.get("wd_result"):
            return 50.0
        wd = self.results["wd_result"]
        # Check for demographic_data first (new structure)
        demo_data = wd.get("demographic_data", {})
        if demo_data and "percentile" in demo_data:
            return float(demo_data["percentile"])
        # Fallback to direct demographic_percentile
        if "demographic_percentile" in wd and wd["demographic_percentile"] is not None:
            return float(wd["demographic_percentile"])
        return 50.0

    @rx.var
    def impulsivity_radar_data(self) -> List[Dict[str, Any]]:
        """Get impulsivity profile data for radar chart (8 dimensions BIS-11)."""
        if not self.results or not self.results.get("forehead_result"):
            return []
        fh = self.results["forehead_result"]
        # Check for impulsivity_profile (detailed BIS-11 dimensions)
        profile = fh.get("impulsivity_profile", {})
        if profile:
            return [
                {"dimension": "Motor", "value": float(profile.get("motor_impulsiveness", 0.5) or 0.5)},
                {"dimension": "Cognitive", "value": float(profile.get("cognitive_impulsiveness", 0.5) or 0.5)},
                {"dimension": "Non-Planning", "value": float(profile.get("non_planning_impulsiveness", 0.5) or 0.5)},
                {"dimension": "Attentional", "value": float(profile.get("attentional_impulsiveness", 0.5) or 0.5)},
                {"dimension": "Risk Taking", "value": float(profile.get("risk_taking_tendency", 0.5) or 0.5)},
                {"dimension": "Sensation Seek", "value": float(profile.get("sensation_seeking", 0.5) or 0.5)},
                {"dimension": "Behavioral Inh.", "value": float(profile.get("behavioral_inhibition", 0.5) or 0.5)},
                {"dimension": "Emotional Reg.", "value": float(profile.get("emotional_regulation", 0.5) or 0.5)},
            ]
        # Fallback: generate basic profile from impulsiveness_level
        level = fh.get("impulsiveness_level", "moderate")
        level_map = {"very_low": 0.1, "low": 0.3, "moderate": 0.5, "high": 0.7, "very_high": 0.9}
        base_val = level_map.get(str(level).lower(), 0.5)
        return [
            {"dimension": "Motor", "value": base_val},
            {"dimension": "Cognitive", "value": base_val * 0.9},
            {"dimension": "Non-Planning", "value": base_val * 1.1},
            {"dimension": "Attentional", "value": base_val * 0.95},
            {"dimension": "Risk Taking", "value": base_val},
            {"dimension": "Sensation Seek", "value": base_val * 1.05},
            {"dimension": "Behavioral Inh.", "value": 1.0 - base_val},
            {"dimension": "Emotional Reg.", "value": 1.0 - base_val * 0.8},
        ]

    @rx.var
    def neuroscience_bar_data(self) -> List[Dict[str, Any]]:
        """Get neuroscience correlations data for bar chart."""
        if not self.results or not self.results.get("forehead_result"):
            return []
        fh = self.results["forehead_result"]
        data = []

        # Get neuroscience data from the extracted results
        neuro = fh.get("neuroscience", {})
        if neuro:
            # Neurotransmitter activity (normalized 0-1 values)
            if neuro.get("dopamine_system_activity") is not None:
                data.append({"metric": "Dopamine Activity", "value": float(neuro["dopamine_system_activity"])})
            if neuro.get("serotonin_system_balance") is not None:
                data.append({"metric": "Serotonin Balance", "value": float(neuro["serotonin_system_balance"])})
            if neuro.get("gaba_system_function") is not None:
                data.append({"metric": "GABA Function", "value": float(neuro["gaba_system_function"])})

            # Cognitive function scores (normalized 0-1 values)
            if neuro.get("executive_function_score") is not None:
                data.append({"metric": "Executive Function", "value": float(neuro["executive_function_score"])})
            if neuro.get("working_memory_capacity") is not None:
                data.append({"metric": "Working Memory", "value": float(neuro["working_memory_capacity"])})
            if neuro.get("attention_control_score") is not None:
                data.append({"metric": "Attention Control", "value": float(neuro["attention_control_score"])})

        return data

    @rx.var
    def face_shape_probabilities(self) -> List[Dict[str, Any]]:
        """Get face shape probability distribution for donut chart."""
        if not self.results or not self.results.get("morphology_result"):
            return []
        morph = self.results["morphology_result"]
        # Check for shape_probabilities (detailed distribution)
        probs = morph.get("shape_probabilities", {})
        if probs:
            return [
                {"shape": shape, "probability": float(prob)}
                for shape, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)
            ]
        # Fallback: create single shape with high probability
        shape = morph.get("face_shape", "Unknown")
        confidence = morph.get("shape_confidence", morph.get("confidence", 0.7))
        return [
            {"shape": shape, "probability": float(confidence)},
            {"shape": "Other", "probability": 1.0 - float(confidence)},
        ]

    @rx.var
    def proportions_bar_data(self) -> List[Dict[str, Any]]:
        """Get facial proportions data for bar chart."""
        if not self.results or not self.results.get("morphology_result"):
            return []
        props = self.results["morphology_result"].get("proportions", {})
        if not props:
            return []
        return [
            {"proportion": "Upper Face", "value": float(props.get("upper_face_ratio", 0.33))},
            {"proportion": "Middle Face", "value": float(props.get("middle_face_ratio", 0.33))},
            {"proportion": "Lower Face", "value": float(props.get("lower_face_ratio", 0.33))},
        ]

    @rx.var
    def canon_deviations_data(self) -> List[Dict[str, Any]]:
        """Get canon deviations data for horizontal bar chart."""
        if not self.results:
            return []
        # Check neoclassical_result first (new structure)
        neo = self.results.get("neoclassical_result", {})
        measurements = neo.get("canon_measurements", {}) if neo else {}
        # Fallback to other structures
        if not measurements:
            measurements = self.results.get("canons_result", {}).get("canon_measurements", {})
        if not measurements:
            measurements = self.results.get("canon_measurements", {})
        if not measurements:
            return []
        return [
            {
                "name": canon_name.replace("_", " ").title(),
                "deviation": float(data.get("deviation", 0)),
                "in_range": data.get("within_range", False),
            }
            for canon_name, data in measurements.items()
        ]

    @rx.var
    def harmony_score_value(self) -> float:
        """Get harmony score for gauge chart (0-1)."""
        return self.canons_overall_score_value

    @rx.var
    def module_confidences(self) -> List[Dict[str, Any]]:
        """Get confidence values for each module (for dashboard)."""
        modules = []
        if self.results:
            # WD module
            if self.results.get("wd_result"):
                modules.append({
                    "module": "WD",
                    "confidence": self.wd_confidence_value,
                    "status": "active",
                })
            # Forehead module
            if self.results.get("forehead_result"):
                modules.append({
                    "module": "Forehead",
                    "confidence": self.forehead_confidence_value,
                    "status": "active",
                })
            # Morphology module
            if self.results.get("morphology_result"):
                modules.append({
                    "module": "Morphology",
                    "confidence": self.morphology_confidence_value,
                    "status": "active",
                })
            # Canons module
            if self.has_canons_results:
                modules.append({
                    "module": "Canons",
                    "confidence": self.canons_overall_score_value,
                    "status": "active",
                })
        return modules

    @rx.var
    def wd_evidence_level(self) -> str:
        """Get evidence level for WD analysis."""
        if self.results and self.results.get("wd_result"):
            return self.results["wd_result"].get("evidence_level", "validated")
        return "validated"

    @rx.var
    def forehead_evidence_level(self) -> str:
        """Get evidence level for forehead analysis."""
        if self.results and self.results.get("forehead_result"):
            return self.results["forehead_result"].get("evidence_level", "validated")
        return "validated"

    @rx.var
    def confidence_intervals_data(self) -> Dict[str, Any]:
        """Get confidence intervals for forehead measurements."""
        if not self.results or not self.results.get("forehead_result"):
            return {}
        return self.results["forehead_result"].get("confidence_intervals", {})

    # =========================================================================
    # Plotly Figure Objects (for rx.plotly)
    # =========================================================================

    @rx.var
    def personality_radar_figure(self) -> go.Figure:
        """Get Plotly figure for personality radar chart."""
        data = self.personality_radar_data
        if not data:
            return go.Figure()
        return create_personality_radar(data)

    @rx.var
    def demographic_gauge_figure(self) -> go.Figure:
        """Get Plotly figure for demographic gauge."""
        percentile = self.demographic_percentile_value
        return create_demographic_gauge(percentile)

    @rx.var
    def impulsivity_radar_figure(self) -> go.Figure:
        """Get Plotly figure for impulsivity radar chart."""
        data = self.impulsivity_radar_data
        if not data:
            return go.Figure()
        return create_impulsivity_radar(data)

    @rx.var
    def neuroscience_bar_figure(self) -> go.Figure:
        """Get Plotly figure for neuroscience bar chart."""
        data = self.neuroscience_bar_data
        return create_neuroscience_bar(data)

    @rx.var
    def face_shape_donut_figure(self) -> go.Figure:
        """Get Plotly figure for face shape donut chart."""
        data = self.face_shape_probabilities
        if not data:
            return go.Figure()
        return create_face_shape_donut(data)

    @rx.var
    def proportions_bar_figure(self) -> go.Figure:
        """Get Plotly figure for proportions bar chart."""
        data = self.proportions_bar_data
        if not data:
            return go.Figure()
        return create_proportions_bar(data)

    @rx.var
    def canon_deviation_bar_figure(self) -> go.Figure:
        """Get Plotly figure for canon deviation bar chart."""
        data = self.canon_deviations_data
        if not data:
            return go.Figure()
        return create_canon_deviation_bar(data)

    @rx.var
    def harmony_gauge_figure(self) -> go.Figure:
        """Get Plotly figure for harmony gauge."""
        score = self.canons_overall_score_value
        return create_harmony_gauge(score)

    @rx.var
    def confidence_dashboard_figure(self) -> go.Figure:
        """Get Plotly figure for confidence dashboard."""
        modules = self.module_confidences
        if not modules:
            return go.Figure()
        return create_confidence_dashboard(modules)

    # Export handler
    def export_results(self):
        """Export results to JSON."""
        if not self.results:
            return

        try:
            export_dir = Path("./exports")
            export_dir.mkdir(exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"demo_analysis_{timestamp}.json"
            filepath = export_dir / filename

            json_data = json.dumps(self.results, indent=2)

            with open(filepath, "w") as f:
                f.write(json_data)

            return rx.download(data=json_data, filename=filename)
        except Exception as e:
            print(f"[ERROR] Failed to export: {e}")
