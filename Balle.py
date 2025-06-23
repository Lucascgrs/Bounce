# -*- coding: utf-8 -*-
import pygame
import numpy as np


class Balle:
    def __init__(self, taille, image=None, couleur="red", contour=None, position=(100, 100), vitesse=(0, 0), coef_gravite=0.5, coef_collision=0.8):
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

        if self.image_path:
            try:
                # Charger l'image originale
                original_image = pygame.image.load(self.image_path)

                # Convertir l'image en format 32-bit RGBA
                original_image = original_image.convert_alpha()

                # Créer une surface circulaire avec canal alpha
                self.image = pygame.Surface((taille * 2, taille * 2), pygame.SRCALPHA)

                # Redimensionner l'image originale
                scaled_size = int(taille * 2.1)  # 5% plus grand
                try:
                    # Essayer d'abord smoothscale
                    scaled_image = pygame.transform.smoothscale(original_image, (scaled_size, scaled_size))
                except ValueError:
                    # Si smoothscale échoue, utiliser scale normal
                    scaled_image = pygame.transform.scale(original_image, (scaled_size, scaled_size))

                # Créer un masque circulaire
                mask_surface = pygame.Surface((taille * 2, taille * 2), pygame.SRCALPHA)
                pygame.draw.circle(mask_surface, (255, 255, 255, 255), (taille, taille), taille)

                # Découper l'image en cercle
                self.image.fill((0, 0, 0, 0))  # Remplir avec du transparent
                self.image.blit(scaled_image,
                                ((taille * 2 - scaled_size) // 2,
                                 (taille * 2 - scaled_size) // 2))

                # Appliquer le masque
                self.image.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            except Exception as e:
                print(f"Erreur lors du chargement de l'image: {self.image_path}")
                print(f"Détail de l'erreur: {e}")
                self.image = None
        else:
            self.image = None

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
            distance_mouvement = ((self.position[0] - old_position[0]) ** 2 + (self.position[1] - old_position[1]) ** 2) ** 0.5

    def collision_avec_balle(self, autre_balle):
        # LOG: Position avant collision
        old_position = self.position.copy()

        # Calcul de la distance entre les centres des balles
        dx = autre_balle.position[0] - self.position[0]
        dy = autre_balle.position[1] - self.position[1]
        distance = np.sqrt(dx * dx + dy * dy)

        # Si collision
        if distance < (self.taille + autre_balle.taille):
            # Éviter la division par zéro
            if distance == 0:
                distance = 0.001

            # Normalisation du vecteur de collision
            nx = dx / distance
            ny = dy / distance

            # Calcul du vecteur tangent
            tx = -ny
            ty = nx

            # Calcul des vitesses normales
            v1n = self.vitesse[0] * nx + self.vitesse[1] * ny
            v2n = autre_balle.vitesse[0] * nx + autre_balle.vitesse[1] * ny

            # Calcul des vitesses tangentielles (conservées)
            v1t = self.vitesse[0] * tx + self.vitesse[1] * ty
            v2t = autre_balle.vitesse[0] * tx + autre_balle.vitesse[1] * ty

            # Calcul des nouvelles vitesses normales avec coefficient de restitution
            v1n_new = v2n * self.coef_collision
            v2n_new = v1n * autre_balle.coef_collision

            # Reconstitution des vecteurs vitesse
            self.vitesse[0] = v1n_new * nx + v1t * tx
            self.vitesse[1] = v1n_new * ny + v1t * ty
            autre_balle.vitesse[0] = v2n_new * nx + v2t * tx
            autre_balle.vitesse[1] = v2n_new * ny + v2t * ty

            # Correction de la position pour éviter les chevauchements
            recouvrement = (self.taille + autre_balle.taille - distance) / 2
            self.position[0] -= recouvrement * nx
            self.position[1] -= recouvrement * ny
            autre_balle.position[0] += recouvrement * nx
            autre_balle.position[1] += recouvrement * ny

    def afficher(self, surface):
        # Position pour le blit (coin supérieur gauche)
        pos_x = int(self.position[0] - self.taille)
        pos_y = int(self.position[1] - self.taille)

        if self.image:
            # Afficher l'image circulaire
            surface.blit(self.image, (pos_x, pos_y))

            # Dessiner la bordure si spécifiée
            if self.contour:
                pygame.draw.circle(surface, self.contour[0], (int(self.position[0]), int(self.position[1])), self.taille, self.contour[1])
        else:
            # Dessiner un cercle si pas d'image
            pygame.draw.circle(surface, self.couleur, (int(self.position[0]), int(self.position[1])), self.taille)
            if self.contour:
                pygame.draw.circle(surface, self.contour[0], (int(self.position[0]), int(self.position[1])), self.taille, self.contour[1])