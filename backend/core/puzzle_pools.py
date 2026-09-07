"""Static puzzle pools for level 1 — daily-life scenarios for mathematical thinking.

Used as a fast, deterministic alternative to AI generation for level 1.
Rotates through puzzles per session to avoid repetition within the same
session, then starts over once all puzzles have been shown.

The math level 1 pool is built from real everyday situations (shopping,
money, food, time-saving). The user practices mathematical THINKING
through scenarios they actually face — math emerges as a tool, not as
the topic. For level 2+ the AI path is used with persona-based prompts
that put the user in the mindset of a swimmer, chess player, teacher,
etc. (see ``skills/math-thinking.yaml`` and ``core/math_thinking.py``).
"""

from __future__ import annotations

import copy
import random
from collections import OrderedDict
from typing import Optional

# Skill_type -> level -> ordered list of puzzle dicts.
#
# Each entry MUST include a ``source`` field citing the verified
# fact/study the puzzle is built on. The source is surfaced to the user
# in the response so they can learn where the data comes from.
PUZZLE_POOLS: dict[str, dict[int, list[dict]]] = {
    # --- IQ Practice -----------------------------------------------------------
    "iq_practice": {
        1: [
            # ---- 4 number_sequence -----------------------------------------
            {
                "puzzle_type": "number_sequence",
                "question": "¿Qué número sigue en la secuencia? 88, 70, 60, 50, ?",
                "options": ["40", "30", "45", "55"],
                "correct_answer": "40",
                "explanation": (
                    "La secuencia disminuye aproximadamente de a 10 cada paso "
                    "(88, 70, 60, 50, 40). Corresponde a velocidades en km/h "
                    "de algunos de los animales más rápidos del mundo."
                ),
                "source": (
                    "Datos zoológicos estándar (velocidades en km/h: "
                    "halcón peregrino en vuelo nivelado, león, gacela, "
                    "antílope, conejo)"
                ),
            },
            {
                "puzzle_type": "number_sequence",
                "question": "¿Qué número sigue? 8.85, 8.61, 8.58, 8.52, ?",
                "options": [
                    "8.46 (Makalu)",
                    "8.0 (Cho Oyu)",
                    "9.0",
                    "7.5",
                ],
                "correct_answer": "8.46 (Makalu)",
                "explanation": (
                    "Estas son las alturas en km de las cinco montañas "
                    "más altas del mundo: Everest, K2, Kangchenjunga, "
                    "Lhotse y Makalu."
                ),
                "source": "Britannica, 'Highest mountains on Earth'",
            },
            {
                "puzzle_type": "number_sequence",
                "question": "¿Qué número sigue en la secuencia? 3, 6, 12, 24, ?",
                "options": ["48", "36", "32", "50"],
                "correct_answer": "48",
                "explanation": (
                    "Cada término se obtiene multiplicando el anterior por 2: "
                    "3×2=6, 6×2=12, 12×2=24, 24×2=48. Es una progresión "
                    "geométrica con razón 2."
                ),
                "source": "Patrón matemático de progresión geométrica binaria",
            },
            {
                "puzzle_type": "number_sequence",
                "question": "¿Qué número sigue? 2.71, 2.718, 2.7182, ?",
                "options": ["2.71828", "2.7183", "2.7184", "2.72"],
                "correct_answer": "2.71828",
                "explanation": (
                    "Son aproximaciones crecientes del número e "
                    "(constante de Euler): 2.71, 2.718, 2.7182, 2.71828..."
                ),
                "source": "Wikipedia, 'Euler's number' (e ≈ 2.718281828...)",
            },
            # ---- 4 verbal_analogy ------------------------------------------
            {
                "puzzle_type": "verbal_analogy",
                "question": "ADN : código genético :: libro : ?",
                "options": ["información", "página", "cubierta", "biblioteca"],
                "correct_answer": "información",
                "explanation": (
                    "El ADN codifica información genética, del mismo modo "
                    "que un libro contiene información en su texto."
                ),
                "source": (
                    "Watson & Crick (1953), 'Molecular structure of "
                    "nucleic acids', Nature"
                ),
            },
            {
                "puzzle_type": "verbal_analogy",
                "question": "Molécula : célula :: palabra : ?",
                "options": ["oración", "letra", "libro", "alfabeto"],
                "correct_answer": "oración",
                "explanation": (
                    "Una molécula es un componente de la célula, igual que "
                    "una palabra es un componente de la oración."
                ),
                "source": "Analogía educativa estándar (biología y lingüística)",
            },
            {
                "puzzle_type": "verbal_analogy",
                "question": "Galaxia : universo :: célula : ?",
                "options": ["tejido", "átomo", "molécula", "planeta"],
                "correct_answer": "tejido",
                "explanation": (
                    "Una galaxia es un componente del universo, del mismo "
                    "modo que una célula es un componente del tejido."
                ),
                "source": "Analogía científica estándar (biología y astronomía)",
            },
            {
                "puzzle_type": "verbal_analogy",
                "question": "Hipotálamo : temperatura :: hipocampo : ?",
                "options": ["memoria", "visión", "audición", "movimiento"],
                "correct_answer": "memoria",
                "explanation": (
                    "El hipotálamo regula la temperatura corporal; el "
                    "hipocampo es clave en la formación de memorias."
                ),
                "source": (
                    "Kandel, Schwartz & Jessell, 'Principles of Neural "
                    "Science' (5th ed., 2013)"
                ),
            },
        ],
        # Level 2 — intermedio (8 puzzles, verified scientific data)
        2: [
            {
                "question": "Fibonacci: 1, 1, 2, 3, 5, 8, ?",
                "options": ["13", "11", "10", "12"],
                "correct_answer": "13",
                "explanation": "Cada término es la suma de los dos anteriores: 5 + 8 = 13.",
                "puzzle_type": "number_sequence",
                "source": "Leonardo Fibonacci, 'Liber Abaci' (1202)",
            },
            {
                "question": "Velocidades (km/h) en orden descendente: guepardo=110, antílope=80, león=70, gacela=60, ?",
                "options": ["50 (caballo)", "40 (conejo)", "55 (perro)", "45 (zorro)"],
                "correct_answer": "50 (caballo)",
                "explanation": "La secuencia decrece ~10-20 km/h. Caballo ~50 km/h es la próxima.",
                "puzzle_type": "number_sequence",
                "source": "National Geographic, 'Los animales más rápidos' (2020)",
            },
            {
                "question": "Potencias de 2: 1, 2, 4, 8, 16, ?",
                "options": ["32", "24", "30", "20"],
                "correct_answer": "32",
                "explanation": "Cada término duplica al anterior: 16 × 2 = 32.",
                "puzzle_type": "number_sequence",
                "source": "Patrón matemático fundamental",
            },
            {
                "question": "Velocidad luz (km/s) × 10²: 3.0, 3.0, 3.0, 3.0, ?",
                "options": ["3.0", "3.1", "2.9", "0.3"],
                "correct_answer": "3.0",
                "explanation": "La velocidad de la luz en el vacío es constante: 299,792 km/s ≈ 3.0 × 10⁵ km/s.",
                "puzzle_type": "number_sequence",
                "source": "Constante física universal, NIST",
            },
            {
                "question": "Neurona : sistema nervioso como hepatocito : ?",
                "options": ["sistema digestivo", "sistema circulatorio", "sistema respiratorio", "sistema óseo"],
                "correct_answer": "sistema digestivo",
                "explanation": "La neurona es célula del sistema nervioso; el hepatocito es célula del hígado, parte del sistema digestivo.",
                "puzzle_type": "verbal_analogy",
                "source": "Guyton & Hall, 'Tratado de Fisiología Médica' (14ª ed.)",
            },
            {
                "question": "Mitosis : célula como meiosis : ?",
                "options": ["gameto", "tejido", "órgano", "sangre"],
                "correct_answer": "gameto",
                "explanation": "La mitosis produce células somáticas; la meiosis produce gametos (células sexuales).",
                "puzzle_type": "verbal_analogy",
                "source": "Alberts et al., 'Molecular Biology of the Cell' (6th ed.)",
            },
            {
                "question": "Clorofila : fotosíntesis como citocromo : ?",
                "options": ["respiración celular", "digestión", "transcripción", "traducción"],
                "correct_answer": "respiración celular",
                "explanation": "La clorofila captura luz para fotosíntesis; el citocromo transporta electrones en la cadena respiratoria.",
                "puzzle_type": "verbal_analogy",
                "source": "Lehninger, 'Principles of Biochemistry' (7th ed.)",
            },
            {
                "question": "Esternocleidomastoideo : cuello como cuádriceps : ?",
                "options": ["muslo", "brazo", "espalda", "abdomen"],
                "correct_answer": "muslo",
                "explanation": "El esternocleidomastoideo es músculo del cuello; el cuádriceps es músculo del muslo.",
                "puzzle_type": "verbal_analogy",
                "source": "Netter, 'Atlas de Anatomía Humana' (7th ed.)",
            },
        ],
    },
    # --- Problem Set (math) ----------------------------------------------------
    # Level 1 design rule: COTIDIANO. Situaciones reales (compras, vuelto,
    # finanzas básicas, comida) donde la matemática emerge como herramienta
    # invisible, no como tema explícito. NO memorización de datos científicos
    # ni abstractos (densidad del agua, velocidad de la luz, frecuencia
    # cardíaca, escala Kelvin, etc.). Respuesta < 10,000. Una o dos
    # operaciones. El objetivo es entrenar mentalidad matemática, no
    # aritmética con datos de libro.
    # Por qué existe: el usuario tiene que confiar en el sistema antes de
    # pasar al nivel 2, donde la IA toma el control con prompts basados
    # en persona (nadador, ajedrecista, profesor, etc.).
    "problem_set": {
        1: [
            {
                "question": (
                    "Compraste 3 cosas: una remera a $250, una gorra "
                    "a $180 y un libro a $420. Si pagás con $1.000, "
                    "¿cuánto te dan de vuelto?"
                ),
                "correct_answer": 150.0,
                "solution_steps": [
                    "total = 250 + 180 + 420 = 850",
                    "vuelto = 1.000 - 850 = 150",
                ],
                "source": "Cotidiano — compra con vuelto",
            },
            {
                "question": (
                    "Tenés 4 paquetes de yerba de 250 gramos cada uno. "
                    "¿Cuántos gramos tenés en total?"
                ),
                "correct_answer": 1000.0,
                "solution_steps": [
                    "gramos = 4 × 250 = 1.000",
                ],
                "source": "Cotidiano — empaque de producto",
            },
            {
                "question": (
                    "Una pizza cuesta $1.200. La cortás en 8 porciones "
                    "iguales para compartir con amigos. ¿Cuánto sale "
                    "cada porción?"
                ),
                "correct_answer": 150.0,
                "solution_steps": [
                    "precio_por_porción = 1.200 / 8 = 150",
                ],
                "source": "Cotidiano — compartir comida",
            },
            {
                "question": (
                    "Saliste a cenar con 2 amigos. La cuenta es "
                    "$1.500. Dividen en partes iguales, sin propina. "
                    "¿Cuánto paga cada uno?"
                ),
                "correct_answer": 500.0,
                "solution_steps": [
                    "por_persona = 1.500 / 3 = 500",
                ],
                "source": "Cotidiano — división de cuenta",
            },
            {
                "question": (
                    "1 kilogramo = 1.000 gramos. Si comprás 3,5 "
                    "kilogramos de naranjas, ¿cuántos gramos son?"
                ),
                "correct_answer": 3500.0,
                "solution_steps": [
                    "gramos = 3,5 × 1.000 = 3.500",
                ],
                "source": "Cotidiano — compra por peso",
            },
            {
                "question": (
                    "Querés juntar $1.800 para comprarte una compu. "
                    "Si podés ahorrar $200 por mes, ¿en cuántos meses "
                    "llegás?"
                ),
                "correct_answer": 9.0,
                "solution_steps": [
                    "meses = 1.800 / 200 = 9",
                ],
                "source": "Cotidiano — ahorro mensual",
            },
            {
                "question": (
                    "Tenés $5.000. Este mes gastás 30% en comida y "
                    "20% en transporte. ¿Cuánto te queda?"
                ),
                "correct_answer": 2500.0,
                "solution_steps": [
                    "gastado = 5.000 × 0,5 = 2.500",
                    "queda = 5.000 - 2.500 = 2.500",
                ],
                "source": "Cotidiano — finanzas personales",
            },
            {
                "question": (
                    "Una remera cuesta $1.200 y te hacen 25% de "
                    "descuento. ¿Cuánto pagás?"
                ),
                "correct_answer": 900.0,
                "solution_steps": [
                    "descuento = 1.200 × 0,25 = 300",
                    "precio final = 1.200 - 300 = 900",
                ],
                "source": "Cotidiano — compra con descuento",
            },
            # --- Nuevos problemas estáticos nivel 1 ---
            {
                "question": (
                    "Tenés 12 huevos en la heladera. Usás 3 para hacer "
                    "tortilla y 2 para una torta. ¿Cuántos quedan?"
                ),
                "correct_answer": 7.0,
                "solution_steps": [
                    "usados = 3 + 2 = 5",
                    "quedan = 12 - 5 = 7",
                ],
                "source": "Cotidiano — uso de ingredientes",
            },
            {
                "question": (
                    "Un bondi sale a las 8:15 y tarda 45 minutos en "
                    "llegar. ¿A qué hora llegás?"
                ),
                "correct_answer": 900.0,
                "solution_steps": [
                    "8:15 + 45 min = 9:00",
                ],
                "source": "Cotidiano — transporte público",
            },
            {
                "question": (
                    "Comprás 2 litros de leche a $800 cada uno y 1 "
                    "paquete de galletitas a $350. ¿Cuánto gastás en total?"
                ),
                "correct_answer": 1950.0,
                "solution_steps": [
                    "leche = 2 × 800 = 1.600",
                    "total = 1.600 + 350 = 1.950",
                ],
                "source": "Cotidiano — compra en supermercado",
            },
            {
                "question": (
                    "Tu celular tiene 64 GB de almacenamiento. Ya usás "
                    "45 GB. ¿Cuántos GB te quedan libres?"
                ),
                "correct_answer": 19.0,
                "solution_steps": [
                    "libres = 64 - 45 = 19 GB",
                ],
                "source": "Cotidiano — almacenamiento digital",
            },
            {
                "question": (
                    "Necesitás pintar una pared de 8 metros de largo "
                    "por 2,5 metros de alto. ¿Cuántos metros cuadrados "
                    "tenés que pintar?"
                ),
                "correct_answer": 20.0,
                "solution_steps": [
                    "área = largo × alto",
                    "área = 8 × 2,5 = 20 m²",
                ],
                "source": "Cotidiano — mejoras del hogar",
            },
            {
                "question": (
                    "Caminás 3.000 pasos por la mañana y 4.500 por la "
                    "tarde. Si cada paso mide 0,75 metros, ¿cuántos "
                    "metros recorrés en total?"
                ),
                "correct_answer": 5625.0,
                "solution_steps": [
                    "total_pasos = 3.000 + 4.500 = 7.500",
                    "metros = 7.500 × 0,75 = 5.625",
                ],
                "source": "Cotidiano — actividad física",
            },
            {
                "question": (
                    "Tenés un presupuesto de $10.000 para la semana. "
                    "Si ya gastaste $3.200 en comida y $1.800 en "
                    "transporte, ¿cuánto te queda para el resto?"
                ),
                "correct_answer": 5000.0,
                "solution_steps": [
                    "gastado = 3.200 + 1.800 = 5.000",
                    "queda = 10.000 - 5.000 = 5.000",
                ],
                "source": "Cotidiano — presupuesto semanal",
            },
            {
                "question": (
                    "Una receta pide 2,5 tazas de harina. Si vos querés "
                    "hacer el doble de la receta, ¿cuántas tazas necesitás?"
                ),
                "correct_answer": 5.0,
                "solution_steps": [
                    "doble = 2,5 × 2 = 5 tazas",
                ],
                "source": "Cotidiano — cocina",
            },
        ],
        # Level 2 — intermedio (8 problemas con datos verificados)
        2: [
            {
                "question": (
                    "El Everest tiene 8,848 m. ¿Cuántos kilómetros es?"
                ),
                "correct_answer": 8.848,
                "solution_steps": [
                    "8,848 m ÷ 1,000 m/km = 8.848 km",
                ],
                "source": "Medición oficial, Survey of Nepal / China (2020)",
            },
            {
                "question": (
                    "La Tierra orbita el Sol a 30 km/s. En 1 día (86,400 s), "
                    "¿cuántos km recorre?"
                ),
                "correct_answer": 2592000,
                "solution_steps": [
                    "30 km/s × 86,400 s = 2,592,000 km",
                ],
                "source": "Velocidad orbital terrestre media, NASA",
            },
            {
                "question": (
                    "El cuerpo humano adulto tiene ~206 huesos. Si un "
                    "bebé nace con ~270, ¿cuántos se fusionan?"
                ),
                "correct_answer": 64,
                "solution_steps": [
                    "270 huesos al nacer - 206 en adulto = 64 que se fusionan",
                ],
                "source": "Anatomía humana estándar, Netter (7ª ed.)",
            },
            {
                "question": (
                    "Un año luz ≈ 9.46 × 10¹² km. Andrómeda está a "
                    "2.5 millones de años luz. ¿A cuántos km? (en notación científica)"
                ),
                "correct_answer": 2.365e19,
                "solution_steps": [
                    "2.5 × 10⁶ × 9.46 × 10¹² = 23.65 × 10¹⁸ = 2.365 × 10¹⁹ km",
                ],
                "source": "NASA / ESA, distancia a galaxia Andrómeda",
            },
            {
                "question": (
                    "Pi (π) ≈ 3.14159. Si un círculo tiene radio 5 cm, "
                    "¿cuál es su circunferencia? (usa π=3.14)"
                ),
                "correct_answer": 31.4,
                "solution_steps": [
                    "Circunferencia = 2πr = 2 × 3.14 × 5 = 31.4 cm",
                ],
                "source": "Geometría euclidiana, π definido por Arquímedes",
            },
            {
                "question": (
                    "El monte Kilimanjaro tiene 5,895 m. El Aconcagua 6,961 m. "
                    "¿Cuántos metros más alto es el Aconcagua?"
                ),
                "correct_answer": 1066,
                "solution_steps": [
                    "6,961 - 5,895 = 1,066 m",
                ],
                "source": "Enciclopedia Britannica, picos más altos por continente",
            },
            {
                "question": (
                    "La velocidad del sonido en el aire ≈ 343 m/s. "
                    "Si un trueno se escucha 3 segundos después del rayo, "
                    "¿a qué distancia cayó?"
                ),
                "correct_answer": 1029,
                "solution_steps": [
                    "343 m/s × 3 s = 1,029 m",
                ],
                "source": "Física acústica, velocidad del sonido al nivel del mar (20°C)",
            },
            {
                "question": (
                    "El Gran Colisionador de Hadrones (LHC) tiene 27 km de "
                    "circunferencia. ¿Cuántas vueltas para recorrer 1,000 km?"
                ),
                "correct_answer": 37,
                "solution_steps": [
                    "1,000 km ÷ 27 km/vuelta ≈ 37.04 vueltas",
                ],
                "source": "CERN, Large Hadron Collider specifications",
            },
            {
                "question": (
                    "El universo tiene ~13.800 millones de años. "
                    "¿Cuántos siglos son?"
                ),
                "correct_answer": 138_000_000.0,
                "solution_steps": [
                    "1 siglo = 100 años",
                    "13.800.000.000 años ÷ 100 = 138.000.000 siglos",
                ],
                "source": (
                    "NASA / Planck Collaboration (2018) — edad del "
                    "universo: 13.797 ± 0.023 mil millones de años"
                ),
            },
            {
                "question": (
                    "La distancia Tierra-Sol es ~150 millones de km y el "
                    "diámetro de la Tierra es 12.742 km. ¿Cuántas veces "
                    "cabe la Tierra en esa distancia?"
                ),
                "correct_answer": 11_773.0,
                "solution_steps": [
                    "150.000.000 km ÷ 12.742 km ≈ 11.773,4",
                    "Aproximadamente 11.773 Tieras en la distancia Tierra-Sol",
                ],
                "source": "NASA Planetary Fact Sheet",
            },
            {
                "question": (
                    "La población mundial es ~8 mil millones de personas "
                    "distribuidas en ~200 países. ¿Cuántas personas por "
                    "país en promedio?"
                ),
                "correct_answer": 40_000_000.0,
                "solution_steps": [
                    "promedio = población total / cantidad de países",
                    "promedio = 8.000.000.000 ÷ 200 = 40.000.000 personas "
                    "por país",
                ],
                "source": "Naciones Unidas — World Population Prospects",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Session tracking
# ---------------------------------------------------------------------------
# Maps session_id -> set of puzzle indices already shown in that session.
# Bounded by ``_MAX_TRACKED_SESSIONS`` to prevent unbounded memory growth in
# long-running processes. Oldest entries are evicted FIFO.
_seen_puzzles: "OrderedDict[int, set[int]]" = OrderedDict()
_MAX_TRACKED_SESSIONS = 1000


def get_pool_puzzle(
    skill_type: str,
    level: int,
    session_id: Optional[int] = None,
) -> Optional[dict]:
    """Return a puzzle from the static pool, or ``None`` if no pool exists.

    Rotates through puzzles so the same puzzle is not shown twice in a
    session. When every puzzle in the pool has been seen, the session's
    seen-set is cleared and rotation starts over.

    Args:
        skill_type: ``"iq_practice"`` or ``"problem_set"``.
        level: Difficulty level (only level 1 currently has a pool).
        session_id: Practice session ID used to track rotation. When
            ``None`` the function returns the first puzzle deterministically
            (no rotation).

    Returns:
        Deep copy of a pool entry (so callers can mutate without affecting
        the canonical pool), or ``None`` if no pool exists for the given
        skill_type/level.
    """
    pool = PUZZLE_POOLS.get(skill_type, {}).get(level)
    if not pool:
        return None

    idx = _pick_pool_index(pool, session_id)
    puzzle = copy.deepcopy(pool[idx])
    _record_seen(session_id, idx)
    return puzzle


def has_pool(skill_type: str, level: int) -> bool:
    """Return ``True`` if a static pool exists for the given skill+level."""
    return bool(PUZZLE_POOLS.get(skill_type, {}).get(level))


def reset_session_puzzles(session_id: int) -> None:
    """Clear the seen-set for a single session. Useful for tests."""
    _seen_puzzles.pop(session_id, None)


def reset_all_puzzles() -> None:
    """Clear all session tracking. Useful for tests."""
    _seen_puzzles.clear()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _pick_pool_index(pool: list, session_id: Optional[int]) -> int:
    """Pick a pool index not yet shown in this session."""
    if session_id is None or len(pool) <= 1:
        # Deterministic fallback: first entry.
        return 0
    seen = _seen_puzzles.get(session_id, set())
    available = [i for i in range(len(pool)) if i not in seen]
    if not available:
        # Every puzzle has been seen — reset and pick from the full pool.
        _seen_puzzles[session_id] = set()
        available = list(range(len(pool)))
    return random.choice(available)


def _record_seen(session_id: Optional[int], idx: int) -> None:
    """Mark a pool index as seen for this session with bounded LRU eviction."""
    if session_id is None:
        return
    if session_id not in _seen_puzzles:
        if len(_seen_puzzles) >= _MAX_TRACKED_SESSIONS:
            # Evict the oldest session (FIFO).
            _seen_puzzles.popitem(last=False)
        _seen_puzzles[session_id] = set()
    _seen_puzzles[session_id].add(idx)
