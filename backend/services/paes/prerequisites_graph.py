from typing import Dict, List, Set
from uuid import UUID


class PrerequisiteCycleError(Exception):
    """Lanzada cuando la adición de un prerrequisito generaría un ciclo en el grafo curricular."""
    pass

def check_no_cycles(
    existing_edges: List[tuple[UUID, UUID]], # Lista de (subtopic_id, prerequisite_id)
    new_subtopic_id: UUID,
    new_prerequisite_id: UUID
) -> None:
    """
    Verifica que la adición de la arista (new_subtopic_id -> new_prerequisite_id)
    no introduzca un ciclo en el grafo dirigido de dependencias.

    Interpretación del grafo:
    Una arista (A, B) significa que A depende de B (B es prerrequisito de A).
    Por tanto, existe un camino dirigido de dependencia A -> B.
    Se generaría un ciclo si ya existe un camino desde B hacia A.
    """
    if new_subtopic_id == new_prerequisite_id:
        raise PrerequisiteCycleError(f"Auto-dependencia no permitida: {new_subtopic_id} no puede ser su propio prerrequisito.")

    # Construir grafo de adyacencia existente: origen -> destinos (A depende de B => A -> B)
    adj: Dict[UUID, List[UUID]] = {}
    for sub, prereq in existing_edges:
        if sub not in adj:
            adj[sub] = []
        adj[sub].append(prereq)

    # Agregar la nueva arista temporalmente
    if new_subtopic_id not in adj:
        adj[new_subtopic_id] = []
    adj[new_subtopic_id].append(new_prerequisite_id)

    # Verificar si existe un ciclo alcanzable desde new_subtopic_id mediante DFS
    visited: Set[UUID] = set()
    recursion_stack: Set[UUID] = set()

    def dfs(node: UUID) -> bool:
        visited.add(node)
        recursion_stack.add(node)

        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True # Ciclo detectado

        recursion_stack.remove(node)
        return False

    # Ejecutar DFS desde todos los nodos para comprobar aciclicidad global
    for node in list(adj.keys()):
        if node not in visited:
            if dfs(node):
                raise PrerequisiteCycleError(
                    f"Ciclo detectado al vincular el subtema {new_subtopic_id} con el prerrequisito {new_prerequisite_id}."
                )
