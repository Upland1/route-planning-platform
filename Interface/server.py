from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import Interface.route_emergency as engine
import osmnx as ox
import networkx as nx
import pyproj # Necesario para traducir Lat/Lon <-> Metros

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CARGA INICIAL ---
print("Cargando grafo y hospitales...")
# Usamos tus funciones
G = engine.bring_map_data("Zapopan, Jalisco, Mexico")
G, hosp_coords, hosp_nodes, _ = engine.search_closests_hospitals(G, "Zapopan, Jalisco, Mexico")

# Preparamos el traductor de coordenadas
# G.graph['crs'] es la proyección en metros (ej. EPSG:32613)
# EPSG:4326 es Latitud/Longitud (lo que usa el GPS y la Web)
project_to_meters = pyproj.Transformer.from_crs("EPSG:4326", G.graph['crs'], always_xy=True).transform
project_to_latlon = pyproj.Transformer.from_crs(G.graph['crs'], "EPSG:4326", always_xy=True).transform

@app.get("/calcular-ruta/")
def calcular_ruta(lat: float, lon: float):
    print(f"Recibido clic en: {lat}, {lon}")
    
    # 1. Traducir Clic (Grados) -> Mapa (Metros)
    x_meters, y_meters = project_to_meters(lon, lat)
    
    # 2. Encontrar el nodo del grafo más cercano al clic
    origin_node = ox.distance.nearest_nodes(G, x_meters, y_meters)
    
    # 3. Ejecutar TU lógica (pasándole el nodo exacto)
    route_nodes, hospital_node = engine.emergency_routing_system(
        G, hosp_coords, hosp_nodes, origin_node=origin_node
    )
    
    if not route_nodes:
        return {"error": "No se encontró ruta"}

    # 4. Traducir la Ruta resultante (Metros -> Grados) para que Leaflet la entienda
    # Extraemos las coordenadas (x,y) de cada nodo de la ruta
    path_coords_meters = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in route_nodes]
    
    # Convertimos cada punto a Lat/Lon
    path_latlon = []
    for x, y in path_coords_meters:
        lon_geo, lat_geo = project_to_latlon(x, y)
        # Leaflet/GeoJSON espera [lon, lat] o [lat, lon]. 
        # GeoJSON estándar es [lon, lat], pero Leaflet a veces prefiere arreglos simples.
        # Para GeoJSON LineString usaremos [lon, lat]
        path_latlon.append([lon_geo, lat_geo])

    # 5. Respuesta GeoJSON real
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