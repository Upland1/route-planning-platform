place = "Zapopan, Jalisco, Mexico"
G = ox.graph_from_address(place, dist=10000,network_type="drive") # 'drive', 'walk', 'bike', or 'all'
