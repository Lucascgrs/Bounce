# -*- coding: utf-8 -*-
import pygame
from Balle import Balle
from Cercle import Cercle
from Particule import Particule, StyleExplosion
import random
import math


class Screen:
    def __init__(self, taille=(800, 600), couleur_fond="black", titre="Bounce",
                 collision_sur_contact=True, brisure_dans_ouverture=False):
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

        # Paramètres de collision globaux
        self.collision_sur_contact = collision_sur_contact
        self.brisure_dans_ouverture = brisure_dans_ouverture

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def retirer_objet(self, objet):
        if objet in self.objets:
            self.objets.remove(objet)

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
                    # Arc : vérifier si la balle touche la partie visible de l'arc (PAS l'ouverture)
                    angle_balle = math.degrees(math.atan2(direction[1], direction[0]))
                    angle_balle = (angle_balle + 360) % 360

                    # Calculer les angles de l'ouverture (partie invisible)
                    angle_ouverture_debut = (cercle.angle_rotation - cercle.angle_ouverture / 2) % 360
                    angle_ouverture_fin = (cercle.angle_rotation + cercle.angle_ouverture / 2) % 360

                    # Vérifier si la balle touche la partie VISIBLE (pas dans l'ouverture)
                    if angle_ouverture_debut <= angle_ouverture_fin:
                        collision_detectee = not (angle_ouverture_debut <= angle_balle <= angle_ouverture_fin)
                    else:  # L'ouverture traverse 0°
                        collision_detectee = not (
                                    angle_balle >= angle_ouverture_debut or angle_balle <= angle_ouverture_fin)

                if collision_detectee:
                    # Rebond traditionnel
                    cercle.life -= 1
                    point_collision = centre_cercle + normal * rayon_cercle

                    vitesse_vec = np.array(balle.vitesse, dtype=float)
                    balle.vitesse = list(vitesse_vec - 2 * np.dot(vitesse_vec, normal) * normal)
                    balle.position = list(centre_cercle + normal * (rayon_cercle - balle.taille))

            # Cas 2 : Brisure dans l'ouverture (sans rebond)
            elif self.brisure_dans_ouverture and cercle.angle_ouverture > 0:
                if cercle.est_dans_ouverture(balle.position):
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
            # Correction : vérifier si collision_point est None ou non-vide
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