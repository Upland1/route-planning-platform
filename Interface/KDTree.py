import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Node:
    def __init__(self, point=None, left=None, right=None, split_axis=None, split_value=None):
        self.point = point          # If value is leaf
        self.left = left            # Left children
        self.right = right          # Right children
        self.split_axis = split_axis # Dividing axis (0=x, 1=y)
        self.split_value = split_value # Median value

class KDTree:
    def __init__(self, points):
        self.root = self.build_kd_tree(points, depth=0)

    def build_kd_tree(self, points, depth):
        # Normalize input
        points = [tuple(p) for p in points]

        if not points:
            return None
        
        k = 2 # 2D
        axis = depth % k # Alternate axis: even->x, odd->y 
        
        # Base case: If only one point, return leaf node
        if len(points) == 1:
            return Node(point=points[0])
        
        # Sort points and find median
        points.sort(key=lambda x: x[axis])
        mid = len(points) // 2
        median_point = points[mid]
        
        # Dividing value is the median point coordinate point
        split_value = median_point[axis]
        
        # Divide sets
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
        if node is None:
            return

        # If it's leaf
        if node.point is not None:
            px, py = node.point
            if (region['x'][0] <= px <= region['x'][1] and 
                region['y'][0] <= py <= region['y'][1]):
                found.append(node.point)
            return

        # Region Intersection Logic
        axis_name = 'x' if node.split_axis == 0 else 'y'
        min_val, max_val = region[axis_name]
        
        # If region intercepts left branch 
        if min_val <= node.split_value:
            self.search_kd_tree(node.left, region, found)
            
        # If region intercepts right branch 
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

    def query(self, target):
        """
        Return a tuple (distance, index) for the nearest neighbour.
        """
        if self.root is None:
            return (None, None)

        tx, ty = target
        best = {'point': None, 'dist': float('inf')}

        def recur(node):
            if node is None:
                return

            if node.point is not None:
                p = node.point
                px, py = p[0], p[1]
                d2 = (px - tx) ** 2 + (py - ty) ** 2
                if d2 < best['dist']:
                    best['point'] = p
                    best['dist'] = d2
                return

            axis = node.split_axis
            coord = tx if axis == 0 else ty

            if coord <= node.split_value:
                near, far = node.left, node.right
            else:
                near, far = node.right, node.left

            if near is not None:
                recur(near)

            plane_dist2 = (coord - node.split_value) ** 2
            if plane_dist2 <= best['dist']:
                if far is not None:
                    recur(far)

        recur(self.root)

        if best['point'] is None:
            return (None, None)

        idx = None
        try:
            if len(best['point']) >= 3:
                idx = best['point'][2]
        except Exception:
            idx = None

        return (best['dist'] ** 0.5, idx)
    