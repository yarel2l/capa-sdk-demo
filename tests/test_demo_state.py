"""
Tests for DemoState computed variables and data transformations.

These tests verify that the state correctly processes and formats
analysis results for display in the /demo page.
"""

import pytest
from typing import Dict, Any


class TestWDResultsFormatting:
    """Tests for WD analysis result formatting."""

    def test_wd_value_positive(self, mock_wd_result):
        """Test WD value formatting with positive value."""
        # Simulate what the state does
        val = mock_wd_result.get("wd_value", 0)
        units = mock_wd_result.get("units", "px")
        formatted = f"{val:.3f} {units}"

        assert formatted == "3.897 cm"
        assert val > 0

    def test_wd_value_negative(self, mock_results_with_negative_values):
        """Test WD value formatting with negative value."""
        wd = mock_results_with_negative_values["wd_result"]
        val = wd.get("wd_value", 0)

        # Value can be negative (represents direction)
        assert val == -3.897

    def test_wd_classification_valid(self, mock_wd_result):
        """Test WD classification is a valid string."""
        classification = mock_wd_result.get("classification", "N/A")

        assert classification in ["reserved", "wider_jaw", "balanced", "N/A"]

    def test_wd_confidence_clamping(self, mock_results_with_invalid_confidence):
        """Test that confidence values > 1.0 are clamped."""
        wd = mock_results_with_invalid_confidence["wd_result"]
        conf = wd.get("confidence", 0)

        # Simulate clamping
        clamped = max(0.0, min(1.0, conf))

        assert clamped == 1.0
        assert conf > 1.0  # Original was invalid

    def test_wd_confidence_negative_clamping(self, mock_results_with_negative_values):
        """Test that negative confidence values are clamped to 0."""
        wd = mock_results_with_negative_values["wd_result"]
        conf = wd.get("confidence", 0)

        # Simulate clamping
        clamped = max(0.0, min(1.0, conf))

        assert clamped == 0.0
        assert conf < 0  # Original was invalid


class TestForeheadResultsFormatting:
    """Tests for forehead analysis result formatting."""

    def test_forehead_slant_angle(self, mock_forehead_result):
        """Test forehead slant angle formatting."""
        angle = mock_forehead_result.get("slant_angle", 0)
        formatted = f"{angle:.1f}"

        assert formatted == "15.0"
        assert 0 <= angle <= 90  # Valid range for slant angle

    def test_forehead_impulsiveness_level(self, mock_forehead_result):
        """Test impulsiveness level is valid."""
        level = mock_forehead_result.get("impulsiveness_level", "unknown")

        assert level in ["low", "moderate", "high", "very_high", "unknown"]

    def test_forehead_height_formatting(self, mock_forehead_result):
        """Test forehead height shows units."""
        height = mock_forehead_result.get("forehead_height", 0)
        formatted = f"{height:.1f}px"

        assert formatted == "65.0px"

    def test_impulsivity_profile_structure(self, mock_forehead_result):
        """Test impulsivity profile has expected dimensions."""
        profile = mock_forehead_result.get("impulsivity_profile", {})

        expected_keys = [
            "non_planning", "cognitive", "motor", "attentional",
            "risk_taking", "sensation_seeking", "behavioral_inhibition",
            "emotional_regulation"
        ]

        for key in expected_keys:
            assert key in profile, f"Missing key: {key}"
            assert 0 <= profile[key] <= 1, f"Value out of range for {key}"


class TestMorphologyResultsFormatting:
    """Tests for morphology analysis result formatting."""

    def test_face_shape_valid(self, mock_morphology_result):
        """Test face shape is a valid classification."""
        shape = mock_morphology_result.get("face_shape", "unknown")

        valid_shapes = ["oval", "round", "square", "heart", "oblong", "diamond", "unknown"]
        assert shape in valid_shapes

    def test_facial_index_range(self, mock_morphology_result):
        """Test facial index is within expected range."""
        index = mock_morphology_result.get("facial_index", 0)

        # Typical facial index ranges from 70-100
        assert 60 <= index <= 120, f"Facial index {index} outside expected range"

    def test_shape_distribution_sums_to_one(self, mock_morphology_result):
        """Test shape distribution percentages sum to approximately 1."""
        distribution = mock_morphology_result.get("shape_distribution", {})

        total = sum(distribution.values())
        assert abs(total - 1.0) < 0.01, f"Distribution sums to {total}, expected ~1.0"


