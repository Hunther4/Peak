"""
Seed script: expand the non-M1 curriculum to realistic subtopic counts.

Adds new topics + subtopics for LECTURA (9 subtopics total),
M2 (10 subtopics), CIENCIAS (12 subtopics), HISTORIA (9 subtopics).
All inserts are idempotent (skip if already exists).
"""
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlmodel import Session, select

from core.database import engine
from models.paes_models import PaesEjeTematico, PaesLearningState, PaesSubtopic, PaesTopic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_curriculum_expansion")

# ---------------------------------------------------------------------------
# Additional TOPICS per subject (extend existing ejes with more topics)
# ---------------------------------------------------------------------------
EXTRA_TOPICS = [
    # LECTURA — extra topics inside existing ejes
    {"id": "top-lec-infografia", "eje_id": "eje-lec-divulgacion", "name": "Infografías y textos discontinuos", "order_index": 2},
    {"id": "top-lec-reportaje", "eje_id": "eje-lec-divulgacion", "name": "Reportajes periodísticos y crónicas", "order_index": 3},
    {"id": "top-lec-debate", "eje_id": "eje-lec-argumentativo", "name": "Discursos públicos y debates formales", "order_index": 4},
    {"id": "top-lec-ensayo", "eje_id": "eje-lec-argumentativo", "name": "Ensayos filosóficos y literarios", "order_index": 5},
    {"id": "top-lec-poesia", "eje_id": "eje-lec-literario", "name": "Lírica y textos poéticos", "order_index": 6},
    {"id": "top-lec-drama", "eje_id": "eje-lec-literario", "name": "Teatro y textos dramáticos", "order_index": 7},
    # M2 — extra topics inside existing ejes
    {"id": "top-m2-trigonometria", "eje_id": "eje-m2-num", "name": "Trigonometría y números complejos", "order_index": 2},
    {"id": "top-m2-derivadas", "eje_id": "eje-m2-alg", "name": "Límites y derivadas (introducción)", "order_index": 3},
    {"id": "top-m2-conicas", "eje_id": "eje-m2-geo", "name": "Cónicas: circunferencia, elipse y parábola", "order_index": 4},
    {"id": "top-m2-combinatoria", "eje_id": "eje-m2-prob", "name": "Combinatoria y probabilidad condicional", "order_index": 5},
    # CIENCIAS — extra topics inside existing ejes
    {"id": "top-cie-evolucion", "eje_id": "eje-cie-bio", "name": "Evolución y biodiversidad", "order_index": 2},
    {"id": "top-cie-termodinamica", "eje_id": "eje-cie-fis", "name": "Termodinámica y electricidad", "order_index": 3},
    {"id": "top-cie-acido-base", "eje_id": "eje-cie-quim", "name": "Ácidos, bases y equilibrio químico", "order_index": 4},
    {"id": "top-cie-electivo-bio", "eje_id": "eje-cie-elec", "name": "Módulo Electivo Biología aplicada", "order_index": 5},
    # HISTORIA — extra topics inside existing ejes
    {"id": "top-his-guerra-fria", "eje_id": "eje-his-chile", "name": "Guerra Fría y orden bipolar", "order_index": 2},
    {"id": "top-his-globalizacion", "eje_id": "eje-his-chile", "name": "Globalización y mundo contemporáneo", "order_index": 3},
    {"id": "top-his-rrhh", "eje_id": "eje-his-ciudadania", "name": "Derechos humanos y mecanismos de protección", "order_index": 4},
    {"id": "top-his-territorio", "eje_id": "eje-his-economia", "name": "Geografía, territorio y planificación urbana", "order_index": 5},
]

