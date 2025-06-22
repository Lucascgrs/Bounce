# -*- coding: utf-8 -*-
import pygame
import math


class Cercle:
    def __init__(self, position, rayon, couleur="black", epaisseur=2, life=20,
                 angle_ouverture=0, angle_rotation=0, vitesse_rotation=0):
        self.position = position
        self.rayon = rayon
        self.couleur = couleur
        self.epaisseur = epaisseur
        self.life = life
        self.life_max = life

        # Paramètres pour les arcs
        self.angle_ouverture = angle_ouverture  # Angle d'ouverture en degrés (0 = cercle complet, >0 = arc avec ouverture)
        self.angle_rotation = angle_rotation  # Angle de rotation actuel en degrés
        self.vitesse_rotation = vitesse_rotation  # Vitesse de rotation en degrés/seconde

    def mettre_a_jour(self, dt):
        """Met à jour la rotation de l'arc"""
        if self.vitesse_rotation != 0:
            self.angle_rotation += self.vitesse_rotation * dt
            self.angle_rotation = self.angle_rotation % 360  # Garder l'angle entre 0 et 360

    def est_dans_ouverture(self, position_balle):
        """Vérifie si une position est dans l'ouverture (partie invisible) de l'arc"""
        if self.angle_ouverture == 0:
            return False  # Pas d'ouverture pour un cercle complet

        # Calculer l'angle de la balle par rapport au centre de l'arc
        dx = position_balle[0] - self.position[0]
        dy = position_balle[1] - self.position[1]
        angle_balle = math.degrees(math.atan2(dy, dx))

        # Normaliser l'angle entre 0 et 360
        angle_balle = (angle_balle + 360) % 360

        # Calculer les angles de début et fin de l'ouverture (partie invisible)
        angle_ouverture_debut = (self.angle_rotation - self.angle_ouverture / 2) % 360
        angle_ouverture_fin = (self.angle_rotation + self.angle_ouverture / 2) % 360

        # Vérifier si l'angle de la balle est dans l'ouverture
        if angle_ouverture_debut <= angle_ouverture_fin:
            return angle_ouverture_debut <= angle_balle <= angle_ouverture_fin
        else:  # L'ouverture traverse 0°
            return angle_balle >= angle_ouverture_debut or angle_balle <= angle_ouverture_fin

    def afficher(self, surface):
        # Calcul de la proportion de vie restante (entre 0 et 1)
        ratio = max(0, min(1, self.life / self.life_max))

        # Interpolation de vert à rouge
        r = int(255 * (1 - ratio))  # de 0 à 255
        g = int(255 * ratio)  # de 255 à 0
        b = 0
        couleur = (r, g, b)

        if self.angle_ouverture == 0:
            # Dessiner un cercle complet (ancien comportement)
            # Surface temporaire plus grande pour lisser
            scale_factor = 4
            rayon_grand = self.rayon * scale_factor
            taille_surface = rayon_grand * 2

            # Création de la surface temporaire avec canal alpha
            temp_surface = pygame.Surface((taille_surface, taille_surface), pygame.SRCALPHA)
            centre = (rayon_grand, rayon_grand)

            # Dessin du cercle sur la surface temporaire
            pygame.draw.circle(temp_surface, (*couleur, 255), centre, rayon_grand, self.epaisseur * scale_factor)

            # Réduction de la surface pour un effet lissé
            cercle_lisse = pygame.transform.smoothscale(temp_surface, (self.rayon * 2, self.rayon * 2))

            # Affichage du cercle sur la surface principale
            surface.blit(cercle_lisse, (self.position[0] - self.rayon, self.position[1] - self.rayon))
        else:
            # Dessiner un arc (la partie visible = 360° - angle_ouverture)
            angle_visible = 360 - self.angle_ouverture

            # Convertir les angles en radians pour la partie VISIBLE
            angle_debut_visible = math.radians(self.angle_rotation + self.angle_ouverture / 2)
            angle_fin_visible = math.radians(self.angle_rotation + self.angle_ouverture / 2 + angle_visible)

            # Créer une surface temporaire pour dessiner l'arc avec anti-aliasing
            scale_factor = 4
            rayon_grand = self.rayon * scale_factor
            epaisseur_grande = self.epaisseur * scale_factor
            taille_surface = rayon_grand * 2 + epaisseur_grande * 2

            temp_surface = pygame.Surface((taille_surface, taille_surface), pygame.SRCALPHA)
            centre_temp = (taille_surface // 2, taille_surface // 2)

            # Dessiner l'arc en utilisant des lignes pour un meilleur rendu
            num_segments = max(10, int(angle_visible / 2))  # Plus de segments pour les gros arcs
            angle_step = (angle_fin_visible - angle_debut_visible) / num_segments

            for i in range(num_segments):
                angle1 = angle_debut_visible + i * angle_step
                angle2 = angle_debut_visible + (i + 1) * angle_step

                # Points de l'arc externe
                x1_ext = centre_temp[0] + (rayon_grand + epaisseur_grande // 2) * math.cos(angle1)
                y1_ext = centre_temp[1] + (rayon_grand + epaisseur_grande // 2) * math.sin(angle1)
                x2_ext = centre_temp[0] + (rayon_grand + epaisseur_grande // 2) * math.cos(angle2)
                y2_ext = centre_temp[1] + (rayon_grand + epaisseur_grande // 2) * math.sin(angle2)

                # Points de l'arc interne
                x1_int = centre_temp[0] + (rayon_grand - epaisseur_grande // 2) * math.cos(angle1)
                y1_int = centre_temp[1] + (rayon_grand - epaisseur_grande // 2) * math.sin(angle1)
                x2_int = centre_temp[0] + (rayon_grand - epaisseur_grande // 2) * math.cos(angle2)
                y2_int = centre_temp[1] + (rayon_grand - epaisseur_grande // 2) * math.sin(angle2)

                # Dessiner le segment comme un polygone
                points = [(x1_ext, y1_ext), (x2_ext, y2_ext), (x2_int, y2_int), (x1_int, y1_int)]
                pygame.draw.polygon(temp_surface, (*couleur, 255), points)

            # Réduire et afficher
            arc_lisse = pygame.transform.smoothscale(temp_surface,
                                                     (self.rayon * 2 + self.epaisseur * 2,
                                                      self.rayon * 2 + self.epaisseur * 2))

            surface.blit(arc_lisse, (self.position[0] - self.rayon - self.epaisseur,
                                     self.position[1] - self.rayon - self.epaisseur))