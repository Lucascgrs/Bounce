# -*- coding: utf-8 -*-
import pygame
from Balle import Balle
from Cercle import Cercle
from Particule import Particule, StyleExplosion
import random
import math


class Screen:
    def __init__(self, taille=(800, 600), couleur_fond="black", titre="Jeu"):
        pygame.init()
        self.taille = taille
        self.couleur_fond = couleur_fond
        self.titre = titre
        self.ecran = pygame.display.set_mode(taille)
        pygame.display.set_caption(titre)
        self.objets = []
        self.particules = []

    def ajouter_objet(self, obj):
        self.objets.append(obj)

    def boucle(self, fps=60, duree=None):
        clock = pygame.time.Clock()
        temps_ecoule = 0
        continuer = True

        # Optimisation : extraire balles et cercles une seule fois
        balles = [obj for obj in self.objets if isinstance(obj, Balle)]
        cercles = [obj for obj in self.objets if isinstance(obj, Cercle)]

        try:
            while continuer:
                dt = clock.tick(fps) / 1000  # en secondes
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        continuer = False

                # Effacement de l'écran
                self.ecran.fill(self.couleur_fond)

                # Mise à jour des balles
                for balle in balles:
                    balle.mettre_a_jour(dt)
                    # Gestion des collisions avec les bords
                    if balle.position[0] - balle.taille < 0 or balle.position[0] + balle.taille > self.taille[0]:
                        balle.vitesse[0] *= -0.8  # Ajout d'amortissement
                        balle.position[0] = max(balle.taille, min(self.taille[0] - balle.taille, balle.position[0]))

                    if balle.position[1] - balle.taille < 0 or balle.position[1] + balle.taille > self.taille[1]:
                        balle.vitesse[1] *= -0.8  # Ajout d'amortissement
                        balle.position[1] = max(balle.taille, min(self.taille[1] - balle.taille, balle.position[1]))

                # Gestion des collisions balle-balle
                for i in range(len(balles)):
                    for j in range(i + 1, len(balles)):
                        balles[i].collision_avec_balle(balles[j])

                # Gestion des collisions balle-cercle et création des particules
                for balle in balles:
                    for cercle in cercles[:]:
                        collision_point = balle.rebondir(cercle)
                        if cercle.life <= 0:
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
                                if collision_point:
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
                    if particule.vie <= 0:
                        self.particules.remove(particule)

                pygame.display.flip()
                temps_ecoule += dt

                if duree and temps_ecoule >= duree:
                    continuer = False

        finally:
            pygame.quit()