import pytest
import pandas as pd
import geopandas as gpd

from tests.utils.weight_utils_core import (
    validate_weights,
    apply_default_weights,
    calculate_safety_score,
    calculate_speed_score,
    calculate_greenery_score,
    calculate_weight,
    calculate_weights,
    DEFAULT_WEIGHTS,
)


def test_validate_weights_valid():
    weights = {
        "distance": 1,
        "lighting": 0.5,
        "greenery": 2,
        "pollution": 0,
        "surface_quality": 3,
        "amenity_proximity": 1,
    }
    assert validate_weights(weights) is True


def test_validate_weights_invalid_key():
    weights = {"distance": 1, "unknown": 5}
    assert validate_weights(weights) is False


def test_validate_weights_negative_value():
    weights = {"distance": -1}
    assert validate_weights(weights) is False


def test_validate_weights_non_numeric():
    weights = {"distance": "abc"}
    assert validate_weights(weights) is False


def test_validate_weights_not_dict():
    assert validate_weights(["not", "a", "dict"]) is False


def test_apply_default_weights_none():
    result = apply_default_weights(None)
    assert result == DEFAULT_WEIGHTS


def test_apply_default_weights_partial():
    result = apply_default_weights({"distance": 5})
    assert result["distance"] == 5
    assert result["lighting"] == 1.0
    assert result["greenery"] == 1.0


def test_apply_default_weights_negative_clamped():
    result = apply_default_weights({"distance": -10})
    assert result["distance"] == 0.0


def test_apply_default_weights_non_numeric_fallback():
    result = apply_default_weights({"distance": "abc"})
    assert result["distance"] == 1.0


def make_row(**kwargs):
    return kwargs


def test_calculate_safety_score():
    row = make_row(lighting=0.8)
    score = calculate_safety_score(row, safety_priority=0.5)
    assert score == pytest.approx((1 - 0.5) * 0.8)


def test_calculate_speed_score_nonzero():
    row = make_row(surface_quality=0.5)
    score = calculate_speed_score(row, speed_priority=0.2)
    expected_speed = 0.5 * 4.8
    assert score == pytest.approx(expected_speed * (1 - 0.2))


def test_calculate_speed_score_zero_surface():
    row = make_row(surface_quality=0)
    score = calculate_speed_score(row, speed_priority=0.5)
    assert score == 999


def test_calculate_greenery_score():
    row = make_row(greenery=0.4, pollution=0.6)
    score = calculate_greenery_score(row, greenery_priority=0.3)
    assert score == pytest.approx((1 - 0.4) * 0.6 * (1 - 0.3))


def test_calculate_weight():
    row = make_row(
        greenery_score=1.0,
        safety_score=2.0,
        speed_score=3.0,
        length=10,
    )
    score = calculate_weight(row)
    assert score == 10 * (1 + 2 + 3)


def test_calculate_weights_full_pipeline():
    df = gpd.GeoDataFrame({
        "lighting": [0.5],
        "surface_quality": [0.5],
        "greenery": [0.4],
        "pollution": [0.6],
        "length": [10],
    })

    out = calculate_weights(df, safety_priority=0.3, speed_priority=0.2, greenery_priority=0.1)

    assert "safety_score" in out.columns
    assert "speed_score" in out.columns
    assert "greenery_score" in out.columns
    assert "weight" in out.columns

    assert out["weight"].iloc[0] > 0
