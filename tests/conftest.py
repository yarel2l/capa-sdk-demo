"""
Test Configuration and Fixtures for Demo Reflex

Shared fixtures for testing state, components, and services.
"""

import pytest
from typing import Dict, Any


# =============================================================================
# Mock Data Fixtures
# =============================================================================

@pytest.fixture
def mock_wd_result() -> Dict[str, Any]:
    """Mock WD analysis result."""
    return {
        "wd_value": 3.897,
        "wd_value_px": 145.2,
        "classification": "reserved",
        "bizygomatic_width": 14.44,
        "bizygomatic_width_px": 542.1,
        "bigonial_width": 10.54,
        "bigonial_width_px": 396.9,
        "confidence": 0.649,
        "units": "cm",
        "personality_profile": {
            "social_orientation": 0.65,
            "relational_field": 0.58,
            "communication_style": 0.72,
            "leadership": 0.45,
        },
        "demographic_data": {
            "percentile": 50.0,
        }
    }


@pytest.fixture
def mock_forehead_result() -> Dict[str, Any]:
    """Mock forehead analysis result."""
    return {
        "slant_angle": 15.0,
        "forehead_height": 65.0,
        "impulsiveness_level": "low",
        "confidence": 0.85,
        "geometry": {
            "slant_angle": 15.0,
            "forehead_height": 65.0,
            "forehead_width": 120.0,
            "curvature": 0.125,
            "frontal_prominence": 0.08,
            "width_height_ratio": 1.85,
        },
        "neuroscience": {
            "dopamine_system_activity": 0.65,
            "serotonin_system_balance": 0.72,
            "gaba_system_function": 0.58,
            "executive_function_score": 0.78,
            "working_memory_capacity": 0.68,
            "attention_control_score": 0.71,
        },
        "impulsivity_profile": {
            "non_planning": 0.35,
            "cognitive": 0.28,
            "motor": 0.42,
            "attentional": 0.31,
            "risk_taking": 0.25,
            "sensation_seeking": 0.38,
            "behavioral_inhibition": 0.72,
            "emotional_regulation": 0.65,
        }
    }


@pytest.fixture
def mock_morphology_result() -> Dict[str, Any]:
    """Mock morphology analysis result."""
    return {
        "face_shape": "oval",
        "facial_index": 88.5,
        "width_height_ratio": 0.78,
        "confidence": 0.92,
        "shape_distribution": {
            "oval": 0.65,
            "round": 0.15,
            "square": 0.10,
            "heart": 0.08,
            "oblong": 0.02,
        },
        "proportions": {
            "upper_face": 0.33,
            "middle_face": 0.34,
            "lower_face": 0.33,
        }
    }


@pytest.fixture
def mock_canons_result() -> Dict[str, Any]:
    """Mock neoclassical canons result."""
    return {
        "overall_score": 0.291,
        "beauty_score": 0.72,
        "confidence": 0.88,
        "canon_measurements": {
            "Canon 1: Equal Facial Thirds": {
                "measured_value": 0.905,
                "deviation": 9.5,
                "within_range": True,
                "confidence": 0.80,
            },
            "Canon 2: Four Equal Face Heights": {
                "measured_value": 0.614,
                "deviation": 38.6,
                "within_range": False,
                "confidence": 0.75,
            },
            "Canon 3: Facial Fifths": {
                "measured_value": 0.902,
                "deviation": 9.8,
                "within_range": True,
                "confidence": 0.90,
            },
            "Canon 4: Intercanthal = Nose Width": {
                "measured_value": 1.296,
                "deviation": 29.6,
                "within_range": False,
                "confidence": 0.90,
            },
            "Canon 5: Eye Width = Nose Width": {
                "measured_value": 0.952,
                "deviation": 4.8,
                "within_range": True,
                "confidence": 0.90,
            },
        }
    }


@pytest.fixture
def mock_full_results(
    mock_wd_result,
    mock_forehead_result,
    mock_morphology_result,
    mock_canons_result
) -> Dict[str, Any]:
    """Complete mock analysis results."""
    return {
        "success": True,
        "wd_result": mock_wd_result,
        "forehead_result": mock_forehead_result,
        "morphology_result": mock_morphology_result,
        "neoclassical_result": mock_canons_result,
        "metadata": {
            "processing_time": 2.45,
            "image_quality": 0.92,
        }
    }


# =============================================================================
# Edge Case Fixtures
# =============================================================================

@pytest.fixture
def mock_results_with_invalid_confidence() -> Dict[str, Any]:
    """Results with confidence > 1.0 to test clamping."""
    return {
        "success": True,
        "wd_result": {
            "wd_value": 3.5,
            "classification": "reserved",
            "confidence": 1.005,  # Invalid: > 1.0
            "units": "cm",
        },
        "forehead_result": {
            "slant_angle": 15.0,
            "confidence": 1.25,  # Invalid: > 1.0
        }
    }


@pytest.fixture
def mock_results_with_negative_values() -> Dict[str, Any]:
    """Results with negative values to test edge cases."""
    return {
        "success": True,
        "wd_result": {
            "wd_value": -3.897,  # Negative WD
            "classification": "reserved",
            "confidence": -0.1,  # Invalid: < 0
            "units": "cm",
        }
    }


@pytest.fixture
def mock_empty_results() -> Dict[str, Any]:
    """Empty results to test null handling."""
    return {}


# =============================================================================
# State Test Helpers
# =============================================================================

def assert_percentage_format(value: str, decimals: int = 1):
    """Assert that a string is properly formatted as percentage."""
    assert value.endswith("%"), f"Expected percentage format, got: {value}"
    numeric_part = value.rstrip("%")
    try:
        float(numeric_part)
    except ValueError:
        pytest.fail(f"Invalid numeric part in percentage: {value}")


def assert_value_clamped(value: float, min_val: float = 0.0, max_val: float = 1.0):
    """Assert that a value is within expected range."""
    assert min_val <= value <= max_val, f"Value {value} not in range [{min_val}, {max_val}]"
