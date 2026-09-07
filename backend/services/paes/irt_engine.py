# -*- coding: utf-8 -*-
from dataclasses import dataclass
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

D_SCALING: float = 1.702

@dataclass
class ItemParameters:
    item_id: Optional[str] = None
    a: float = 1.0     # Discriminacion [0.2, 3.0]
    b: float = 0.0     # Dificultad [-4.0, 4.0]
    c: float = 0.20    # Pseudo-azar / guessing [0.0, 0.35]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "a": round(float(self.a), 4),
            "b": round(float(self.b), 4),
            "c": round(float(self.c), 4),
        }

@dataclass
class AbilityEstimate:
    theta: float
    se: float
    method: str  # EAP, MLE, HYBRID
    paes_score: int
    paes_min: int
    paes_max: int
    information: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theta": round(float(self.theta), 4),
            "se": round(float(self.se), 4),
            "method": self.method,
            "paes_score": self.paes_score,
            "paes_min": self.paes_min,
            "paes_max": self.paes_max,
            "information": round(float(self.information), 4),
        }

def prob_3pl(
    theta: Union[float, np.ndarray],
    a: float,
    b: float,
    c: float,
    d: float = D_SCALING,
) -> Union[float, np.ndarray]:
    z = d * a * (theta - b)
    z_clipped = np.clip(z, -30.0, 30.0)
    p_star = 1.0 / (1.0 + np.exp(-z_clipped))
    return c + (1.0 - c) * p_star

def item_information(
    theta: Union[float, np.ndarray],
    a: float,
    b: float,
    c: float,
    d: float = D_SCALING,
) -> Union[float, np.ndarray]:
    p = prob_3pl(theta, a, b, c, d)
    p_safe = np.clip(p, 1e-9, 1.0 - 1e-9)
    q = 1.0 - p_safe
    numerator = (p_safe - c) ** 2
    denominator = ((1.0 - c) ** 2) * p_safe
    return (d ** 2) * (a ** 2) * (numerator / denominator) * q

def calculate_test_information(
    theta: Union[float, np.ndarray],
    items: List[ItemParameters],
    d: float = D_SCALING,
) -> Union[float, np.ndarray]:
    if not items:
        return 0.0 if isinstance(theta, (int, float)) else np.zeros_like(theta)
    infos = [item_information(theta, it.a, it.b, it.c, d) for it in items]
    return np.sum(infos, axis=0)

def standard_error(
    theta: Union[float, np.ndarray],
    items: List[ItemParameters],
    d: float = D_SCALING,
) -> Union[float, np.ndarray]:
    info = calculate_test_information(theta, items, d)
    info_safe = np.maximum(info, 1e-6)
    return 1.0 / np.sqrt(info_safe)

def theta_to_demre_score(
    theta: float,
    se: Optional[float] = None,
    mean_paes: float = 500.0,
    std_paes: float = 150.0,
) -> Tuple[int, int, int]:
    score = int(round(np.clip(mean_paes + std_paes * theta, 100.0, 1000.0)))
    if se is not None and se > 0:
        lower_theta = theta - 1.96 * se
        upper_theta = theta + 1.96 * se
        p_min = int(round(np.clip(mean_paes + std_paes * lower_theta, 100.0, 1000.0)))
        p_max = int(round(np.clip(mean_paes + std_paes * upper_theta, 100.0, 1000.0)))
    else:
        p_min, p_max = max(100, score - 30), min(1000, score + 30)
    return score, p_min, p_max

def estimate_theta_eap(
    responses: List[int],
    items: List[ItemParameters],
    num_nodes: int = 41,
    theta_bounds: Tuple[float, float] = (-4.0, 4.0),
    prior_mean: float = 0.0,
    prior_std: float = 1.0,
    d: float = D_SCALING,
) -> AbilityEstimate:
    if len(responses) != len(items) or len(items) == 0:
        score, p_min, p_max = theta_to_demre_score(0.0, 1.0)
        return AbilityEstimate(0.0, 1.0, "EAP", score, p_min, p_max, 0.0)

    nodes = np.linspace(theta_bounds[0], theta_bounds[1], num_nodes)
    prior = np.exp(-0.5 * ((nodes - prior_mean) / prior_std) ** 2) / (prior_std * np.sqrt(2 * np.pi))
    prior /= np.sum(prior)

    log_likelihood = np.zeros(num_nodes)
    for u, item in zip(responses, items):
        p = prob_3pl(nodes, item.a, item.b, item.c, d)
        p = np.clip(p, 1e-12, 1.0 - 1e-12)
        if u == 1:
            log_likelihood += np.log(p)
        else:
            log_likelihood += np.log(1.0 - p)

    max_log = np.max(log_likelihood)
    likelihood = np.exp(log_likelihood - max_log)

    posterior = likelihood * prior
    post_sum = np.sum(posterior)
    if post_sum <= 0 or np.isnan(post_sum):
        posterior = prior
    else:
        posterior /= post_sum

    theta_est = float(np.sum(nodes * posterior))
    var_est = float(np.sum(((nodes - theta_est) ** 2) * posterior))
    se_est = float(np.sqrt(max(var_est, 1e-4)))
    info = float(calculate_test_information(theta_est, items, d))

    score, p_min, p_max = theta_to_demre_score(theta_est, se_est)
    return AbilityEstimate(
        theta=theta_est,
        se=se_est,
        method="EAP",
        paes_score=score,
        paes_min=p_min,
        paes_max=p_max,
        information=info,
    )

