# -*- coding: utf-8 -*-
class Rectangle:
    """Rectangle pour représenter une région"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        """Vérifie si un point est à l'intérieur du rectangle"""
        return (self.x <= point[0] < self.x + self.width and
                self.y <= point[1] < self.y + self.height)

    def intersects(self, range_rect):
        """Vérifie si ce rectangle intersecte un autre rectangle"""
        return not (range_rect.x + range_rect.width < self.x or
                    range_rect.x > self.x + self.width or
                    range_rect.y + range_rect.height < self.y or
                    range_rect.y > self.y + self.height)


class Quadtree:
    """Structure de données Quadtree pour optimiser la détection de collision"""

    def __init__(self, boundary, capacity=4, max_depth=10, depth=0):
        """
        Initialise un Quadtree

        Args:
            boundary (Rectangle): Limites du Quadtree
            capacity (int): Nombre max d'éléments avant subdivision
            max_depth (int): Profondeur maximale de l'arbre
            depth (int): Profondeur actuelle du nœud
        """
        self.boundary = boundary
        self.capacity = capacity
        self.max_depth = max_depth
        self.depth = depth
        self.points = []  # Objets dans ce nœud
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def insert(self, point, data=None):
        """
        Insère un point dans le Quadtree

        Args:
            point (list): Position [x, y]
            data (any): Données associées au point (e.g., balle)

        Returns:
            bool: True si l'insertion a réussi, False sinon
        """
        # Si le point est hors des limites, ne pas l'insérer
        if not self.boundary.contains(point):
            return False

        # Si nous avons de la place et pas subdivisé, ajouter le point ici
        if len(self.points) < self.capacity and not self.divided and self.depth < self.max_depth:
            self.points.append((point, data))
            return True

        # Subdiviser si nécessaire
        if not self.divided and self.depth < self.max_depth:
            self.subdivide()

        # Si déjà subdivisé ou vient d'être subdivisé, insérer dans les sous-arbres appropriés
        if self.divided:
            if self.northwest.insert(point, data): return True
            if self.northeast.insert(point, data): return True
            if self.southwest.insert(point, data): return True
            if self.southeast.insert(point, data): return True

        # Si on atteint ce point, insérer même si la capacité est dépassée
        if self.depth >= self.max_depth:
            self.points.append((point, data))
            return True

        return False

    def subdivide(self):
        """Divise le Quadtree en quatre quadrants"""
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width / 2
        h = self.boundary.height / 2
        next_depth = self.depth + 1

        # Créer les sous-arbres
        nw = Rectangle(x, y, w, h)
        ne = Rectangle(x + w, y, w, h)
        sw = Rectangle(x, y + h, w, h)
        se = Rectangle(x + w, y + h, w, h)

        self.northwest = Quadtree(nw, self.capacity, self.max_depth, next_depth)
        self.northeast = Quadtree(ne, self.capacity, self.max_depth, next_depth)
        self.southwest = Quadtree(sw, self.capacity, self.max_depth, next_depth)
        self.southeast = Quadtree(se, self.capacity, self.max_depth, next_depth)

        self.divided = True

        # Redistribuer les points existants
        points_copy = self.points.copy()
        self.points = []
        for point, data in points_copy:
            self.insert(point, data)

    def query_range(self, range_rect, found=None):
        """
        Trouve tous les points dans une région donnée

        Args:
            range_rect (Rectangle): Région à vérifier
            found (list): Liste pour accumuler les résultats

        Returns:
            list: Liste de tuples (point, data) dans la région
        """
        if found is None:
            found = []

        # Sortir si la région ne chevauche pas ce quadrant
        if not self.boundary.intersects(range_rect):
            return found

        # Vérifier les points dans ce nœud
        for point, data in self.points:
            if range_rect.contains(point):
                found.append((point, data))

        # Si subdivisé, vérifier dans les sous-quadrants
        if self.divided:
            self.northwest.query_range(range_rect, found)
            self.northeast.query_range(range_rect, found)
            self.southwest.query_range(range_rect, found)
            self.southeast.query_range(range_rect, found)

        return found

    def query_radius(self, center, radius, found=None):
        """
        Trouve tous les points dans un cercle donné

        Args:
            center (list): Centre du cercle [x, y]
            radius (float): Rayon du cercle
            found (list): Liste pour accumuler les résultats

        Returns:
            list: Liste de tuples (point, data) dans le cercle
        """
        if found is None:
            found = []

        # Créer un rectangle englobant le cercle
        r = Rectangle(center[0] - radius, center[1] - radius, radius * 2, radius * 2)

        # Si le rectangle ne chevauche pas ce quadrant, sortir
        if not self.boundary.intersects(r):
            return found

        # Vérifier les points dans ce nœud
        for point, data in self.points:
            dx = center[0] - point[0]
            dy = center[1] - point[1]
            distance_squared = dx * dx + dy * dy
            if distance_squared <= radius * radius:
                found.append((point, data))

        # Si subdivisé, vérifier dans les sous-quadrants
        if self.divided:
            self.northwest.query_radius(center, radius, found)
            self.northeast.query_radius(center, radius, found)
            self.southwest.query_radius(center, radius, found)
            self.southeast.query_radius(center, radius, found)

        return found

    def clear(self):
        """Vide l'arbre"""
        self.points = []
        if self.divided:
            self.northwest.clear()
            self.northeast.clear()
            self.southwest.clear()
            self.southeast.clear()
            self.divided = False
            self.northwest = None
            self.northeast = None
            self.southwest = None
            self.southeast = None