from KDTree import KDTree
import osmnx as ox
import time
import math
import random

def bring_map_data(place: str):
    G = ox.graph_from_address(place, dist=10000,network_type="drive")
    G_new = ox.project_graph(G)
    return G_new

# Extract all (x, y) coordinates from the nodes of the graph and build the KDtTree
def create_kd_tree(G):
    points = []
    for _, data in G.nodes(data=True):
        if 'x' in data and 'y' in data:
            points.append((data['x'], data['y']))
    tree = KDTree(points)
    return tree

# Exhaustive Search Function (Brute Force)
def exhaustive_search(G_nodes, target):
    best_node = None
    min_dist = float('inf')
    target_x, target_y = target
    
    for node_id, data in G_nodes:
        dist = math.sqrt((data['x'] - target_x)**2 + (data['y'] - target_y)**2)
        if dist < min_dist:
            min_dist = dist
            best_node = node_id
    
    return best_node

# Generate random points inside the map
def generate_random_points(nodes_list):    
    xs = [d['x'] for _, d in nodes_list]
    ys = [d['y'] for _, d in nodes_list]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    test_points = []
    for _ in range(20):
        rx = random.uniform(min_x, max_x)
        ry = random.uniform(min_y, max_y)
        test_points.append((rx, ry))

    return test_points
 
if __name__ == "__main__":
    place = "Zapopan, Jalisco, Mexico"
    G = bring_map_data(place)
    # Print graph size: number of nodes (vertex) y edges
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    print(f"Graph size: {n_nodes} nodes, {n_edges} edges")
    
    nodes_list = list(G.nodes(data=True))

    # --- Measurement begins ---
    start_time = time.time()
    
    kd_tree = create_kd_tree(G)
    
    # --- Measurement ends ---
    end_time = time.time()
    
    total_time = end_time - start_time
    
    print(f"Total time to build KD-Tree: {total_time:.6f} seconds")
    
    print("\n--- INICIANDO COMPARACIÓN (20 Puntos) ---\n")
    print(f"{'Punto (X, Y)':<30} | {'KD-Tree (s)':<15} | {'Exhaustiva (s)':<15} | {'Ganador'}")
    print("-" * 80)

    test_points = generate_random_points(nodes_list)
    total_kd = 0
    total_ex = 0

    for i, p in enumerate(test_points):
        # 1. Medir KD-Tree
        start = time.perf_counter() # perf_counter es más preciso que time.time()
        # Asumiendo que tu KDTree tiene un método 'closest_point' o similar
        # Si tu KDTree devuelve el punto, asegúrate de recuperar el ID del nodo después si es necesario
        _ = kd_tree.closest_point(p) 
        end = time.perf_counter()
        time_kd = end - start
        
        # 2. Medir Exhaustiva
        start = time.perf_counter()
        _ = exhaustive_search(nodes_list, p)
        end = time.perf_counter()
        time_ex = end - start
        
        total_kd += time_kd
        total_ex += time_ex
        
        speedup = time_ex / time_kd if time_kd > 0 else 0
        print(f"Pto {i+1}: ({p[0]:.1f}, {p[1]:.1f})   | {time_kd:.6f} s      | {time_ex:.6f} s      | KD es {speedup:.1f}x más rápido")

    print("-" * 80)
    print(f"Promedio KD-Tree:   {total_kd/20:.6f} s")
    print(f"Promedio Exhaustiva: {total_ex/20:.6f} s")
