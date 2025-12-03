import osmnx as ox
import numpy as np
import networkx as nx
from scipy.spatial import Voronoi, voronoi_plot_2d, KDTree # Using scipy's KDTree for compatibility
import matplotlib.pyplot as plt

def bring_map_data(place: str):
    print("Downloading map data...")
    G = ox.graph_from_address(place, dist=6000, network_type="drive")
    G_new = ox.project_graph(G)
    return G_new

def search_closests_hospitals(G, place: str):
    print("Searching for hospitals...")
    tags = {'amenity': ['hospital', 'clinic', 'doctors'], 'healthcare': 'hospital'}
    
    # Download hospital geometries
    hospitals_gdf = ox.features_from_address(place, tags=tags, dist=6000)
    
    # Safety Check
    if hospitals_gdf.empty:
        print("Warning: No hospitals found with these tags in this area!")
        return G, np.array([]), [], None

    # Filter just by ones with valid geometry
    hospitals_gdf = hospitals_gdf[hospitals_gdf.geometry.notnull()]

    # Project the hospitals to match the Graph's CRS (Meters)
    hospitals_proj = hospitals_gdf.to_crs(G.graph['crs'])
    
    # Calculate Centroids after projection
    hospitals_proj['centroid'] = hospitals_proj.geometry.centroid
    
    hospitals_coords = []
    hospitals_nodes = []
    
    print("Mapping hospitals to grid...")
    
    # Extract X and Y for nearest_nodes search
    # We use the centroids of the projected data
    X = hospitals_proj['centroid'].apply(lambda x: x.x).values
    Y = hospitals_proj['centroid'].apply(lambda x: x.y).values
    
    # Bulk search for nearest nodes (faster than loop)
    hospitals_nodes = ox.distance.nearest_nodes(G, X, Y)
    
    # Zip coordinates for the return
    hospitals_coords = np.array(list(zip(X, Y)))
            
    print(f"   -> {len(hospitals_coords)} health centers were found.")
    return G, hospitals_coords, hospitals_nodes, hospitals_proj

def generate_voronoi(hospitals_coords, G):
    if len(hospitals_coords) < 2:
        print("Cannot generate Voronoi Diagram (Need at least 2 points)")
        return 

    print("Generating Voronoi...")
    vor = Voronoi(hospitals_coords)
    
    # --- Visualization ---
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # --- Convert list to Numpy Array for slicing ---
    node_points = []
    for _, data in G.nodes(data=True):
        if 'x' in data and 'y' in data:
            node_points.append((data['x'], data['y']))
    
    node_points = np.array(node_points) # Converting to numpy array
    
    ax.scatter(node_points[:,0], node_points[:,1], c='lightgray', s=1, alpha=0.5, label='Map nodes')
    
    # Draw Voronoi regions
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='blue', line_width=2, line_alpha=0.6, point_size=0)
    
    # Draw hospitals
    ax.scatter(hospitals_coords[:,0], hospitals_coords[:,1], c='red', s=100, marker='P', label='Hospitals', zorder=5)

    ax.set_title("Voronoi Partition: Hospital Influence Areas")
    ax.legend()
    ax.axis('off')
    plt.show()

def emergency_routing_system(G, hospitals_coords, hospitals_nodes):
    # We use a KDtree of the hospitals to mathematically determine in which Voronoi region
    # a point falls (closest neighbor = Voronoi Region)
    tree_hospitals = KDTree(hospitals_coords)
    
    # Generate a random emergency location within the map
    node_ids = list(G.nodes())
    random_origin = node_ids[np.random.randint(len(node_ids))]
    
    x_orig = G.nodes[random_origin]['x']
    y_orig = G.nodes[random_origin]['y']
    
    print(f"User located at UTM coordinates: ({x_orig:.1f}, {y_orig:.1f})")
    
    # Determine Voronoi region (nearest hospital straight ahead)
    dist, idx_hospital = tree_hospitals.query((x_orig, y_orig))
    
    hospital_assigned_node = hospitals_nodes[idx_hospital]
    
    print(f"The nearest hospital (region {idx_hospital}) is {dist:.1f} meters away (Euclidean)")
    
    # Calculate real route
    try:
        route = nx.shortest_path(G, random_origin, hospital_assigned_node, weight='length')
        route_length = nx.shortest_path_length(G, random_origin, hospital_assigned_node, weight='length')
        print(f"Calculated route: {len(route)} steps. Travel distance: {route_length:.1f} meters")
        
        # Visualize route
        fig, ax = ox.plot_graph_route(G, route, node_size=0, route_color='red', route_linewidth=3, show=False, close=False)
        
        ax.scatter(x_orig, y_orig, c='yellow', s=150, edgecolors='black', label='User', zorder=6)
        ax.scatter(hospitals_coords[idx_hospital][0], hospitals_coords[idx_hospital][1], c='white', s=150, marker='P', edgecolors='red', label='Target Hospital', zorder=6)
        ax.set_title(f"Emergency route: {route_length:.0f}m")
        plt.legend()
        plt.show()
        
    except nx.NetworkXNoPath:
        print("No path found between origin and hospital (nodes might be disconnected).")

if __name__ == "__main__":
    place = "Zapopan, Jalisco, Mexico"
    G = bring_map_data(place)
    G, hosp_coords, hosp_nodes, _ = search_closests_hospitals(G, place)
    
    generate_voronoi(hosp_coords, G)
    emergency_routing_system(G, hosp_coords, hosp_nodes)