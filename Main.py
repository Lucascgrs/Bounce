# jeu.py
import os
from Balle import Balle
from Screen import Screen
from Cercle import Cercle
from Images import GestionnaireImages  # Correction du chemin d'import
import time
import random
import math


class Jeu:
    def __init__(self, nb_balles=1, nb_cercles=1, taille_ecran=(800, 600), couleur_fond="black", titre="Balles",
                 duree=30, fps=120, marge=10):
        self.taille_ecran = taille_ecran
        self.couleur_fond = couleur_fond
        self.titre = titre
        self.duree = duree
        self.fps = fps
        self.balles = []
        self.cercles = []
        # Correction du chemin des images pour plus de portabilité
        self.gestionnaire_images = GestionnaireImages(os.path.join(os.getcwd(), "Images"))

        # Calcul du centre de l'écran
        centre_x = taille_ecran[0] // 2
        centre_y = taille_ecran[1] // 2
        self.centre = (centre_x, centre_y)

        rayon = (min(taille_ecran[0], taille_ecran[1]) - 2 * marge) // 2

        # Créer l'écran
        self.screen = Screen(taille=taille_ecran, couleur_fond=couleur_fond, titre=titre)

        epaisseur = 5
        decalage = 15

        # Créer les cercles imbriqués
        for k in range(nb_cercles):
            r = rayon - k * (epaisseur + decalage)
            if r <= 0:
                break

            cercle = Cercle(position=self.centre, rayon=r, couleur="red", epaisseur=epaisseur)
            self.cercles.append(cercle)
            self.screen.ajouter_objet(cercle)

        # Récupérer le rayon du plus petit cercle
        rayon_min = self.cercles[-1].rayon if self.cercles else rayon

        # Liste des chemins d'images disponibles
        images_disponibles = list(self.gestionnaire_images.images.values())

        # Ajouter les balles dans le plus petit cercle
        for _ in range(nb_balles):
            # Position aléatoire dans le cercle le plus petit
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, rayon_min * 0.8)  # 0.8 pour s'assurer qu'elles restent dans le cercle

            # Calcul de la position par rapport au centre
            x = self.centre[0] + r * math.cos(angle)
            y = self.centre[1] + r * math.sin(angle)

            # Vitesse initiale aléatoire
            vitesse = [random.uniform(-100, 100), random.uniform(-100, 100)]

            # Sélection aléatoire d'une image de drapeau
            image = random.choice(images_disponibles) if images_disponibles else None

            # Création de la balle avec une plus grande taille
            balle = Balle(
                taille=30,
                image=image,
                position=(x, y),
                vitesse=vitesse,
                coef_collision=1.1,  # Augmenté pour des rebonds plus dynamiques
                coef_gravite=0.6,    # Nouveau paramètre pour ajuster la gravité
                #contour=("white", 2)  # Ajout d'une bordure blanche
            )
            self.balles.append(balle)
            self.screen.ajouter_objet(balle)

    def demarrer(self):
        self.screen.boucle(fps=self.fps, duree=self.duree)


if __name__ == "__main__":
    jeu = Jeu(nb_balles=2, nb_cercles=2, duree=61)
    time.sleep(0.5)
    jeu.demarrer()