def estimate_theta_mle(
    responses: List[int],
    items: List[ItemParameters],
    initial_theta: float = 0.0,
    max_iter: int = 30,
    tol: float = 1e-4,
    d: float = D_SCALING,
) -> Optional[AbilityEstimate]:
    n_correct = sum(responses)
    n_total = len(responses)
    if n_correct == 0 or n_correct == n_total or n_total == 0:
        return None

    theta = float(initial_theta)
    for _ in range(max_iter):
        score_derivative = 0.0
        info_sum = 0.0

        for u, item in zip(responses, items):
            p = float(prob_3pl(theta, item.a, item.b, item.c, d))
            p_safe = min(max(p, 1e-9), 1.0 - 1e-9)
            term_score = d * item.a * ((p_safe - item.c) / (1.0 - item.c)) * ((u - p_safe) / p_safe)
            score_derivative += term_score

            term_info = float(item_information(theta, item.a, item.b, item.c, d))
            info_sum += term_info

        if info_sum < 1e-5:
            return None

        step = score_derivative / info_sum
        step = max(min(step, 0.75), -0.75)
        theta += step
        theta = max(min(theta, 4.0), -4.0)

        if abs(step) < tol:
            break

    info = float(calculate_test_information(theta, items, d))
    se_est = float(1.0 / np.sqrt(max(info, 1e-5)))
    score, p_min, p_max = theta_to_demre_score(theta, se_est)

    return AbilityEstimate(
        theta=theta,
        se=se_est,
        method="MLE",
        paes_score=score,
        paes_min=p_min,
        paes_max=p_max,
        information=info,
    )

def estimate_theta_hybrid(
    responses: List[int],
    items: List[ItemParameters],
    d: float = D_SCALING,
) -> AbilityEstimate:
    mle_res = estimate_theta_mle(responses, items, d=d)
    if mle_res is not None and not np.isnan(mle_res.theta) and mle_res.se < 2.0:
        return mle_res
    return estimate_theta_eap(responses, items, d=d)

def select_next_adaptive_item(
    theta: float,
    candidate_items: List[ItemParameters],
    administered_ids: Optional[List[str]] = None,
    d: float = D_SCALING,
) -> Optional[ItemParameters]:
    administered = set(administered_ids or [])
    available = [it for it in candidate_items if it.item_id not in administered]
    if not available:
        return None

    best_item = None
    max_info = -1.0
    for it in available:
        info = float(item_information(theta, it.a, it.b, it.c, d))
        if info > max_info:
            max_info = info
            best_item = it

    return best_item

def calibrate_mmle_em(
    response_matrix: np.ndarray,
    initial_items: Optional[List[ItemParameters]] = None,
    num_nodes: int = 31,
    max_iter: int = 20,
    tol: float = 1e-3,
    d: float = D_SCALING,
) -> List[ItemParameters]:
    M, N = response_matrix.shape
    if M == 0 or N == 0:
        return initial_items or []

    items: List[ItemParameters] = []
    if initial_items and len(initial_items) == N:
        items = [ItemParameters(it.item_id, it.a, it.b, it.c) for it in initial_items]
    else:
        for j in range(N):
            col = response_matrix[:, j]
            valid = col[~np.isnan(col)]
            p_val = float(np.mean(valid)) if len(valid) > 0 else 0.5
            p_val = max(min(p_val, 0.95), 0.05)
            b_init = -math.log(p_val / (1.0 - p_val)) / 1.702
            items.append(ItemParameters(item_id=f"item_{j+1}", a=1.0, b=float(b_init), c=0.20))

    nodes = np.linspace(-4.0, 4.0, num_nodes)
    weights = np.exp(-0.5 * nodes ** 2) / np.sqrt(2 * np.pi)
    weights /= np.sum(weights)

    for iteration in range(max_iter):
        max_delta = 0.0

        # Paso E
        log_L = np.zeros((M, num_nodes))
        for j, item in enumerate(items):
            pj = prob_3pl(nodes, item.a, item.b, item.c, d)
            pj = np.clip(pj, 1e-12, 1.0 - 1e-12)
            col = response_matrix[:, j]
            for i in range(M):
                resp = col[i]
                if not np.isnan(resp):
                    if resp == 1:
                        log_L[i] += np.log(pj)
                    else:
                        log_L[i] += np.log(1.0 - pj)

        posterior = np.zeros((M, num_nodes))
        for i in range(M):
            shift = np.max(log_L[i])
            num = np.exp(log_L[i] - shift) * weights
            s = np.sum(num)
            posterior[i] = num / s if s > 0 else weights

        n_bar = np.sum(posterior, axis=0)

        # Paso M
        for j in range(N):
            col = response_matrix[:, j]
            valid_mask = ~np.isnan(col)
            if not np.any(valid_mask):
                continue
            r_bar = np.sum(posterior[valid_mask] * col[valid_mask, None], axis=0)

            old_b = items[j].b
            old_a = items[j].a

            total_r = np.sum(r_bar)
            total_n = np.sum(n_bar)
            p_bar = total_r / max(total_n, 1e-5)
            c_j = items[j].c
            p_star = max((p_bar - c_j) / (1.0 - c_j), 0.01)
            p_star = min(p_star, 0.99)
            new_b = float(np.clip(-math.log(p_star / (1.0 - p_star)) / (d * old_a), -3.5, 3.5))

            delta_b = abs(new_b - old_b)
            items[j].b = 0.5 * old_b + 0.5 * new_b
            max_delta = max(max_delta, delta_b)

        if max_delta < tol:
            break

    return items