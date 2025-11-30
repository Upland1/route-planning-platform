import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# --- Clase Nodo y Estructura KD-Tree ---
class Node:
    def __init__(self, point=None, left=None, right=None, split_axis=None, split_value=None):
        self.point = point          # Valor si es hoja
        self.left = left            # Hijo izquierdo
        self.right = right          # Hijo derecho
        self.split_axis = split_axis # Eje de división (0=x, 1=y)
        self.split_value = split_value # Valor de la mediana

class KDTree:
    def __init__(self, points):
        self.root = self.build_kd_tree(points, depth=0)

    def build_kd_tree(self, points, depth):
        """
        Implementación del algoritmo de la diapositiva 22.
        """
        if not points:
            return None
        
        k = 2 # Dimensión (2D)
        axis = depth % k # Alternar ejes: par->x, impar->y (Slide 22)
        
        # Caso base: Si es un solo punto, regresar nodo hoja (Slide 22)
        if len(points) == 1:
            return Node(point=points[0])
        
        # Ordenar puntos y encontrar la mediana
        points.sort(key=lambda x: x[axis])
        mid = len(points) // 2
        median_point = points[mid]
        
        # El valor de división es la coordenada del punto mediano
        split_value = median_point[axis]
        
        # Dividir conjuntos (Slide 22)
        # points_left: incluye la mediana según la lógica común de partición <=
        points_left = points[:mid]
        points_right = points[mid:]
        
        node = Node(split_axis=axis, split_value=split_value)
        node.left = self.build_kd_tree(points_left, depth + 1)
        node.right = self.build_kd_tree(points_right, depth + 1)
        
        return node

    def search(self, x_range, y_range):
        found_points = []
        region = {'x': x_range, 'y': y_range}
        self.search_kd_tree(self.root, region, found_points)
        return found_points

    def search_kd_tree(self, node, region, found):
        """
        Implementación del algoritmo de la diapositiva 35.
        """
        if node is None:
            return

        # Si es nodo hoja (Slide 35)
        if node.point is not None:
            px, py = node.point
            # Reporta si está dentro de la región
            if (region['x'][0] <= px <= region['x'][1] and 
                region['y'][0] <= py <= region['y'][1]):
                found.append(node.point)
            return

        # Lógica de intersección de regiones (Slide 35)
        # Eje 0 es x, Eje 1 es y
        axis_name = 'x' if node.split_axis == 0 else 'y'
        min_val, max_val = region[axis_name]
        
        # Si la región se intercepta con la rama izquierda (valores <= split_value)
        if min_val <= node.split_value:
            self.search_kd_tree(node.left, region, found)
            
        # Si la región se intercepta con la rama derecha (valores > split_value)
        if max_val > node.split_value:
             self.search_kd_tree(node.right, region, found)

    def closest_point(self, target):
        """Return the nearest point stored in the KD-Tree to the given target (x, y).

        Uses a recursive nearest-neighbour search. Returns the point tuple or
        `None` if the tree is empty.
        """
        if self.root is None:
            return None

        tx, ty = target
        best = {'point': None, 'dist': float('inf')}  # store squared distance

        def recur(node):
            if node is None:
                return

            # If it's a leaf node, check its point
            if node.point is not None:
                px, py = node.point
                d2 = (px - tx) ** 2 + (py - ty) ** 2
                if d2 < best['dist']:
                    best['point'] = node.point
                    best['dist'] = d2
                return

            # Internal node: choose branch based on splitting axis/value
            axis = node.split_axis
            coord = tx if axis == 0 else ty

            # Decide which subtree is nearer
            if coord <= node.split_value:
                near, far = node.left, node.right
            else:
                near, far = node.right, node.left

            # Search nearer side first
            if near is not None:
                recur(near)

            # If hypersphere crosses splitting plane, search far side
            plane_dist2 = (coord - node.split_value) ** 2
            if plane_dist2 <= best['dist']:
                if far is not None:
                    recur(far)

        recur(self.root)
        return best['point']
    
if __name__ == "__main__":
    # Demo/ejemplo: generación de puntos, construcción del árbol y guardado de figura.
    random.seed(42) # Para reproducibilidad
    points_200 = [(random.uniform(-10, 10), random.uniform(-10, 10)) for _ in range(200)]

    # Construir el árbol
    tree = KDTree(points_200)

    # --- Consultas y Gráficas (ejemplo) ---
    queries = [
        ([-1, 1], [-2, 2]),
        ([-2, 1], [3, 5]),
        ([-7, 0], [-6, 4]),
        ([-2, 2], [-3, 3]),
        ([-7, 5], [-3, 1])
    ]

    # Configuración de subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    # Graficar todos los puntos inicialmente (sin filtro)
    ax = axes[0]
    x_vals, y_vals = zip(*points_200)
    ax.scatter(x_vals, y_vals, c='lightgray', label='Puntos')
    ax.set_title("Totalidad de Puntos (200)")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.grid(True)

    # Ejecutar búsquedas y graficar
    for i, (xr, yr) in enumerate(queries):
        ax = axes[i+1]
        
        # Buscar
        found = tree.search(xr, yr)
        
        # Graficar puntos de fondo
        ax.scatter(x_vals, y_vals, c='lightgray', alpha=0.5)
        
        # Graficar puntos encontrados
        if found:
            fx, fy = zip(*found)
            ax.scatter(fx, fy, c='red', label='Encontrados')
        
        # Dibujar rectángulo de búsqueda
        width = xr[1] - xr[0]
        height = yr[1] - yr[0]
        rect = patches.Rectangle((xr[0], yr[0]), width, height, linewidth=2, edgecolor='blue', facecolor='none')
        ax.add_patch(rect)
        
        ax.set_title(f"Rango: X{xr}, Y{yr}\nEncontrados: {len(found)}")
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.grid(True)

    plt.tight_layout()
    plt.savefig('kd_tree_results.png')