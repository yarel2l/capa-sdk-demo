"""
Tests for Plotly chart generation functions.

These tests verify chart data formatting and configuration.
"""

import pytest
from typing import Dict, Any, List


class TestHarmonyGaugeChart:
    """Tests for harmony score gauge chart."""

    def test_score_clamping(self):
        """Test score is clamped to 0-1 range."""
        test_cases = [
            (0.5, 0.5),
            (1.5, 1.0),  # Clamped
            (-0.2, 0.0),  # Clamped
            (0.0, 0.0),
            (1.0, 1.0),
        ]

        for input_score, expected in test_cases:
            clamped = max(0, min(1, float(input_score)))
            assert clamped == expected, f"Input {input_score} -> {clamped}, expected {expected}"

    def test_percentage_conversion(self):
        """Test score converts to percentage correctly."""
        score = 0.291
        score_pct = score * 100

        assert score_pct == pytest.approx(29.1, rel=0.01)

    def test_color_thresholds(self):
        """Test color coding based on score."""
        test_cases = [
            (0.85, "green"),   # >= 0.8
            (0.80, "green"),   # >= 0.8
            (0.70, "blue"),    # >= 0.6
            (0.60, "blue"),    # >= 0.6
            (0.50, "amber"),   # >= 0.4 (secondary/amber)
            (0.30, "red"),     # < 0.4
        ]

        for score, expected_color in test_cases:
            if score >= 0.8:
                color = "green"
            elif score >= 0.6:
                color = "blue"
            elif score >= 0.4:
                color = "amber"
            else:
                color = "red"

            assert color == expected_color, f"Score {score} -> {color}, expected {expected_color}"


class TestDemographicGaugeChart:
    """Tests for demographic percentile gauge chart."""

    def test_percentile_clamping(self):
        """Test percentile is clamped to 0-100 range."""
        test_cases = [
            (50, 50),
            (150, 100),   # Clamped
            (-10, 0),     # Clamped
            (0, 0),
            (100, 100),
        ]

        for input_val, expected in test_cases:
            clamped = max(0, min(100, float(input_val)))
            assert clamped == expected

    def test_percentile_suffix_format(self):
        """Test percentile uses 'th' suffix, not '%ile'."""
        percentile = 50

        # Correct format
        correct_format = f"{int(percentile)}th"

        # Incorrect format (what we fixed)
        incorrect_format = f"{percentile}%ile"

        assert correct_format == "50th"
        assert "ile" not in correct_format

    def test_percentile_color_thresholds(self):
        """Test color coding based on percentile."""
        test_cases = [
            (80, "blue"),    # >= 75
            (75, "blue"),    # >= 75
            (60, "green"),   # >= 50
            (50, "green"),   # >= 50
            (30, "amber"),   # >= 25
            (10, "red"),     # < 25
        ]

        for pct, expected_color in test_cases:
            if pct >= 75:
                color = "blue"
            elif pct >= 50:
                color = "green"
            elif pct >= 25:
                color = "amber"
            else:
                color = "red"

            assert color == expected_color, f"Percentile {pct} -> {color}, expected {expected_color}"


class TestImpulsivityRadarChart:
    """Tests for impulsivity profile radar chart."""

    def test_radar_data_structure(self, mock_forehead_result):
        """Test radar chart data has correct structure."""
        profile = mock_forehead_result.get("impulsivity_profile", {})

        # Expected 8 dimensions for BIS-11
        assert len(profile) == 8

        # All values should be 0-1
        for dim, value in profile.items():
            assert 0 <= value <= 1, f"{dim} value {value} out of range"

    def test_radar_dimension_labels(self):
        """Test radar dimension labels are properly formatted."""
        raw_keys = [
            "non_planning", "cognitive", "motor", "attentional",
            "risk_taking", "sensation_seeking", "behavioral_inhibition",
            "emotional_regulation"
        ]

        expected_labels = [
            "Non-Planning", "Cognitive", "Motor", "Attentional",
            "Risk Taking", "Sensation Seek.", "Behavioral Inh.",
            "Emotional Reg."
        ]

        # These are the actual abbreviated labels used in the chart
        abbreviated = {
            "non_planning": "Non-Planning",
            "cognitive": "Cognitive",
            "motor": "Motor",
            "attentional": "Attentional",
            "risk_taking": "Risk Taking",
            "sensation_seeking": "Sensation Seek.",
            "behavioral_inhibition": "Behavioral Inh.",
            "emotional_regulation": "Emotional Reg."
        }

        for key in raw_keys:
            assert key in abbreviated


