# -*- coding: utf-8 -*-
import pygame
import os


class SurfaceManager:
    """Gestionnaire de surfaces pour réduire les créations temporaires et réutiliser les ressources"""

    _instance = None

    @staticmethod
    def get_instance():
        """Accès singleton au gestionnaire"""
        if SurfaceManager._instance is None:
            SurfaceManager._instance = SurfaceManager()
        return SurfaceManager._instance

    def __init__(self):
        self.image_cache = {}  # Cache pour les images chargées
        self.circle_cache = {}  # Cache pour les cercles dessinés
        self.temp_surfaces = {}  # Surfaces temporaires réutilisables

    def get_circle_surface(self, taille, couleur, contour=None):
        """Obtient une surface de cercle du cache ou en crée une nouvelle"""
        # Créer une clé unique pour ce cercle
        contour_str = f"_{contour[0]}_{contour[1]}" if contour else ""
        if isinstance(couleur, list):
            color_str = f"{couleur[0]}_{couleur[1]}_{couleur[2]}"
        else:
            color_str = str(couleur)
        key = f"circle_{taille}_{color_str}{contour_str}"

        # Vérifier si elle existe déjà en cache
        if key in self.circle_cache:
            return self.circle_cache[key]

        # Sinon créer une nouvelle surface
        diameter = int(taille * 2)
        circle_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        circle_surface.fill((0, 0, 0, 0))  # Transparent

        # Dessiner le cercle
        pygame.draw.circle(circle_surface, couleur, (taille, taille), taille)

        # Ajouter le contour si nécessaire
        if contour:
            pygame.draw.circle(circle_surface, contour[0],
                               (taille, taille), taille, contour[1])

        # Mettre en cache et retourner
        self.circle_cache[key] = circle_surface
        return circle_surface

    def get_image(self, path):
        """Charge une image depuis un chemin avec mise en cache"""
        if path is None:
            return None

        # Utiliser le chemin absolu comme clé
        abs_path = os.path.abspath(path) if path else None

        # Retourner depuis le cache si disponible
        if abs_path in self.image_cache:
            return self.image_cache[abs_path]

        # Sinon charger et mettre en cache
        try:
            image = pygame.image.load(path).convert_alpha()
            self.image_cache[abs_path] = image
            return image
        except Exception as e:
            print(f"Erreur lors du chargement de l'image {path}: {e}")
            return None

    def get_scaled_image(self, path, size):
        """Obtient une image redimensionnée avec mise en cache"""
        if path is None:
            return None

        abs_path = os.path.abspath(path) if path else None
        key = f"{abs_path}_{size[0]}_{size[1]}"

        # Vérifier si cette version existe en cache
        if key in self.image_cache:
            return self.image_cache[key]

        # Charger l'image de base
        base_image = self.get_image(path)
        if base_image is None:
            return None

        # Redimensionner et mettre en cache
        try:
            scaled = pygame.transform.smoothscale(base_image, size)
            self.image_cache[key] = scaled
            return scaled
        except ValueError:
            # Fallback au scale standard
            try:
                scaled = pygame.transform.scale(base_image, size)
                self.image_cache[key] = scaled
                return scaled
            except Exception as e:
                print(f"Erreur lors du redimensionnement de l'image {path}: {e}")
                return base_image

    def get_temp_surface(self, size, flags=pygame.SRCALPHA):
        """Obtient une surface temporaire réutilisable"""
        key = f"{size[0]}x{size[1]}_{flags}"

        if key in self.temp_surfaces:
            # Réinitialiser la surface existante
            surface = self.temp_surfaces[key]
            surface.fill((0, 0, 0, 0) if flags & pygame.SRCALPHA else (0, 0, 0))
            return surface

        # Créer une nouvelle surface
        surface = pygame.Surface(size, flags)
        if flags & pygame.SRCALPHA:
            surface.fill((0, 0, 0, 0))

        # Stocker pour réutilisation future
        self.temp_surfaces[key] = surface
        return surface

    def cleanup(self):
        """Libère les ressources non essentielles"""
        # Conserver uniquement les images les plus utilisées
        if len(self.temp_surfaces) > 20:  # Limite arbitraire
            self.temp_surfaces.clear()