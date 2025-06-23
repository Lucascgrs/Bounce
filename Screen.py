# -*- coding: utf-8 -*-
import pygame
from Balle import Balle
from Cercle import Cercle
from Particule import Particule, StyleExplosion
import random
import math


class Screen:
    def __init__(self, taille=(800, 600), couleur_fond="black", titre="Bounce",
                 collision_sur_contact=True, brisure_dans_ouverture=False, marge_suppression=100):
        pygame.init()
        self.taille = taille
        self.couleur_fond = couleur_fond
        self.titre = titre
        self.ecran = pygame.display.set_mode(taille)
        pygame.display.set_caption(titre)
        self.horloge = pygame.time.Clock()
        self.objets = []
        self.particules = []
        self.en_cours = True
        self.marge_suppression = marge_suppression

        # Paramètres de collision globaux
        self.collision_sur_contact = collision_sur_contact
        self.brisure_dans_ouverture = brisure_dans_ouverture

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def retirer_objet(self, objet):
        if objet in self.objets:
            self.objets.remove(objet)

    def retirer_objets_hors_ecran(self):
        """Retire les objets qui sont sortis de l'écran avec une marge"""
        objets_a_retirer = []

        for obj in self.objets:
            if hasattr(obj, 'position'):
                x, y = obj.position

                # Obtenir la taille de l'objet (différents attributs selon le type)
                taille = 0
                if hasattr(obj, 'taille'):
                    taille = obj.taille
                elif hasattr(obj, 'rayon'):
                    taille = obj.rayon

                # Vérifier si l'objet est complètement hors de l'écran avec marge
                if (x + taille < -self.marge_suppression or
                        x - taille > self.taille[0] + self.marge_suppression or
                        y + taille < -self.marge_suppression or
                        y - taille > self.taille[1] + self.marge_suppression):
                    objets_a_retirer.append(obj)

        # Retirer les objets identifiés
        for obj in objets_a_retirer:
            self.retirer_objet(obj)

        return len(objets_a_retirer)

    def boucle(self, fps=60, duree=None):
        import time
        debut = time.time()

        while self.en_cours:
            dt = self.horloge.tick(fps) / 1000.0

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.en_cours = False

            # Vérification de la durée
            if duree and (time.time() - debut) >= duree:
                self.en_cours = False

            # Effacer l'écran
            self.ecran.fill(self.couleur_fond)

            # Séparer les objets par type
            balles = [obj for obj in self.objets if isinstance(obj, Balle)]
            cercles = [obj for obj in self.objets if isinstance(obj, Cercle)]

            # Mise à jour des objets
            for obj in self.objets:
                if hasattr(obj, 'mettre_a_jour'):
                    obj.mettre_a_jour(dt)

            # Retirer les objets hors écran
            objets_retires = self.retirer_objets_hors_ecran()

            # Gestion des collisions entre balles
            for i in range(len(balles)):
                for j in range(i + 1, len(balles)):
                    balles[i].collision_avec_balle(balles[j])

            # Gestion des collisions balle-cercle avec nouvelle logique
            for balle in balles:
                for cercle in cercles[:]:
                    collision_point = self._gerer_collision_balle_cercle(balle, cercle)

                    if cercle.life <= 0:
                        self._creer_explosion(cercle, collision_point)
                        # Suppression du cercle
                        if cercle in self.objets:
                            self.objets.remove(cercle)
                        if cercle in cercles:
                            cercles.remove(cercle)

            # Affichage des objets
            for obj in self.objets:
                obj.afficher(self.ecran)

            # Mise à jour et affichage des particules
            for particule in self.particules[:]:
                particule.mettre_a_jour(dt)
                particule.afficher(self.ecran)

                # Supprimer les particules expirées
                if particule.vie <= 0:
                    self.particules.remove(particule)

            # Mise à jour de l'affichage
            pygame.display.flip()

        pygame.quit()

    def _est_entierement_dans_ouverture(self, balle, cercle):
        """Vérifie si TOUTE la balle est dans l'ouverture"""
        if cercle.angle_ouverture == 0:
            return False

        # Calculer l'angle du centre de la balle
        dx = balle.position[0] - cercle.position[0]
        dy = balle.position[1] - cercle.position[1]
        distance_centre = math.sqrt(dx * dx + dy * dy)

        if distance_centre == 0:
            return False

        angle_centre_balle = math.degrees(math.atan2(dy, dx))
        angle_centre_balle = (angle_centre_balle + 360) % 360

        # Calculer l'angle que couvre la balle depuis le centre du cercle
        if balle.taille > 0 and distance_centre > 0:
            angle_couverture_balle = math.degrees(math.asin(min(1.0, balle.taille / distance_centre)))
        else:
            angle_couverture_balle = 0

        # Calculer les angles de l'ouverture
        angle_ouverture_debut = (cercle.angle_rotation - cercle.angle_ouverture / 2) % 360
        angle_ouverture_fin = (cercle.angle_rotation + cercle.angle_ouverture / 2) % 360

        # Calculer les angles extrêmes de la balle
        angle_balle_min = (angle_centre_balle - angle_couverture_balle) % 360
        angle_balle_max = (angle_centre_balle + angle_couverture_balle) % 360

        # Fonction pour vérifier si un angle est dans l'ouverture
        def angle_dans_ouverture(angle):
            if angle_ouverture_debut <= angle_ouverture_fin:
                return angle_ouverture_debut <= angle <= angle_ouverture_fin
            else:
                return angle >= angle_ouverture_debut or angle <= angle_ouverture_fin

        # Vérifier si TOUTE la balle est dans l'ouverture
        if angle_balle_min <= angle_balle_max:
            return angle_dans_ouverture(angle_balle_min) and angle_dans_ouverture(angle_balle_max)
        else:
            # Cas où la balle traverse 0°
            points_a_verifier = 5
            for i in range(points_a_verifier + 1):
                if i == 0:
                    angle_test = angle_balle_min
                elif i == points_a_verifier:
                    angle_test = angle_balle_max
                else:
                    angle_test = (angle_balle_min + (
                            360 + angle_balle_max - angle_balle_min) * i / points_a_verifier) % 360

                if not angle_dans_ouverture(angle_test):
                    return False
            return True

    def _gerer_collision_balle_cercle(self, balle, cercle):
        """Gère la collision entre une balle et un cercle selon les paramètres configurés"""
        import numpy as np

        centre_cercle = np.array(cercle.position)
        rayon_cercle = cercle.rayon
        position = np.array(balle.position)
        direction = position - centre_cercle
        distance = np.linalg.norm(direction)

        if distance == 0:
            direction = np.array([1.0, 0.0])
            distance = 1.0

        normal = direction / distance

        # Vérifier si la balle est proche du cercle/arc
        balle_pres_du_cercle = distance + balle.taille >= rayon_cercle

        if balle_pres_du_cercle:
            collision_detectee = False
            point_collision = None

            # Cas 1 : Collision sur contact avec l'arc visible
            if self.collision_sur_contact:
                if cercle.angle_ouverture == 0:
                    # Cercle complet
                    collision_detectee = True
                else:
                    # Arc : vérifier si la balle est ENTIÈREMENT dans l'ouverture
                    # Si elle n'est PAS entièrement dans l'ouverture, alors il y a collision
                    collision_detectee = not self._est_entierement_dans_ouverture(balle, cercle)

                if collision_detectee:
                    # Rebond traditionnel
                    cercle.life -= 1
                    point_collision = centre_cercle + normal * rayon_cercle

                    vitesse_vec = np.array(balle.vitesse, dtype=float)
                    balle.vitesse = list(vitesse_vec - 2 * np.dot(vitesse_vec, normal) * normal)
                    balle.position = list(centre_cercle + normal * (rayon_cercle - balle.taille))

            # Cas 2 : Brisure dans l'ouverture (sans rebond)
            elif self.brisure_dans_ouverture and cercle.angle_ouverture > 0:
                # Utiliser la même logique pour vérifier si la balle traverse l'ouverture
                if self._est_entierement_dans_ouverture(balle, cercle):
                    # La balle traverse l'ouverture : brise le cercle directement
                    cercle.life = 0  # Brise immédiatement
                    point_collision = list(position)  # Point d'impact = position de la balle
                    # Pas de rebond, la balle continue sa trajectoire

            # S'assurer que point_collision est toujours une liste ou None
            if point_collision is not None and hasattr(point_collision, 'tolist'):
                point_collision = point_collision.tolist()

            return point_collision

        return None

    def _creer_explosion(self, cercle, collision_point):
        """Crée l'animation d'explosion pour un cercle détruit"""
        # Choisir un style d'explosion
        style = random.choice([
            StyleExplosion.NORMAL,
            StyleExplosion.MULTICOLOR,
            StyleExplosion.RAINBOW,
            StyleExplosion.FIREWORK
        ])

        # Choisir une palette de couleurs
        palette = random.choice(list(Particule.PALETTES.keys()))

        # Création d'un motif d'explosion sur la circonférence
        num_particules = 75
        for i in range(num_particules):
            # Calcul de la position sur la circonférence
            angle = (i / num_particules) * 2 * math.pi
            pos_x = cercle.position[0] + cercle.rayon * math.cos(angle)
            pos_y = cercle.position[1] + cercle.rayon * math.sin(angle)

            # Ajout d'un léger décalage aléatoire
            pos_x += random.uniform(-2, 2)
            pos_y += random.uniform(-2, 2)

            # La direction initiale des particules suit la forme du cercle
            direction_angle = angle + random.uniform(-0.2, 0.2)

            # Vitesse des particules selon la distance au point d'impact
            if collision_point is not None and len(collision_point) >= 2:
                dx = pos_x - collision_point[0]
                dy = pos_y - collision_point[1]
                distance_impact = math.sqrt(dx * dx + dy * dy)
                vitesse_base = 400 - min(200, distance_impact)
            else:
                vitesse_base = 200

            vitesse_min = vitesse_base
            vitesse_max = vitesse_base * 1.5

            # Création de la particule avec le nouveau système
            particule = Particule(
                position=[pos_x, pos_y],
                style=style,
                palette_name=palette,
                vitesse_min=vitesse_min,
                vitesse_max=vitesse_max,
                direction_angle=direction_angle
            )
            self.particules.append(particule)