import json
import logging
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlmodel import Session, select
from core.database import engine
from models.paes_models import (
    PaesCurriculumVersion,
    PaesSubject,
    PaesCompetency,
    PaesEjeTematico,
    PaesTopic,
    PaesSubtopic,
    PaesQuestion,
    PaesLearningState,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_multidisciplinary")

MULTIDISCIPLINARY_DATA = {
    "subjects": [
        {
            "id": "subj-lectura",
            "code": "LECTURA",
            "name": "Competencia Lectora",
            "is_mandatory": True,
            "total_questions": 65,
            "scored_questions": 60,
            "pilot_questions": 5,
            "duration_minutes": 150,
        },
        {
            "id": "subj-m2",
            "code": "M2",
            "name": "Competencia Matemática 2",
            "is_mandatory": False,
            "total_questions": 55,
            "scored_questions": 50,
            "pilot_questions": 5,
            "duration_minutes": 140,
        },
        {
            "id": "subj-ciencias",
            "code": "CIENCIAS",
            "name": "Ciencias (Módulo Común + Electivo)",
            "is_mandatory": False,
            "total_questions": 80,
            "scored_questions": 75,
            "pilot_questions": 5,
            "duration_minutes": 160,
        },
        {
            "id": "subj-historia",
            "code": "HISTORIA",
            "name": "Historia y Ciencias Sociales",
            "is_mandatory": False,
            "total_questions": 65,
            "scored_questions": 60,
            "pilot_questions": 5,
            "duration_minutes": 120,
        },
    ],
    "competencies": [
        {
            "id": "comp-lect-rastrear",
            "code": "RASTREAR_LOCALIZAR",
            "name": "Rastrear - Localizar",
            "description": "Identificar y extraer información explícita formulada en el texto sin tergiversar el sentido original.",
        },
        {
            "id": "comp-lect-relacionar",
            "code": "RELACIONAR_INTERPRETAR",
            "name": "Relacionar - Interpretar",
            "description": "Establecer conexiones entre partes del texto, inferir sentidos implícitos y deducir el propósito comunicativo.",
        },
        {
            "id": "comp-lect-evaluar",
            "code": "EVALUAR_REFLEXIONAR",
            "name": "Evaluar - Reflexionar",
            "description": "Enjuiciar críticamente la forma, contenido, recursos argumentativos y posición del emisor.",
        },
        {
            "id": "comp-cien-analizar",
            "code": "PENSAMIENTO_CIENTIFICO_ANALIZAR",
            "name": "Procesar y analizar evidencia",
            "description": "Interpretar gráficos, tablas y relaciones cuantitativas en datos experimentales de laboratorio.",
        },
        {
            "id": "comp-hist-fuentes",
            "code": "ANALISIS_FUENTES",
            "name": "Análisis de fuentes históricas",
            "description": "Interpretar documentos primarios y contrastar visiones historiográficas sobre un mismo fenómeno.",
        },
    ],
    "ejes": [
        # LECTURA
        {"id": "eje-lec-divulgacion", "subject_id": "subj-lectura", "name": "Textos No Literarios Expositivos", "order_index": 1},
        {"id": "eje-lec-argumentativo", "subject_id": "subj-lectura", "name": "Textos No Literarios Argumentativos", "order_index": 2},
        {"id": "eje-lec-literario", "subject_id": "subj-lectura", "name": "Textos Literarios", "order_index": 3},
        # M2
        {"id": "eje-m2-num", "subject_id": "subj-m2", "name": "Números (M2)", "order_index": 1},
        {"id": "eje-m2-alg", "subject_id": "subj-m2", "name": "Álgebra y Funciones (M2)", "order_index": 2},
        {"id": "eje-m2-geo", "subject_id": "subj-m2", "name": "Geometría (M2)", "order_index": 3},
        {"id": "eje-m2-prob", "subject_id": "subj-m2", "name": "Probabilidad y Estadística (M2)", "order_index": 4},
        # CIENCIAS
        {"id": "eje-cie-bio", "subject_id": "subj-ciencias", "name": "Módulo Común Biología", "order_index": 1},
        {"id": "eje-cie-fis", "subject_id": "subj-ciencias", "name": "Módulo Común Física", "order_index": 2},
        {"id": "eje-cie-quim", "subject_id": "subj-ciencias", "name": "Módulo Común Química", "order_index": 3},
        {"id": "eje-cie-elec", "subject_id": "subj-ciencias", "name": "Módulo Electivo / Método Científico", "order_index": 4},
        # HISTORIA
        {"id": "eje-his-chile", "subject_id": "subj-historia", "name": "Historia: Chile y el Mundo en el Siglo XX", "order_index": 1},
        {"id": "eje-his-ciudadania", "subject_id": "subj-historia", "name": "Formación Ciudadana y Democracia", "order_index": 2},
        {"id": "eje-his-economia", "subject_id": "subj-historia", "name": "Economía y Sociedad", "order_index": 3},
    ],
    "topics": [
        # LECTURA
        {"id": "top-lec-divulgacion", "eje_id": "eje-lec-divulgacion", "name": "Divulgación Científica y Tecnología", "order_index": 1},
        {"id": "top-lec-editorial", "eje_id": "eje-lec-argumentativo", "name": "Editoriales y Columnas de Opinión", "order_index": 2},
        {"id": "top-lec-narrativa", "eje_id": "eje-lec-literario", "name": "Narrativa Contemporánea", "order_index": 3},
        # M2
        {"id": "top-m2-log", "eje_id": "eje-m2-num", "name": "Logaritmos y Complejos", "order_index": 1},
        {"id": "top-m2-func", "eje_id": "eje-m2-alg", "name": "Funciones Inversa y Potencia", "order_index": 2},
        {"id": "top-m2-vec", "eje_id": "eje-m2-geo", "name": "Vectores en el Espacio y Rectas", "order_index": 3},
        {"id": "top-m2-dist", "eje_id": "eje-m2-prob", "name": "Distribución Normal y Bayes", "order_index": 4},
        # CIENCIAS
        {"id": "top-cie-bio", "eje_id": "eje-cie-bio", "name": "Herencia y Biología Celular", "order_index": 1},
        {"id": "top-cie-fis", "eje_id": "eje-cie-fis", "name": "Mecánica y Ondas", "order_index": 2},
        {"id": "top-cie-quim", "eje_id": "eje-cie-quim", "name": "Enlaces y Estequiometría", "order_index": 3},
        {"id": "top-cie-exp", "eje_id": "eje-cie-elec", "name": "Diseño Experimental", "order_index": 4},
        # HISTORIA
        {"id": "top-his-chile", "eje_id": "eje-his-chile", "name": "Transformaciones del Siglo XX en Chile", "order_index": 1},
        {"id": "top-his-demo", "eje_id": "eje-his-ciudadania", "name": "Institucionalidad y Derechos Humanos", "order_index": 2},
        {"id": "top-his-eco", "eje_id": "eje-his-economia", "name": "Mercado, Inflación y Políticas Públicas", "order_index": 3},
    ],
    "subtopics": [
        # LECTURA
        {
            "id": "sub-lec-ia-sociedad",
            "topic_id": "top-lec-divulgacion",
            "name": "Comprensión de artículos de ciencia y tecnología",
            "slug": "lectura-divulgacion-ia-ciencia",
            "description": "Análisis comprensivo de textos explicativos con rigor científico y terminología especializada.",
            "order_index": 1,
        },
        {
            "id": "sub-lec-columnas-opinion",
            "topic_id": "top-lec-editorial",
            "name": "Análisis de columnas y ensayos de opinión",
            "slug": "lectura-columnas-opinion-ensayos",
            "description": "Detección de tesis central, contrargumentos, sesgos y recursos retóricos del emisor.",
            "order_index": 2,
        },
        {
            "id": "sub-lec-narrativa-latam",
            "topic_id": "top-lec-narrativa",
            "name": "Interpretación de relatos y novelas contemporáneas",
            "slug": "lectura-narrativa-latam-ficcion",
            "description": "Caracterización psicológica de personajes, conflicto dramático y simbolismo en textos literarios.",
            "order_index": 3,
        },
        # M2
        {
            "id": "sub-m2-logaritmos",
            "topic_id": "top-m2-log",
            "name": "Ecuaciones y propiedades de logaritmos",
            "slug": "m2-num-logaritmos-avanzados",
            "description": "Definición rigurosa, cambio de base y resolución analítica de ecuaciones logarítmicas en R.",
            "order_index": 4,
        },
        {
            "id": "sub-m2-funcion-inversa",
            "topic_id": "top-m2-func",
            "name": "Función potencia, inversa y composición",
            "slug": "m2-alg-funcion-inversa-potencia",
            "description": "Dominio, recorrido, inyectividad, biyectividad y cálculo de funciones inversas.",
            "order_index": 5,
        },
        {
            "id": "sub-m2-vectores-r3",
            "topic_id": "top-m2-vec",
            "name": "Vectores en R3 y ecuación vectorial de la recta",
            "slug": "m2-geo-vectores-r3-rectas",
            "description": "Operaciones vectoriales en el espacio tridimensional y ecuaciones continua y paramétrica de la recta.",
            "order_index": 6,
        },
        {
            "id": "sub-m2-dist-normal",
            "topic_id": "top-m2-dist",
            "name": "Distribución normal y tipificación",
            "slug": "m2-prob-distribucion-normal-z",
            "description": "Cálculo de probabilidades en la curva gaussiana mediante estandarización Z.",
            "order_index": 7,
        },
        # CIENCIAS
        {
            "id": "sub-cie-genetica",
            "topic_id": "top-cie-bio",
            "name": "Herencia, genética y ciclo celular",
            "slug": "ciencias-bio-genetica-mendeliana",
            "description": "Leyes de Mendel, cariotipos, mitosis, meiosis y transmisión de caracteres biológicos.",
            "order_index": 8,
        },
        {
            "id": "sub-cie-mecanica",
            "topic_id": "top-cie-fis",
            "name": "Leyes de Newton, energía y trabajo mecánico",
            "slug": "ciencias-fis-newton-energia",
            "description": "Dinámica del movimiento rectilíneo, conservación de la energía mecánica y roce.",
            "order_index": 9,
        },
        {
            "id": "sub-cie-estequiometria",
            "topic_id": "top-cie-quim",
            "name": "Estequiometría y soluciones químicas",
            "slug": "ciencias-quim-estequiometria-molaridad",
            "description": "Cálculos molares, balance de ecuaciones químicas, reactivo limitante y concentración.",
            "order_index": 10,
        },
        {
            "id": "sub-cie-metodo",
            "topic_id": "top-cie-exp",
            "name": "Análisis de evidencia experimental y variables",
            "slug": "ciencias-elec-control-variables-graficos",
            "description": "Diferenciación entre variables dependientes e independientes y formulación de conclusiones válidas.",
            "order_index": 11,
        },
        # HISTORIA
        {
            "id": "sub-his-siglo-xx",
            "topic_id": "top-his-chile",
            "name": "Transformaciones sociales y políticas en Chile (s. XX)",
            "slug": "historia-chile-transformaciones-siglo-xx",
            "description": "Procesos de democratización, reformas estructurales y quiebre institucional de 1973.",
            "order_index": 12,
        },
        {
            "id": "sub-his-ciudadania",
            "topic_id": "top-his-demo",
            "name": "Estado de derecho, democracia y Constitución",
            "slug": "historia-ciudadania-estado-derecho",
            "description": "Principios republicanos, separación de poderes, garantías constitucionales y deberes cívicos.",
            "order_index": 13,
        },
        {
            "id": "sub-his-mercado",
            "topic_id": "top-his-eco",
            "name": "El problema de la escasez, mercado e inflación",
            "slug": "historia-economia-escasez-inflacion",
            "description": "Asignación de recursos, oferta y demanda, rol del Banco Central y políticas fiscales.",
            "order_index": 14,
        },
    ],
}

def seed_multidisciplinary(session_arg: Session = None):
    def _seed(session):
        # 1. Ensure DEMRE-2026 version
        cv = session.exec(select(PaesCurriculumVersion).where(PaesCurriculumVersion.code == "DEMRE-2026")).first()
        if not cv:
            cv = PaesCurriculumVersion(
                id="cv-demre-2026",
                code="DEMRE-2026",
                name="Proceso Oficial Admisión DEMRE 2026",
                year=2026,
                is_active=True,
            )
            session.add(cv)
            session.flush()

        # 2. Subjects
        for s_data in MULTIDISCIPLINARY_DATA["subjects"]:
            sub = session.get(PaesSubject, s_data["id"])
            if not sub:
                sub = PaesSubject(
                    id=s_data["id"],
                    curriculum_version_id=cv.id,
                    code=s_data["code"],
                    name=s_data["name"],
                    is_mandatory=s_data["is_mandatory"],
                    total_questions=s_data["total_questions"],
                    scored_questions=s_data["scored_questions"],
                    pilot_questions=s_data["pilot_questions"],
                    duration_minutes=s_data["duration_minutes"],
                )
                session.add(sub)
                logger.info("Subject added: %s (%s)", sub.code, sub.name)

        # 3. Competencies
        for comp_data in MULTIDISCIPLINARY_DATA["competencies"]:
            c = session.get(PaesCompetency, comp_data["id"])
            if not c:
                c = PaesCompetency(
                    id=comp_data["id"],
                    code=comp_data["code"],
                    name=comp_data["name"],
                    description=comp_data["description"],
                )
                session.add(c)
                logger.info("Competency added: %s", c.code)

        # 4. Ejes
        for eje_data in MULTIDISCIPLINARY_DATA["ejes"]:
            e = session.get(PaesEjeTematico, eje_data["id"])
            if not e:
                e = PaesEjeTematico(
                    id=eje_data["id"],
                    subject_id=eje_data["subject_id"],
                    name=eje_data["name"],
                    order_index=eje_data["order_index"],
                )
                session.add(e)
                logger.info("Eje added: %s", e.name)

        # 5. Topics
        for top_data in MULTIDISCIPLINARY_DATA["topics"]:
            t = session.get(PaesTopic, top_data["id"])
            if not t:
                t = PaesTopic(
                    id=top_data["id"],
                    eje_id=top_data["eje_id"],
                    name=top_data["name"],
                    order_index=top_data["order_index"],
                )
                session.add(t)
                logger.info("Topic added: %s", t.name)

        # 6. Subtopics & initial learning state for user 1
        for sub_data in MULTIDISCIPLINARY_DATA["subtopics"]:
            st = session.get(PaesSubtopic, sub_data["id"])
            if not st:
                st = PaesSubtopic(
                    id=sub_data["id"],
                    topic_id=sub_data["topic_id"],
                    name=sub_data["name"],
                    slug=sub_data["slug"],
                    description=sub_data["description"],
                    order_index=sub_data["order_index"],
                )
                session.add(st)
                logger.info("Subtopic added: %s (%s)", st.slug, st.name)

            # Ensure initial learning state
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

        session.commit()
        logger.info("Multidisciplinary curriculum seeded successfully!")

    if session_arg:
        _seed(session_arg)
    else:
        with Session(engine) as session:
            _seed(session)

if __name__ == "__main__":
    seed_multidisciplinary()
