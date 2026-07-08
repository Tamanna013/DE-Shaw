import pytest
import math
from services.analytics_batch.application.use_cases.compute_flaky_scores import (
    calculate_flip_rate, 
    calculate_wilson_score_lower_bound
)

def test_calculate_flip_rate():
    # 0 flips, n=1
    assert calculate_flip_rate(["passed"]) == (0.0, 0)
    
    # 0 flips, n=5
    assert calculate_flip_rate(["passed"] * 5) == (0.0, 0)
    
    # Alternating perfectly
    assert calculate_flip_rate(["passed", "failed", "passed", "failed"]) == (1.0, 3)
    
    # 1 flip, n=3
    assert calculate_flip_rate(["passed", "passed", "failed"]) == (0.5, 1)

@pytest.mark.parametrize("flip_rate, sample_size, expected_approx", [
    (1.0, 1, 0.20),   # Only 1 transition which flipped. Huge uncertainty, lower bound heavily penalized.
    (1.0, 2, 0.34),   # 2 transitions, both flipped.
    (1.0, 5, 0.56),   # 5 transitions, all flipped. Getting more confident.
    (1.0, 50, 0.92),  # 50 transitions, all flipped. Very confident.
    (0.5, 100, 0.40), # 100 transitions, 50% flip rate. Confident it's truly around 50%.
    (0.1, 500, 0.07), # 500 transitions, 10% flip rate. Tight bound.
    (0.0, 10, 0.0),   # 0 flip rate is always 0 lower bound
])
def test_wilson_score_lower_bound_scaling(flip_rate, sample_size, expected_approx):
    bound = calculate_wilson_score_lower_bound(flip_rate, sample_size)
    assert math.isclose(bound, expected_approx, abs_tol=0.05)

def test_wilson_score_zero_sample():
    assert calculate_wilson_score_lower_bound(1.0, 0) == 0.0
