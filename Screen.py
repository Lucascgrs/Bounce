# -*- coding: utf-8 -*-
import pygame
from Balle import Balle
from Cercle import Cercle
from Particule import Particule


class Screen:
    def __init__(self, taille=(800, 600), couleur_fond="white", titre="Game"):
        pygame.init()
        self.taille = taille
        self.couleur_fond = couleur_fond
        self.ecran = pygame.display.set_mode(taille)
        pygame.display.set_caption(titre)
        self.clock = pygame.time.Clock()
        self.objets = []  # objets à dessiner (comme des balles)
        self.particules = []

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def boucle(self, fps=60, duree=None):
        clock = pygame.time.Clock()
        temps_ecoule = 0
        continuer = True

        # Optimisation : extraire balles et cercles une seule fois
        balles = [obj for obj in self.objets if isinstance(obj, Balle)]
        cercles = [obj for obj in self.objets if isinstance(obj, Cercle)]

        while continuer:
            dt = clock.tick(fps) / 1000  # en secondes
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    continuer = False

            self.ecran.fill(self.couleur_fond)

            # Mettre à jour les objets (balles)
            for balle in balles:
                balle.mettre_a_jour(dt)

            # Gérer collisions balle-cercle
            for balle in balles:
                for cercle in cercles:
                    balle.rebondir(cercle)
                    if cercle.life <= 0:
                        # Explosion du cercle en particules
                        for _ in range(50):  # nombre de particules
                            self.particules.append(Particule(cercle.position))
                        if cercle in self.objets:
                            self.objets.remove(cercle)
                        if cercle in cercles:
                            cercles.remove(cercle)

            # Gérer collisions balle-balle
            for i in range(len(balles)):
                for j in range(i + 1, len(balles)):
                    balles[i].collision_avec_balle(balles[j])

            # Afficher objets
            for obj in self.objets:
                obj.afficher(self.ecran)

            # Mettre à jour et afficher les particules
            for particule in self.particules[:]:
                particule.mettre_a_jour(dt)
                particule.afficher(self.ecran)
                if particule.vie <= 0:
                    self.particules.remove(particule)

            pygame.display.flip()
            temps_ecoule += dt

            if duree and temps_ecoule >= duree:
                continuer = False

        pygame.quit()
