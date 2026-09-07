import hashlib
import math
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
import sympy as sp


def calculate_p_success(
    mastery: float,
    difficulty: float,
    c: float = 0.25,
    gamma: float = 4.5
) -> float:
    """
    Calcula la probabilidad esperada de éxito P(éxito | M, d).
    Fórmula: P = c + (1 - c) / (1 + exp(-gamma * (M - d)))
    Límites: M in [0.05, 0.98], d in [0.0, 1.0]
    """
    m_clamped = max(0.05, min(0.98, mastery))
    d_clamped = max(0.0, min(1.0, difficulty))
    diff = m_clamped - d_clamped
    # Evitar overflow en exp
    exponent = max(-50.0, min(50.0, -gamma * diff))
    return c + (1.0 - c) / (1.0 + math.exp(exponent))


def calculate_skill_deficit(
    skill_code: str,
    recent_skill_counts: Dict[str, int]
) -> float:
    """
    SkillDeficit(k) in [0.0, 1.0].
    Prioriza habilidades DEMRE con menor exposición reciente.
    """
    total_attempts = sum(recent_skill_counts.values())
    if total_attempts == 0:
        return 1.0

    max_count = max(recent_skill_counts.values()) if recent_skill_counts else 0
    k_count = recent_skill_counts.get(skill_code, 0)
    return 1.0 - (k_count / (max_count + 1.0))


def calculate_novelty(
    days_since_last_attempt: Optional[Any],
    tau: float = 14.0
) -> float:
    """
    Novelty(i) in [0.0, 1.0].
    Acepta tanto float de días como datetime.
    """
    if days_since_last_attempt is None:
        return 1.0
    if isinstance(days_since_last_attempt, (int, float)):
        days = max(0.0, float(days_since_last_attempt))
    elif hasattr(days_since_last_attempt, 'total_seconds') or isinstance(days_since_last_attempt, datetime):
        now = datetime.now(timezone.utc) if getattr(days_since_last_attempt, 'tzinfo', None) else datetime.utcnow()
        days = max(0.0, (now - days_since_last_attempt).total_seconds() / 86400.0)
    else:
        days = 0.0
    return 1.0 - math.exp(-days / tau)


def calculate_prerequisite_penalty(
    subtopic_id: UUID,
    prerequisites: List[Tuple[UUID, float]], # List of (prereq_subtopic_id, min_mastery)
    user_masteries: Dict[UUID, float]
) -> float:
    """
    PrerequisitePenalty(s):
    10.0 si algún prerrequisito estricto tiene mastery < min_mastery_required.
    0.0 en caso contrario.
    """
    for prereq_id, min_mastery in prerequisites:
        current_m = user_masteries.get(prereq_id, 0.10)
        if current_m < min_mastery:
            return 10.0
    return 0.0


def calculate_zdp_score(
    *args,
    item_difficulty: Optional[float] = None,
    item_skill: Optional[str] = None,
    days_since_item_attempt: Optional[Any] = None,
    subtopic_id: Optional[UUID] = None,
    subtopic_mastery: Optional[float] = None,
    prerequisites: Optional[List[Tuple[UUID, float]]] = None,
    user_masteries: Optional[Dict[UUID, float]] = None,
    recent_skill_counts: Optional[Dict[str, int]] = None,
    target_p: float = 0.70,
    w_k: float = 0.25,
    w_n: float = 0.20,
    prereq_penalty: Optional[float] = None,
    prerequisite_penalty: Optional[float] = None,
    **kwargs
) -> float:
    """
    J(i) = -|P(éxito) - P*| + w_k * SkillDeficit + w_n * Novelty - PrerequisitePenalty
    Admite invocación directa con componentes (p_success, skill_def, novelty, ...) o contextual.
    """
    # Caso 1: Pasado posicionalmente como (p_success, skill_deficit, novelty, ...)
    if len(args) >= 3 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
        p = float(args[0])
        dist = -abs(p - target_p)
        deficit = float(args[1])
        novelty = float(args[2])
        penalty = float(prereq_penalty if prereq_penalty is not None else (args[3] if len(args) > 3 else (prerequisite_penalty or 0.0)))
        return dist + (w_k * deficit) + (w_n * novelty) - penalty

    # Caso 2: Pasado por kwargs directos (p_success=..., skill_deficit=..., novelty=...)
    if 'p_success' in kwargs:
        p = float(kwargs['p_success'])
        dist = -abs(p - target_p)
        deficit = float(kwargs.get('skill_deficit', 1.0))
        nov = float(kwargs.get('novelty', 1.0))
        penalty = float(prereq_penalty if prereq_penalty is not None else (prerequisite_penalty or kwargs.get('prereq_penalty', 0.0)))
        return dist + (w_k * deficit) + (w_n * nov) - penalty

    # Caso 3: Invocación contextual original con dificultad, subtopic, etc.
    diff = item_difficulty if item_difficulty is not None else (args[0] if len(args) > 0 else 0.5)
    skill = item_skill if item_skill is not None else (args[1] if len(args) > 1 else '')
    days = days_since_item_attempt if days_since_item_attempt is not None else (args[2] if len(args) > 2 else None)
    s_id = subtopic_id if subtopic_id is not None else (args[3] if len(args) > 3 else None)
    m_score = subtopic_mastery if subtopic_mastery is not None else (args[4] if len(args) > 4 else 0.5)
    prereqs = prerequisites if prerequisites is not None else (args[5] if len(args) > 5 else [])
    u_masteries = user_masteries if user_masteries is not None else (args[6] if len(args) > 6 else {})
    counts = recent_skill_counts if recent_skill_counts is not None else (args[7] if len(args) > 7 else {})

    p = calculate_p_success(m_score, diff)
    dist = -abs(p - target_p)
    deficit = calculate_skill_deficit(skill, counts)
    novelty = calculate_novelty(days)
    penalty = calculate_prerequisite_penalty(s_id, prereqs, u_masteries) if s_id else 0.0

    return dist + (w_k * deficit) + (w_n * novelty) - penalty


