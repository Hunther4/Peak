"""
Seed Oficial para Competencia Matemática 1 (M1) - Proceso de Admisión 2026.
Contiene el currículo oficial completo con 4 Ejes Temáticos, 13 Subtemas y 65 preguntas PAES verificadas
(60 regulares puntuables + 5 experimentales piloto).
"""

from typing import Any, Dict
from uuid import NAMESPACE_DNS, UUID, uuid5


def generate_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"paes.m1.{name}")

CURRICULUM_VERSION_ID = UUID("a2a931a3-310b-5854-92ec-093c530cedb0")
SUBJECT_M1_ID = UUID("12ff38c7-817d-5fa8-b799-682a805d803c")

SEED_DATA: Dict[str, Any] = {
    "curriculum_version": {
        "id": "a2a931a3-310b-5854-92ec-093c530cedb0",
        "code": "DEMRE-PAES-REGULAR-2026",
        "name": "Temario Oficial PAES Regular 2026",
        "year": 2026,
        "is_active": True
    },
    "subject": {
        "id": "12ff38c7-817d-5fa8-b799-682a805d803c",
        "curriculum_version_id": "a2a931a3-310b-5854-92ec-093c530cedb0",
        "code": "M1",
        "name": "Competencia Matemática 1",
        "is_mandatory": True,
        "total_questions": 65,
        "scored_questions": 60,
        "pilot_questions": 5,
        "duration_minutes": 140
    },
    "skills": [
        {
            "id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "code": "RESOLVER_PROBLEMAS",
            "name": "Resolver problemas",
            "description": "Capacidad de solucionar situaciones matemáticas en diversos contextos."
        },
        {
            "id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "code": "MODELAR",
            "name": "Modelar",
            "description": "Capacidad de usar, ajustar y evaluar modelos matemáticos."
        },
        {
            "id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "code": "REPRESENTAR",
            "name": "Representar",
            "description": "Capacidad de transferir información entre diferentes formatos simbólicos y gráficos."
        },
        {
            "id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "code": "ARGUMENTAR",
            "name": "Argumentar",
            "description": "Capacidad de validar o refutar proposiciones deductivas y detectar errores."
        }
    ],
    "subject_skills": [
        {
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce"
        },
        {
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b"
        },
        {
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28"
        },
        {
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e"
        }
    ],
    "ejes": [
        {
            "id": "d4f80f01-079f-55ae-bfab-1ccca5d31919",
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "name": "Números",
            "order_index": 1
        },
        {
            "id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "name": "Álgebra y Funciones",
            "order_index": 2
        },
        {
            "id": "ee3f29c9-6322-5535-b41a-733e897cf26c",
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "name": "Geometría",
            "order_index": 3
        },
        {
            "id": "6c041cc4-7fbd-54f0-a350-25034762aab1",
            "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
            "name": "Probabilidad y Estadística",
            "order_index": 4
        }
    ],
    "eje": {
        "id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
        "subject_id": "12ff38c7-817d-5fa8-b799-682a805d803c",
        "name": "Álgebra y Funciones",
        "order_index": 2
    },
    "topics": [
        {
            "id": "f8a96b4f-56c2-5614-9601-94696239bb9f",
            "eje_id": "d4f80f01-079f-55ae-bfab-1ccca5d31919",
            "name": "Números",
            "order_index": 1
        },
        {
            "id": "3bfa1d88-b459-57a2-8ebf-260be37c54a4",
            "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "name": "Álgebra",
            "order_index": 2
        },
        {
            "id": "16415cba-8dab-511d-b91e-f3009f3a0729",
            "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "name": "Funciones",
            "order_index": 3
        },
        {
            "id": "63efa6b0-f211-5e45-8f13-cd12628c1e85",
            "eje_id": "ee3f29c9-6322-5535-b41a-733e897cf26c",
            "name": "Geometría",
            "order_index": 4
        },
        {
            "id": "56888642-36c3-50c7-8616-2884ba8ad2dd",
            "eje_id": "6c041cc4-7fbd-54f0-a350-25034762aab1",
            "name": "Probabilidad y Estadística",
            "order_index": 5
        }
    ],
    "topic": {
        "id": "3bfa1d88-b459-57a2-8ebf-260be37c54a4",
        "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
        "name": "Álgebra",
        "order_index": 2
    },
    "subtopics": [
        {
            "id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "topic_id": "f8a96b4f-56c2-5614-9601-94696239bb9f",
            "eje_id": "d4f80f01-079f-55ae-bfab-1ccca5d31919",
            "eje_name": "Números",
            "topic_name": "Números",
            "name": "Operaciones en enteros y racionales",
            "slug": "m1-num-operaciones-enteros-racionales",
            "description": "Operaciones fundamentales, fracciones, decimales, orden y propiedades en Z y Q.",
            "order_index": 1
        },
        {
            "id": "313b3e06-f800-5add-8da5-61ce582cc933",
            "topic_id": "f8a96b4f-56c2-5614-9601-94696239bb9f",
            "eje_id": "d4f80f01-079f-55ae-bfab-1ccca5d31919",
            "eje_name": "Números",
            "topic_name": "Números",
            "name": "Porcentajes y problemas financieros",
            "slug": "m1-num-porcentajes-financieros",
            "description": "Cálculo de porcentajes, aumentos y descuentos sucesivos, IVA e interés simple.",
            "order_index": 2
        },
        {
            "id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "topic_id": "f8a96b4f-56c2-5614-9601-94696239bb9f",
            "eje_id": "d4f80f01-079f-55ae-bfab-1ccca5d31919",
            "eje_name": "Números",
            "topic_name": "Números",
            "name": "Potencias y raíces",
            "slug": "m1-num-potencias-raices",
            "description": "Propiedades de potencias de base racional y exponente entero, cálculo y descomposición de raíces cuadradas.",
            "order_index": 3
        },
        {
            "id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "topic_id": "3bfa1d88-b459-57a2-8ebf-260be37c54a4",
            "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "eje_name": "Álgebra y Funciones",
            "topic_name": "Álgebra",
            "name": "Ecuaciones lineales de primer grado",
            "slug": "m1-algebra-ecuaciones-lineales",
            "description": "Resolución analítica, representación y modelamiento de ecuaciones ax + b = c en Q.",
            "order_index": 4
        },
        {
            "id": "3619d611-2424-584d-a40f-4235202f246f",
            "topic_id": "3bfa1d88-b459-57a2-8ebf-260be37c54a4",
            "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "eje_name": "Álgebra y Funciones",
            "topic_name": "Álgebra",
            "name": "Sistemas de ecuaciones 2x2",
            "slug": "m1-alg-sistemas-ecuaciones",
            "description": "Resolución algebraica e interpretación geométrica de sistemas lineales 2x2 en Q.",
            "order_index": 5
        },
        {
            "id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "topic_id": "16415cba-8dab-511d-b91e-f3009f3a0729",
            "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "eje_name": "Álgebra y Funciones",
            "topic_name": "Funciones",
            "name": "Función lineal y afín",
            "slug": "m1-alg-funcion-lineal-afin",
            "description": "Pendiente, coeficiente de posición, tablas de valores y gráficas de funciones f(x) = mx + n.",
            "order_index": 6
        },
        {
            "id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "topic_id": "16415cba-8dab-511d-b91e-f3009f3a0729",
            "eje_id": "151a79c6-338a-5ad3-886e-99e84129dbc5",
            "eje_name": "Álgebra y Funciones",
            "topic_name": "Funciones",
            "name": "Función cuadrática",
            "slug": "m1-alg-funcion-cuadratica",
            "description": "Vértice, concavidad, eje de simetría, intersecciones con ejes y problemas de máximos y mínimos cuadráticos.",
            "order_index": 7
        },
        {
            "id": "29d5f909-b289-593d-8a0f-758a0e213cec",
            "topic_id": "63efa6b0-f211-5e45-8f13-cd12628c1e85",
            "eje_id": "ee3f29c9-6322-5535-b41a-733e897cf26c",
            "eje_name": "Geometría",
            "topic_name": "Geometría",
            "name": "Perímetros y áreas de polígonos",
            "slug": "m1-geo-perimetros-areas-poligonos",
            "description": "Cálculo de perímetros y áreas en triángulos, cuadriláteros y figuras compuestas, áreas sombreadas.",
            "order_index": 8
        },
        {
            "id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "topic_id": "63efa6b0-f211-5e45-8f13-cd12628c1e85",
            "eje_id": "ee3f29c9-6322-5535-b41a-733e897cf26c",
            "eje_name": "Geometría",
            "topic_name": "Geometría",
            "name": "Teorema de Pitágoras",
            "slug": "m1-geo-teorema-pitagoras",
            "description": "Aplicación directa, cálculo de diagonales, distancias en el plano cartesiano y recíproco de Pitágoras.",
            "order_index": 9
        },
        {
            "id": "0ed0ae36-4f7c-5880-b5f5-3889c6199615",
            "topic_id": "63efa6b0-f211-5e45-8f13-cd12628c1e85",
            "eje_id": "ee3f29c9-6322-5535-b41a-733e897cf26c",
            "eje_name": "Geometría",
            "topic_name": "Geometría",
            "name": "Transformaciones isométricas",
            "slug": "m1-geo-transformaciones-isometricas",
            "description": "Traslaciones vectoriales, reflexiones axiales y centrales, rotaciones respecto al origen y congruencia.",
            "order_index": 10
        },
        {
            "id": "882718aa-40f4-5098-9f8c-fc56e71c136f",
            "topic_id": "56888642-36c3-50c7-8616-2884ba8ad2dd",
            "eje_id": "6c041cc4-7fbd-54f0-a350-25034762aab1",
            "eje_name": "Probabilidad y Estadística",
            "topic_name": "Estadística",
            "name": "Medidas de tendencia central y posición",
            "slug": "m1-est-tendencia-central-posicion",
            "description": "Media aritmética, mediana, moda, cuartiles, percentiles y diagramas de cajón.",
            "order_index": 11
        },
        {
            "id": "0a90ccdf-9fc5-5fac-8972-9616c11a7473",
            "topic_id": "56888642-36c3-50c7-8616-2884ba8ad2dd",
            "eje_id": "6c041cc4-7fbd-54f0-a350-25034762aab1",
            "eje_name": "Probabilidad y Estadística",
            "topic_name": "Estadística",
            "name": "Tablas y gráficos estadísticos",
            "slug": "m1-est-tablas-graficos-estadisticos",
            "description": "Tablas de frecuencia absoluta, relativa y acumulada, histogramas, polígonos de frecuencia y circulares.",
            "order_index": 12
        },
        {
            "id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "topic_id": "56888642-36c3-50c7-8616-2884ba8ad2dd",
            "eje_id": "6c041cc4-7fbd-54f0-a350-25034762aab1",
            "eje_name": "Probabilidad y Estadística",
            "topic_name": "Probabilidad",
            "name": "Regla de Laplace y probabilidad clásica",
            "slug": "m1-est-regla-laplace-probabilidad",
            "description": "Espacio muestral, regla de Laplace, evento complementario y suma de probabilidades disjuntas.",
            "order_index": 13
        }
    ],
    "subtopic_prerequisites": [
        {
            "subtopic_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "prerequisite_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "relationship_type": "STRICT_PREREQUISITE",
            "minimum_mastery_required": 0.6
        },
        {
            "subtopic_id": "3619d611-2424-584d-a40f-4235202f246f",
            "prerequisite_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "relationship_type": "STRICT_PREREQUISITE",
            "minimum_mastery_required": 0.6
        },
        {
            "subtopic_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "prerequisite_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "relationship_type": "STRICT_PREREQUISITE",
            "minimum_mastery_required": 0.6
        },
        {
            "subtopic_id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "prerequisite_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "relationship_type": "RECOMMENDED_PREVIOUS",
            "minimum_mastery_required": 0.55
        },
        {
            "subtopic_id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "prerequisite_id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "relationship_type": "STRICT_PREREQUISITE",
            "minimum_mastery_required": 0.6
        },
        {
            "subtopic_id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "prerequisite_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "relationship_type": "STRICT_PREREQUISITE",
            "minimum_mastery_required": 0.55
        }
    ],
    "questions": [
        {
            "id": "ce66842d-a886-5908-866c-f4b952824671",
            "subtopic_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es el resultado de resolver la operación $\\frac{3}{4} - \\frac{1}{2} \\cdot \\left(\\frac{2}{3} + \\frac{1}{6}\\right)$?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\frac{1}{3}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\frac{5}{24}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$\\frac{7}{12}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$-\\frac{1}{3}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Resolver el paréntesis, luego el producto y finalmente la sustracción en Q.",
                "step_by_step": "1) Paréntesis: $2/3 + 1/6 = (4+1)/6 = 5/6$.\\n2) Producto: $(1/2) * (5/6) = 5/12$.\\n3) Sustracción: $3/4 - 5/12 = 9/12 - 5/12 = 4/12 = 1/3$.",
                "key_concept": "Prioridad de operaciones y adición/multiplicación en los números racionales.",
                "frequent_mistake": "Restar $3/4 - 1/2 = 1/4$ antes de efectuar la multiplicación con el paréntesis."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "50ec07f0-f0ec-5a05-80ba-4108a3ff7b8a",
            "subtopic_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un estanque de agua contiene $\\frac{2}{5}$ de su capacidad total. Si se agregan $180$ litros, el estanque queda lleno hasta los $\\frac{7}{10}$ de su capacidad. ¿Cuál es la capacidad total del estanque en litros?",
            "options": [
                {
                    "id": "A",
                    "content": "$600\\text{ litros}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$540\\text{ litros}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$450\\text{ litros}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$720\\text{ litros}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Plantear la diferencia de fracciones correspondiente al volumen agregado: $(7/10 - 2/5)C = 180$.",
                "step_by_step": "1) Fracción agregada: $7/10 - 2/5 = 7/10 - 4/10 = 3/10$.\\n2) Ecuación: $(3/10) * C = 180$.\\n3) Despejar: $C = 180 * 10 / 3 = 600\\text{ litros}$.",
                "key_concept": "Fracciones como operadores sobre cantidades continuas y resolución de ecuaciones en Q.",
                "frequent_mistake": "Restar directamente los numeradores sin igualar denominadores o confundir la fracción agregada con la final."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "e1a6fcc4-6043-5d70-a969-4c703698f944",
            "subtopic_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál de las siguientes relaciones de orden es correcta para los números racionales $p = \\frac{5}{8}$, $q = 0,\\overline{6}$ y $r = \\frac{7}{12}$?",
            "options": [
                {
                    "id": "A",
                    "content": "$r < p < q$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$p < r < q$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$q < p < r$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$r < q < p$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Convertir a decimal o común denominador para comparar: $r \\approx 0,583$, $p = 0,625$, $q \\approx 0,667$.",
                "step_by_step": "1) $r = 7/12 \\approx 0,5833...$\\n2) $p = 5/8 = 0,625$.\\n3) $q = 2/3 \\approx 0,6666...$\\n4) Orden ascendente: $0,5833... < 0,625 < 0,6666... \\implies r < p < q$.",
                "key_concept": "Densidad y orden en el conjunto de los números racionales.",
                "frequent_mistake": "Truncar el decimal periódico $0,\\overline{6}$ a $0,6$ y asumir erróneamente que es menor que $0,625$."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "5bcaed5d-01f3-5a47-b4ea-0cb31fbec4b1",
            "subtopic_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere la afirmación: «Para todo número racional $x > 0$, su inverso multiplicativo $\\frac{1}{x}$ es menor que $x$». ¿Cuál de los siguientes contraejemplos demuestra que esta afirmación es FALSA?",
            "options": [
                {
                    "id": "A",
                    "content": "$x = \\frac{1}{2}$, pues $\\frac{1}{1/2} = 2$ y $2 > \\frac{1}{2}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$x = 2$, pues $\\frac{1}{2} < 2$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "$x = 3$, pues $\\frac{1}{3} < 3$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "D",
                    "content": "$x = 1$, pues $\\frac{1}{1} = 1$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Para $0 < x < 1$, el recíproco $1/x$ es estrictamente mayor que $1$, refutando la afirmación universal.",
                "step_by_step": "1) Evaluar $x = 1/2$: su inverso es $1 / (1/2) = 2$.\\n2) Comparar: $2 > 1/2$, lo que contradice $1/x < x$.\\n3) Por ende, $x = 1/2$ refuta deductivamente la afirmación.",
                "key_concept": "Propiedades de orden del inverso multiplicativo para racionales en el intervalo $(0, 1)$.",
                "frequent_mistake": "Probar únicamente con números enteros mayores que 1, donde la propiedad sí se cumple aparentemente."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "c87fd607-06ca-5e49-937c-4529178597f3",
            "subtopic_id": "f12b90e9-0ac9-565d-8d73-487671345191",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "En una receta de repostería se mezclan $\\frac{3}{4}\\text{ kg}$ de harina, $\\frac{2}{5}\\text{ kg}$ de azúcar y $\\frac{1}{8}\\text{ kg}$ de mantequilla. ¿Cuál es la masa total de la mezcla?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\frac{51}{40}\\text{ kg}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\frac{6}{17}\\text{ kg}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$\\frac{49}{40}\\text{ kg}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$\\frac{23}{20}\\text{ kg}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Calcular mcm(4, 5, 8) = 40 y sumar numeradores amplificados: $(30 + 16 + 5)/40 = 51/40$.",
                "step_by_step": "1) mcm(4, 5, 8) = 40.\\n2) $3/4 = 30/40$, $2/5 = 16/40$, $1/8 = 5/40$.\\n3) Suma: $(30 + 16 + 5)/40 = 51/40\\text{ kg}$.",
                "key_concept": "Adición de números racionales con distinto denominador mediante mínimo común múltiplo.",
                "frequent_mistake": "Sumar linealmente numeradores y denominadores: $(3+2+1)/(4+5+8) = 6/17$."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "ea69bfb2-ca06-59ba-ba19-c9635079d40b",
            "subtopic_id": "313b3e06-f800-5add-8da5-61ce582cc933",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "El precio original de una chaqueta es de $\\$50.000$. En una liquidación se le aplica un primer descuento del $20\\%$ y, al momento de pagar con tarjeta de la tienda, se aplica un descuento adicional del $10\\%$ sobre el valor ya rebajado. ¿Cuál es el precio final que se paga por la chaqueta?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\$36.000$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\$35.000$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$\\$38.000$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$\\$40.000$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                }
            ],
            "explanation": {
                "short_summary": "Aplicar factores sucesivos de descuento: $50000 * 0,80 * 0,90 = 36000$.",
                "step_by_step": "1) Primer descuento del 20%: $50000 * (1 - 0,20) = 50000 * 0,80 = \\$40000$.\\n2) Segundo descuento del 10% sobre 40000: $40000 * (1 - 0,10) = 40000 * 0,90 = \\$36000$.",
                "key_concept": "Descuentos sucesivos encadenados y variación porcentual compuesta.",
                "frequent_mistake": "Sumar los porcentajes de descuento: $20\\% + 10\\% = 30\\%$, descontando el 30% a 50000 para llegar erróneamente a 35000."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "e7ecb6cc-2dc6-5ff9-a312-70e67faadcd1",
            "subtopic_id": "313b3e06-f800-5add-8da5-61ce582cc933",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un comerciante adquiere un producto a un costo neto $P$ y desea fijar un precio de venta que le otorgue un margen de ganancia del $25\\%$ sobre el costo neto. Si al venderlo debe agregar el Impuesto al Valor Agregado (IVA) del $19\\%$, ¿cuál de las siguientes expresiones representa el precio final de venta?",
            "options": [
                {
                    "id": "A",
                    "content": "$1,19 \\cdot 1,25 \\cdot P$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(1 + 0,25 + 0,19)P$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$1,25 P + 0,19$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "D",
                    "content": "$0,25 \\cdot 0,19 \\cdot P$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Multiplicar consecutivamente por los factores de incremento: $(1 + 0,25)$ y $(1 + 0,19)$.",
                "step_by_step": "1) Precio con ganancia del 25%: $P * (1 + 0,25) = 1,25P$.\\n2) Agregar IVA del 19% sobre el precio de venta neto: $1,25P * (1 + 0,19) = 1,19 * 1,25 * P$.",
                "key_concept": "Modelamiento algebraico de factores multiplicativos en recargos e impuestos sucesivos.",
                "frequent_mistake": "Sumar aritméticamente las tasas porcentuales como si compartieran la misma base de cálculo."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "eca86e76-e519-5a8c-bada-92f73577d737",
            "subtopic_id": "313b3e06-f800-5add-8da5-61ce582cc933",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "En una institución educativa, el presupuesto se distribuye en: $40\\%$ remuneraciones, $30\\%$ infraestructura, $20\\%$ tecnología y el resto en biblioteca. Si esta información se representa en un gráfico circular, ¿cuántos grados sexagesimales corresponden al sector de biblioteca?",
            "options": [
                {
                    "id": "A",
                    "content": "$36^\\circ$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$10^\\circ$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$72^\\circ$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$45^\\circ$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Calcular porcentaje restante (10%) y multiplicar por 360 grados: $0,10 * 360 = 36$.",
                "step_by_step": "1) Porcentaje biblioteca: $100\\% - (40\\% + 30\\% + 20\\%) = 10\\%$.\\n2) Proporción angular: $10\\% * 360^\\circ = (10/100) * 360^\\circ = 36^\\circ$.",
                "key_concept": "Correspondencia proporcional entre porcentajes y ángulos en representaciones circulares.",
                "frequent_mistake": "Confundir directamente el valor porcentual (10) con los grados sexagesimales (10°)."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "ac060f23-e00b-5ee6-9a5e-a2bcaa31085d",
            "subtopic_id": "313b3e06-f800-5add-8da5-61ce582cc933",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "El valor de un activo financiero subió un $20\\%$ durante la primera semana del mes y bajó un $20\\%$ durante la segunda semana. Un inversionista afirma: «Al cabo de las dos semanas, el activo recuperó exactamente su valor inicial». ¿Por qué es FALSA la afirmación del inversionista?",
            "options": [
                {
                    "id": "A",
                    "content": "Porque el valor final equivale al $96\\%$ del valor inicial (hubo una pérdida neta del $4\\%$)",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Porque el valor final equivale al $104\\%$ del valor inicial",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "Porque un aumento y una disminución de igual porcentaje siempre se anulan",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "D",
                    "content": "Porque el porcentaje de disminución se aplica sobre el capital original",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "La base sobre la que se aplica la disminución es mayor: $1,20 * 0,80 = 0,96$, lo que implica una reducción neta del 4%.",
                "step_by_step": "1) Sea $V_0$ el valor inicial. Tras el alza del 20%: $V_1 = 1,20 V_0$.\\n2) La baja del 20% actúa sobre $V_1$: $V_2 = V_1 * (1 - 0,20) = 1,20 V_0 * 0,80 = 0,96 V_0$.\\n3) Como $0,96 V_0 < V_0$, el activo no recuperó su valor, sino que perdió un 4%.",
                "key_concept": "Asimetría en variaciones porcentuales sucesivas sobre bases dinámicas.",
                "frequent_mistake": "Creer que sumas algebraicas de porcentajes sobre distintas bases tienen balance nulo."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "36232be7-7922-53d0-9dcb-1061b61612bc",
            "subtopic_id": "313b3e06-f800-5add-8da5-61ce582cc933",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Una persona coloca un capital inicial $C$ en una inversión a interés simple con una tasa anual del $r\\%$. ¿Cuál expresión modela el monto total acumulado al término de $t$ años?",
            "options": [
                {
                    "id": "A",
                    "content": "$C \\cdot \\left(1 + \\frac{r \\cdot t}{100}\\right)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$C \\cdot \\left(1 + \\frac{r}{100}\\right)^t$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "$C + \\frac{r \\cdot t}{100}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$C \\cdot \\frac{r \\cdot t}{100}$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                }
            ],
            "explanation": {
                "short_summary": "Monto = Capital + Interés, donde el interés simple es $I = C * (r*t / 100)$.",
                "step_by_step": "1) Interés simple ganado: $I = C * (r/100) * t$.\\n2) Monto total acumulado: $M = C + I = C + C * (r*t/100) = C * (1 + (r*t)/100)$.",
                "key_concept": "Fórmula canónica del interés simple y factorización del capital inicial.",
                "frequent_mistake": "Confundir la fórmula lineal del interés simple con la fórmula exponencial del interés compuesto (opción B)."
            },
            "difficulty_estimate": 0.6,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": True,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "ad812c93-1150-55e0-ac3a-f3bfeb9b2ae0",
            "subtopic_id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es el valor simplificado de la expresión $\\left(\\frac{2}{3}\\right)^{-2} \\cdot \\left(\\frac{4}{9}\\right)^2$?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\frac{4}{9}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\frac{9}{4}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$\\frac{16}{81}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$\\frac{8}{27}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Invertir la fracción del exponente negativo y simplificar: $(9/4) * (16/81) = 4/9$.",
                "step_by_step": "1) $(2/3)^{-2} = (3/2)^2 = 9/4$.\\n2) $(4/9)^2 = 16/81$.\\n3) Multiplicar y simplificar: $(9/4) * (16/81) = (9*16)/(4*81) = (1*4)/(1*9) = 4/9$.",
                "key_concept": "Propiedades de potencias de exponente negativo y simplificación cruzada.",
                "frequent_mistake": "Olvidar invertir la base al eliminar el signo negativo del exponente."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "3251e783-824c-5a93-9760-67d800072047",
            "subtopic_id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Una población inicial de $500$ bacterias se duplica cada $3$ horas en un medio de cultivo favorable. ¿Cuál de las siguientes funciones modela la cantidad de bacterias presentes al cabo de $t$ horas?",
            "options": [
                {
                    "id": "A",
                    "content": "$N(t) = 500 \\cdot 2^{t/3}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$N(t) = 500 \\cdot 2^{3t}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$N(t) = 500 \\cdot 3^{t/2}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "D",
                    "content": "$N(t) = 500 + 2^{t/3}$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                }
            ],
            "explanation": {
                "short_summary": "El exponente representa el número de períodos de duplicación transcurridos: $t/3$.",
                "step_by_step": "1) En 3 horas se multiplica por 2 (1 duplicación).\\n2) En $t$ horas han transcurrido $t/3$ períodos.\\n3) Población: $N(t) = 500 * 2^{t/3}$.",
                "key_concept": "Modelamiento geométrico/exponencial de crecimiento poblacional.",
                "frequent_mistake": "Multiplicar el tiempo por 3 en lugar de dividirlo, produciendo un crecimiento astronómico irreal."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "6285741c-855a-52f6-88f1-ea509cbde5c8",
            "subtopic_id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "¿Entre cuáles dos números enteros consecutivos se ubica en la recta numérica el valor de $\\sqrt{70}$?",
            "options": [
                {
                    "id": "A",
                    "content": "Entre $8$ y $9$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Entre $7$ y $8$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "Entre $34$ y $36$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "Entre $9$ y $10$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Comparar cuadrados perfectos: $8^2 = 64 < 70 < 81 = 9^2 \\implies 8 < \\sqrt{70} < 9$.",
                "step_by_step": "1) Identificar cuadrados perfectos cercanos a 70: $64$ y $81$.\\n2) Como $64 < 70 < 81$, aplicando raíz cuadrada monótona creciente: $\\sqrt{64} < \\sqrt{70} < \\sqrt{81}$.\\n3) Conclusión: $8 < \\sqrt{70} < 9$.",
                "key_concept": "Aproximación y acotamiento de raíces cuadradas inexactas.",
                "frequent_mistake": "Dividir el número 70 por 2 resultando 35 y asumir que la raíz está cerca de 35."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "15e2873d-ac2c-5b28-b28a-d6c7057845b1",
            "subtopic_id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere la proposición: «Para todo par de números reales positivos $a$ y $b$, se cumple siempre que $\\sqrt{a + b} = \\sqrt{a} + \\sqrt{b}$». ¿Por qué es FALSA esta proposición?",
            "options": [
                {
                    "id": "A",
                    "content": "Porque si $a = 9$ y $b = 16$, se tiene $\\sqrt{9 + 16} = 5$, mientras que $\\sqrt{9} + \\sqrt{16} = 7$, resultando $5 \\neq 7$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Porque la raíz cuadrada de una suma solo está definida cuando $a = b$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "Porque $\\sqrt{a} + \\sqrt{b}$ siempre da un número irracional",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "Porque la igualdad solo se cumple si $a$ y $b$ son negativos",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "La radicación no es distributiva con respecto a la adición, demostrado por el contraejemplo $a=9, b=16$.",
                "step_by_step": "1) Evaluar lado izquierdo con $a=9, b=16$: $\\sqrt{9+16} = \\sqrt{25} = 5$.\\n2) Evaluar lado derecho: $\\sqrt{9} + \\sqrt{16} = 3 + 4 = 7$.\\n3) Como $5 \\neq 7$, la propiedad universal queda refutada.",
                "key_concept": "No linealidad del operador radical frente a la estructura aditiva.",
                "frequent_mistake": "Extrapolar erróneamente la distributividad de la raíz en la multiplicación $(\\sqrt{ab} = \\sqrt{a}\\sqrt{b})$ hacia la suma."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "e500f451-8364-532d-83a8-f335b27400c4",
            "subtopic_id": "6ee9ce75-3ad3-5d30-8e79-30ae0b5f2510",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es el resultado de simplificar la expresión $\\sqrt{75} - \\sqrt{12} + \\sqrt{27}$?",
            "options": [
                {
                    "id": "A",
                    "content": "$6\\sqrt{3}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\sqrt{90}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$4\\sqrt{3}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$10\\sqrt{3}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Descomponer en factores primos con cuadrados perfectos: $5\\sqrt{3} - 2\\sqrt{3} + 3\\sqrt{3} = 6\\sqrt{3}$.",
                "step_by_step": "1) $\\sqrt{75} = \\sqrt{25 * 3} = 5\\sqrt{3}$.\\n2) $\\sqrt{12} = \\sqrt{4 * 3} = 2\\sqrt{3}$.\\n3) $\\sqrt{27} = \\sqrt{9 * 3} = 3\\sqrt{3}$.\\n4) Agrupar coeficientes: $(5 - 2 + 3)\\sqrt{3} = 6\\sqrt{3}$.",
                "key_concept": "Descomposición y adición de radicales semejantes.",
                "frequent_mistake": "Operar los radicandos directamente bajo una sola raíz: $\\sqrt{75 - 12 + 27} = \\sqrt{90}$."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "845d7c7b-c0c1-5a58-97d3-3edbbd9308a7",
            "subtopic_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es el valor de $x$ en la ecuación $3(2x - 5) + 4 = 19$?",
            "options": [
                {
                    "id": "A",
                    "content": "$x = 5$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$x = 4$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$x = 10$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$x = -5$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Distribuir el factor 3 y despejar x.",
                "step_by_step": "1) $3(2x - 5) + 4 = 19 \\implies 6x - 15 + 4 = 19$.\\n2) $6x - 11 = 19$.\\n3) $6x = 19 + 11 = 30$.\\n4) $x = 30 / 6 = 5$.",
                "key_concept": "Propiedad distributiva y transposición aditiva en Z.",
                "frequent_mistake": "Omitir la distribución del factor 3 sobre el término -5 o cometer errores aritméticos al sumar 19 + 11."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "4946ad4b-588e-5849-9799-0cac6558def8",
            "subtopic_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "DERIVED",
            "stem": "Si $\\frac{x - 1}{3} - \\frac{x + 2}{4} = \\frac{1}{2}$, entonces el valor de $x$ es:",
            "options": [
                {
                    "id": "A",
                    "content": "$x = 16$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$x = 4$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$x = 10$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$x = 14$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Multiplicar por el mcm(3,4,2) = 12 y cuidar el signo del binomio sustraendo.",
                "step_by_step": "1) Multiplicar por 12: $4(x - 1) - 3(x + 2) = 6$.\\n2) $4x - 4 - 3x - 6 = 6$.\\n3) $x - 10 = 6$.\\n4) $x = 16$.",
                "key_concept": "Resolución de ecuaciones lineales fraccionarias y ley de signos en numeradores.",
                "frequent_mistake": "No aplicar el signo negativo a ambos términos del binomio (x + 2), escribiendo erróneamente -3x + 6."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "1cbff982-34a7-5133-805d-df844310b0a5",
            "subtopic_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un servicio de transporte cobra una tarifa base fija de $1.200 más $650 por cada kilómetro recorrido. Si una persona pagó un total de $9.000, ¿cuántos kilómetros recorrió exactamente?",
            "options": [
                {
                    "id": "A",
                    "content": "$12\\text{ km}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$11\\text{ km}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$13,8\\text{ km}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$15,7\\text{ km}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Plantear la ecuación lineal de costo: Cargo Fijo + (Tarifa/km)*k = Costo Total.",
                "step_by_step": "1) $1200 + 650k = 9000$.\\n2) $650k = 9000 - 1200 = 7800$.\\n3) $k = 7800 / 650 = 12\\text{ km}$.",
                "key_concept": "Modelamiento de funciones afines y ecuaciones lineales en problemas de la vida diaria.",
                "frequent_mistake": "Dividir el monto total directamente por 650 sin descontar el cargo fijo inicial."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "75c0e735-b604-5f70-99b3-6b8e283929d3",
            "subtopic_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere la ecuación en $x$: $kx + 6 = 4x + 2k$, donde $k$ es una constante real. ¿Para cuál de los siguientes valores de $k$ la ecuación NO tiene una solución única?",
            "options": [
                {
                    "id": "A",
                    "content": "$k = 4$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$k = 0$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "$k = 3$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$k = -4$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Reagrupar en (k - 4)x = 2k - 6. Si el coeficiente de x se anula (k = 4), se obtiene 0 = 2 (inconsistencia, 0 soluciones).",
                "step_by_step": "1) $kx - 4x = 2k - 6 \\implies (k - 4)x = 2k - 6$.\\n2) Existe solución única si y solo si $k - 4 \\neq 0$.\\n3) Por tanto, NO tiene solución única si $k - 4 = 0 \\implies k = 4$.\\n4) Si $k = 4$, $0x = 2 \\implies$ ecuación sin solución (conjunto vacío).",
                "key_concept": "Condición de unicidad de soluciones en ecuaciones lineales Ax = B.",
                "frequent_mistake": "Confundir el valor que anula el coeficiente de x con el valor que anula el término libre independiente."
            },
            "difficulty_estimate": 0.7,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "fde8291d-9377-54fa-8f5f-d98cee8d9038",
            "subtopic_id": "a208a62b-10c0-5392-8a29-0549b2496e06",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "PARAMETRIC",
            "stem": "El perímetro de un terreno rectangular es de $46$ metros. Si la longitud del largo excede en $5$ metros a la longitud del ancho $x$, ¿cuál de las siguientes ecuaciones permite determinar correctamente el valor del ancho $x$?",
            "options": [
                {
                    "id": "A",
                    "content": "$2x + 2(x + 5) = 46$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$x + (x + 5) = 46$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$x(x + 5) = 46$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "D",
                    "content": "$2x + 2(x - 5) = 46$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Traducir las dimensiones a expresiones algebraicas y aplicar la fórmula del perímetro rectangular: 2*ancho + 2*largo = 46.",
                "step_by_step": "1) Ancho = $x$.\\n2) Largo = $x + 5$.\\n3) Perímetro = $2(ancho) + 2(largo) = 2x + 2(x + 5)$.\\n4) Igualar a 46: $2x + 2(x + 5) = 46$.",
                "key_concept": "Representación simbólica algebraica de relaciones geométricas de perímetro.",
                "frequent_mistake": "Confundir perímetro con semiperímetro (opción B) o con fórmula de área (opción C)."
            },
            "difficulty_estimate": 0.6,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "c7ac533f-2d74-54a9-a165-0347ba1e4bf6",
            "subtopic_id": "3619d611-2424-584d-a40f-4235202f246f",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es la solución $(x, y)$ del sistema de ecuaciones lineales formado por $2x + y = 11$ y $x - y = 1$?",
            "options": [
                {
                    "id": "A",
                    "content": "$(4, 3)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(3, 5)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$(5, 1)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$(4, -3)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Sumar ambas ecuaciones para eliminar la variable y: $3x = 12 \\implies x = 4$, luego $y = 3$.",
                "step_by_step": "1) Sumando miembro a miembro: $(2x + y) + (x - y) = 11 + 1 \\implies 3x = 12$.\\n2) Despejar $x$: $x = 12 / 3 = 4$.\\n3) Sustituir en la segunda ecuación: $4 - y = 1 \\implies y = 3$.\\n4) Par ordenado: $(4, 3)$.",
                "key_concept": "Método de reducción en sistemas de ecuaciones lineales de 2x2.",
                "frequent_mistake": "Cometer error de signo al sustituir $x=4$ en $x - y = 1$, concluyendo erróneamente $y = -3$."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "e93e59d2-f7a2-5d9a-b943-7ecc17c1d1da",
            "subtopic_id": "3619d611-2424-584d-a40f-4235202f246f",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "A un concierto asistieron $40$ personas en total entre adultos y niños. La entrada de adulto costó $\\$5.000$ y la de niño $\\$3.000$. Si la recaudación total fue de $\\$160.000$, ¿cuántos adultos asistieron?",
            "options": [
                {
                    "id": "A",
                    "content": "$20\\text{ adultos}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$15\\text{ adultos}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$25\\text{ adultos}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$32\\text{ adultos}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Modelar con el sistema $a + n = 40$ y $5000a + 3000n = 160000$, obteniendo $a = 20$.",
                "step_by_step": "1) Sean $a$ los adultos y $n$ los niños: $a + n = 40 \\implies n = 40 - a$.\\n2) Ecuación de dinero: $5000a + 3000(40 - a) = 160000$.\\n3) Simplificar dividiendo por 1000: $5a + 120 - 3a = 160 \\implies 2a = 40 \\implies a = 20$.",
                "key_concept": "Modelamiento algebraico de problemas de mezclas y compras con sistemas 2x2.",
                "frequent_mistake": "Dividir la recaudación total 160.000 entre 5.000 directamente, asumiendo erróneamente que todos eran adultos."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "9080e52e-84fe-5808-aa31-5c09ea1bb392",
            "subtopic_id": "3619d611-2424-584d-a40f-4235202f246f",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "¿En qué punto del plano cartesiano se intersecan las rectas asociadas a las ecuaciones $y = 2x - 1$ e $y = -x + 5$?",
            "options": [
                {
                    "id": "A",
                    "content": "$(2, 3)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(3, 2)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$(1, 1)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$(2, 5)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Igualar expresiones de y: $2x - 1 = -x + 5 \\implies 3x = 6 \\implies x = 2$, luego $y = 3$.",
                "step_by_step": "1) Igualación: $2x - 1 = -x + 5$.\\n2) Agrupar términos: $3x = 6 \\implies x = 2$.\\n3) Evaluar en cualquiera: $y = 2(2) - 1 = 3$.\\n4) Punto de corte geométrico: $(2, 3)$.",
                "key_concept": "Interpretación geométrica de la solución de un sistema lineal como punto de intersección.",
                "frequent_mistake": "Invertir las coordenadas en el par ordenado, marcando $(3, 2)$ en lugar de $(2, 3)$."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "929beec4-0038-5ab1-b37f-61946902f19c",
            "subtopic_id": "3619d611-2424-584d-a40f-4235202f246f",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere el sistema de ecuaciones: $2x + 4y = 8$ y $x + 2y = c$, donde $c$ es una constante real. ¿Cuál condición sobre $c$ garantiza que el sistema NO tenga soluciones?",
            "options": [
                {
                    "id": "A",
                    "content": "$c \\neq 4$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$c = 4$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "$c = 0$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$c = 8$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Las rectas tienen la misma pendiente (son paralelas). Para que no haya solución, deben ser disjuntas ($c \\neq 4$).",
                "step_by_step": "1) Dividir la primera ecuación por 2: $x + 2y = 4$.\\n2) Comparar con la segunda ecuación: $x + 2y = c$.\\n3) Si $c = 4$, las rectas son coincidentes (infinitas soluciones).\\n4) Si $c \\neq 4$, las rectas son paralelas distintas y no se tocan jamás (0 soluciones).",
                "key_concept": "Criterio de incompatibilidad geométrica y analítica en sistemas lineales 2x2.",
                "frequent_mistake": "Confundir la condición de infinitas soluciones ($c = 4$) con la condición de no existencia de soluciones ($c \\neq 4$)."
            },
            "difficulty_estimate": 0.6,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "f5bc1e26-70fe-5ad7-8b30-c0051b180c7e",
            "subtopic_id": "3619d611-2424-584d-a40f-4235202f246f",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "¿Para qué valor de la constante $a$ el sistema de ecuaciones $ax + 6y = 12$ y $2x + 3y = 6$ tiene infinitas soluciones?",
            "options": [
                {
                    "id": "A",
                    "content": "$a = 4$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$a = 2$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$a = 1$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$a = 6$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Para rectas coincidentes, los coeficientes deben ser proporcionales: $a/2 = 6/3 = 12/6 = 2 \\implies a = 4$.",
                "step_by_step": "1) Razón entre coeficientes conocidos: $6/3 = 2$ y $12/6 = 2$.\\n2) La razón de la variable $x$ debe ser idéntica: $a/2 = 2$.\\n3) Despejar: $a = 4$.",
                "key_concept": "Proporcionalidad de coeficientes en sistemas compatibles indeterminados.",
                "frequent_mistake": "Igualar $a$ directamente al coeficiente de la segunda ecuación ($a = 2$) sin considerar la constante de amplificación."
            },
            "difficulty_estimate": 0.65,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": True,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "c19e66a2-f85b-5986-852e-226943215eae",
            "subtopic_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Una recta pasa por los puntos $A(1, 3)$ y $B(3, 7)$ en el plano cartesiano. ¿Cuál es la ecuación de la función afín $f(x)$ que representa a dicha recta?",
            "options": [
                {
                    "id": "A",
                    "content": "$f(x) = 2x + 1$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$f(x) = 2x - 1$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$f(x) = 4x - 1$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$f(x) = \\frac{1}{2}x + \\frac{5}{2}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Calcular pendiente $m = (7-3)/(3-1) = 2$ y coeficiente de posición $n = 3 - 2(1) = 1$.",
                "step_by_step": "1) Pendiente: $m = (y_2 - y_1)/(x_2 - x_1) = (7 - 3)/(3 - 1) = 4/2 = 2$.\\n2) Sustituir punto $(1, 3)$: $3 = 2(1) + n \\implies n = 3 - 2 = 1$.\\n3) Función afín: $f(x) = 2x + 1$.",
                "key_concept": "Determinación analítica de la ecuación de la recta conociendo dos puntos.",
                "frequent_mistake": "Invertir el cálculo de la pendiente como $\\Delta x / \\Delta y$ obteniendo $m = 1/2$."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "63bad002-2943-5187-9fac-129b50660122",
            "subtopic_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un plan de telefonía móvil tiene un cargo fijo mensual de $\\$8.000$ e incluye una tarifa de $\\$1.500$ por cada gigabyte (GB) de datos adicional consumido. Si $g$ representa los GB adicionales consumidos en el mes, ¿cuál función modela el costo total mensual $C(g)$?",
            "options": [
                {
                    "id": "A",
                    "content": "$C(g) = 1.500g + 8.000$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$C(g) = 8.000g + 1.500$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$C(g) = 9.500g$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$C(g) = 1.500g - 8.000$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Estructura de función afín: Cargo fijo como intercepto $n = 8000$ y tarifa unitaria como pendiente $m = 1500$.",
                "step_by_step": "1) Pendiente (tasa de cambio): $m = 1500$ por unidad de $g$.\\n2) Coeficiente de posición (costo base fijo): $n = 8000$.\\n3) Modelo afín: $C(g) = 1500g + 8000$.",
                "key_concept": "Modelamiento lineal afín de costos fijos y variables.",
                "frequent_mistake": "Invertir las constantes asignando el cargo fijo a la variable independiente (opción B)."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "25bccaa6-a1d6-5092-9fbc-dde4ac54bd22",
            "subtopic_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere la función afín $f(x) = -2x + 6$. ¿Cuáles son los puntos de corte de su gráfica con los ejes coordenados $Y$ y $X$, respectivamente?",
            "options": [
                {
                    "id": "A",
                    "content": "$(0, 6)$ y $(3, 0)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(0, 6)$ y $(-3, 0)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$(6, 0)$ y $(0, 3)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "D",
                    "content": "$(0, -2)$ y $(6, 0)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Corte con eje Y: evaluar en $x=0 \\implies (0, 6)$. Corte con eje X: resolver $-2x + 6 = 0 \\implies (3, 0)$.",
                "step_by_step": "1) Intersección con eje Y: $x = 0 \\implies f(0) = -2(0) + 6 = 6 \\implies (0, 6)$.\\n2) Intersección con eje X: $f(x) = 0 \\implies -2x + 6 = 0 \\implies 2x = 6 \\implies x = 3 \\implies (3, 0)$.",
                "key_concept": "Ceros de la función y coeficiente de posición en el plano cartesiano.",
                "frequent_mistake": "Cometer error de signo al despejar $-2x + 6 = 0$ obteniendo erróneamente $x = -3$."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "11a7438c-6a80-50a7-a725-051111e9ec97",
            "subtopic_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Si en la función afín $f(x) = mx + n$ (con $m > 0$) se aumenta el valor del coeficiente de posición $n$ en $3$ unidades manteniendo $m$ constante, ¿qué transformación geométrica experimenta la gráfica de la recta en el plano cartesiano?",
            "options": [
                {
                    "id": "A",
                    "content": "Se traslada verticalmente $3$ unidades hacia arriba",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Aumenta su inclinación (se hace más empinada)",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "Se traslada horizontalmente $3$ unidades hacia la derecha",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "D",
                    "content": "Rota en sentido horario respecto al origen",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Modificar el término independiente $n$ produce una traslación vertical rígida de la gráfica.",
                "step_by_step": "1) La pendiente $m$ controla exclusivamente la inclinación o ángulo de la recta.\\n2) El parámetro $n$ es el intercepto $(0, n)$.\\n3) Cambiar $n$ a $n + 3$ traslada cada punto $(x, y)$ a $(x, y + 3)$, es decir, 3 unidades hacia arriba.",
                "key_concept": "Efecto geométrico de la variación de parámetros en funciones afines.",
                "frequent_mistake": "Creer que aumentar $n$ modifica la pendiente haciendo la recta más inclinada."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "0440dbbd-e535-5a00-8f97-7c21c80ecee4",
            "subtopic_id": "c29b1808-52c5-59db-bc68-018e9185dc15",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Dada la función afín $f(x) = 5x - 8$, ¿cuál es la preimagen de $17$?",
            "options": [
                {
                    "id": "A",
                    "content": "$5$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$77$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$1,8$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$-5$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "La preimagen es el valor de x tal que $f(x) = 17$: $5x - 8 = 17 \\implies x = 5$.",
                "step_by_step": "1) Plantear: $f(x) = 17 \\implies 5x - 8 = 17$.\\n2) Sumar 8: $5x = 25$.\\n3) Dividir por 5: $x = 25 / 5 = 5$.",
                "key_concept": "Diferenciación conceptual entre imagen $f(a)$ y preimagen $f^{-1}(b)$.",
                "frequent_mistake": "Calcular la imagen de 17 en vez de la preimagen: $f(17) = 5(17) - 8 = 85 - 8 = 77$ (opción B)."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "6ee641af-bafd-5069-b26a-0e0b89507d67",
            "subtopic_id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuáles son las coordenadas del vértice de la parábola asociada a la función cuadrática $f(x) = x^2 - 6x + 5$?",
            "options": [
                {
                    "id": "A",
                    "content": "$(3, -4)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(-3, 32)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$(3, 4)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$(6, 5)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Coordenada $x_v = -b/(2a) = 3$, y evaluar: $f(3) = 9 - 18 + 5 = -4$.",
                "step_by_step": "1) Parámetros: $a = 1, b = -6, c = 5$.\\n2) $x_v = -(-6) / (2 * 1) = 6 / 2 = 3$.\\n3) $y_v = (3)^2 - 6(3) + 5 = 9 - 18 + 5 = -4$.\\n4) Vértice: $(3, -4)$.",
                "key_concept": "Cálculo analítico del vértice de una parábola.",
                "frequent_mistake": "Olvidar el signo negativo en la fórmula del vértice usando $b/(2a) = -3$ (opción B)."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "a6bd0f5e-3d18-5794-91fc-ede8a98081db",
            "subtopic_id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "La altura $h$ en metros que alcanza un objeto lanzado verticalmente hacia arriba en función del tiempo $t$ en segundos está dada por $h(t) = -5t^2 + 20t$. ¿Cuál es la altura máxima que alcanza el objeto?",
            "options": [
                {
                    "id": "A",
                    "content": "$20\\text{ metros}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$2\\text{ metros}$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                },
                {
                    "id": "C",
                    "content": "$25\\text{ metros}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$40\\text{ metros}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "El instante de altura máxima es en el vértice $t = 2\\text{ s}$, alcanzando $h(2) = 20\\text{ m}$.",
                "step_by_step": "1) Tiempo del vértice: $t = -20 / (2 * (-5)) = -20 / (-10) = 2\\text{ segundos}$.\\n2) Evaluar altura: $h(2) = -5(2)^2 + 20(2) = -5(4) + 40 = -20 + 40 = 20\\text{ metros}$.",
                "key_concept": "Optimización cuadrática y valor extremo del vértice en problemas físicos.",
                "frequent_mistake": "Confundir el tiempo en que se alcanza la altura máxima ($2\\text{ s}$) con la altura máxima misma (opción B)."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "fa90a2f7-09a6-50aa-927d-eab7cc48f2f6",
            "subtopic_id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuáles son los puntos de corte con el eje $X$ de la parábola cuya función es $f(x) = x^2 - 5x + 6$?",
            "options": [
                {
                    "id": "A",
                    "content": "$(2, 0)$ y $(3, 0)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(-2, 0)$ y $(-3, 0)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$(0, 2)$ y $(0, 3)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "D",
                    "content": "$(1, 0)$ y $(6, 0)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Factorizar $x^2 - 5x + 6 = (x - 2)(x - 3) = 0 \\implies x_1 = 2, x_2 = 3$.",
                "step_by_step": "1) Resolver $f(x) = 0 \\implies x^2 - 5x + 6 = 0$.\\n2) Factorización en binomios: $(x - 2)(x - 3) = 0$.\\n3) Soluciones: $x = 2$ o $x = 3$.\\n4) Puntos coordenados en el eje X: $(2, 0)$ y $(3, 0)$.",
                "key_concept": "Ceros o raíces de una función cuadrática y su representación gráfica.",
                "frequent_mistake": "Invertir los signos de las raíces tras factorizar, marcando $(-2, 0)$ y $(-3, 0)$."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "8b799692-e7b6-59c6-81e4-034153ac37bc",
            "subtopic_id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere la función cuadrática $f(x) = 2x^2 - 4x + 5$. Un estudiante afirma que la parábola asociada corta al eje $X$ en dos puntos distintos. ¿Es correcta la afirmación del estudiante?",
            "options": [
                {
                    "id": "A",
                    "content": "No, porque el discriminante es $\\Delta = -24 < 0$, por lo que la parábola no corta al eje $X$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Sí, porque el coeficiente de $x^2$ es positivo ($a = 2 > 0$)",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "No, porque la parábola corta al eje $X$ en un único punto",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "Sí, porque el discriminante es $\\Delta = 56 > 0$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Calcular discriminante: $\\Delta = b^2 - 4ac = 16 - 40 = -24$. Al ser negativo, no existen raíces reales.",
                "step_by_step": "1) Coeficientes: $a = 2, b = -4, c = 5$.\\n2) Discriminante: $\\Delta = (-4)^2 - 4(2)(5) = 16 - 40 = -24$.\\n3) Como $\\Delta < 0$, la ecuación $f(x) = 0$ no tiene soluciones reales.\\n4) Geométricamente, la parábola está completamente sobre el eje X y no lo interseca.",
                "key_concept": "El discriminante como indicador geométrico de intersección con el eje de las abscisas.",
                "frequent_mistake": "Confundir la concavidad positiva ($a > 0$) con la existencia de cortes con el eje horizontal."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "0aeb7e70-e08c-5b3e-8d6f-aab93706e7db",
            "subtopic_id": "f0471ef2-68b3-520f-9c89-98894f842122",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es la ecuación del eje de simetría de la parábola asociada a la función cuadrática $f(x) = -2x^2 + 8x - 3$?",
            "options": [
                {
                    "id": "A",
                    "content": "$x = 2$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$x = -2$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$x = 4$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$y = 5$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Eje de simetría vertical: $x = -b / (2a) = -8 / (2 * (-2)) = 2$.",
                "step_by_step": "1) Coeficientes: $a = -2, b = 8$.\\n2) Ecuación del eje de simetría: $x = -b / (2a)$.\\n3) Sustituir: $x = -8 / (2 * (-2)) = -8 / (-4) = 2$.\\n4) Recta vertical: $x = 2$.",
                "key_concept": "Eje de simetría de una parábola como recta vertical que pasa por el vértice.",
                "frequent_mistake": "Cometer error en la división de signos negativos, concluyendo $x = -2$."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": True,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "86422b43-04a0-5f36-8ec1-be58d63b9e5d",
            "subtopic_id": "29d5f909-b289-593d-8a0f-758a0e213cec",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Una figura compuesta está formada por un rectángulo de base $6\\text{ cm}$ y altura $4\\text{ cm}$, al cual se le adosa en uno de sus lados menores un triángulo de base $4\\text{ cm}$ y altura $3\\text{ cm}$. ¿Cuál es el área total de la figura compuesta?",
            "options": [
                {
                    "id": "A",
                    "content": "$30\\text{ cm}^2$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$36\\text{ cm}^2$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$27\\text{ cm}^2$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$24\\text{ cm}^2$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                }
            ],
            "explanation": {
                "short_summary": "Área total = Área rectángulo ($6*4=24$) + Área triángulo ($(4*3)/2 = 6$) = 30 cm².",
                "step_by_step": "1) Área del rectángulo: $A_1 = 6 * 4 = 24\\text{ cm}^2$.\\n2) Área del triángulo: $A_2 = (4 * 3) / 2 = 12 / 2 = 6\\text{ cm}^2$.\\n3) Área total: $A = 24 + 6 = 30\\text{ cm}^2$.",
                "key_concept": "Descomposición y adición de áreas poligonales elementales.",
                "frequent_mistake": "Olvidar dividir por 2 el área del triángulo, sumando $24 + 12 = 36\\text{ cm}^2$ (opción B)."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "585a2343-9d5d-52e6-949e-3499e36de1a0",
            "subtopic_id": "29d5f909-b289-593d-8a0f-758a0e213cec",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Se desea embaldosar un piso rectangular de $4\\text{ metros}$ de largo por $3\\text{ metros}$ de ancho utilizando cerámicas cuadradas de $20\\text{ cm}$ de lado. ¿Cuántas cerámicas se necesitan en total?",
            "options": [
                {
                    "id": "A",
                    "content": "$300\\text{ cerámicas}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$60\\text{ cerámicas}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$150\\text{ cerámicas}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$3.000\\text{ cerámicas}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Convertir unidades a metros: baldosa $0,2\\text{ m} * 0,2\\text{ m} = 0,04\\text{ m}^2$. Total = $12 / 0,04 = 300$.",
                "step_by_step": "1) Área del piso: $4\\text{ m} * 3\\text{ m} = 12\\text{ m}^2$.\\n2) Área de una baldosa: $20\\text{ cm} = 0,2\\text{ m} \\implies 0,2 * 0,2 = 0,04\\text{ m}^2$.\\n3) Cantidad de baldosas: $12 / 0,04 = 1200 / 4 = 300$.",
                "key_concept": "Conversión dimensional de unidades métricas y cálculo de cobertura.",
                "frequent_mistake": "Dividir el área de 12 m² entre 0.2 m (longitud de lado) en vez del área de la baldosa (0.04 m²)."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "519df742-b796-503c-8663-bd3ce32cde73",
            "subtopic_id": "29d5f909-b289-593d-8a0f-758a0e213cec",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un cuadrado de lado $8\\text{ cm}$ tiene inscrito un círculo de radio $4\\text{ cm}$. ¿Cuál es la expresión exacta para el área de la región comprendida entre el cuadrado y el círculo (área sombreada)?",
            "options": [
                {
                    "id": "A",
                    "content": "$64 - 16\\pi\\text{ cm}^2$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$64 - 8\\pi\\text{ cm}^2$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$32 - 16\\pi\\text{ cm}^2$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$16\\pi - 64\\text{ cm}^2$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Área sombreada = Área cuadrado ($8^2 = 64$) - Área círculo ($\\pi * 4^2 = 16\\pi$).",
                "step_by_step": "1) Área del cuadrado: $A_{\\text{cuadrado}} = 8^2 = 64\\text{ cm}^2$.\\n2) Área del círculo inscrito: radio $r = 4\\text{ cm} \\implies A_{\\text{círculo}} = \\pi * 4^2 = 16\\pi\\text{ cm}^2$.\\n3) Diferencia de áreas: $64 - 16\\pi\\text{ cm}^2$.",
                "key_concept": "Cálculo de áreas sombreadas por sustracción de figuras geométricas inscritas.",
                "frequent_mistake": "Usar la fórmula del perímetro del círculo $2\\pi r = 8\\pi$ en lugar del área $\\pi r^2$ (opción B)."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "502dd65d-7f75-599d-800c-c1300a195d8f",
            "subtopic_id": "29d5f909-b289-593d-8a0f-758a0e213cec",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Si la longitud del lado de un cuadrado se triplica, ¿qué ocurre con su área?",
            "options": [
                {
                    "id": "A",
                    "content": "Se multiplica por $9$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Se triplica (se multiplica por $3$)",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "Se multiplica por $6$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "Aumenta en $9\\text{ unidades}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "El área es cuadrática respecto al lado: $A' = (3L)^2 = 9L^2 = 9A$.",
                "step_by_step": "1) Sea $L$ el lado inicial, $A = L^2$.\\n2) Nuevo lado: $L' = 3L$.\\n3) Nueva área: $A' = (3L)^2 = 9L^2 = 9A$.\\n4) El área se multiplica por el factor de escala al cuadrado ($3^2 = 9$).",
                "key_concept": "Escalamiento dimensional no lineal de magnitudes bidimensionales.",
                "frequent_mistake": "Asumir relación lineal y creer que el área se triplica al triplicarse el lado (opción B)."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "2757a53c-7b6f-5738-9cb8-6708605c9afe",
            "subtopic_id": "29d5f909-b289-593d-8a0f-758a0e213cec",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Un trapecio isósceles tiene base mayor de $16\\text{ cm}$, base menor de $6\\text{ cm}$ y una altura de $12\\text{ cm}$. ¿Cuál es el perímetro del trapecio?",
            "options": [
                {
                    "id": "A",
                    "content": "$48\\text{ cm}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$35\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$44\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$50\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Proyección lateral $x = (16-6)/2 = 5$. Lado oblicuo $= \\sqrt{5^2 + 12^2} = 13$. Perímetro $= 16 + 6 + 13 + 13 = 48$.",
                "step_by_step": "1) Semidiferencia de las bases: $(16 - 6) / 2 = 10 / 2 = 5\\text{ cm}$.\\n2) Teorema de Pitágoras en triángulo lateral: $L^2 = 5^2 + 12^2 = 25 + 144 = 169 \\implies L = 13\\text{ cm}$.\\n3) Perímetro = Base Mayor + Base Menor + 2*(Lado oblicuo): $P = 16 + 6 + 2(13) = 22 + 26 = 48\\text{ cm}$.",
                "key_concept": "Propiedades métricas del trapecio isósceles y aplicación de triángulos rectángulos auxiliares.",
                "frequent_mistake": "Restar directamente $16 - 6 = 10$ sin dividir por 2 para el cateto adyacente."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "44400c91-ef1f-59a7-a3b4-180c159017c4",
            "subtopic_id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "En un triángulo rectángulo, los catetos miden $15\\text{ cm}$ y $20\\text{ cm}$. ¿Cuánto mide su hipotenusa?",
            "options": [
                {
                    "id": "A",
                    "content": "$25\\text{ cm}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$35\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$22\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$24\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Terna pitagórica $3-4-5$ multiplicada por 5: $\\sqrt{15^2 + 20^2} = \\sqrt{225 + 400} = 25\\text{ cm}$.",
                "step_by_step": "1) Teorema de Pitágoras: $h^2 = 15^2 + 20^2$.\\n2) $h^2 = 225 + 400 = 625$.\\n3) $h = \\sqrt{625} = 25\\text{ cm}$.",
                "key_concept": "Cálculo de la hipotenusa mediante el Teorema de Pitágoras.",
                "frequent_mistake": "Sumar linealmente los catetos: $15 + 20 = 35\\text{ cm}$ (opción B)."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "12128bd8-6952-52f1-945b-aa73c8e21477",
            "subtopic_id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Una escalera de $10\\text{ metros}$ de longitud está apoyada contra una pared vertical. Si la base de la escalera se encuentra a $6\\text{ metros}$ de distancia de la pared sobre el suelo horizontal, ¿a qué altura de la pared llega el extremo superior de la escalera?",
            "options": [
                {
                    "id": "A",
                    "content": "$8\\text{ metros}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$4\\text{ metros}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$11,6\\text{ metros}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$7\\text{ metros}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Despejar cateto: $\\sqrt{10^2 - 6^2} = \\sqrt{100 - 36} = \\sqrt{64} = 8\\text{ m}$.",
                "step_by_step": "1) La escalera actúa como hipotenusa ($h = 10\\text{ m}$) y la distancia al suelo como cateto ($d = 6\\text{ m}$).\\n2) Altura en la pared: $a^2 = 10^2 - 6^2 = 100 - 36 = 64$.\\n3) $a = \\sqrt{64} = 8\\text{ metros}$.",
                "key_concept": "Modelamiento de situaciones reales con triángulos rectángulos y cálculo de catetos.",
                "frequent_mistake": "Sumar los cuadrados en lugar de restarlos: $\\sqrt{100 + 36} = \\sqrt{136} \\approx 11,6$ (opción C)."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "91cd75d4-d40d-551b-a031-f90e431f6ef9",
            "subtopic_id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuál es la longitud de la diagonal de un rectángulo cuyos lados miden $8\\text{ cm}$ y $6\\text{ cm}$?",
            "options": [
                {
                    "id": "A",
                    "content": "$10\\text{ cm}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$14\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$7\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$\\sqrt{28}\\text{ cm}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "La diagonal divide al rectángulo en dos triángulos rectángulos: $d = \\sqrt{8^2 + 6^2} = \\sqrt{100} = 10\\text{ cm}$.",
                "step_by_step": "1) Aplicar Pitágoras: $d^2 = 8^2 + 6^2 = 64 + 36 = 100$.\\n2) $d = \\sqrt{100} = 10\\text{ cm}$.",
                "key_concept": "Cálculo de la diagonal de paralelogramos rectángulos.",
                "frequent_mistake": "Sumar directamente las longitudes de los lados: $8 + 6 = 14\\text{ cm}$."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "3c3dad3a-4f56-52f2-be15-f3245f471acc",
            "subtopic_id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un carpintero mide los tres lados de una pieza triangular de madera y obtiene $9\\text{ cm}$, $12\\text{ cm}$ y $15\\text{ cm}$. Para verificar si la pieza tiene un ángulo recto, aplica el recíproco del Teorema de Pitágoras. ¿Cuál de las siguientes conclusiones es formalmente correcta?",
            "options": [
                {
                    "id": "A",
                    "content": "Es un triángulo rectángulo, porque $9^2 + 12^2 = 81 + 144 = 225 = 15^2$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "No es rectángulo, porque la suma de sus catetos $9 + 12 = 21 \\neq 15$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "Es obtusángulo, porque $15^2 > 9^2 + 12^2$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "No es posible saberlo sin conocer los ángulos interiores",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Por el recíproco de Pitágoras, si $a^2 + b^2 = c^2$, el triángulo es obligatoriamente rectángulo.",
                "step_by_step": "1) Cuadrado del lado mayor: $15^2 = 225$.\\n2) Suma de cuadrados de lados menores: $9^2 + 12^2 = 81 + 144 = 225$.\\n3) Como $225 = 225$, el ángulo opuesto a $15\\text{ cm}$ es un ángulo recto ($90^\\circ$).",
                "key_concept": "Recíproco del Teorema de Pitágoras como criterio de perpendicularidad.",
                "frequent_mistake": "Intentar aplicar la desigualdad triangular lineal en vez de la suma de cuadrados."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "a5bff14e-c821-5b36-b9a5-d7f47199fab2",
            "subtopic_id": "22089b2e-ffad-5a77-b7fd-7ff1d37e2858",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "En el plano cartesiano, ¿cuál es la distancia entre los puntos $A(1, 2)$ y $B(4, 6)$?",
            "options": [
                {
                    "id": "A",
                    "content": "$5$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$7$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$\\sqrt{7}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$25$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Distancia euclidiana: $d = \\sqrt{(4-1)^2 + (6-2)^2} = \\sqrt{3^2 + 4^2} = 5$.",
                "step_by_step": "1) Diferencias de coordenadas: $\\Delta x = 4 - 1 = 3$, $\\Delta y = 6 - 2 = 4$.\\n2) Teorema de Pitágoras en el plano: $d = \\sqrt{3^2 + 4^2} = \\sqrt{9 + 16} = \\sqrt{25} = 5$.",
                "key_concept": "Distancia entre dos puntos en el plano cartesiano deducida por Pitágoras.",
                "frequent_mistake": "Olvidar extraer la raíz cuadrada final, marcando $25$ en lugar de $5$."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": True,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "292c7b87-5908-5442-9d1d-c2214fba4987",
            "subtopic_id": "0ed0ae36-4f7c-5880-b5f5-3889c6199615",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Al punto $P(3, -2)$ del plano cartesiano se le aplica una traslación según el vector $\\vec{v} = (-4, 5)$. ¿Cuáles son las coordenadas del punto transformado $P'$?",
            "options": [
                {
                    "id": "A",
                    "content": "$(-1, 3)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(7, -7)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$(-1, -7)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$(3, -1)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Sumar componentes homólogas: $(3 + (-4), -2 + 5) = (-1, 3)$.",
                "step_by_step": "1) $x' = x + v_x = 3 + (-4) = -1$.\\n2) $y' = y + v_y = -2 + 5 = 3$.\\n3) Punto transformado: $P'(-1, 3)$.",
                "key_concept": "Traslación de puntos en el plano mediante adición vectorial.",
                "frequent_mistake": "Restar las componentes del vector en vez de sumarlas, obteniendo $(7, -7)$."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "eaabe0d0-ab59-5c4f-9f4f-b2e67a7de591",
            "subtopic_id": "0ed0ae36-4f7c-5880-b5f5-3889c6199615",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Si el punto $A(-3, 4)$ se refleja con respecto al eje de las abscisas (eje $X$), ¿cuáles son las coordenadas del punto imagen $A'$?",
            "options": [
                {
                    "id": "A",
                    "content": "$(-3, -4)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(3, 4)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$(3, -4)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$(4, -3)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Reflexión axial respecto al eje X: $(x, y) \\to (x, -y) \\implies (-3, 4) \\to (-3, -4)$.",
                "step_by_step": "1) Regla de reflexión respecto al eje X: la abscisa se mantiene constante y la ordenada cambia de signo.\\n2) $x' = -3$, $y' = -4$.\\n3) Imagen: $A'(-3, -4)$.",
                "key_concept": "Reflexiones axiales en el plano cartesiano respecto a los ejes coordenados.",
                "frequent_mistake": "Cambiar el signo de la coordenada x (reflejando respecto al eje Y, opción B)."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "7210a652-7017-5c62-87f7-8f7cc4a22afc",
            "subtopic_id": "0ed0ae36-4f7c-5880-b5f5-3889c6199615",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "¿Cuáles son las coordenadas del punto resultante de rotar el punto $P(2, 5)$ en $90^\\circ$ en sentido antihorario respecto al origen de coordenadas?",
            "options": [
                {
                    "id": "A",
                    "content": "$(-5, 2)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(5, -2)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$(-2, -5)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$(2, -5)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Rotación de 90° antihorario con centro en el origen: $(x, y) \\to (-y, x) \\implies (-5, 2)$.",
                "step_by_step": "1) Regla canónica para rotación antihoraria de $90^\\circ$: $(x, y) \\to (-y, x)$.\\n2) Aplicando a $P(2, 5)$: $x' = -5$, $y' = 2$.\\n3) Punto rotado: $(-5, 2)$.",
                "key_concept": "Rotaciones cartesianas de ángulos múltiplos de 90 grados respecto al origen.",
                "frequent_mistake": "Confundir sentido antihorario con sentido horario $(y, -x) = (5, -2)$ (opción B)."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "aea11c6f-0ec4-5b93-b200-ffa7fd8641ad",
            "subtopic_id": "0ed0ae36-4f7c-5880-b5f5-3889c6199615",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un estudiante afirma: «Si a un triángulo se le aplica una rotación de $180^\\circ$ y luego una traslación, el área del triángulo resultante puede ser mayor que el área del triángulo original». ¿Es verdadera la afirmación del estudiante?",
            "options": [
                {
                    "id": "A",
                    "content": "No, es falsa, porque tanto la rotación como la traslación son transformaciones isométricas que conservan rigurosamente las distancias y el área (congruencia)",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Sí, es verdadera, porque la traslación amplía las longitudes de los lados",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "Sí, es verdadera, siempre que el vector de traslación sea positivo",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "No, es falsa, únicamente si la rotación se hace respecto al baricentro",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Toda isometría preserva la forma y las dimensiones métricas euclidianas.",
                "step_by_step": "1) Una transformación isométrica por definición no altera distancias ni ángulos interiores.\\n2) La figura resultante es congruente con la original ($T \\cong T'$).\\n3) Por tanto, el área se mantiene estrictamente invariante.",
                "key_concept": "Invarianza métrica y congruencia en transformaciones isométricas.",
                "frequent_mistake": "Confundir transformaciones isométricas (rigidas) con homotecias o dilataciones que sí alteran el área."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "a4177707-f8a9-5e73-84c5-d8cd73ed8ee1",
            "subtopic_id": "0ed0ae36-4f7c-5880-b5f5-3889c6199615",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "El punto $A(1, 3)$ se traslada primero mediante el vector $\\vec{u} = (2, -1)$ y, a continuación, al punto resultante se le aplica una reflexión respecto al origen de coordenadas $(0, 0)$. ¿Cuáles son las coordenadas finales del punto?",
            "options": [
                {
                    "id": "A",
                    "content": "$(-3, -2)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$(3, 2)$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                },
                {
                    "id": "C",
                    "content": "$(-3, 2)$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$(2, 3)$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Traslación a $(3, 2)$, luego reflexión respecto al origen: $(x, y) \\to (-x, -y) \\implies (-3, -2)$.",
                "step_by_step": "1) Traslación: $A' = (1 + 2, 3 - 1) = (3, 2)$.\\n2) Reflexión respecto al origen: $(x, y) \\to (-x, -y)$.\\n3) Punto final: $A'' = (-3, -2)$.",
                "key_concept": "Composición sucesiva de transformaciones isométricas en el plano.",
                "frequent_mistake": "Olvidar aplicar la segunda transformación (reflexión), quedándose en el punto intermedio $(3, 2)$."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "51c54d9a-f18f-545e-b2e0-675ee1b90966",
            "subtopic_id": "882718aa-40f4-5098-9f8c-fc56e71c136f",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Un estudiante obtuvo las siguientes calificaciones en cinco evaluaciones: $5,0$; $6,0$; $7,0$; $4,0$ y $6,0$. ¿Cuál es el promedio (media aritmética) de sus notas?",
            "options": [
                {
                    "id": "A",
                    "content": "$5,6$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$6,0$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$5,4$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$5,8$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Suma de notas dividida por 5: $(5,0 + 6,0 + 7,0 + 4,0 + 6,0) / 5 = 28,0 / 5 = 5,6$.",
                "step_by_step": "1) Suma: $5,0 + 6,0 + 7,0 + 4,0 + 6,0 = 28,0$.\\n2) División: $28,0 / 5 = 5,6$.",
                "key_concept": "Cálculo directo de la media aritmética en conjuntos de datos no agrupados.",
                "frequent_mistake": "Confundir la media con la moda o la mediana del conjunto, las cuales son 6,0."
            },
            "difficulty_estimate": 0.3,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "bd3ccba3-60b4-5e85-8507-aafc632a88e0",
            "subtopic_id": "882718aa-40f4-5098-9f8c-fc56e71c136f",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Considere el siguiente conjunto ordenado de datos: $\\{4, 6, 7, 9, 11, 13\\}$. ¿Cuál es el valor de la mediana?",
            "options": [
                {
                    "id": "A",
                    "content": "$8$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$7$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$9$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$8,3$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Al ser cantidad par (6 datos), la mediana es el promedio de los dos datos centrales: $(7 + 9)/2 = 8$.",
                "step_by_step": "1) Número de datos: $n = 6$ (par).\\n2) Datos centrales en posiciones 3 y 4: $7$ y $9$.\\n3) Mediana: $(7 + 9) / 2 = 16 / 2 = 8$.",
                "key_concept": "Mediana en distribuciones con número par de observaciones.",
                "frequent_mistake": "Elegir arbitrariamente uno de los dos valores centrales ($7$ o $9$) en lugar de su promedio."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "43a279be-98b3-5134-b0d8-4361e1f9941d",
            "subtopic_id": "882718aa-40f4-5098-9f8c-fc56e71c136f",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "En un diagrama de cajón (box-plot) que resume los puntajes de un grupo de estudiantes, el primer cuartil es $Q_1 = 20$ y el tercer cuartil es $Q_3 = 35$. ¿Cuál es el rango intercuartílico (RIC) de los puntajes?",
            "options": [
                {
                    "id": "A",
                    "content": "$15$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$55$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$27,5$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$10$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "El rango intercuartílico es la diferencia entre el tercer y el primer cuartil: $Q_3 - Q_1 = 35 - 20 = 15$.",
                "step_by_step": "1) Definición: $\\text{RIC} = Q_3 - Q_1$.\\n2) Sustitución: $\\text{RIC} = 35 - 20 = 15$.",
                "key_concept": "Medidas de dispersión basadas en posición y lectura de diagramas de cajón.",
                "frequent_mistake": "Calcular la media de los cuartiles $(20 + 35)/2 = 27,5$ o sumar ambos valores (55)."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "7d159c75-4678-57d7-be6f-df5399c6139e",
            "subtopic_id": "882718aa-40f4-5098-9f8c-fc56e71c136f",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Considere el conjunto de datos $\\{10, 12, 14, 15, 100\\}$. Si el valor atípico $100$ se reemplaza por $20$, ¿cuál de las siguientes afirmaciones describe con precisión el comportamiento de la media y la mediana?",
            "options": [
                {
                    "id": "A",
                    "content": "La media disminuye sustancialmente (pasa de $30,2$ a $14,2$), mientras que la mediana permanece inalterada en $14$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Tanto la media como la mediana disminuyen en la misma proporción",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "La mediana disminuye, pero la media se mantiene constante",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "D",
                    "content": "Ninguna de las dos medidas cambia porque el orden de los datos no varió",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "La media es sensible a valores extremos atípicos (outliers), mientras que la mediana es una medida robusta.",
                "step_by_step": "1) Conjunto original: Media $= (10+12+14+15+100)/5 = 151/5 = 30,2$. Mediana $= 14$.\\n2) Nuevo conjunto $\\{10, 12, 14, 15, 20\\}$: Media $= (10+12+14+15+20)/5 = 71/5 = 14,2$. Mediana $= 14$.\\n3) La mediana no varió, pero la media se redujo en 16 unidades.",
                "key_concept": "Robustez estadística de la mediana versus sensibilidad de la media.",
                "frequent_mistake": "Creer que la mediana siempre cambia cuando cualquier dato individual del conjunto se modifica."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "fd790ec9-50a3-572d-b82a-2efc132dd666",
            "subtopic_id": "882718aa-40f4-5098-9f8c-fc56e71c136f",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un alumno tiene notas $5,0$; $6,0$ y $6,4$ en tres pruebas de igual ponderación. ¿Qué nota $x$ debe obtener en la cuarta prueba para que su promedio final sea exactamente $6,0$?",
            "options": [
                {
                    "id": "A",
                    "content": "$6,6$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$6,0$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$6,8$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$7,0$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Suma total requerida = $4 * 6,0 = 24,0$. Restar notas obtenidas: $24,0 - (5,0 + 6,0 + 6,4) = 6,6$.",
                "step_by_step": "1) Promedio deseado: $(5,0 + 6,0 + 6,4 + x) / 4 = 6,0$.\\n2) Multiplicar por 4: $17,4 + x = 24,0$.\\n3) Despejar: $x = 24,0 - 17,4 = 6,6$.",
                "key_concept": "Modelamiento algebraico de la media aritmética ponderada.",
                "frequent_mistake": "Calcular la media de las tres notas actuales $(5,8)$ y promediar con 6,0, asumiendo ponderaciones desiguales."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "5a58d6c1-477d-5358-94b8-bbfd8262c56f",
            "subtopic_id": "0a90ccdf-9fc5-5fac-8972-9616c11a7473",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "En una encuesta aplicada a un grupo de $50$ personas sobre su deporte favorito, $15$ de ellas eligieron fútbol. ¿Cuál es la frecuencia relativa porcentual correspondiente a fútbol?",
            "options": [
                {
                    "id": "A",
                    "content": "$30\\%$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$15\\%$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$0,3\\%$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$35\\%$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Frecuencia relativa porcentual = (Frecuencia absoluta / Total) * 100% = (15 / 50) * 100% = 30%.",
                "step_by_step": "1) Razón: $15 / 50 = 3/10 = 0,30$.\\n2) Expresar en porcentaje: $0,30 * 100\\% = 30\\%$.",
                "key_concept": "Frecuencia relativa porcentual en tablas de distribución de frecuencias.",
                "frequent_mistake": "Confundir la frecuencia absoluta (15 personas) directamente con el porcentaje (15%)."
            },
            "difficulty_estimate": 0.3,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "4dda9ea8-8108-531f-ba70-ccfb7fd3d19c",
            "subtopic_id": "0a90ccdf-9fc5-5fac-8972-9616c11a7473",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "En un estudio de estaturas agrupadas en intervalos, se obtienen las siguientes frecuencias absolutas: $[150, 160): 8$; $[160, 170): 22$; $[170, 180): 14$; $[180, 190): 6$. ¿Cuál es el intervalo modal de la muestra?",
            "options": [
                {
                    "id": "A",
                    "content": "$[160, 170)$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$22$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$[170, 180)$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$165$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "El intervalo modal es aquel que concentra la mayor frecuencia absoluta ($22 \\implies [160, 170)$).",
                "step_by_step": "1) Identificar la frecuencia absoluta máxima: $22$.\\n2) Ubicar el intervalo asociado a dicha frecuencia máxima: $[160, 170)$.\\n3) Intervalo modal: $[160, 170)$.",
                "key_concept": "Identificación del intervalo modal en distribuciones de datos agrupados.",
                "frequent_mistake": "Responder con el valor de la frecuencia absoluta máxima (22) en lugar del intervalo mismo."
            },
            "difficulty_estimate": 0.35,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "d5e9effe-8cc0-5f73-9629-c4a33cfebccc",
            "subtopic_id": "0a90ccdf-9fc5-5fac-8972-9616c11a7473",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "En un gráfico circular que resume las preferencias de un total de $200$ estudiantes, el sector correspondiente a «Música» tiene un ángulo central de $72^\\circ$. ¿Cuántos estudiantes prefieren Música?",
            "options": [
                {
                    "id": "A",
                    "content": "$40\\text{ estudiantes}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$72\\text{ estudiantes}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$20\\text{ estudiantes}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$36\\text{ estudiantes}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Proporción angular: $(72 / 360) * 200 = (1 / 5) * 200 = 40$ estudiantes.",
                "step_by_step": "1) Fracción del círculo: $72^\\circ / 360^\\circ = 1/5 = 0,20$ ($20\\%$).\\n2) Calcular cantidad de estudiantes: $0,20 * 200 = 40\\text{ estudiantes}$.",
                "key_concept": "Modelamiento y cálculo de frecuencias a partir de sectores angulares.",
                "frequent_mistake": "Asumir que el número de grados equivale directamente a la cantidad de personas (72)."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "e3eea65f-cc1c-5caa-baa8-47ec6b9f14dc",
            "subtopic_id": "0a90ccdf-9fc5-5fac-8972-9616c11a7473",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Un medio de comunicación presenta un gráfico de barras comparando las ventas de dos marcas: Marca A ($92$ unidades) y Marca B ($98$ unidades). El eje vertical comienza en $90$ en lugar de $0$, haciendo que la barra de B se vea cuatro veces más alta que la de A. ¿Por qué este gráfico induce a una interpretación errónea?",
            "options": [
                {
                    "id": "A",
                    "content": "Porque el truncamiento del eje vertical exagera visualmente la diferencia relativa entre ambas marcas, que en realidad es de solo un $6,5\\%$ aproximadamente",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "Porque los gráficos de barras solo se pueden utilizar para variables cualitativas",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                },
                {
                    "id": "C",
                    "content": "Porque la barra B debería medir exactamente el doble que la barra A",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "Porque siempre es obligatorio ordenar las barras de mayor a menor",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Truncar el origen de la escala vertical distorsiona la proporcionalidad geométrica de las barras.",
                "step_by_step": "1) Razón real de ventas: $98 / 92 \\approx 1,065$ (diferencia real del $6,5\\%$).\\n2) Al truncar el eje en 90, las alturas graficadas representan $92 - 90 = 2$ y $98 - 90 = 8$.\\n3) Visualmente $8 / 2 = 4$ veces más grande, generando una percepción desproporcionada de la ventaja.",
                "key_concept": "Lectura crítica y detección de sesgos en representaciones gráficas estadísticas.",
                "frequent_mistake": "Considerar que el punto de inicio del eje vertical es irrelevante para la interpretación visual."
            },
            "difficulty_estimate": 0.5,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "4c977f44-1d5e-521c-a9fb-43970a16c3db",
            "subtopic_id": "0a90ccdf-9fc5-5fac-8972-9616c11a7473",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Una tabla de frecuencias de tiempos de espera registra: Intervalo 1: $5$ personas; Intervalo 2: $8$ personas; Intervalo 3: $12$ personas; Intervalo 4: $10$ personas. ¿Cuál es la frecuencia acumulada hasta el Intervalo 3?",
            "options": [
                {
                    "id": "A",
                    "content": "$25\\text{ personas}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$12\\text{ personas}$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                },
                {
                    "id": "C",
                    "content": "$35\\text{ personas}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$13\\text{ personas}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                }
            ],
            "explanation": {
                "short_summary": "Sumar frecuencias absolutas hasta el intervalo 3: $5 + 8 + 12 = 25$.",
                "step_by_step": "1) Frecuencia acumulada $F_3 = f_1 + f_2 + f_3$.\\n2) Sustituir: $F_3 = 5 + 8 + 12 = 25\\text{ personas}$.",
                "key_concept": "Frecuencia absoluta acumulada en distribuciones estadísticas.",
                "frequent_mistake": "Indicar solo la frecuencia simple del intervalo 3 ($12$) en lugar del acumulado."
            },
            "difficulty_estimate": 0.3,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "486ecfe4-4038-5118-9cb5-c03d2bed5802",
            "subtopic_id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "Al lanzar simultáneamente dos dados tradicionales de $6$ caras numeradas del $1$ al $6$, ¿cuál es la probabilidad de que la suma de los puntos obtenidos sea igual a $7$?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\frac{1}{6}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\frac{7}{36}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$\\frac{1}{12}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$\\frac{5}{36}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Casos favorables: $(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)$ (6 casos). Probabilidad $= 6/36 = 1/6$.",
                "step_by_step": "1) Espacio muestral: $6 * 6 = 36$ resultados equiprobables.\\n2) Pares con suma 7: $(1,6), (2,5), (3,4), (4,3), (5,2), (6,1) \\implies 6$ casos favorables.\\n3) Regla de Laplace: $P = 6 / 36 = 1/6$.",
                "key_concept": "Regla de Laplace y enumeración sistemática de pares en experimentos compuestos.",
                "frequent_mistake": "No considerar el orden de los dados y contar solo pares no ordenados, omitiendo la mitad de los casos."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "8e881af4-cdf5-55ba-8a8e-395c3e55dc36",
            "subtopic_id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "skill_id": "61e5f823-31f2-548b-b960-5b5784474a0b",
            "skill_code": "MODELAR",
            "provenance_type": "ORIGINAL",
            "stem": "En una urna hay $4$ bolitas rojas y $6$ bolitas azules de idéntico tamaño y peso. ¿Cuántas bolitas rojas adicionales se deben agregar a la urna para que la probabilidad de extraer una bolita roja al azar sea exactamente $\\frac{1}{2}$?",
            "options": [
                {
                    "id": "A",
                    "content": "$2\\text{ bolitas}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$1\\text{ bolita}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "C",
                    "content": "$4\\text{ bolitas}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "D",
                    "content": "$3\\text{ bolitas}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Para probabilidad 1/2, debe haber igual cantidad de rojas y azules: $4 + k = 6 \\implies k = 2$.",
                "step_by_step": "1) Sea $k$ la cantidad de bolitas rojas agregadas.\\n2) Total de rojas: $4 + k$. Total general: $10 + k$.\\n3) Ecuación: $(4 + k) / (10 + k) = 1/2 \\implies 2(4 + k) = 10 + k \\implies 8 + 2k = 10 + k \\implies k = 2$.",
                "key_concept": "Modelamiento algebraico de probabilidades clásicas condicionadas por adición de elementos.",
                "frequent_mistake": "Calcular la mitad de 10 (5) y agregar solo 1 bolita roja, olvidando que al agregarla el total también aumenta."
            },
            "difficulty_estimate": 0.45,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "32133aa9-66d5-5b18-8777-7773c8773297",
            "subtopic_id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "skill_id": "77255936-c7af-56b6-97ec-8cba40386b28",
            "skill_code": "REPRESENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "Se lanza una moneda equilibrada al aire $3$ veces consecutivas. ¿Cuál es la probabilidad de obtener exactamente $2$ caras y $1$ sello?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\frac{3}{8}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\frac{2}{3}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                },
                {
                    "id": "C",
                    "content": "$\\frac{1}{4}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$\\frac{1}{2}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                }
            ],
            "explanation": {
                "short_summary": "Espacio muestral de 8 elementos ($2^3$). Casos con exactamente 2 caras: (C,C,S), (C,S,C), (S,C,C) (3 casos) $\\implies 3/8$.",
                "step_by_step": "1) Espacio muestral: $\\{CCC, CCS, CSC, SCC, CSS, SCS, SSC, SSS\\} \\implies 8$ casos.\\n2) Casos favorables con 2 caras: $\\{CCS, CSC, SCC\\} \\implies 3$ casos.\\n3) Probabilidad: $3/8$.",
                "key_concept": "Representación de espacios muestrales finitos de ensayos de Bernoulli independientes.",
                "frequent_mistake": "Poner en el numerador las 2 caras y en el denominador los 3 lanzamientos: $2/3$ (opción B)."
            },
            "difficulty_estimate": 0.4,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "013370f1-337a-52d3-b2fe-75d1ce945234",
            "subtopic_id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "skill_id": "b910a521-9fc0-50e6-9d8f-20c09b77370e",
            "skill_code": "ARGUMENTAR",
            "provenance_type": "ORIGINAL",
            "stem": "La probabilidad de que un evento meteorológico $A$ ocurra en una determinada jornada es $P(A) = 0,35$. ¿Cuál es la probabilidad de que el evento $A$ NO ocurra en dicha jornada?",
            "options": [
                {
                    "id": "A",
                    "content": "$0,65$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$0,35$",
                    "is_correct": False,
                    "distractor_type": "LECTURA"
                },
                {
                    "id": "C",
                    "content": "$0,75$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$-0,35$",
                    "is_correct": False,
                    "distractor_type": "CONCEPTUAL"
                }
            ],
            "explanation": {
                "short_summary": "Probabilidad del evento complementario: $P(A^c) = 1 - P(A) = 1 - 0,35 = 0,65$.",
                "step_by_step": "1) Axioma de Kolmogorov del evento complementario: $P(A^c) = 1 - P(A)$.\\n2) Sustituir: $P(A^c) = 1 - 0,35 = 0,65$.",
                "key_concept": "Propiedad del evento complementario en la teoría clásica de probabilidades.",
                "frequent_mistake": "Cometer error aritmético elemental en la resta con decimales $1 - 0,35 = 0,75$ (opción C)."
            },
            "difficulty_estimate": 0.3,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": False,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        },
        {
            "id": "973c7d8d-9859-5f60-974f-2f246bb557fc",
            "subtopic_id": "ce3f6244-3b26-56de-a79b-10b20c489487",
            "skill_id": "a3da57b1-2533-572d-857b-27063e83c1ce",
            "skill_code": "RESOLVER_PROBLEMAS",
            "provenance_type": "ORIGINAL",
            "stem": "De un mazo de naipes inglés tradicional de $52$ cartas (sin comodines), se extrae una carta al azar. ¿Cuál es la probabilidad de que la carta extraída sea un As O una carta del palo de Corazones?",
            "options": [
                {
                    "id": "A",
                    "content": "$\\frac{4}{13}$",
                    "is_correct": True,
                    "distractor_type": None
                },
                {
                    "id": "B",
                    "content": "$\\frac{17}{52}$",
                    "is_correct": False,
                    "distractor_type": "PROCEDIMENTAL"
                },
                {
                    "id": "C",
                    "content": "$\\frac{1}{13}$",
                    "is_correct": False,
                    "distractor_type": "CALCULO"
                },
                {
                    "id": "D",
                    "content": "$\\frac{1}{4}$",
                    "is_correct": False,
                    "distractor_type": "INTERPRETACION"
                }
            ],
            "explanation": {
                "short_summary": "Regla aditiva para eventos no disjuntos: $P(A \\cup C) = P(A) + P(C) - P(A \\cap C) = 4/52 + 13/52 - 1/52 = 16/52 = 4/13$.",
                "step_by_step": "1) Cantidad de Ases: $4$. Cantidad de Corazones: $13$.\\n2) Intersección (As de Corazones): $1$ carta.\\n3) Cartas favorables: $4 + 13 - 1 = 16$.\\n4) Probabilidad: $16 / 52 = 4 / 13$.",
                "key_concept": "Principio de inclusión-exclusión y adición de probabilidades no excluyentes.",
                "frequent_mistake": "Sumar $4 + 13 = 17$ sin descontar la intersección, contando el As de Corazones dos veces (opción B)."
            },
            "difficulty_estimate": 0.55,
            "difficulty_source": "INITIAL_HEURISTIC",
            "irt_status": "UNINITIALIZED",
            "is_pilot": True,
            "source_attribution": {
                "source": "Banco Oficial Ampliado PAES M1 2026",
                "year": 2026,
                "license": "Uso Educativo Interno"
            }
        }
    ]
}
