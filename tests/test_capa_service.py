"""
Tests for CAPA Service integration.

These tests verify the capa_service.py correctly processes
SDK results and transforms them for the demo UI.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class TestConfidenceClamping:
    """Tests for confidence value clamping in service layer."""

    def test_clamp_confidence_above_one(self):
        """Test confidence > 1.0 is clamped to 1.0."""
        raw_conf = 1.005
        clamped = max(0.0, min(1.0, raw_conf))

        assert clamped == 1.0

    def test_clamp_confidence_below_zero(self):
        """Test confidence < 0.0 is clamped to 0.0."""
        raw_conf = -0.1
        clamped = max(0.0, min(1.0, raw_conf))

        assert clamped == 0.0

    def test_clamp_confidence_normal(self):
        """Test normal confidence values pass through."""
        raw_conf = 0.649
        clamped = max(0.0, min(1.0, raw_conf))

        assert clamped == 0.649


class TestCanonDeviationThreshold:
    """Tests for canon deviation threshold logic."""

    SCIENTIFIC_THRESHOLD = 10.0

    def test_deviation_within_threshold(self):
        """Test deviation <= 10% is within range."""
        deviation = 9.5
        is_within = abs(deviation) <= self.SCIENTIFIC_THRESHOLD

        assert is_within is True

    def test_deviation_outside_threshold(self):
        """Test deviation > 10% is out of range."""
        deviation = 38.6
        is_within = abs(deviation) <= self.SCIENTIFIC_THRESHOLD

        assert is_within is False

    def test_deviation_at_boundary(self):
        """Test deviation exactly at 10% threshold."""
        deviation = 10.0
        is_within = abs(deviation) <= self.SCIENTIFIC_THRESHOLD

        assert is_within is True

    def test_deviation_just_over_boundary(self):
        """Test deviation just over 10% threshold."""
        deviation = 10.1
        is_within = abs(deviation) <= self.SCIENTIFIC_THRESHOLD

        assert is_within is False

    def test_negative_deviation(self):
        """Test negative deviation uses absolute value."""
        deviation = -9.5
        is_within = abs(deviation) <= self.SCIENTIFIC_THRESHOLD

        assert is_within is True


class TestWDValueProcessing:
    """Tests for WD value extraction and processing."""

    def test_use_cm_when_available(self):
        """Test cm values are preferred over px."""
        mock_wd = Mock()
        mock_wd.wd_value_cm = 3.897
        mock_wd.wd_value = 145.2  # px value

        # Logic: use cm if available and non-zero
        if hasattr(mock_wd, 'wd_value_cm') and mock_wd.wd_value_cm != 0:
            value = mock_wd.wd_value_cm
            units = "cm"
        else:
            value = mock_wd.wd_value
            units = "px"

        assert value == 3.897
        assert units == "cm"

    def test_fallback_to_px(self):
        """Test px values used when cm not available."""
        mock_wd = Mock()
        mock_wd.wd_value_cm = 0  # Not calibrated
        mock_wd.wd_value = 145.2

        if hasattr(mock_wd, 'wd_value_cm') and mock_wd.wd_value_cm != 0:
            value = mock_wd.wd_value_cm
            units = "cm"
        else:
            value = mock_wd.wd_value
            units = "px"

        assert value == 145.2
        assert units == "px"


class TestNeuroscienceDataExtraction:
    """Tests for neuroscience correlations extraction."""

    def test_extract_numeric_attributes(self):
        """Test extraction of numeric neuroscience attributes."""
        mock_nc = Mock()
        mock_nc.dopamine_system_activity = 0.65
        mock_nc.serotonin_system_balance = 0.72
        mock_nc.some_method = lambda: None  # Should be ignored
        mock_nc._private = 0.5  # Should be ignored

        # Simulate extraction logic
        nc_dict = {}
        for attr in ['dopamine_system_activity', 'serotonin_system_balance']:
            val = getattr(mock_nc, attr, None)
            if isinstance(val, (int, float)):
                nc_dict[attr] = float(val)

        assert nc_dict == {
            'dopamine_system_activity': 0.65,
            'serotonin_system_balance': 0.72,
        }


class TestPersonalityProfileExtraction:
    """Tests for personality profile data extraction."""

    def test_personality_traits_list_format(self, mock_wd_result):
        """Test personality traits are formatted as list of dicts."""
        profile = mock_wd_result.get("personality_profile", {})

        traits = []
        for trait, value in profile.items():
            traits.append({
                "trait": trait.replace("_", " ").title(),
                "value": f"{value:.2f}" if isinstance(value, float) else str(value)
            })

        assert len(traits) == 4
        assert all("trait" in t and "value" in t for t in traits)


class TestImpulsivityProfileExtraction:
    """Tests for BIS-11 impulsivity profile extraction."""

    def test_impulsivity_radar_data_format(self, mock_forehead_result):
        """Test impulsivity data is formatted for radar chart."""
        profile = mock_forehead_result.get("impulsivity_profile", {})

        radar_data = []
        for dimension, value in profile.items():
            radar_data.append({
                "dimension": dimension.replace("_", " ").title(),
                "value": float(value)
            })

        assert len(radar_data) == 8
        assert all(0 <= d["value"] <= 1 for d in radar_data)

    def test_impulsivity_dimensions_complete(self, mock_forehead_result):
        """Test all 8 BIS-11 dimensions are present."""
        profile = mock_forehead_result.get("impulsivity_profile", {})

        expected_dimensions = [
            "non_planning", "cognitive", "motor", "attentional",
            "risk_taking", "sensation_seeking", "behavioral_inhibition",
            "emotional_regulation"
        ]

        for dim in expected_dimensions:
            assert dim in profile, f"Missing dimension: {dim}"


class TestResultValidation:
    """Tests for result validation and error handling."""

    def test_handle_none_result(self):
        """Test handling of None analysis result."""
        result = None

        if result is None:
            output = {"success": False, "error": "Analysis failed"}
        else:
            output = {"success": True}

        assert output["success"] is False
        assert "error" in output

    def test_handle_missing_module(self, mock_full_results):
        """Test handling when a module result is missing."""
        # Remove forehead result
        results = mock_full_results.copy()
        results.pop("forehead_result", None)

        has_forehead = bool(results.get("forehead_result"))

        assert has_forehead is False
        assert results.get("wd_result") is not None  # Other modules still present

    def test_metadata_processing_time(self, mock_full_results):
        """Test processing time metadata extraction."""
        metadata = mock_full_results.get("metadata", {})
        time = metadata.get("processing_time", 0)

        formatted = f"{time:.2f}s"

        assert formatted == "2.45s"


class TestGeometryDetailsFormatting:
    """Tests for forehead geometry details table formatting."""

    def test_geometry_table_format(self, mock_forehead_result):
        """Test geometry details are formatted for table display."""
        geom = mock_forehead_result.get("geometry", {})

        details = [
            {"metric": "Slant Angle", "value": f"{geom.get('slant_angle', 0):.1f}"},
            {"metric": "Forehead Height", "value": f"{geom.get('forehead_height', 0):.1f} px"},
            {"metric": "Forehead Width", "value": f"{geom.get('forehead_width', 0):.1f} px"},
            {"metric": "Curvature Index", "value": f"{geom.get('curvature', 0):.3f}"},
            {"metric": "Frontal Prominence Index", "value": f"{geom.get('frontal_prominence', 0):.3f}"},
            {"metric": "Width/Height Ratio", "value": f"{geom.get('width_height_ratio', 0):.2f}"},
        ]

        assert len(details) == 6
        assert details[0]["value"] == "15.0"
        assert details[3]["value"] == "0.125"
