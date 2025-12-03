import osmnx as ox
import networkx as nx
import heapq
import time
import math
import random
from collections import deque

# ==========================================
# 1. PREPARACIÓN DEL GRAFO Y HEURÍSTICA
# ==========================================

def get_coordinates(G, node):
    """Obtiene coordenadas (y, x) del nodo. En grafo proyectado son metros."""
    return G.nodes[node]['y'], G.nodes[node]['x']

def heuristic(G, node, goal):
    """
    Calcula la distancia Euclidiana.
    Correcto para A* en grafos proyectados (unidades en metros).
    """
    y1, x1 = get_coordinates(G, node)
    y2, x2 = get_coordinates(G, goal)
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# ==========================================
# 2. ALGORITMOS CON TIMEOUT (Para evitar congelamientos)
# ==========================================

def bfs_search(G, start, goal, timeout=20):
    """BFS con límite de tiempo"""
    t_start = time.time()
    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        if time.time() - t_start > timeout: return None 

        current, path = queue.popleft()

        if current == goal:
            return path

        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

def dfs_search(G, start, goal, timeout=20):
    """DFS con límite de tiempo"""
    t_start = time.time()
    stack = [(start, [start])]
    visited = set([start])

    while stack:
        if time.time() - t_start > timeout: return None 
        
        current, path = stack.pop()

        if current == goal:
            return path
        
        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))
    return None

def iddfs_search(G, start, goal, max_depth=50, timeout=20):
    """IDDFS con límite de tiempo y profundidad"""
    t_start = time.time()

    def dls(current, goal, depth, path, visited_in_path):
        # Chequeo de tiempo en cada paso recursivo
        if time.time() - t_start > timeout: return "TIMEOUT"

        if current == goal:
            return path
        if depth <= 0:
            return None
        
        for neighbor in G.neighbors(current):
            if neighbor not in visited_in_path:
                visited_in_path.add(neighbor)
                result = dls(neighbor, goal, depth - 1, path + [neighbor], visited_in_path)
                if result == "TIMEOUT": return "TIMEOUT"
                if result: return result
                visited_in_path.remove(neighbor)
        return None

    # Iteramos profundidad
    for limit in range(1, max_depth + 1, 5): 
        if time.time() - t_start > timeout: return None
        
        visited = set([start])
        result = dls(start, goal, limit, [start], visited)
        if result == "TIMEOUT": return None
        if result:
            return result
    return None

# ==========================================
# 3. ALGORITMOS INFORMADOS CON TIMEOUT
# ==========================================

def ucs_search(G, start, goal, timeout=20):
    """UCS (Dijkstra) con límite de tiempo"""
    t_start = time.time()
    pq = [(0, start, [start])]
    visited = set()
    cost_so_far = {start: 0}

    while pq:
        if time.time() - t_start > timeout: return None

        current_cost, current, path = heapq.heappop(pq)

        if current == goal:
            return path
        
        if current in visited:
            continue
        visited.add(current)

        for neighbor in G.neighbors(current):
            edge_data = G.get_edge_data(current, neighbor)[0]
            # En grafo proyectado 'length' está en metros
            weight = edge_data.get('length', 1)
            new_cost = current_cost + weight
            
            if new_cost < cost_so_far.get(neighbor, float('inf')):
                cost_so_far[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))
    return None

def a_star_search(G, start, goal, timeout=20):
    """A* con límite de tiempo"""
    t_start = time.time()
    pq = [(0, 0, start, [start])]
    visited = set()
    g_costs = {start: 0}

    while pq:
        if time.time() - t_start > timeout: return None

        _, current_g, current, path = heapq.heappop(pq)

        if current == goal:
            return path
        
        if current in visited and current_g > g_costs.get(current, float('inf')):
            continue
        visited.add(current)

        for neighbor in G.neighbors(current):
            edge_data = G.get_edge_data(current, neighbor)[0]
            weight = edge_data.get('length', 1)
            
            new_g = current_g + weight
            
            if new_g < g_costs.get(neighbor, float('inf')):
                g_costs[neighbor] = new_g
                h = heuristic(G, neighbor, goal)
                f = new_g + h
                heapq.heappush(pq, (f, new_g, neighbor, path + [neighbor]))
    return None

