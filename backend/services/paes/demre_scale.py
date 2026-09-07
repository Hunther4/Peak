"""
Módulo de Conversión de Puntajes Oficiales DEMRE para Competencia Matemática 1 (M1).
Basado en la Tabla de Transformación de Puntajes PAES Regular - Proceso de Admisión 2026 (DEMRE).
Fuente oficial: https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-m1
"""

from typing import Any, Dict

# Tabla oficial DEMRE PAES Regular 2026: Aciertos (0 a 60) -> Puntaje PAES (100 a 1000)
M1_DEMRE_TABLE_2026: Dict[int, int] = {
    0: 100,
    1: 170,
    2: 194,
    3: 216,
    4: 236,
    5: 256,
    6: 275,
    7: 292,
    8: 307,
    9: 320,
    10: 334,
    11: 349,
    12: 365,
    13: 380,
    14: 393,
    15: 403,
    16: 412,
    17: 421,
    18: 432,
    19: 446,
    20: 460,
    21: 474,
    22: 486,
    23: 495,
    24: 502,
    25: 508,
    26: 516,
    27: 526,
    28: 539,
    29: 553,
    30: 567,
    31: 579,
    32: 587,
    33: 595,
    34: 601,
    35: 609,
    36: 618,
    37: 631,
    38: 645,
    39: 660,
    40: 672,
    41: 682,
    42: 690,
    43: 699,
    44: 710,
    45: 723,
    46: 738,
    47: 753,
    48: 767,
    49: 780,
    50: 793,
    51: 807,
    52: 824,
    53: 842,
    54: 861,
    55: 880,
    56: 900,
    57: 923,
    58: 948,
    59: 975,
    60: 1000
}

# Alias para compatibilidad
DEMRE_M1_CONVERSION_TABLE = M1_DEMRE_TABLE_2026

def _estimate_percentile(raw_score: int) -> float:
    if raw_score <= 0:
        return 1.0
    if raw_score >= 60:
        return 99.9
    # Sigmoide centrada en media ~24 aciertos (mediana ~502 pts)
    pct = 100.0 / (1.0 + pow(2.71828, -0.11 * (raw_score - 24.5)))
    return round(max(1.0, min(99.9, pct)), 1)

def raw_score_to_paes(raw_score: int, total_valid: int = 60) -> Dict[str, Any]:
    """
    Convierte el número de respuestas correctas puntuables (0 a 60) en la estimación de puntaje PAES M1.
    """
    clamped_raw = max(0, min(total_valid, int(raw_score)))
    score = M1_DEMRE_TABLE_2026.get(clamped_raw, 100)

    margin = 25 if (5 <= clamped_raw <= 55) else 20
    score_min = max(100, score - margin)
    score_max = min(1000, score + margin)

    percentile = _estimate_percentile(clamped_raw)

    return {
        "raw_score": clamped_raw,
        "total_scored_items": total_valid,
        "base_paes_score": score,
        "estimated_score": score,
        "score_range_min": score_min,
        "score_range_max": score_max,
        "estimated_range_str": f"{score_min} - {score_max} pts",
        "performance_estimate_label": "Estimación interna de rendimiento",
        "confidence_level": "ALTA" if total_valid >= 50 else "MEDIA",
        "percentile_approx": percentile,
        "official_source": "DEMRE - Tabla de Transformación PAES Regular Proceso 2026 M1",
        "source_url": "https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-m1"
    }
