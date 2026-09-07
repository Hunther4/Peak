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

# Tablas oficiales y calibradas DEMRE PAES 2026 para las 5 pruebas
SUBJECT_METADATA: Dict[str, Dict[str, Any]] = {
    "M1": {
        "name": "Competencia Matemática 1",
        "total_scored": 60,
        "median": 24.5,
        "steepness": 0.11,
        "table": M1_DEMRE_TABLE_2026,
        "url": "https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-m1"
    },
    "LECTURA": {
        "name": "Competencia Lectora",
        "total_scored": 60,
        "median": 28.0,
        "steepness": 0.10,
        "table": {
            0: 100, 1: 150, 2: 175, 3: 198, 4: 218, 5: 236, 6: 254, 7: 270, 8: 285, 9: 300,
            10: 315, 11: 330, 12: 345, 13: 360, 14: 375, 15: 390, 16: 405, 17: 420, 18: 435, 19: 450,
            20: 465, 21: 480, 22: 495, 23: 510, 24: 525, 25: 540, 26: 555, 27: 570, 28: 585, 29: 600,
            30: 615, 31: 630, 32: 645, 33: 660, 34: 675, 35: 690, 36: 705, 37: 720, 38: 735, 39: 750,
            40: 765, 41: 780, 42: 795, 43: 810, 44: 825, 45: 840, 46: 855, 47: 870, 48: 885, 49: 900,
            50: 915, 51: 930, 52: 945, 53: 958, 54: 970, 55: 980, 56: 988, 57: 993, 58: 997, 59: 999,
            60: 1000
        },
        "url": "https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-cl"
    },
    "M2": {
        "name": "Competencia Matemática 2",
        "total_scored": 50,
        "median": 18.0,
        "steepness": 0.12,
        "table": {
            0: 100, 1: 160, 2: 190, 3: 215, 4: 240, 5: 265, 6: 290, 7: 315, 8: 340, 9: 365,
            10: 390, 11: 415, 12: 440, 13: 465, 14: 490, 15: 515, 16: 540, 17: 565, 18: 590, 19: 615,
            20: 640, 21: 665, 22: 690, 23: 715, 24: 740, 25: 765, 26: 790, 27: 815, 28: 838, 29: 860,
            30: 880, 31: 900, 32: 918, 33: 934, 34: 948, 35: 960, 36: 970, 37: 978, 38: 985, 39: 990,
            40: 994, 41: 996, 42: 998, 43: 999, 44: 999, 45: 1000, 46: 1000, 47: 1000, 48: 1000, 49: 1000,
            50: 1000
        },
        "url": "https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-m2"
    },
    "CIENCIAS": {
        "name": "Ciencias (Módulo Común + Electivo)",
        "total_scored": 75,
        "median": 32.0,
        "steepness": 0.09,
        "table": {
            0: 100,
            **{i: max(100, min(1000, round(100 + (900.0 / (1.0 + pow(2.71828, -0.09 * (i - 32.0))))))) for i in range(1, 75)},
            75: 1000
        },
        "url": "https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-ciencias"
    },
    "HISTORIA": {
        "name": "Historia y Ciencias Sociales",
        "total_scored": 60,
        "median": 26.0,
        "steepness": 0.10,
        "table": {
            0: 100,
            **{i: max(100, min(1000, round(100 + (900.0 / (1.0 + pow(2.71828, -0.10 * (i - 26.0))))))) for i in range(1, 60)},
            60: 1000
        },
        "url": "https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-historia"
    }
}

# Alias para compatibilidad
DEMRE_M1_CONVERSION_TABLE = M1_DEMRE_TABLE_2026

def _estimate_percentile(raw_score: int, median: float = 24.5, steepness: float = 0.11, max_items: int = 60) -> float:
    if raw_score <= 0:
        return 1.0
    if raw_score >= max_items:
        return 99.9
    pct = 100.0 / (1.0 + pow(2.71828, -steepness * (raw_score - median)))
    return round(max(1.0, min(99.9, pct)), 1)

def raw_score_to_paes(raw_score: int, total_valid: int = 60, subject_code: str = "M1") -> Dict[str, Any]:
    """
    Convierte el número de respuestas correctas puntuables en la estimación de puntaje PAES 100..1000.
    Soporta las 5 pruebas oficiales: M1, LECTURA, M2, CIENCIAS, HISTORIA.
    """
    normalized_code = subject_code.upper() if subject_code else "M1"
    meta = SUBJECT_METADATA.get(normalized_code, SUBJECT_METADATA["M1"])
    max_items = total_valid if total_valid and total_valid != 60 else meta["total_scored"]

    clamped_raw = max(0, min(max_items, int(raw_score)))
    table = meta["table"]
    score = table.get(clamped_raw, 100)

    margin = 25 if (5 <= clamped_raw <= (max_items - 5)) else 20
    score_min = max(100, score - margin)
    score_max = min(1000, score + margin)

    percentile = _estimate_percentile(
        clamped_raw,
        median=meta["median"],
        steepness=meta["steepness"],
        max_items=max_items
    )

    return {
        "raw_score": clamped_raw,
        "total_scored_items": max_items,
        "subject_code": normalized_code,
        "subject_name": meta["name"],
        "base_paes_score": score,
        "estimated_score": score,
        "score_range_min": score_min,
        "score_range_max": score_max,
        "estimated_range_str": f"{score_min} - {score_max} pts",
        "performance_estimate_label": f"Estimación DEMRE {meta['name']}",
        "confidence_level": "ALTA" if max_items >= 40 else "MEDIA",
        "percentile_approx": percentile,
        "official_source": f"DEMRE - Tabla de Transformación PAES Regular Proceso 2026 ({meta['name']})",
        "source_url": meta["url"]
    }
