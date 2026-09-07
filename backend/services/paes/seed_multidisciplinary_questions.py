import json
import logging
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlmodel import Session, select
from core.database import engine
from models.paes_models import PaesQuestion, PaesCompetency, PaesSubtopic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_multidisciplinary_questions")

QUESTIONS = [
    # --- LECTURA 1: Divulgación Científica (Microbioma) ---
    {
        "id": "q-lec-01",
        "subtopic_id": "sub-lec-ia-sociedad",
        "skill_code": "RASTREAR_LOCALIZAR",
        "stimulus_title": "El microbioma humano y la comunicación bidireccional del eje intestino-cerebro",
        "stimulus_text": """La microbiota intestinal, compuesta por billones de microorganismos que habitan el tracto gastrointestinal, ha dejado de ser considerada una simple comunidad comensal para ser entendida como un órgano endocrino y metabólico altamente activo. A través del denominado 'eje intestino-cerebro', estas bacterias se comunican de forma bidireccional con el sistema nervioso central mediante vías neuronales, inmunológicas y neuroendocrinas.

Uno de los mecanismos bioquímicos más documentados reside en la síntesis de ácidos grasos de cadena corta (AGCC), tales como el butirato, propionato y acetato, generados tras la fermentación de fibras dietéticas solubles. Específicamente, el butirato ejerce un rol clave al actuar como inhibidor de histona deacetilasas y preservar la integridad de la barrera hematoencefálica, limitando el paso de endotoxinas inflamatorias hacia el parénquima cerebral. Asimismo, más del 90% de la serotonina corporal es sintetizada en las células enterocromafines del epitelio intestinal bajo la modulación directa de metabolitos bacterianos.

Estudios clínicos recientes de la Universidad de Oxford han vinculado patrones de disbiosis (alteración del equilibrio de la flora intestinal) con estados de neuroinflamación y vulnerabilidad a trastornos del ánimo y deterioro cognitivo leve. Aunque los modelos animales en ratones libres de gérmenes han mostrado cambios dramáticos en la neurogénesis hipocampal ante la reconstitución microbiana, la comunidad médica internacional enfatiza que las intervenciones con psicobióticos en humanos deben ser interpretadas con cautela metodológica, requiriendo ensayos clínicos aleatorizados a gran escala antes de considerarse terapias coadyuvantes estándar.""",
        "stem": "¿Cuál es la función específica del butirato mencionada explícitamente en el segundo párrafo del texto?",
        "options": [
            {"key": "A", "text": "Preservar la integridad de la barrera hematoencefálica e inhibir histona deacetilasas.", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "B", "text": "Sintetizar más del 90% de la serotonina corporal en el epitelio del hipocampo.", "is_correct": False, "distractor_type": "CONFUSION_CELLS"},
            {"key": "C", "text": "Reemplazar directamente las terapias farmacológicas en pacientes con disbiosis.", "is_correct": False, "distractor_type": "OVERGENERALIZATION"},
            {"key": "D", "text": "Acelerar la fermentación de proteínas animales en el tracto gástrico superior.", "is_correct": False, "distractor_type": "INCORRECT_SUBSTRATE"},
        ],
        "explanation": {
            "correct_solution": "El segundo párrafo estipula de forma textual: 'el butirato ejerce un rol clave al actuar como inhibidor de histona deacetilasas y preservar la integridad de la barrera hematoencefálica'.",
            "skill_evaluated": "Rastrear - Localizar (información explícita sin paráfrasis deformante).",
            "key_concept": "Localización precisa en párrafos científicos densos."
        }
    },
    {
        "id": "q-lec-02",
        "subtopic_id": "sub-lec-ia-sociedad",
        "skill_code": "RELACIONAR_INTERPRETAR",
        "stimulus_title": "El microbioma humano y la comunicación bidireccional del eje intestino-cerebro",
        "stimulus_text": """La microbiota intestinal, compuesta por billones de microorganismos que habitan el tracto gastrointestinal, ha dejado de ser considerada una simple comunidad comensal para ser entendida como un órgano endocrino y metabólico altamente activo... (texto idéntico)""",
        "stem": "A partir de lo expuesto en el texto, ¿qué relación se puede inferir entre los hábitos alimenticios y la función neurológica?",
        "options": [
            {"key": "A", "text": "Una dieta rica en fibras solubles favorece la producción de metabolitos que protegen el microambiente cerebral.", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "B", "text": "El consumo de psicobióticos suprime por completo la necesidad de serotonina en el sistema nervioso central.", "is_correct": False, "distractor_type": "EXTREME_ABSOLUTE"},
            {"key": "C", "text": "La alimentación carece de influencia frente a factores genéticos hereditarios del hipocampo.", "is_correct": False, "distractor_type": "CONTRADICTION"},
            {"key": "D", "text": "La proliferación bacteriana en el estómago es indispensable para evitar trastornos digestivos.", "is_correct": False, "distractor_type": "ANATOMICAL_ERROR"},
        ],
        "explanation": {
            "correct_solution": "El texto vincula la fermentación de fibras solubles con la síntesis de AGCC (como el butirato), los cuales protegen la barrera hematoencefálica. Se deduce que la dieta influye en la protección neurológica.",
            "skill_evaluated": "Relacionar - Interpretar (inferencia válida a partir de premisas textuales).",
            "key_concept": "Causalidad indirecta mediada por metabolitos."
        }
    },
    {
        "id": "q-lec-03",
        "subtopic_id": "sub-lec-columnas-opinion",
        "skill_code": "EVALUAR_REFLEXIONAR",
        "stimulus_title": "La tiranía del algoritmo y la pérdida de la atención profunda",
        "stimulus_text": """Vivimos atrapados en la economía de la distracción planificada. Plataformas digitales diseñadas con técnicas de condicionamiento operante nos bombardean con recompensas variables e infinitas cascadas de microcontenido, atomizando nuestra capacidad de sumergirnos en la lectura reposada y el análisis crítico. La promesa inicial de democratizar el conocimiento ha degenerado en un ecosistema donde la indignación superficial cotiza al alza y el silencio reflexivo es penalizado por las métricas de retención. Si delegamos nuestro discernimiento en algoritmos predictivos que solo nos confirman lo que ya creemos, renunciamos a la virtud cívica de confrontar la complejidad del mundo real.""",
        "stem": "¿Cuál es la postura fundamental del emisor respecto al impacto de las plataformas digitales contemporáneas?",
        "options": [
            {"key": "A", "text": "Adopta una mirada entusiasta ante las ventajas comerciales del condicionamiento operante.", "is_correct": False, "distractor_type": "OPPOSITE_TONE"},
            {"key": "B", "text": "Mantiene una posición crítica y de denuncia ante el deterioro deliberado de la autonomía cognitiva y el debate cívico.", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "C", "text": "Presenta una descripción neutral y técnica sobre la arquitectura de redes neuronales predictivas.", "is_correct": False, "distractor_type": "INCORRECT_GENRE"},
            {"key": "D", "text": "Propone la abolición total de internet como única salida para recuperar la concentración humana.", "is_correct": False, "distractor_type": "EXAGGERATION"},
        ],
        "explanation": {
            "correct_solution": "El autor utiliza un lenguaje valorativo severo ('economía de la distracción planificada', 'atomizando nuestra capacidad', 'renunciamos a la virtud cívica') para denunciar el impacto negativo.",
            "skill_evaluated": "Evaluar - Reflexionar (identificación del tono, perspectiva y propósito discursivo).",
            "key_concept": "Tono crítico y postura ideológica del emisor."
        }
    },

    # --- M2: Matemática 2 ---
    {
        "id": "q-m2-01",
        "subtopic_id": "sub-m2-logaritmos",
        "skill_code": "RESOLVER_PROBLEMAS",
        "stimulus_title": None,
        "stimulus_text": None,
        "stem": "¿Cuál es el conjunto solución de la ecuación logarítmica $\\log_2(x) + \\log_2(x - 2) = 3$ en el conjunto de los números reales?",
        "options": [
            {"key": "A", "text": "$\\{-2, 4\\}$", "is_correct": False, "distractor_type": "EXTRANEOUS_ROOT"},
            {"key": "B", "text": "$\\{-2\\}$", "is_correct": False, "distractor_type": "INVALID_DOMAIN"},
            {"key": "C", "text": "$\\{4\\}$", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "D", "text": "$\\{8\\}$", "is_correct": False, "distractor_type": "ARITHMETIC_ERROR"},
        ],
        "explanation": {
            "correct_solution": "Restricción de dominio: $x > 0$ y $x - 2 > 0 \\implies x > 2$. Propiedad del producto: $\\log_2(x(x - 2)) = 3 \\iff x(x - 2) = 2^3 = 8 \\iff x^2 - 2x - 8 = 0 \\iff (x - 4)(x + 2) = 0$. Como $x > 2$, la única solución admisible es $x = 4$.",
            "skill_evaluated": "Resolver problemas en R (ecuaciones logarítmicas y validación estricta de dominio).",
            "key_concept": "Dominio de la función logarítmica real."
        }
    },
    {
        "id": "q-m2-02",
        "subtopic_id": "sub-m2-dist-normal",
        "skill_code": "MODELAR",
        "stimulus_title": None,
        "stimulus_text": None,
        "stem": "Los puntajes de un ensayo estandarizado se distribuyen de forma normal con media $\\mu = 500$ puntos y desviación estándar $\\sigma = 100$ puntos. Si un estudiante obtiene un puntaje $X = 680$, ¿cuál es su puntaje tipificado $Z$?",
        "options": [
            {"key": "A", "text": "$Z = 1.20$", "is_correct": False, "distractor_type": "INCORRECT_SUBTRACTION"},
            {"key": "B", "text": "$Z = 1.80$", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "C", "text": "$Z = 0.68$", "is_correct": False, "distractor_type": "RAW_PERCENTAGE"},
            {"key": "D", "text": "$Z = 2.40$", "is_correct": False, "distractor_type": "SCALE_MISMATCH"},
        ],
        "explanation": {
            "correct_solution": "La fórmula de tipificación para una variable normal es $Z = \\frac{X - \\mu}{\\sigma}$. Sustituyendo: $Z = \\frac{680 - 500}{100} = \\frac{180}{100} = 1.80$.",
            "skill_evaluated": "Modelar distribuciones continuas (estandarización gaussiana).",
            "key_concept": "Puntaje Z en distribución normal."
        }
    },

    # --- CIENCIAS: Módulo Común & Electivo ---
    {
        "id": "q-cie-01",
        "subtopic_id": "sub-cie-genetica",
        "skill_code": "PENSAMIENTO_CIENTIFICO_ANALIZAR",
        "stimulus_title": None,
        "stimulus_text": None,
        "stem": "En las plantas de arveja, el color amarillo de la semilla ($A$) es dominante sobre el verde ($a$), y la forma lisa ($B$) es dominante sobre la rugosa ($b$). Si se cruzan dos plantas dihíbridas con genotipo $AaBb \\times AaBb$, ¿cuál es la probabilidad teórica esperada de obtener descendientes con semillas verdes y rugosas?",
        "options": [
            {"key": "A", "text": "$\\frac{9}{16}$", "is_correct": False, "distractor_type": "DOUBLE_DOMINANT"},
            {"key": "B", "text": "$\\frac{3}{16}$", "is_correct": False, "distractor_type": "SINGLE_RECESSIVE"},
            {"key": "C", "text": "$\\frac{1}{16}$", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "D", "text": "$\\frac{1}{4}$", "is_correct": False, "distractor_type": "MONOHYBRID_PROPORTION"},
        ],
        "explanation": {
            "correct_solution": "Para que la semilla sea verde y rugosa, su genotipo debe ser homocigoto recesivo para ambos alelos: $aabb$. En un cruce dihíbrido clásico de Mendel con surtido independiente: $P(aa) = \\frac{1}{4}$ y $P(bb) = \\frac{1}{4}$. Por regla del producto: $P(aabb) = \\frac{1}{4} \\times \\frac{1}{4} = \\frac{1}{16}$.",
            "skill_evaluated": "Procesar y analizar evidencia en genética mendeliana.",
            "key_concept": "Ley de transmisión independiente (proporción 9:3:3:1)."
        }
    },
    {
        "id": "q-cie-02",
        "subtopic_id": "sub-cie-metodo",
        "skill_code": "PENSAMIENTO_CIENTIFICO_ANALIZAR",
        "stimulus_title": "Investigación experimental sobre actividad enzimática",
        "stimulus_text": "Un equipo de investigadores mide la velocidad de degradación de peróxido de hidrógeno por la enzima catalasa a diferentes temperaturas ($10^\\circ\\text{C}, 20^\\circ\\text{C}, 37^\\circ\\text{C}, 60^\\circ\\text{C}$). En todos los tubos de ensayo se mantiene idéntica la concentración de la enzima, el volumen de sustrato y el pH neutro constante (7.0).",
        "stem": "¿Cuál es la variable independiente en el diseño experimental descrito?",
        "options": [
            {"key": "A", "text": "La concentración de la enzima catalasa.", "is_correct": False, "distractor_type": "CONTROLLED_VARIABLE"},
            {"key": "B", "text": "El pH del medio de reacción.", "is_correct": False, "distractor_type": "CONTROLLED_VARIABLE"},
            {"key": "C", "text": "La velocidad de degradación del peróxido de hidrógeno.", "is_correct": False, "distractor_type": "DEPENDENT_VARIABLE"},
            {"key": "D", "text": "La temperatura a la cual se somete cada tubo de ensayo.", "is_correct": True, "distractor_type": "CORRECT"},
        ],
        "explanation": {
            "correct_solution": "La variable independiente es aquella manipulada activamente por el experimentador para observar su efecto sobre el sistema. En este caso, la temperatura es el factor manipulado deliberadamente en 4 niveles.",
            "skill_evaluated": "Planificar e interpretar variables en investigación científica.",
            "key_concept": "Identificación de variables (independiente vs dependiente vs controladas)."
        }
    },

    # --- HISTORIA: Historia y Cs Sociales ---
    {
        "id": "q-his-01",
        "subtopic_id": "sub-his-ciudadania",
        "skill_code": "ANALISIS_FUENTES",
        "stimulus_title": "Principio fundamental de la separación de poderes",
        "stimulus_text": """'Para que no se pueda abusar del poder, es preciso que el poder detenga al poder. Una constitución puede ser tal que nadie sea obligado a hacer cosas a que la ley no le obliga, ni a no hacer las que la ley le permite.' — Montesquieu, Del espíritu de las leyes (1748).""",
        "stem": "A partir del fragmento citado, ¿cuál es el objetivo primordial de la doctrina republicana de división de los poderes del Estado?",
        "options": [
            {"key": "A", "text": "Concentrar la toma de decisiones económicas exclusivamente en el poder judicial.", "is_correct": False, "distractor_type": "ABSURD_DISTRACTOR"},
            {"key": "B", "text": "Evitar la concentración despótica de la autoridad mediante mecanismos institucionales de control recíproco.", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "C", "text": "Eliminar la vigencia de las leyes para otorgar libertad absoluta a los gobernantes.", "is_correct": False, "distractor_type": "CONTRADICTION"},
            {"key": "D", "text": "Garantizar que el poder legislativo subordine de forma permanente a los tribunales de justicia.", "is_correct": False, "distractor_type": "OPPOSITE_PRINCIPLE"},
        ],
        "explanation": {
            "correct_solution": "Montesquieu formula explícitamente el sistema de frenos y contrapesos (checks and balances): el poder dividido en órganos autónomos evita el abuso y la tiranía garantizando las libertades civiles.",
            "skill_evaluated": "Análisis de fuentes doctrinales y formación ciudadana.",
            "key_concept": "Separación de poderes y Estado de Derecho."
        }
    },
    {
        "id": "q-his-02",
        "subtopic_id": "sub-his-mercado",
        "skill_code": "PENSAMIENTO_CRITICO",
        "stimulus_title": None,
        "stimulus_text": None,
        "stem": "Cuando un Banco Central decide aumentar su Tasa de Política Monetaria (TPM) en una economía que experimenta presiones inflacionarias sostenidas, ¿cuál es el mecanismo macroeconómico esperado?",
        "options": [
            {"key": "A", "text": "Aumentar el crédito de consumo para acelerar el gasto agregado de los hogares.", "is_correct": False, "distractor_type": "OPPOSITE_EFFECT"},
            {"key": "B", "text": "Incentivar el endeudamiento comercial y depreciar la moneda nacional inmediatamente.", "is_correct": False, "distractor_type": "WRONG_TRANSMISSION"},
            {"key": "C", "text": "Encarecer el costo del crédito y desincentivar el gasto, contrayendo la demanda agregada para estabilizar los precios.", "is_correct": True, "distractor_type": "CORRECT"},
            {"key": "D", "text": "Fijar los precios de la canasta básica familiar por decreto supremo del Ministerio de Hacienda.", "is_correct": False, "distractor_type": "NON_MONETARY_TOOL"},
        ],
        "explanation": {
            "correct_solution": "El alza de la TPM eleva las tasas de interés interbancarias, encareciendo los préstamos a personas y empresas. Esto desincentiva el consumo y la inversión, enfriando la demanda agregada y frenando la inflación.",
            "skill_evaluated": "Pensamiento crítico y comprensión de variables macroeconómicas.",
            "key_concept": "Política monetaria contractiva y control inflacionario."
        }
    }
]