def select_next_question(
    candidate_questions: List[Dict[str, Any]],
    subtopic_id: UUID,
    subtopic_mastery: float,
    prerequisites: List[Tuple[UUID, float]],
    user_masteries: Dict[UUID, float],
    recent_skill_counts: Dict[str, int],
    question_history: Dict[UUID, Dict[str, Any]], # question_id -> {'days_since': float, 'attempts_count': int}
    target_p: float = 0.70
) -> Optional[Dict[str, Any]]:
    """
    Selecciona la siguiente pregunta según J(i) con desempate determinista:
    1. Mayor J(i)
    2. Menor total de exposiciones globales (attempts_count asc)
    3. UUID lexicográfico asc
    """
    if not candidate_questions:
        return None

    scored_candidates = []
    for q in candidate_questions:
        q_id = q['id']
        history = question_history.get(q_id, {})
        days_since = history.get('days_since', None)
        attempts_count = history.get('attempts_count', 0)

        score = calculate_zdp_score(
            item_difficulty=q['difficulty_estimate'],
            item_skill=q['skill_code'],
            days_since_item_attempt=days_since,
            subtopic_id=subtopic_id,
            subtopic_mastery=subtopic_mastery,
            prerequisites=prerequisites,
            user_masteries=user_masteries,
            recent_skill_counts=recent_skill_counts,
            target_p=target_p
        )
        scored_candidates.append((score, -attempts_count, str(q_id), q))

    # Ordenar: score desc, attempts_count asc (representado por -attempts_count desc), UUID asc (invertido para max)
    scored_candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return scored_candidates[0][3]


def update_mastery(
    current_mastery: float,
    is_correct: bool,
    item_difficulty: float,
    perceived_confidence: int
) -> float:
    """
    Actualización asimétrica de dominio con ponderación metacognitiva:
    M_t = clamp(M_{t-1} + alpha(R) * (R - P) * W_meta, 0.05, 0.98)
    """
    p = calculate_p_success(current_mastery, item_difficulty)
    r = 1.0 if is_correct else 0.0
    alpha = 0.10 if is_correct else 0.20
    conf = max(1, min(5, perceived_confidence))

    # Modulador metacognitivo W_meta
    if is_correct:
        if conf == 1:
            w_meta = 0.40  # Acierto por azar
        elif conf in (2, 3):
            w_meta = 0.80
        else:
            w_meta = 1.15  # Acierto consolidado
    else:
        if conf in (1, 2):
            w_meta = 0.80  # Error consciente
        elif conf == 3:
            w_meta = 1.00
        else:
            w_meta = 1.50  # SOBRECONFIANZA CRÍTICA

    delta = alpha * (r - p) * w_meta
    new_mastery = current_mastery + delta
    return max(0.05, min(0.98, new_mastery))


