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
        # Correction de la gravité pour être indépendante du FPS
        self.gravite = gravite * 3600  # Ajusté pour une meilleure expérience
        self.direction = [1, 1]

        if self.image_path:
            try:
                self.image = pygame.image.load(self.image_path)
                self.image = pygame.transform.scale(self.image, (taille * 2, taille * 2))
            except pygame.error:
                print(f"Erreur lors du chargement de l'image: {self.image_path}")
                self.image = None
        else:
            self.image = None

    def mettre_a_jour(self, dt):
        # Ajoute la gravité à la vitesse verticale
        self.vitesse[1] += self.gravite * dt
        # Met à jour la position en fonction de la vitesse
        self.position[0] += self.vitesse[0] * dt
        self.position[1] += self.vitesse[1] * dt

    def collision_avec_balle(self, autre_balle):
        # Calcul de la distance entre les centres des balles
        dx = autre_balle.position[0] - self.position[0]
        dy = autre_balle.position[1] - self.position[1]
        distance = np.sqrt(dx * dx + dy * dy)

        # Si collision
        if distance < (self.taille + autre_balle.taille):
            # Normalisation du vecteur de collision
            if distance != 0:
                nx = dx / distance
                ny = dy / distance
            else:
                nx, ny = 1, 0

            # Calcul des vitesses relatives
            vx = self.vitesse[0] - autre_balle.vitesse[0]
            vy = self.vitesse[1] - autre_balle.vitesse[1]

            # Produit scalaire
            produit_scalaire = vx * nx + vy * ny

            # Si les balles se rapprochent
            if produit_scalaire < 0:
                # Coefficient de restitution (élasticité de la collision)
                e = 0.8

                # Application de l'impulsion
                j = -(1 + e) * produit_scalaire
                self.vitesse[0] -= j * nx
                self.vitesse[1] -= j * ny
                autre_balle.vitesse[0] += j * nx
                autre_balle.vitesse[1] += j * ny

    def afficher(self, surface):
        if self.image:
            surface.blit(self.image, (self.position[0] - self.taille, self.position[1] - self.taille))
        else:
            pygame.draw.circle(surface, self.couleur, (int(self.position[0]), int(self.position[1])), self.taille)
            if self.contour:
                pygame.draw.circle(surface, self.contour, (int(self.position[0]), int(self.position[1])), self.taille, 2)

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
