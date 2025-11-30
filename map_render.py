import osmnx as ox

place = "Zapopan, Jalisco, Mexico"
G = ox.graph_from_address(place, dist=10000,network_type="drive") # 'drive', 'walk', 'bike', or 'all'
fig, ax = ox.plot_graph(G)

fig.savefig('mapa_zapopan.png')