def seed_questions(session_arg: Session = None):
    def _seed(session):
        added = 0
        for q_data in QUESTIONS:
            existing = session.get(PaesQuestion, q_data["id"])
            comp = session.exec(select(PaesCompetency).where(PaesCompetency.code == q_data["skill_code"])).first()
            if not comp:
                # Fallback to resolver_problemas or first
                comp = session.exec(select(PaesCompetency)).first()

            if not existing:
                q = PaesQuestion(
                    id=q_data["id"],
                    subtopic_id=q_data["subtopic_id"],
                    skill_id=comp.id,
                    provenance_type="OFFICIAL",
                    stem=q_data["stem"],
                    stimulus_title=q_data.get("stimulus_title"),
                    stimulus_text=q_data.get("stimulus_text"),
                    options_json=json.dumps(q_data["options"], ensure_ascii=False),
                    explanation_json=json.dumps(q_data["explanation"], ensure_ascii=False),
                    difficulty_estimate=0.5,
                    difficulty_source="OFFICIAL_DEMRE",
                )
                session.add(q)
                added += 1
                logger.info("Question added: %s (%s)", q.id, q.stem[:40])
            else:
                existing.stimulus_title = q_data.get("stimulus_title")
                existing.stimulus_text = q_data.get("stimulus_text")
                session.add(existing)

        session.commit()
        logger.info("Seeded %d multidisciplinary questions successfully!", added)

    if session_arg:
        _seed(session_arg)
    else:
        with Session(engine) as session:
            _seed(session)

if __name__ == "__main__":
    seed_questions()
