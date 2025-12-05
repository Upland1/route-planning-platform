from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import Interface.route_emergency as engine
import osmnx as ox
import networkx as nx
import pyproj

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initial loading ---
print("Cargando grafo y hospitales...")

G = engine.bring_map_data("Zapopan, Jalisco, Mexico")
G, hosp_coords, hosp_nodes, _ = engine.search_closests_hospitals(G, "Zapopan, Jalisco, Mexico")

# We prepare coordinate translator
project_to_meters = pyproj.Transformer.from_crs("EPSG:4326", G.graph['crs'], always_xy=True).transform
project_to_latlon = pyproj.Transformer.from_crs(G.graph['crs'], "EPSG:4326", always_xy=True).transform

@app.get("/calcular-ruta/")
def calcular_ruta(lat: float, lon: float):
    print(f"Recibido clic en: {lat}, {lon}")
    
    # Translate click (degrees) to map (meters) 
    x_meters, y_meters = project_to_meters(lon, lat)
    
    # Find the closest node to the click
    origin_node = ox.distance.nearest_nodes(G, x_meters, y_meters)
    
    # Run passing the exact node
    route_nodes, hospital_node = engine.emergency_routing_system(
        G, hosp_coords, hosp_nodes, origin_node=origin_node
    )
    
    if not route_nodes:
        return {"error": "No se encontró ruta"}

    # Translate resulting path (meters -> degrees) 
    # Extract coordinates (x,y) of each node in the route
    path_coords_meters = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in route_nodes]
    
    # Convert each point to Lat/Lon
    path_latlon = []
    for x, y in path_coords_meters:
        lon_geo, lat_geo = project_to_latlon(x, y)
        # Leaflet/GeoJSON waits for [lon, lat] or [lat, lon]. 
        path_latlon.append([lon_geo, lat_geo])

    # GeoJSON real answer
    return {
        "ruta": {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": path_latlon
            },
            "properties": {"color": "blue"}
        }
    }