# ---------------------------------------------------------------------------
# Additional SUBTOPICS per subject
# ---------------------------------------------------------------------------
EXTRA_SUBTOPICS = [
    # ── LECTURA ──────────────────────────────────────────────────────────────
    {
        "id": "sub-lec-infografia",
        "topic_id": "top-lec-infografia",
        "name": "Lectura e interpretación de infografías y gráficos estadísticos",
        "slug": "lectura-infografia-graficos",
        "description": "Extracción e integración de información en textos discontinuos: tablas, gráficos y diagramas.",
        "order_index": 15,
    },
    {
        "id": "sub-lec-reportaje",
        "topic_id": "top-lec-reportaje",
        "name": "Análisis de reportajes y crónicas periodísticas",
        "slug": "lectura-reportaje-cronica",
        "description": "Identificación del propósito informativo, selección de hechos y diferenciación hecho/opinión.",
        "order_index": 16,
    },
    {
        "id": "sub-lec-debate",
        "topic_id": "top-lec-debate",
        "name": "Evaluación de argumentos en discursos y debates formales",
        "slug": "lectura-discurso-debate-formal",
        "description": "Análisis de la estructura argumentativa, falacias y estrategias retóricas en discursos orales transcritos.",
        "order_index": 17,
    },
    {
        "id": "sub-lec-ensayo",
        "topic_id": "top-lec-ensayo",
        "name": "Interpretación de ensayos filosóficos y de ideas",
        "slug": "lectura-ensayo-filosofico",
        "description": "Comprensión de argumentos abstractos, tesis implícitas y postura crítica del ensayista.",
        "order_index": 18,
    },
    {
        "id": "sub-lec-lirica",
        "topic_id": "top-lec-poesia",
        "name": "Comprensión de textos líricos y recursos poéticos",
        "slug": "lectura-lirica-recursos-poeticos",
        "description": "Identificación del hablante lírico, temple de ánimo, recursos de nivel fónico y semántico.",
        "order_index": 19,
    },
    {
        "id": "sub-lec-drama",
        "topic_id": "top-lec-drama",
        "name": "Análisis de textos teatrales y conflicto dramático",
        "slug": "lectura-teatro-conflicto-dramatico",
        "description": "Caracterización de personajes, tipos de conflicto dramático y estructura del acto teatral.",
        "order_index": 20,
    },

    # ── M2 ───────────────────────────────────────────────────────────────────
    {
        "id": "sub-m2-trigonometria",
        "topic_id": "top-m2-trigonometria",
        "name": "Identidades trigonométricas y ecuaciones",
        "slug": "m2-num-trigonometria-identidades",
        "description": "Identidades pitagóricas, suma y diferencia de arcos, y resolución de ecuaciones trigonométricas en R.",
        "order_index": 21,
    },
    {
        "id": "sub-m2-complejos",
        "topic_id": "top-m2-trigonometria",
        "name": "Números complejos y forma trigonométrica",
        "slug": "m2-num-complejos-forma-trigonometrica",
        "description": "Operaciones con números complejos, módulo, argumento y forma polar (De Moivre).",
        "order_index": 22,
    },
    {
        "id": "sub-m2-limites",
        "topic_id": "top-m2-derivadas",
        "name": "Límites y continuidad de funciones",
        "slug": "m2-alg-limites-continuidad",
        "description": "Límite lateral, bilateral, indeterminaciones y condición de continuidad en un punto.",
        "order_index": 23,
    },
    {
        "id": "sub-m2-conicas",
        "topic_id": "top-m2-conicas",
        "name": "Ecuación de la circunferencia, elipse y parábola",
        "slug": "m2-geo-conicas-circunferencia-elipse",
        "description": "Identificación y graficación de cónicas a partir de su ecuación canónica y completación de cuadrados.",
        "order_index": 24,
    },
    {
        "id": "sub-m2-combinatoria",
        "topic_id": "top-m2-combinatoria",
        "name": "Combinatoria: permutaciones, combinaciones y principio de conteo",
        "slug": "m2-prob-combinatoria-permutaciones",
        "description": "Permutaciones con y sin repetición, combinaciones y aplicación a probabilidad discreta.",
        "order_index": 25,
    },
    {
        "id": "sub-m2-prob-condicional",
        "topic_id": "top-m2-combinatoria",
        "name": "Probabilidad condicional y teorema de Bayes",
        "slug": "m2-prob-condicional-bayes",
        "description": "Regla del producto, probabilidad condicionada P(A|B) y aplicación del teorema de Bayes.",
        "order_index": 26,
    },

    # ── CIENCIAS ─────────────────────────────────────────────────────────────
    {
        "id": "sub-cie-evolucion",
        "topic_id": "top-cie-evolucion",
        "name": "Teoría sintética de la evolución y selección natural",
        "slug": "ciencias-bio-evolucion-seleccion-natural",
        "description": "Mecanismos evolutivos: mutación, deriva génica, flujo génico y selección natural darwiniana.",
        "order_index": 27,
    },
    {
        "id": "sub-cie-termodinamica",
        "topic_id": "top-cie-termodinamica",
        "name": "Leyes de la termodinámica y transferencia de calor",
        "slug": "ciencias-fis-termodinamica-calor",
        "description": "Primera y segunda ley de la termodinámica, ciclos termodinámicos y eficiencia.",
        "order_index": 28,
    },
    {
        "id": "sub-cie-electricidad",
        "topic_id": "top-cie-termodinamica",
        "name": "Circuitos eléctricos: ley de Ohm y potencia",
        "slug": "ciencias-fis-circuitos-ohm",
        "description": "Resistencia, corriente, diferencia de potencial, circuitos serie/paralelo y potencia disipada.",
        "order_index": 29,
    },
    {
        "id": "sub-cie-acido-base",
        "topic_id": "top-cie-acido-base",
        "name": "Teorías ácido-base y escala de pH",
        "slug": "ciencias-quim-acido-base-ph",
        "description": "Teorías de Arrhenius, Brønsted-Lowry y Lewis; cálculo de pH y soluciones amortiguadoras.",
        "order_index": 30,
    },
    {
        "id": "sub-cie-electivo-bio",
        "topic_id": "top-cie-electivo-bio",
        "name": "Fisiología humana: sistemas digestivo, circulatorio y nervioso",
        "slug": "ciencias-elec-bio-fisiologia-humana",
        "description": "Integración funcional de los sistemas biológicos humanos y su regulación homeostática.",
        "order_index": 31,
    },

    # ── HISTORIA ─────────────────────────────────────────────────────────────
    {
        "id": "sub-his-guerra-fria",
        "topic_id": "top-his-guerra-fria",
        "name": "Orden bipolar, descolonización y movimientos de liberación",
        "slug": "historia-mundo-guerra-fria-bipolar",
        "description": "Características del sistema bipolar, crisis de los misiles y procesos de descolonización en Asia y África.",
        "order_index": 32,
    },
    {
        "id": "sub-his-globalizacion",
        "topic_id": "top-his-globalizacion",
        "name": "Globalización, integración regional y DDHH en el siglo XXI",
        "slug": "historia-globalizacion-siglo-xxi",
        "description": "Interdependencia económica, rol de los organismos multilaterales y nuevos desafíos geopolíticos.",
        "order_index": 33,
    },
    {
        "id": "sub-his-ddhh",
        "topic_id": "top-his-rrhh",
        "name": "Sistema internacional de protección de los derechos humanos",
        "slug": "historia-ddhh-sistema-internacional",
        "description": "Declaración Universal de 1948, tratados, organismos de protección (ONU, CIDH) y jurisprudencia.",
        "order_index": 34,
    },
    {
        "id": "sub-his-territorio",
        "topic_id": "top-his-territorio",
        "name": "Geografía de Chile: territorio, recursos y medio ambiente",
        "slug": "historia-geografia-chile-recursos",
        "description": "Características geomorfológicas, climáticas y biogeográficas de Chile y sus implicancias económicas.",
        "order_index": 35,
    },
]


