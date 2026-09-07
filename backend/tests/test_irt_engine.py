# -*- coding: utf-8 -*-
import pytest
import numpy as np
from services.paes.irt_engine import (
    ItemParameters,
    prob_3pl,
    item_information,
    calculate_test_information,
    standard_error,
    theta_to_demre_score,
    estimate_theta_eap,
    estimate_theta_mle,
    estimate_theta_hybrid,
    select_next_adaptive_item,
    calibrate_mmle_em,
)

def test_3pl_probability_properties():
    a = 1.2
    b = 0.5
    c = 0.20
    # Higher theta -> higher probability
    p_low = prob_3pl(-2.0, a, b, c)
    p_mid = prob_3pl(0.5, a, b, c)
    p_high = prob_3pl(3.0, a, b, c)

    assert p_low < p_mid < p_high
    # At difficulty b, P = c + (1-c)/2 = 0.20 + 0.40 = 0.60
    assert abs(p_mid - 0.60) < 1e-4
    # For theta -> -inf, P -> c
    assert abs(prob_3pl(-15.0, a, b, c) - c) < 1e-3
    # For theta -> +inf, P -> 1.0
    assert abs(prob_3pl(15.0, a, b, c) - 1.0) < 1e-3

def test_information_and_standard_error():
    items = [
        ItemParameters("i1", a=1.0, b=-1.0, c=0.20),
        ItemParameters("i2", a=1.5, b=0.0, c=0.20),
        ItemParameters("i3", a=1.2, b=1.0, c=0.20),
    ]
    info_0 = float(calculate_test_information(0.0, items))
    assert info_0 > 0.0

    se_0 = float(standard_error(0.0, items))
    assert abs(se_0 - (1.0 / np.sqrt(info_0))) < 1e-4

def test_theta_to_demre_scale():
    score, p_min, p_max = theta_to_demre_score(0.0, se=0.3)
    assert score == 500
    assert p_min < 500 < p_max

    score_low, _, _ = theta_to_demre_score(-3.5, se=0.2)
    assert score_low >= 100

    score_high, _, _ = theta_to_demre_score(4.0, se=0.2)
    assert score_high <= 1000

def test_eap_robustness():
    items = [ItemParameters(f"q_{i}", a=1.0, b=(i - 5) * 0.4, c=0.20) for i in range(10)]
    # All 0s does not diverge
    est_zero = estimate_theta_eap([0] * 10, items)
    assert est_zero.theta < -1.0
    assert not np.isnan(est_zero.theta)

    # All 1s does not diverge
    est_one = estimate_theta_eap([1] * 10, items)
    assert est_one.theta > 1.0
    assert not np.isnan(est_one.theta)

    # Half correct around theta=0
    responses_mid = [1 if i < 5 else 0 for i in range(10)]
    est_mid = estimate_theta_eap(responses_mid, items)
    assert -0.8 < est_mid.theta < 0.8
    assert 100 <= est_mid.paes_score <= 1000

def test_mle_and_hybrid():
    items = [ItemParameters(f"q_{i}", a=1.2, b=(i - 5) * 0.3, c=0.20) for i in range(10)]
    # Homogeneous returns None for MLE
    assert estimate_theta_mle([0] * 10, items) is None
    assert estimate_theta_mle([1] * 10, items) is None

    # Mixed responses converge with MLE
    responses = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    mle_est = estimate_theta_mle(responses, items)
    assert mle_est is not None
    assert mle_est.method == "MLE"
    assert -1.5 < mle_est.theta < 1.5

    # Hybrid estimator gracefully falls back for all 0s
    hyb_zero = estimate_theta_hybrid([0] * 10, items)
    assert hyb_zero.method == "EAP"

    # Hybrid estimator uses MLE for mixed
    hyb_mixed = estimate_theta_hybrid(responses, items)
    assert hyb_mixed.method == "MLE"

def test_cat_adaptive_selection():
    candidate_items = [
        ItemParameters("easy", a=1.5, b=-2.0, c=0.20),
        ItemParameters("medium", a=1.5, b=0.0, c=0.20),
        ItemParameters("hard", a=1.5, b=2.0, c=0.20),
    ]
    # For a low ability student (theta=-1.8), "easy" gives higher information
    selected_low = select_next_adaptive_item(-1.8, candidate_items)
    assert selected_low.item_id == "easy"

    # For a high ability student (theta=1.9), "hard" gives higher information
    selected_high = select_next_adaptive_item(1.9, candidate_items)
    assert selected_high.item_id == "hard"

    # Excludes already administered items
    selected_next = select_next_adaptive_item(1.9, candidate_items, administered_ids=["hard"])
    assert selected_next.item_id != "hard"

def test_mmle_em_calibration():
    # 20 examinees x 5 items
    np.random.seed(42)
    resp_matrix = np.random.choice([0, 1], size=(20, 5), p=[0.4, 0.6])
    calibrated = calibrate_mmle_em(resp_matrix, max_iter=5)
    assert len(calibrated) == 5
    for item in calibrated:
        assert 0.2 <= item.a <= 3.0
        assert -3.5 <= item.b <= 3.5
        assert 0.0 <= item.c <= 0.35