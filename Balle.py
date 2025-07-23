# -*- coding: utf-8 -*-
import pygame
import numpy as np
from SurfaceManager import SurfaceManager


class Balle:
    def __init__(self, taille, image=None, couleur="red", contour=None, position=(100, 100), vitesse=(0, 0),
                 coef_gravite=0.5, coef_collision=0.8):
        self.taille = taille
        self.image_path = image
        self.couleur = couleur
        self.contour = contour
        self.position = list(position)
        self.vitesse = list(vitesse)
        self.gravite = 980 * coef_gravite  # ~9.8 m/s² * coefficient
        self.direction = [1, 1]
        self.coef_collision = coef_collision

        # Compteur pour les logs
        self.log_counter = 0

        # Référence au gestionnaire de surfaces
        self.surface_manager = SurfaceManager.get_instance()

        # Image préchargée
        self.image = None

        if self.image_path:
            self._prepare_image()

    def _prepare_image(self):
        """Charge et prépare l'image de la balle en utilisant le cache"""
        try:
            # Charger l'image originale
            original_image = self.surface_manager.get_image(self.image_path)
            if original_image is None:
                return

            # Créer une surface circulaire avec canal alpha
            self.image = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)

            # Redimensionner l'image originale
            scaled_size = int(self.taille * 2.1)  # 5% plus grand
            scaled_image = self.surface_manager.get_scaled_image(self.image_path, (scaled_size, scaled_size))
            if scaled_image is None:
                return

            # Créer un masque circulaire (réutilisable)
            mask_key = f"mask_{int(self.taille * 2)}"
            if mask_key in self.surface_manager.circle_cache:
                mask_surface = self.surface_manager.circle_cache[mask_key]
            else:
                mask_surface = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)
                pygame.draw.circle(mask_surface, (255, 255, 255, 255), (self.taille, self.taille), self.taille)
                self.surface_manager.circle_cache[mask_key] = mask_surface

            # Découper l'image en cercle
            self.image.fill((0, 0, 0, 0))  # Remplir avec du transparent
            self.image.blit(scaled_image,
                            ((self.taille * 2 - scaled_size) // 2,
                             (self.taille * 2 - scaled_size) // 2))

            # Appliquer le masque
            self.image.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        except Exception as e:
            print(f"Erreur lors de la préparation de l'image: {self.image_path}")
            print(f"Détail de l'erreur: {e}")
            self.image = None

    # Le reste des méthodes restent inchangées
    def mettre_a_jour(self, dt):
        # LOG: Position avant mise à jour
        old_position = self.position.copy()

        # Ajoute la gravité à la vitesse verticale
        self.vitesse[1] += self.gravite * dt
        # Met à jour la position en fonction de la vitesse
        self.position[0] += self.vitesse[0] * dt
        self.position[1] += self.vitesse[1] * dt

        # LOG: Détecter les changements brusques de position
        self.log_counter += 1
        if self.log_counter % 120 == 0:  # Toutes les 2 secondes à 60 FPS
            distance_mouvement = ((self.position[0] - old_position[0]) ** 2 + (
                        self.position[1] - old_position[1]) ** 2) ** 0.5

    def collision_avec_balle(self, autre_balle):
        """Gère la collision avec une autre balle de façon stable"""
        import numpy as np

        # Vecteur de distance entre les centres des balles
        delta_position = np.array([
            autre_balle.position[0] - self.position[0],
            autre_balle.position[1] - self.position[1]
        ])

        # Distance entre les centres
        distance_squared = delta_position[0] ** 2 + delta_position[1] ** 2
        somme_rayons = self.taille + autre_balle.taille

        # Test rapide: si les balles sont trop éloignées, sortir immédiatement
        if distance_squared > somme_rayons ** 2:
            return False

        # Éviter division par zéro
        if distance_squared < 0.0001:  # Presque parfaitement superposées
            # Générer une direction aléatoire pour séparer les balles
            import random
            angle = random.uniform(0, 2 * np.pi)
            delta_position = np.array([np.cos(angle), np.sin(angle)])
            distance = 0.01  # Petite valeur non-nulle
        else:
            distance = np.sqrt(distance_squared)

        # Normaliser le vecteur de direction
        direction = delta_position / distance

        # Calcul du chevauchement
        overlap = somme_rayons - distance

        # Si collision
        if overlap > 0:
            # Vecteur vitesse relative
            delta_v = np.array([
                autre_balle.vitesse[0] - self.vitesse[0],
                autre_balle.vitesse[1] - self.vitesse[1]
            ])

            # Produit scalaire pour déterminer si les balles s'approchent
            vitesse_relative_selon_direction = np.dot(delta_v, direction)

            # Ne traiter la collision que si les balles s'approchent
            if vitesse_relative_selon_direction < 0:
                # Masse des balles (proportionnelle au volume)
                m1 = self.taille ** 3
                m2 = autre_balle.taille ** 3
                total_mass = m1 + m2

                # Éviter division par zéro si les masses sont trop faibles
                if total_mass < 0.0001:
                    total_mass = 0.0001

                # Calculer les impulsions
                j = -(1 + 0.8) * vitesse_relative_selon_direction
                j /= (1 / m1 + 1 / m2)

                # Appliquer les forces
                impulsion = j * direction

                # Calculer les nouvelles vitesses
                nouvelle_vitesse1 = np.array(self.vitesse) - (impulsion / m1)
                nouvelle_vitesse2 = np.array(autre_balle.vitesse) + (impulsion / m2)

                # Correction de position pour éviter superposition
                correction = (overlap / 2) * direction
                self.position[0] -= correction[0]
                self.position[1] -= correction[1]
                autre_balle.position[0] += correction[0]
                autre_balle.position[1] += correction[1]

                # Mise à jour des vitesses
                self.vitesse = nouvelle_vitesse1.tolist()
                autre_balle.vitesse = nouvelle_vitesse2.tolist()

                return True

        return False

    def afficher(self, surface):
        """Affiche la balle avec réutilisation des surfaces"""
        # Position pour le blit (coin supérieur gauche)
        pos_x = int(self.position[0] - self.taille)
        pos_y = int(self.position[1] - self.taille)

        if self.image:
            # Utiliser l'image préparée
            surface.blit(self.image, (pos_x, pos_y))

            # Dessiner la bordure si spécifiée
            if self.contour:
                pygame.draw.circle(surface, self.contour[0],
                                   (int(self.position[0]), int(self.position[1])),
                                   self.taille, self.contour[1])
        else:
            # Utiliser une surface de cercle en cache
            circle_surface = self.surface_manager.get_circle_surface(
                self.taille, self.couleur, self.contour)
            surface.blit(circle_surface, (pos_x, pos_y))