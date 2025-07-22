# -*- coding: utf-8 -*-
import pygame
import math


class Cercle:
    def __init__(self, position, rayon, couleur="black", epaisseur=2, life=20, angle_ouverture=0, angle_rotation=0,
                 vitesse_rotation=0):
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

        # Attributs pour le prérendu
        self.surface_prerendue = None
        self.rect_surface = None
        self.derniers_params = {}
        self.derniere_life_ratio = -1  # Pour détecter les changements de couleur basés sur life

    def mettre_a_jour(self, dt):
        """Met à jour la rotation de l'arc"""
        rotation_modifiee = False

        if self.vitesse_rotation != 0:
            self.angle_rotation += self.vitesse_rotation * dt
            self.angle_rotation = self.angle_rotation % 360  # Garder l'angle entre 0 et 360
            rotation_modifiee = True

        # Si la rotation a changé, il faut recréer la surface prérendue
        if rotation_modifiee and self.surface_prerendue is not None:
            # On indique que la surface doit être recréée en la mettant à None
            self.surface_prerendue = None

    def est_dans_ouverture(self, position_balle, rayon_balle=0):
        """Vérifie si une balle est entièrement dans l'ouverture (partie invisible) de l'arc"""
        # Méthode inchangée - déjà robuste avec les divisions par zéro
        # [code existant inchangé]
        if self.angle_ouverture == 0:
            return False  # Pas d'ouverture pour un cercle complet

        # Vecteur du centre du cercle au point
        dx = position_balle[0] - self.position[0]
        dy = position_balle[1] - self.position[1]

        # Éviter la division par zéro
        if abs(dx) < 0.0001 and abs(dy) < 0.0001:
            return False  # Balle au centre du cercle = pas entièrement dans l'ouverture

        distance_centre = math.sqrt(dx * dx + dy * dy)

        # Calculer l'angle du centre de la balle
        angle_centre_balle = math.degrees(math.atan2(dy, dx))
        angle_centre_balle = (angle_centre_balle + 360) % 360

        # Calculer l'angle que couvre la balle depuis le centre du cercle
        # Avec gestion du cas où distance_centre est très petite
        if rayon_balle > 0 and distance_centre > rayon_balle:
            # Sinus limité à 1.0 pour éviter les erreurs numériques
            sin_value = min(1.0, rayon_balle / max(0.0001, distance_centre))
            angle_couverture_balle = math.degrees(math.asin(sin_value))
        else:
            # Si la balle est très proche du centre ou plus grande que la distance
            # On considère un angle large pour être sûr
            angle_couverture_balle = 90.0

        # Calculer les angles de l'ouverture
        angle_ouverture_debut = (self.angle_rotation - self.angle_ouverture / 2) % 360
        angle_ouverture_fin = (self.angle_rotation + self.angle_ouverture / 2) % 360

        # Calculer les angles extrêmes de la balle
        angle_balle_min = (angle_centre_balle - angle_couverture_balle) % 360
        angle_balle_max = (angle_centre_balle + angle_couverture_balle) % 360

        # Fonction pour vérifier si un angle est dans l'ouverture
        def angle_dans_ouverture(angle):
            if angle_ouverture_debut <= angle_ouverture_fin:
                return angle_ouverture_debut <= angle <= angle_ouverture_fin
            else:  # L'ouverture traverse 0°
                return angle >= angle_ouverture_debut or angle <= angle_ouverture_fin

        # Vérifier si TOUTE la balle est dans l'ouverture
        if angle_balle_min <= angle_balle_max:
            # Cas normal : la balle ne traverse pas 0°
            return angle_dans_ouverture(angle_balle_min) and angle_dans_ouverture(angle_balle_max)
        else:
            # Cas où la balle traverse 0° : vérifier que tout l'arc couvert est dans l'ouverture
            points_a_verifier = 5
            for i in range(points_a_verifier + 1):
                if i == 0:
                    angle_test = angle_balle_min
                elif i == points_a_verifier:
                    angle_test = angle_balle_max
                else:
                    # Points intermédiaires en traversant 0°
                    angle_test = (angle_balle_min + (
                            360 + angle_balle_max - angle_balle_min) * i / points_a_verifier) % 360

                if not angle_dans_ouverture(angle_test):
                    return False
            return True

    def a_change(self):
        """Vérifie si le cercle a changé depuis le dernier prérendu"""
        # Calculer le ratio actuel de vie
        ratio = max(0, min(1, self.life / self.life_max))

        # Vérifier si l'un des paramètres a changé
        return (not self.derniers_params or
                self.derniers_params['rayon'] != self.rayon or
                self.derniers_params['epaisseur'] != self.epaisseur or
                self.derniers_params['angle_rotation'] != self.angle_rotation or
                self.derniers_params['angle_ouverture'] != self.angle_ouverture or
                abs(self.derniere_life_ratio - ratio) > 0.05)  # 5% de changement de couleur

    def creer_surface_prerendue(self):
        """Crée une surface prérendue pour ce cercle"""
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

            # Stocker comme surface prérendue
            self.surface_prerendue = cercle_lisse
            self.rect_surface = self.surface_prerendue.get_rect(
                center=(self.position[0], self.position[1])
            )
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

            # Réduire et stocker
            arc_lisse = pygame.transform.smoothscale(temp_surface,
                                                     (self.rayon * 2 + self.epaisseur * 2,
                                                      self.rayon * 2 + self.epaisseur * 2))

            # Stocker comme surface prérendue
            self.surface_prerendue = arc_lisse
            self.rect_surface = self.surface_prerendue.get_rect(
                center=(self.position[0], self.position[1])
            )

        # Mémoriser les paramètres utilisés pour ce rendu
        self.derniers_params = {
            'rayon': self.rayon,
            'epaisseur': self.epaisseur,
            'angle_rotation': self.angle_rotation,
            'angle_ouverture': self.angle_ouverture,
        }
        self.derniere_life_ratio = ratio

    def afficher(self, surface):
        """Affiche le cercle sur la surface, en utilisant la surface prérendue si possible"""
        # Si la surface prérendue n'existe pas ou si le cercle a changé, recréer la surface
        if self.surface_prerendue is None or self.a_change():
            self.creer_surface_prerendue()

        # Afficher la surface prérendue
        if self.angle_ouverture == 0:
            surface.blit(self.surface_prerendue, (self.position[0] - self.rayon, self.position[1] - self.rayon))
        else:
            surface.blit(self.surface_prerendue, (self.position[0] - self.rayon - self.epaisseur,
                                                  self.position[1] - self.rayon - self.epaisseur))