def seed_expansion(session_arg: Session = None):
    def _seed(session):
        added_topics = 0
        added_subtopics = 0
        added_states = 0

        # 1. Extra Topics
        for top_data in EXTRA_TOPICS:
            # Verify parent eje exists
            eje = session.get(PaesEjeTematico, top_data["eje_id"])
            if not eje:
                logger.warning("Eje %s not found — skipping topic %s", top_data["eje_id"], top_data["id"])
                continue
            existing = session.get(PaesTopic, top_data["id"])
            if not existing:
                t = PaesTopic(
                    id=top_data["id"],
                    eje_id=top_data["eje_id"],
                    name=top_data["name"],
                    order_index=top_data["order_index"],
                )
                session.add(t)
                added_topics += 1
                logger.info("Topic added: %s", t.name)

        session.flush()

        # 2. Extra Subtopics + learning states for user 1
        for sub_data in EXTRA_SUBTOPICS:
            topic = session.get(PaesTopic, sub_data["topic_id"])
            if not topic:
                logger.warning("Topic %s not found — skipping subtopic %s", sub_data["topic_id"], sub_data["id"])
                continue

            existing = session.get(PaesSubtopic, sub_data["id"])
            if not existing:
                st = PaesSubtopic(
                    id=sub_data["id"],
                    topic_id=sub_data["topic_id"],
                    name=sub_data["name"],
                    slug=sub_data["slug"],
                    description=sub_data["description"],
                    order_index=sub_data["order_index"],
                )
                session.add(st)
                added_subtopics += 1
                logger.info("Subtopic added: %s (%s)", st.slug, st.name)

            # Ensure initial learning state for user 1
            state = session.exec(
                select(PaesLearningState).where(
                    PaesLearningState.user_id == 1,
                    PaesLearningState.subtopic_id == sub_data["id"],
                )
            ).first()
            if not state:
                state = PaesLearningState(
                    id=f"st-1-{sub_data['id']}",
                    user_id=1,
                    subtopic_id=sub_data["id"],
                    mastery_score=0.0,
                    confidence_score=0.0,
                    total_attempts=0,
                    total_correct=0,
                    leitner_box=1,
                )
                session.add(state)
                added_states += 1

        session.commit()
        logger.info(
            "Curriculum expansion complete — %d topics, %d subtopics, %d learning states added.",
            added_topics,
            added_subtopics,
            added_states,
        )

    if session_arg:
        _seed(session_arg)
    else:
        with Session(engine) as session:
            _seed(session)


if __name__ == "__main__":
    seed_expansion()