# ==========================================
# 4. BENCHMARKING (CORREGIDO)
# ==========================================

def get_distance_km(G, u, v):
    """
    CORRECCIÓN: Usa distancia Euclidiana porque el grafo está proyectado en metros.
    Antes fallaba porque usaba great_circle con coordenadas en metros.
    """
    y1, x1 = get_coordinates(G, u)
    y2, x2 = get_coordinates(G, v)
    # Pitágoras simple porque x, y ya son metros planos
    dist_meters = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return dist_meters / 1000.0  # Convertir a KM

def generate_test_pairs(G, num_pairs=3):
    """Genera pares verificando distancias correctas en KM."""
    nodes = list(G.nodes())
    pairs = {
        "Corta (<1 km)": [],
        "Media (1 km - 5 km)": [],
        "Larga (>5 km)": []
    }
    
    print("Generando pares de prueba en Zapopan... (Buscando...)")
    
    count = 0
    while any(len(v) < num_pairs for v in pairs.values()):
        count += 1
        if count % 2000 == 0:
            # Imprimir estado para saber qué falta
            faltantes = [k for k, v in pairs.items() if len(v) < num_pairs]
            print(f"  ...Intento {count}. Buscando categorías faltantes: {faltantes}")

        u = random.choice(nodes)
        v = random.choice(nodes)
        if u == v: continue
        
        # Ahora dist_km será correcta (ej. 3.5 km, no 18000 km)
        dist_km = get_distance_km(G, u, v)
        
        category = None
        if dist_km < 1.0:
            category = "Corta (<1 km)"
        elif 1.0 <= dist_km <= 5.0:
            category = "Media (1 km - 5 km)"
        elif dist_km > 5.0:
            category = "Larga (>5 km)"
            
        if category and len(pairs[category]) < num_pairs:
            # Validar que exista ruta
            if nx.has_path(G, u, v):
                pairs[category].append((u, v))
                print(f"  [OK] {category}: {dist_km:.2f} km")
    
    return pairs

def run_benchmark():
    place = "Zapopan, Mexico"
    print(f"1. Descargando grafo de {place}...")
    G = ox.graph_from_place(place, network_type='drive')
    
    print("2. Proyectando grafo a metros (UTM)...")
    G = ox.project_graph(G) 
    
    # 3. Generar Pares
    test_suite = generate_test_pairs(G, num_pairs=3)
    
    # 4. Configurar algoritmos con timeout
    TIMEOUT = 10 # Segundos
    algorithms = {
        "BFS": lambda g, s, e: bfs_search(g, s, e, timeout=TIMEOUT),
        "DFS": lambda g, s, e: dfs_search(g, s, e, timeout=TIMEOUT),
        "UCS": lambda g, s, e: ucs_search(g, s, e, timeout=TIMEOUT),
        "A*": lambda g, s, e: a_star_search(g, s, e, timeout=TIMEOUT),
        "IDDFS": lambda g, s, e: iddfs_search(g, s, e, max_depth=50, timeout=TIMEOUT)
    }
    
    print("\n" + "="*80)
    print(f"{'CATEGORÍA':<20} | {'ALGORITMO':<10} | {'TIEMPO (s)':<12} | {'ESTADO'}")
    print("="*80)
    
    for category, pairs in test_suite.items():
        print(f"--- {category} ---")
        for name, func in algorithms.items():
            total_time = 0
            successes = 0
            timeouts = 0
            
            for start, goal in pairs:
                t0 = time.time()
                try:
                    path = func(G, start, goal)
                    dur = time.time() - t0
                    
                    if path:
                        total_time += dur
                        successes += 1
                    else:
                        timeouts += 1
                except Exception:
                    pass 
            
            if successes > 0:
                avg = total_time / successes
                # El time out son checkpoints para poner un limite de tiempo
                print(f"{'':<20} | {name:<10} | {avg:.6f} s   | {successes} Ok / {timeouts} T.O.")
            else:
                print(f"{'':<20} | {name:<10} | --             | Tiempo Excedido")

if __name__ == "__main__":
    run_benchmark()