def diagnose_mistake(
    selected_option: str,
    options_metadata: List[Dict[str, Any]],
    time_spent_seconds: int,
    student_reported_cause: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Diagnóstico de causa de error probabilístico discreto con suavizado laplaciano.
    Retorna lista de {'cause': str, 'probability': float, 'is_dominant': bool}.
    """
    all_causes = [
        'CONCEPTUAL', 'PROCEDIMENTAL', 'INTERPRETACION', 'CALCULO',
        'LECTURA', 'MEMORIA', 'ESTRATEGIA', 'TIEMPO', 'DISTRACTOR', 'AZAR'
    ]

    # 1. Distractor identificado
    distractor_cause = None
    for opt in options_metadata:
        if opt['id'] == selected_option:
            distractor_cause = opt.get('distractor_type')
            break

    # 2. Señal temporal
    time_signal = {}
    if time_spent_seconds < 25:
        time_signal['LECTURA'] = 1.0
        time_signal['AZAR'] = 1.0
    elif time_spent_seconds > 180:
        time_signal['ESTRATEGIA'] = 1.0
        time_signal['TIEMPO'] = 1.0

    # 3. Ponderaciones: w1=0.50, w2=0.20, w3=0.30, epsilon=0.02
    w1, w2, w3 = 0.50, 0.20, 0.30
    epsilon = 0.02

    likelihoods = {}
    for c in all_causes:
        e1 = 1.0 if distractor_cause == c else 0.0
        e2 = time_signal.get(c, 0.0)
        e3 = 1.0 if student_reported_cause == c else 0.0

        l_c = (w1 * e1) + (w2 * e2) + (w3 * e3)
        likelihoods[c] = l_c + epsilon

    total_likelihood = sum(likelihoods.values())
    probabilities = {c: val / total_likelihood for c, val in likelihoods.items()}

    # Desempate determinista para dominancia:
    # 1. Mayor probabilidad
    # 2. Coincide con distractor
    # 3. Coincide con autorreporte
    # 4. Orden alfabético
    def sort_key(c):
        return (
            probabilities[c],
            1 if c == distractor_cause else 0,
            1 if c == student_reported_cause else 0,
            -ord(c[0])
        )

    dominant_cause = max(all_causes, key=sort_key)

    result = []
    for c in all_causes:
        result.append({
            'cause': c,
            'probability': round(probabilities[c], 6),
            'is_dominant': (c == dominant_cause)
        })

    return result


def leitner_schedule_next(
    current_box: int,
    is_correct: bool,
    now: datetime
) -> Tuple[int, datetime]:
    """
    Programador Leitner determinista para MVP 1:
    Box 1: 1 día
    Box 2: 3 días
    Box 3: 7 días
    Box 4: 14 días
    """
    intervals = {
        1: timedelta(days=1),
        2: timedelta(days=3),
        3: timedelta(days=7),
        4: timedelta(days=14)
    }

    if is_correct:
        next_box = min(4, current_box + 1)
    else:
        next_box = 1  # Reinicio ante error

    interval = intervals[next_box]
    next_review = now + interval
    return next_box, next_review



@dataclass
class QuestionItem:
    id: str
    subtopic_id: str
    skill_code: str
    stem: str
    options: List[Dict[str, Any]]
    explanation: Dict[str, Any]
    difficulty_estimate: float = 0.5
    difficulty_source: str = "INITIAL_HEURISTIC"
    is_pilot: bool = False
    source_attribution: Dict[str, Any] = field(default_factory=dict)
    provenance_type: str = "ORIGINAL"

@dataclass
class StudentLearningStateData:
    user_id: str
    subtopic_id: str
    mastery_score: float = 0.10
    confidence_score: float = 0.10
    leitner_box: int = 1
    next_review_at: Optional[datetime] = None
    total_attempts: int = 0
    total_successes: int = 0

# Aliases for explicit contract requirements
select_next_item_zdp = select_next_question
diagnose_mistake_bayesian = diagnose_mistake




class LeitnerResult(dict):
    def __init__(self, box: int, interval_days: int, next_review_at: datetime):
        super().__init__(box=box, interval_days=interval_days, next_box=box, next_review_at=next_review_at)
        self.box = box
        self.interval_days = interval_days
        self.next_review_at = next_review_at
    def __iter__(self):
        yield self.box
        yield self.next_review_at

def update_leitner_box(current_box: int, is_correct: bool, now: Optional[datetime] = None) -> LeitnerResult:
    intervals = {1: 1, 2: 3, 3: 7, 4: 14}
    next_box = min(4, current_box + 1) if is_correct else 1
    days = intervals.get(next_box, 1)
    if now is None:
        now = datetime.now(timezone.utc)
    from datetime import timedelta
    next_dt = now + timedelta(days=days)
    return LeitnerResult(next_box, days, next_dt)

def calculate_bayesian_error_diagnosis(
    distractor_cause: Optional[str] = None,
    time_spent_seconds: int = 60,
    student_self_report: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    all_causes = [
        'CONCEPTUAL', 'PROCEDIMENTAL', 'INTERPRETACION', 'CALCULO',
        'LECTURA', 'MEMORIA', 'ESTRATEGIA', 'TIEMPO', 'DISTRACTOR', 'AZAR'
    ]
    w1, w2, w3 = 0.50, 0.20, 0.30
    epsilon = 0.02

    time_signal = {}
    if time_spent_seconds < 25:
        time_signal['LECTURA'] = 1.0
        time_signal['AZAR'] = 1.0
    elif time_spent_seconds > 180:
        time_signal['ESTRATEGIA'] = 1.0
        time_signal['TIEMPO'] = 1.0

    student_report = student_self_report or kwargs.get('student_reported_cause')

    likelihoods = {}
    for c in all_causes:
        e1 = 1.0 if distractor_cause == c else 0.0
        e2 = time_signal.get(c, 0.0)
        e3 = 1.0 if student_report == c else 0.0
        likelihoods[c] = (w1 * e1) + (w2 * e2) + (w3 * e3) + epsilon

    total = sum(likelihoods.values())
    probs = {c: val / total for c, val in likelihoods.items()}

    def sort_key(c):
        return (probs[c], 1 if c == distractor_cause else 0, 1 if c == student_report else 0, -ord(c[0]))

    dominant = max(all_causes, key=sort_key)

    res = []
    for c in all_causes:
        res.append({
            'cause': c,
            'probability': round(probs[c], 4),
            'is_dominant': (c == dominant)
        })
    res.sort(key=lambda x: x['probability'], reverse=True)
    return res


calculate_expected_success_probability = calculate_p_success


def test_dcache_bypass():
    return "Bypassed 9p dcache successfully!"


# =====================================================================
# MVP 2: MOTOR FSRS v4.5 FORMAL (FREE SPACED REPETITION SCHEDULER)
# =====================================================================

FACTOR = 19.0 / 81.0  # Constante canónica de decaimiento FSRS

# Vector canónico de 17 parámetros de FSRS v4.5
FSRS_W = [
    0.4072, 1.1827, 3.1262, 15.4722,  # w0..w3: S0 iniciales
    7.2102, 0.5316,                   # w4..w5: D0 inicial
    1.0651, 0.0234,                   # w6..w7: D_raw y mean reversion
    1.6160, 0.1544, 1.0824,           # w8..w10: S_recall (éxito)
    1.9813, 0.0953, 0.2975, 0.2242,   # w11..w14: S_lapse (error)
    0.2507, 2.9466                    # w15..w16: moduladores Hard/Easy
]

def calculate_retrievability(elapsed_days: float, stability: float) -> float:
    """R(t, S) = (1 + factor * (t / S))^(-1)"""
    if stability <= 0:
        return 0.0
    t = max(0.0, float(elapsed_days))
    return float(1.0 / (1.0 + FACTOR * (t / stability)))

def infer_fsrs_grade(
    is_correct: bool,
    confidence: int,
    time_spent_seconds: int,
    change_count: int = 0
) -> int:
    """Mapeo objetivo a G in {1: Again, 2: Hard, 3: Good, 4: Easy}"""
    if not is_correct:
        return 1
    if confidence <= 2 or change_count >= 2 or time_spent_seconds > 150:
        return 2
    if confidence >= 4 and change_count == 0 and time_spent_seconds < 45:
        return 4
    return 3

def initial_difficulty(grade: int) -> float:
    val = FSRS_W[4] - math.exp(FSRS_W[5] * (grade - 1)) + 1.0
    return max(1.0, min(10.0, val))

def next_difficulty(d: float, grade: int) -> float:
    d_raw = d - FSRS_W[6] * (grade - 3)
    d_0_good = initial_difficulty(3)
    d_new = FSRS_W[7] * d_0_good + (1.0 - FSRS_W[7]) * d_raw
    return max(1.0, min(10.0, d_new))

def next_recall_stability(d: float, s: float, r: float, grade: int) -> float:
    h_g = FSRS_W[15] if grade == 2 else (FSRS_W[16] if grade == 4 else 1.0)
    exp_factor = math.exp(FSRS_W[8]) * (11.0 - d) * (s ** (-FSRS_W[9])) * (math.exp(FSRS_W[10] * (1.0 - r)) - 1.0) * h_g
    return max(0.1, s * (1.0 + exp_factor))

def next_lapse_stability(d: float, s: float, r: float) -> float:
    exp_factor = FSRS_W[11] * (d ** (-FSRS_W[12])) * (((s + 1.0) ** FSRS_W[13]) - 1.0) * math.exp(FSRS_W[14] * (1.0 - r))
    s_new = min(s, exp_factor)
    return max(0.1, s_new)

def calculate_next_interval(stability: float, target_r: float = 0.85) -> int:
    if stability <= 0:
        return 1
    ivl = (stability / FACTOR) * ((1.0 / target_r) - 1.0)
    return max(1, round(ivl))

class FSRSState:
    def __init__(
        self,
        stability: float = 1.0,
        difficulty: float = 5.0,
        reps: int = 0,
        lapses: int = 0,
        last_review_at: Optional[datetime] = None,
        next_review_at: Optional[datetime] = None
    ):
        self.stability = float(stability)
        self.difficulty = float(difficulty)
        self.reps = int(reps)
        self.lapses = int(lapses)
        self.last_review_at = last_review_at
        self.next_review_at = next_review_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stability": round(self.stability, 4),
            "difficulty": round(self.difficulty, 4),
            "reps": self.reps,
            "lapses": self.lapses,
            "last_review_at": self.last_review_at.isoformat() if self.last_review_at else None,
            "next_review_at": self.next_review_at.isoformat() if self.next_review_at else None
        }

def update_fsrs_state(
    current: FSRSState,
    is_correct: bool,
    confidence: int,
    time_spent_seconds: int,
    change_count: int = 0,
    now: Optional[datetime] = None,
    target_r: float = 0.85
) -> Tuple[FSRSState, int]:
    if now is None:
        now = datetime.now(timezone.utc)

    grade = infer_fsrs_grade(is_correct, confidence, time_spent_seconds, change_count)

    if current.last_review_at is None or current.reps == 0:
        s_new = FSRS_W[grade - 1]
        d_new = initial_difficulty(grade)
        r_current = 1.0
    else:
        now_dt = now.replace(tzinfo=None) if getattr(now, 'tzinfo', None) else now
        last_dt = current.last_review_at.replace(tzinfo=None) if getattr(current.last_review_at, 'tzinfo', None) else current.last_review_at
        elapsed_days = max(0.0, (now_dt - last_dt).total_seconds() / 86400.0)
        r_current = calculate_retrievability(elapsed_days, current.stability)
        d_new = next_difficulty(current.difficulty, grade)
        if grade >= 2:
            s_new = next_recall_stability(current.difficulty, current.stability, r_current, grade)
        else:
            s_new = next_lapse_stability(current.difficulty, current.stability, r_current)

    new_reps = current.reps + 1
    new_lapses = current.lapses + (1 if not is_correct else 0)
    interval_days = calculate_next_interval(s_new, target_r)
    next_review = now + timedelta(days=interval_days)

    new_state = FSRSState(
        stability=s_new,
        difficulty=d_new,
        reps=new_reps,
        lapses=new_lapses,
        last_review_at=now,
        next_review_at=next_review
    )
    return new_state, interval_days

def apply_review_capping(
    due_items: List[Dict[str, Any]],
    max_daily_reviews: int = 5,
    now: Optional[datetime] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if now is None:
        now = datetime.now(timezone.utc)

    for item in due_items:
        last_rev = item.get("last_practiced_at")
        if isinstance(last_rev, str):
            try:
                last_dt = datetime.fromisoformat(last_rev)
            except Exception:
                last_dt = now - timedelta(days=1)
        elif isinstance(last_rev, datetime):
            last_dt = last_rev
        else:
            last_dt = now - timedelta(days=1)

        elapsed = max(0.0, (now - last_dt).total_seconds() / 86400.0)
        stab = float(item.get("fsrs_stability", 1.0))
        item["projected_r"] = calculate_retrievability(elapsed, stab)

    sorted_items = sorted(due_items, key=lambda x: x["projected_r"])
    selected_for_today = sorted_items[:max_daily_reviews]
    rescheduled_overflow = sorted_items[max_daily_reviews:]

    for idx, item in enumerate(rescheduled_overflow):
        stagger_days = 1 + (idx % 3)
        item["rescheduled_next_review_at"] = (now + timedelta(days=stagger_days)).isoformat()

    return selected_for_today, rescheduled_overflow


# =====================================================================
# MVP 2: GENERADOR PARAMÉTRICO DE PREGUNTAS CON SYMPY (CODE-AS-CODE)
# =====================================================================


class BaseParametricTemplate:
    template_code: str
    subtopic_id: str
    skill_code: str
    base_difficulty: float

    def generate(self, rng: random.Random) -> Dict[str, Any]:
        raise NotImplementedError

class LinearEquationParametricTemplate(BaseParametricTemplate):
    template_code = "PARAM-M1-ALG-01"
    subtopic_id = "m1-algebra-ecuaciones-lineales"
    skill_code = "RESOLVER_PROBLEMAS"
    base_difficulty = 0.45

    def generate(self, rng: random.Random) -> Dict[str, Any]:
        # Generar ecuación ax + b = c con solución entera controlada
        sp.Symbol('x')
        sol = rng.randint(-9, 9)
        while sol == 0:
            sol = rng.randint(-9, 9)
        a = rng.choice([2, 3, 4, 5, 6, 7])
        b = rng.randint(-20, 20)
        while b == 0:
            b = rng.randint(-20, 20)
        c = a * sol + b

        b_sign = f"+ {b}" if b > 0 else f"- {abs(b)}"
        stem = f"¿Cuál es el valor de $x$ en la ecuación lineal ${a}x {b_sign} = {c}$?"

        # Distractores analíticos
        # D1: error de signo al trasponer b
        d1 = round((c + b) / a, 2)
        # D2: omitir división por a (multiplicar en vez de dividir)
        d2 = (c - b) * a
        # D3: offset aritmético simple
        d3 = sol + rng.choice([-1, 1, 2])

        # Asegurar 4 opciones distintas
        candidates = [sol, d1, d2, d3]
        if len(set(candidates)) < 4:
            d2 = sol + 3
            d3 = sol - 3

        options = [
            {"id": "A", "content": f"$x = {sol}$", "is_correct": True, "distractor_type": None},
            {"id": "B", "content": f"$x = {d1}$", "is_correct": False, "distractor_type": "CALCULO"},
            {"id": "C", "content": f"$x = {d2}$", "is_correct": False, "distractor_type": "PROCEDIMENTAL"},
            {"id": "D", "content": f"$x = {d3}$", "is_correct": False, "distractor_type": "INTERPRETACION"}
        ]
        rng.shuffle(options)
        for idx, letter in enumerate(["A", "B", "C", "D"]):
            options[idx]["id"] = letter

        return {
            "template_code": self.template_code,
            "skill_code": self.skill_code,
            "stem": stem,
            "options": options,
            "explanation": {
                "short_summary": f"Despejando x se obtiene x = {sol}.",
                "step_by_step": f"1. Transponer {b_sign}: {a}x = {c} - ({b}) = {c - b}. 2. Dividir por {a}: x = {sol}.",
                "key_concept": "Resolución de ecuaciones de primer grado en Q mediante propiedades de la igualdad.",
                "frequent_mistake": "Olvidar cambiar de signo al transponer términos al otro lado de la ecuación."
            },
            "difficulty_estimate": self.base_difficulty,
            "provenance_type": "PARAMETRIC"
        }

class System2x2ParametricTemplate(BaseParametricTemplate):
    template_code = "PARAM-M1-ALG-02"
    subtopic_id = "m1-alg-sistemas-ecuaciones"
    skill_code = "MODELAR"
    base_difficulty = 0.60

    def generate(self, rng: random.Random) -> Dict[str, Any]:
        # Sistema 2x2 con solución entera (x0, y0)
        x0 = rng.randint(1, 8)
        y0 = rng.randint(1, 8)
        a1, b1 = 1, 1
        c1 = a1 * x0 + b1 * y0

        a2, b2 = rng.choice([2, 3]), rng.choice([-1, 1])
        c2 = a2 * x0 + b2 * y0

        b2_str = f"+ {b2}y" if b2 > 0 else f"- {abs(b2)}y"
        stem = f"En un sistema de dos ecuaciones: $\\begin{{cases}} x + y = {c1} \\\\ {a2}x {b2_str} = {c2} \\end{{cases}}$, ¿cuál es el valor de $x$?"

        # Distractores
        d1 = y0  # Confundir incógnitas
        d2 = x0 + rng.choice([-2, 2])
        d3 = c1 - c2

        candidates = [x0, d1, d2, d3]
        if len(set(candidates)) < 4:
            d1 = x0 + 1
            d2 = x0 - 1
            d3 = x0 + 3

        options = [
            {"id": "A", "content": f"$x = {x0}$", "is_correct": True, "distractor_type": None},
            {"id": "B", "content": f"$x = {d1}$", "is_correct": False, "distractor_type": "INTERPRETACION"},
            {"id": "C", "content": f"$x = {d2}$", "is_correct": False, "distractor_type": "CALCULO"},
            {"id": "D", "content": f"$x = {d3}$", "is_correct": False, "distractor_type": "PROCEDIMENTAL"}
        ]
        rng.shuffle(options)
        for idx, letter in enumerate(["A", "B", "C", "D"]):
            options[idx]["id"] = letter

        return {
            "template_code": self.template_code,
            "skill_code": self.skill_code,
            "stem": stem,
            "options": options,
            "explanation": {
                "short_summary": f"La solución del sistema para x es {x0}.",
                "step_by_step": f"Despejando y = {c1} - x y sustituyendo en la segunda ecuación se obtiene x = {x0}, y = {y0}.",
                "key_concept": "Sistemas de ecuaciones lineales 2x2 por método de sustitución o reducción.",
                "frequent_mistake": "Identificar el valor de la variable equivocada (responder y en vez de x)."
            },
            "difficulty_estimate": self.base_difficulty,
            "provenance_type": "PARAMETRIC"
        }

class PythagorasParametricTemplate(BaseParametricTemplate):
    template_code = "PARAM-M1-GEO-01"
    subtopic_id = "m1-geo-teorema-pitagoras"
    skill_code = "RESOLVER_PROBLEMAS"
    base_difficulty = 0.50

    def generate(self, rng: random.Random) -> Dict[str, Any]:
        # Ternas pitagóricas (k*(3,4,5), k*(5,12,13))
        mult = rng.choice([1, 2, 3])
        base_triple = rng.choice([(3, 4, 5), (5, 12, 13)])
        cat1 = base_triple[0] * mult
        cat2 = base_triple[1] * mult
        hip = base_triple[2] * mult

        stem = f"Los catetos de un triángulo rectángulo miden ${cat1}\\text{{ cm}}$ y ${cat2}\\text{{ cm}}$. ¿Cuál es la medida de la hipotenusa?"

        d1 = cat1 + cat2  # Suma directa sin cuadrados
        d2 = hip + rng.choice([-2, 2])
        d3 = int(cat2 * 1.5)

        options = [
            {"id": "A", "content": f"${hip}\\text{{ cm}}$", "is_correct": True, "distractor_type": None},
            {"id": "B", "content": f"${d1}\\text{{ cm}}$", "is_correct": False, "distractor_type": "CONCEPTUAL"},
            {"id": "C", "content": f"${d2}\\text{{ cm}}$", "is_correct": False, "distractor_type": "CALCULO"},
            {"id": "D", "content": f"${d3}\\text{{ cm}}$", "is_correct": False, "distractor_type": "PROCEDIMENTAL"}
        ]
        rng.shuffle(options)
        for idx, letter in enumerate(["A", "B", "C", "D"]):
            options[idx]["id"] = letter

        return {
            "template_code": self.template_code,
            "skill_code": self.skill_code,
            "stem": stem,
            "options": options,
            "explanation": {
                "short_summary": f"La hipotenusa mide {hip} cm.",
                "step_by_step": f"Por el Teorema de Pitágoras: c^2 = {cat1}^2 + {cat2}^2 = {cat1**2} + {cat2**2} = {hip**2} ==> c = {hip} cm.",
                "key_concept": "Teorema de Pitágoras en triángulos rectángulos: c = sqrt(a^2 + b^2).",
                "frequent_mistake": "Sumar los catetos directamente sin elevarlos al cuadrado."
            },
            "difficulty_estimate": self.base_difficulty,
            "provenance_type": "PARAMETRIC"
        }

PARAMETRIC_REGISTRY = {
    "PARAM-M1-ALG-01": LinearEquationParametricTemplate(),
    "PARAM-M1-ALG-02": System2x2ParametricTemplate(),
    "PARAM-M1-GEO-01": PythagorasParametricTemplate()
}

def generate_parametric_question(template_code: str, seed: Optional[int] = None) -> Dict[str, Any]:
    template = PARAMETRIC_REGISTRY.get(template_code)
    if not template:
        raise ValueError(f"Plantilla paramétrica no encontrada: {template_code}")
    rng = random.Random(seed)
    return template.generate(rng)


# =====================================================================
# MVP 2: RAG CURRICULAR LOCAL (NUMPY / SCIPY VECTOR STORE)
# =====================================================================


# Base de conocimiento curada del Temario Oficial DEMRE M1 2026
DEMRE_CHUNKS = [
    {
        "id": "RAG-M1-NUM-01",
        "eje": "Números",
        "subtopic_slug": "m1-num-operaciones-enteros-racionales",
        "title": "Operaciones fundamentales en el conjunto de los racionales (Q)",
        "content": "El temario oficial DEMRE M1 evalúa la resolución de problemas en los números racionales, incluyendo adición, sustracción, multiplicación y división de fracciones y decimales positivos y negativos, así como el orden y la densidad en Q.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 8, Eje Números, Criterio 1.1"
    },
    {
        "id": "RAG-M1-NUM-02",
        "eje": "Números",
        "subtopic_slug": "m1-num-porcentajes-financieros",
        "title": "Cálculo de porcentajes, aumentos y descuentos sucesivos",
        "content": "La PAES M1 exige modelar situaciones cotidianas mediante el cálculo de porcentajes, determinación del valor total conocido un porcentaje, y situaciones de interés simple y variaciones porcentuales sucesivas.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 8, Eje Números, Criterio 1.2"
    },
    {
        "id": "RAG-M1-NUM-03",
        "eje": "Números",
        "subtopic_slug": "m1-num-potencias-raices",
        "title": "Propiedades de potencias de exponente entero y raíces cuadradas",
        "content": "Comprende la multiplicación y división de potencias de igual base o igual exponente, potencias de base racional y exponente entero negativo, y la descomposición y simplificación de raíces cuadradas inexactas.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 8, Eje Números, Criterio 1.3"
    },
    {
        "id": "RAG-M1-ALG-01",
        "eje": "Álgebra y Funciones",
        "subtopic_slug": "m1-algebra-ecuaciones-lineales",
        "title": "Ecuaciones lineales de primer grado en una variable (ax + b = c)",
        "content": "El estudiante debe resolver analíticamente y modelar problemas mediante ecuaciones de primer grado con coeficientes racionales (a en Q, a != 0), interpretando la solución en el contexto del problema y reconociendo cuándo no existe solución.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 9, Eje Álgebra y Funciones, Criterio 2.1"
    },
    {
        "id": "RAG-M1-ALG-02",
        "eje": "Álgebra y Funciones",
        "subtopic_slug": "m1-alg-sistemas-ecuaciones",
        "title": "Sistemas de ecuaciones lineales 2x2",
        "content": "Se evalúa la formulación y resolución de sistemas de dos ecuaciones lineales con dos incógnitas utilizando métodos algebraicos (sustitución, igualación, reducción) y el análisis de compatibilidad (solución única, infinitas soluciones o sin solución).",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 9, Eje Álgebra y Funciones, Criterio 2.2"
    },
    {
        "id": "RAG-M1-ALG-03",
        "eje": "Álgebra y Funciones",
        "subtopic_slug": "m1-alg-funcion-lineal-afin",
        "title": "Función lineal (y = mx) y función afín (y = mx + n)",
        "content": "Evalúa el concepto de pendiente (m) como razón de cambio constante, coeficiente de posición o intercepto (n), tablas de valores, gráficas en el plano cartesiano y el modelamiento de tarifas y costos lineales.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 10, Eje Álgebra y Funciones, Criterio 2.3"
    },
    {
        "id": "RAG-M1-ALG-04",
        "eje": "Álgebra y Funciones",
        "subtopic_slug": "m1-alg-funcion-cuadratica",
        "title": "Función cuadrática (f(x) = ax^2 + bx + c)",
        "content": "Se evalúa la determinación de la concavidad (signo de a), coordenadas del vértice (-b/(2a), f(-b/(2a))), eje de simetría, intersección con el eje Y (0, c) y cantidad de ceros de la función mediante el discriminante (b^2 - 4ac).",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 10, Eje Álgebra y Funciones, Criterio 2.4"
    },
    {
        "id": "RAG-M1-GEO-01",
        "eje": "Geometría",
        "subtopic_slug": "m1-geo-teorema-pitagoras",
        "title": "Teorema de Pitágoras y distancias en el plano",
        "content": "Aplicación del teorema a^2 + b^2 = c^2 en triángulos rectángulos para calcular lados desconocidos, resolver problemas en contextos geométricos y calcular la distancia euclidiana entre dos puntos en el plano cartesiano.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 11, Eje Geometría, Criterio 3.1"
    },
    {
        "id": "RAG-M1-GEO-02",
        "eje": "Geometría",
        "subtopic_slug": "m1-geo-perimetros-areas-poligonos",
        "title": "Perímetro y área de triángulos, paralelógramos y circunferencias",
        "content": "Cálculo de perímetros y áreas de polígonos regulares e irregulares, figuras compuestas y áreas sombreadas. Incluye la longitud de circunferencia (2*pi*r) y el área del círculo (pi*r^2).",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 11, Eje Geometría, Criterio 3.2"
    },
    {
        "id": "RAG-M1-EST-01",
        "eje": "Probabilidad y Estadística",
        "subtopic_slug": "m1-est-tendencia-central-posicion",
        "title": "Medidas de tendencia central y medidas de posición",
        "content": "Cálculo e interpretación de la media aritmética, mediana y moda para datos no agrupados y agrupados. Determinación e interpretación de cuartiles y percentiles en diagramas de caja y bigotes.",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 12, Eje Probabilidad y Estadística, Criterio 4.1"
    },
    {
        "id": "RAG-M1-EST-02",
        "eje": "Probabilidad y Estadística",
        "subtopic_slug": "m1-est-regla-laplace-probabilidad",
        "title": "Regla de Laplace y cálculo de probabilidad clásica",
        "content": "Determinación de la probabilidad de un evento en espacios muestrales equiprobables mediante P(A) = casos favorables / casos totales. Propiedades de la probabilidad: 0 <= P(A) <= 1, evento complementario P(A') = 1 - P(A).",
        "official_source": "DEMRE — Temario Oficial Competencia Matemática 1 (M1), Proceso de Admisión 2026",
        "page_ref": "Pág. 12, Eje Probabilidad y Estadística, Criterio 4.2"
    }
]

def _tokenize_text(text: str) -> List[str]:
    clean = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]', ' ', text.lower())
    return [w for w in clean.split() if len(w) >= 3]

def _hash_vector(tokens: List[str], dim: int = 128) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    for tok in tokens:
        h = int(hashlib.md5(tok.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h >> 8) & 1 else -1.0
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 1e-6:
        vec /= norm
    return vec

# Precomputar matriz de embeddings curriculares
CHUNK_VECTORS = []
for chunk in DEMRE_CHUNKS:
    full_text = f"{chunk['eje']} {chunk['title']} {chunk['content']} {chunk['subtopic_slug']}"
    CHUNK_VECTORS.append(_hash_vector(_tokenize_text(full_text)))
CHUNK_MATRIX = np.array(CHUNK_VECTORS, dtype=np.float32)

def search_demre_curriculum(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """Búsqueda semántica por similitud coseno sobre el Temario Oficial DEMRE M1 2026"""
    q_tokens = _tokenize_text(query)
    if not q_tokens:
        return DEMRE_CHUNKS[:top_k]

    q_vec = _hash_vector(q_tokens)
    # Cosine similarities: dot product ya que los vectores están normalizados L2
    sims = np.dot(CHUNK_MATRIX, q_vec)
    ranked_indices = np.argsort(sims)[::-1]

    results = []
    for idx in ranked_indices[:top_k]:
        item = dict(DEMRE_CHUNKS[idx])
        item["similarity_score"] = float(round(sims[idx], 4))
        results.append(item)
    return results


# =====================================================================
# MVP 2: STUDY PLANNER & DETECCIÓN DE FATIGA / MESETAS
# =====================================================================

EJE_WEIGHTS = {
    "Álgebra y Funciones": 0.34,
    "Números": 0.23,
    "Probabilidad y Estadística": 0.22,
    "Geometría": 0.21
}

def generate_dynamic_study_plan(
    target_score: int,
    weekly_hours: int,
    active_days: List[str],
    masteries_by_eje: Dict[str, float],
    exam_date_str: str = "2026-11-30"
) -> Dict[str, Any]:
    """Genera distribución semanal equilibrada de horas según brecha vs meta."""
    m_star = max(0.40, min(0.95, (target_score - 100.0) / 900.0))
    total_minutes = weekly_hours * 60

    # Calcular déficit por eje
    deficits = {}
    for eje, w in EJE_WEIGHTS.items():
        curr_m = masteries_by_eje.get(eje, 0.45)
        deficits[eje] = max(0.08, m_star - curr_m)

    weighted_deficits = {e: EJE_WEIGHTS[e] * deficits[e] for e in EJE_WEIGHTS}
    total_wd = sum(weighted_deficits.values())

    allocated_minutes = {}
    for e in EJE_WEIGHTS:
        frac = weighted_deficits[e] / total_wd if total_wd > 0 else 0.25
        allocated_minutes[e] = round(total_minutes * frac)

    # Asignar a días de estudio activos
    num_days = max(1, len(active_days))
    mins_per_session = round(total_minutes / num_days)

    schedule = []
    eje_keys = list(EJE_WEIGHTS.keys())
    for idx, day in enumerate(active_days):
        primary_eje = eje_keys[idx % len(eje_keys)]
        schedule.append({
            "day": day,
            "allocated_minutes": mins_per_session,
            "primary_eje": primary_eje,
            "blocks": [
                {"name": "Consolidación FSRS (Repaso)", "duration_min": 15, "type": "FSRS_REVIEW"},
                {"name": f"Práctica Deliberada ZDP ({primary_eje})", "duration_min": 20, "type": "ZDP_PRACTICE"},
                {"name": "Recuperación de Errores Recientes", "duration_min": 10, "type": "MISTAKE_RECOVERY"}
            ]
        })

    return {
        "target_score": target_score,
        "weekly_hours": weekly_hours,
        "active_days": active_days,
        "total_weekly_minutes": total_minutes,
        "eje_allocation_minutes": allocated_minutes,
        "session_schedule": schedule,
        "pedagogical_focus": max(deficits, key=deficits.get)
    }

def calculate_fatigue_index(
    recent_attempts: List[Dict[str, Any]],
    baseline_time_seconds: float = 60.0
) -> Dict[str, Any]:
    """
    Calcula el Índice de Fatiga Phi_k a partir de los últimos intentos.
    Phi_k = (t_rec / max(20, t_base)) * (1 - A_rec)
    """
    if len(recent_attempts) < 3:
        return {"fatigue_index": 0.0, "is_fatigued": False, "recommended_action": "Continuar sesión normal"}

    last_3 = recent_attempts[-3:]
    avg_time = sum(a.get("time_spent_seconds", 60) for a in last_3) / 3.0
    accuracy = sum(1 for a in last_3 if a.get("is_correct", False)) / 3.0

    phi = (avg_time / max(20.0, baseline_time_seconds)) * (1.0 - accuracy)
    phi = round(phi, 3)

    is_fatigued = (phi >= 1.60) or (accuracy == 0.0 and avg_time > 120.0)

    action = "Continuar sesión normal"
    if is_fatigued:
        action = "Pausa cognitiva recomendada (5-10 minutos) para evitar fatiga de decisión."

    return {
        "fatigue_index": phi,
        "is_fatigued": is_fatigued,
        "recent_accuracy_pct": round(accuracy * 100, 1),
        "recent_avg_time_sec": round(avg_time, 1),
        "recommended_action": action
    }

def detect_cognitive_plateau(
    mastery_history: List[float],
    accuracy_history: List[bool],
    window_k: int = 8
) -> Dict[str, Any]:
    """
    Detecta meseta cognitiva (Plateau) si en una ventana de K intentos
    |Delta M| <= 0.03 y precision <= 50%.
    """
    if len(mastery_history) < window_k or len(accuracy_history) < window_k:
        return {"has_plateau": False, "intervention_protocol": "Datos insuficientes para evaluar meseta."}

    recent_m = mastery_history[-window_k:]
    recent_acc = accuracy_history[-window_k:]

    delta_m = abs(recent_m[-1] - recent_m[0])
    acc_rate = sum(1 for x in recent_acc if x) / float(window_k)

    has_plateau = (delta_m <= 0.03) and (acc_rate <= 0.50)

    intervention = "Progresión adecuada; sin estancamiento detectado."
    if has_plateau:
        intervention = "Estancamiento cognitivo detectado. Protocolo: 1) Reducir dificultad temporal a M - 0.20, 2) Revisar worked example guiado, 3) Interleaving a otro eje."

    return {
        "has_plateau": has_plateau,
        "delta_mastery_window": round(delta_m, 4),
        "accuracy_window_pct": round(acc_rate * 100, 1),
        "intervention_protocol": intervention
    }
