# -*- coding: utf-8 -*-
import pygame


class Cercle:
    def __init__(self, position, rayon, couleur="black", epaisseur=2, life=20):
        self.position = position
        self.rayon = rayon
        self.couleur = couleur
        self.epaisseur = epaisseur
        self.life = life
        self.life_max = life

    def afficher(self, surface):
        # Calcul de la proportion de vie restante (entre 0 et 1)
        ratio = max(0, min(1, self.life / self.life_max))

        # Interpolation de vert à rouge
        r = int(255 * (1 - ratio))  # de 0 à 255
        g = int(255 * ratio)        # de 255 à 0
        b = 0
        couleur = (r, g, b)

        # Surface temporaire plus grande pour lisser
        scale_factor = 4
        rayon_grand = self.rayon * scale_factor
        taille_surface = rayon_grand * 2

        temp_surface = pygame.Surface((taille_surface, taille_surface), pygame.SRCALPHA)
        centre = (rayon_grand, rayon_grand)

        # Dessin du cercle sur la surface temporaire
        pygame.draw.circle(temp_surface, couleur, centre, rayon_grand, self.epaisseur * scale_factor)

        # Réduction de la surface pour un effet lissé
        cercle_lisse = pygame.transform.smoothscale(temp_surface, (self.rayon * 2, self.rayon * 2))

        # Affichage du cercle sur la surface principale
        surface.blit(cercle_lisse, (self.position[0] - self.rayon, self.position[1] - self.rayon))
