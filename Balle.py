# -*- coding: utf-8 -*-
import pygame
import numpy as np


class Balle:
    def __init__(self, taille, image=None, couleur="red", contour=None, position=(100, 100), vitesse=(0, 0), gravite=0.1):
        self.taille = taille
        self.image_path = image
        self.couleur = couleur
        self.contour = contour
        self.position = list(position)
        self.vitesse = list(vitesse)
        self.gravite = gravite * 60**2
        self.direction = (1, 1)

        if self.image_path:
            self.image = pygame.image.load(self.image_path)
            self.image = pygame.transform.scale(self.image, (taille * 2, taille * 2))
        else:
            self.image = None

    def mettre_a_jour(self, dt):
        # Ajoute la gravité à la vitesse verticale
        self.vitesse[1] += self.gravite * dt
        # Met à jour la position en fonction de la vitesse
        self.position[0] += self.vitesse[0] * dt
        self.position[1] += self.vitesse[1] * dt

    def afficher(self, surface):
        if self.image:
            # S'assurer que l'image est en 32 bits avec alpha
            if self.image.get_bitsize() not in (24, 32):
                self.image = self.image.convert_alpha()

            image_redim = pygame.transform.smoothscale(self.image, (self.taille * 2, self.taille * 2))

            masque = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)
            pygame.draw.circle(masque, (255, 255, 255, 255), (self.taille, self.taille), self.taille)

            image_ronde = image_redim.copy()
            image_ronde.blit(masque, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            rect = image_ronde.get_rect(center=self.position)
            surface.blit(image_ronde, rect)
        else:
            pygame.draw.circle(surface, self.couleur, self.position, self.taille)

    def rebondir(self, cercle, facteur_vitesse=1.01):
        centre_cercle = cercle.position
        rayon_cercle = cercle.rayon

        direction_x = self.position[0] - centre_cercle[0]
        direction_y = self.position[1] - centre_cercle[1]
        direction = (direction_x, direction_y)

        distance = np.linalg.norm(direction)

        epaisseur_contour = self.contour[1] if self.contour else 0
        rayon_visuel_balle = self.taille + epaisseur_contour / 2

        if distance + rayon_visuel_balle >= rayon_cercle:

            cercle.life -= 1

            if distance == 0:
                direction = np.array([1.0, 0.0])  # direction arbitraire pour éviter division par 0
                distance = 1.0

            normal = direction / distance

            # Calcul du rebond (réflexion du vecteur vitesse par rapport à la normale)
            vitesse_vec = np.array(self.vitesse, dtype=float)
            self.vitesse = list(vitesse_vec - 2 * np.dot(vitesse_vec, normal) * normal * facteur_vitesse)

            # Repositionner la balle juste à l'intérieur du cercle
            self.position = list(centre_cercle + normal * (rayon_cercle - self.taille))

    def collision_avec_balle(self, autre_balle, coef_restitution=0.02):
        dx = self.position[0] - autre_balle.position[0]
        dy = self.position[1] - autre_balle.position[1]
        distance = np.sqrt(dx ** 2 + dy ** 2)

        if distance < self.taille + autre_balle.taille:
            normal = np.array([dx, dy]) / distance if distance != 0 else np.array([1.0, 0.0])

            v1 = np.array(self.vitesse)
            v2 = np.array(autre_balle.vitesse)
            vitesse_rel = v1 - v2
            vitesse_normale = np.dot(vitesse_rel, normal)

            if vitesse_normale < 0:
                # application du coefficient de restitution ici
                impulse = (1 + coef_restitution) * vitesse_normale
                self.vitesse = (v1 - impulse * normal).tolist()
                autre_balle.vitesse = (v2 + impulse * normal).tolist()

            overlap = self.taille + autre_balle.taille - distance
            correction = normal * (overlap / 2)
            self.position += correction
            autre_balle.position -= correction