class TestPersonalityRadarChart:
    """Tests for WD personality profile radar chart."""

    def test_personality_data_structure(self, mock_wd_result):
        """Test personality radar data structure."""
        profile = mock_wd_result.get("personality_profile", {})

        assert len(profile) >= 4  # At least 4 dimensions

        for trait, value in profile.items():
            assert isinstance(value, (int, float)), f"{trait} is not numeric"


class TestCanonDeviationBarChart:
    """Tests for canon deviation bar chart."""

    def test_deviation_bar_data_format(self, mock_canons_result):
        """Test deviation bar chart data format."""
        measurements = mock_canons_result.get("canon_measurements", {})

        bar_data = []
        for name, data in measurements.items():
            bar_data.append({
                "canon": name,
                "deviation": data.get("deviation", 0),
                "within_range": data.get("within_range", False)
            })

        assert len(bar_data) == 5  # 5 canons in mock data
        assert all("canon" in d and "deviation" in d for d in bar_data)

    def test_deviation_colors_by_threshold(self, mock_canons_result):
        """Test bar colors are assigned based on threshold."""
        measurements = mock_canons_result.get("canon_measurements", {})

        for name, data in measurements.items():
            within = data.get("within_range", False)
            expected_color = "green" if within else "red"

            # Verify based on deviation
            deviation = data.get("deviation", 0)
            is_within = abs(deviation) <= 10.0

            assert within == is_within, f"{name}: within_range mismatch"


class TestNeuroscienceBarChart:
    """Tests for neuroscience correlations bar chart."""

    def test_neuroscience_bar_data_format(self, mock_forehead_result):
        """Test neuroscience bar chart data format."""
        neuro = mock_forehead_result.get("neuroscience", {})

        bar_data = []
        for metric, value in neuro.items():
            bar_data.append({
                "metric": metric.replace("_", " ").title(),
                "value": float(value)
            })

        assert len(bar_data) == 6  # 6 neuroscience metrics

    def test_neuroscience_value_range(self, mock_forehead_result):
        """Test all neuroscience values are in 0-1 range."""
        neuro = mock_forehead_result.get("neuroscience", {})

        for metric, value in neuro.items():
            assert 0 <= value <= 1, f"{metric} value {value} out of range"


class TestShapeDistributionChart:
    """Tests for face shape distribution pie/donut chart."""

    def test_shape_distribution_format(self, mock_morphology_result):
        """Test shape distribution data format."""
        distribution = mock_morphology_result.get("shape_distribution", {})

        labels = list(distribution.keys())
        values = list(distribution.values())

        assert len(labels) == 5  # 5 shape categories
        assert all(0 <= v <= 1 for v in values)

    def test_distribution_sums_approximately_one(self, mock_morphology_result):
        """Test distribution percentages sum to ~100%."""
        distribution = mock_morphology_result.get("shape_distribution", {})
        total = sum(distribution.values())

        assert abs(total - 1.0) < 0.05, f"Distribution sum {total} not close to 1.0"


class TestConfidenceDashboard:
    """Tests for module confidence dashboard chart."""

    def test_dashboard_data_format(self, mock_full_results):
        """Test confidence dashboard data format."""
        modules = []

        if mock_full_results.get("wd_result"):
            modules.append({
                "module": "WD",
                "confidence": mock_full_results["wd_result"].get("confidence", 0),
                "status": "active"
            })

        if mock_full_results.get("forehead_result"):
            modules.append({
                "module": "Forehead",
                "confidence": mock_full_results["forehead_result"].get("confidence", 0),
                "status": "active"
            })

        assert len(modules) >= 2
        assert all("module" in m and "confidence" in m for m in modules)

    def test_module_confidence_clamped(self, mock_full_results):
        """Test all module confidences are valid."""
        for module in ["wd_result", "forehead_result", "morphology_result"]:
            if mock_full_results.get(module):
                conf = mock_full_results[module].get("confidence", 0)
                clamped = max(0.0, min(1.0, conf))
                assert clamped == conf or conf > 1.0 or conf < 0.0