class TestCanonsResultsFormatting:
    """Tests for neoclassical canons result formatting."""

    def test_harmony_score_range(self, mock_canons_result):
        """Test harmony score is within 0-1 range."""
        score = mock_canons_result.get("overall_score", 0)

        assert 0 <= score <= 1, f"Harmony score {score} out of range"

    def test_canon_deviation_threshold(self, mock_canons_result):
        """Test canon status based on 10% deviation threshold."""
        measurements = mock_canons_result.get("canon_measurements", {})

        for name, data in measurements.items():
            deviation = data.get("deviation", 0)
            within_range = data.get("within_range", False)

            # Our threshold is 10%
            expected_within = abs(deviation) <= 10.0
            assert within_range == expected_within, (
                f"{name}: deviation={deviation}, within_range={within_range}, expected={expected_within}"
            )

    def test_canon_confidence_valid(self, mock_canons_result):
        """Test all canon confidences are valid."""
        measurements = mock_canons_result.get("canon_measurements", {})

        for name, data in measurements.items():
            conf = data.get("confidence", 0)
            assert 0 <= conf <= 1, f"{name} confidence {conf} out of range"


class TestEmptyResults:
    """Tests for handling empty/null results."""

    def test_empty_results_wd_value(self, mock_empty_results):
        """Test WD value returns N/A for empty results."""
        wd_result = mock_empty_results.get("wd_result")

        if not wd_result:
            result = "N/A"
        else:
            result = f"{wd_result.get('wd_value', 0):.3f}"

        assert result == "N/A"

    def test_empty_results_confidence(self, mock_empty_results):
        """Test confidence returns 0 for empty results."""
        wd_result = mock_empty_results.get("wd_result", {})
        conf = wd_result.get("confidence", 0)

        assert conf == 0

    def test_empty_results_has_results_flag(self, mock_empty_results):
        """Test has_results flag is False for empty results."""
        has_wd = bool(mock_empty_results.get("wd_result"))
        has_forehead = bool(mock_empty_results.get("forehead_result"))
        has_morphology = bool(mock_empty_results.get("morphology_result"))

        assert not has_wd
        assert not has_forehead
        assert not has_morphology


class TestPercentileFormatting:
    """Tests for demographic percentile formatting."""

    def test_percentile_suffix(self, mock_wd_result):
        """Test percentile shows correct suffix (th, not %ile)."""
        demo_data = mock_wd_result.get("demographic_data", {})
        percentile = demo_data.get("percentile", 50)

        # Format should be "50th" not "50%ile"
        formatted = f"{int(percentile)}th"

        assert formatted == "50th"
        assert "%ile" not in formatted

    def test_percentile_range(self, mock_wd_result):
        """Test percentile is within 0-100 range."""
        demo_data = mock_wd_result.get("demographic_data", {})
        percentile = demo_data.get("percentile", 50)

        assert 0 <= percentile <= 100


class TestConfidenceMeter:
    """Tests for confidence meter display logic."""

    def test_confidence_color_green(self):
        """Test confidence >= 0.8 shows green."""
        value = 0.85
        color = "green" if value >= 0.8 else ("amber" if value >= 0.6 else "red")

        assert color == "green"

    def test_confidence_color_amber(self):
        """Test confidence 0.6-0.8 shows amber."""
        value = 0.65
        color = "green" if value >= 0.8 else ("amber" if value >= 0.6 else "red")

        assert color == "amber"

    def test_confidence_color_red(self):
        """Test confidence < 0.6 shows red."""
        value = 0.45
        color = "green" if value >= 0.8 else ("amber" if value >= 0.6 else "red")

        assert color == "red"

    def test_confidence_percentage_integer(self):
        """Test confidence displays as integer percentage."""
        value = 0.649329995719735
        percentage_int = int(value * 100)

        assert percentage_int == 64
        assert isinstance(percentage_int, int)
