# jeu.py
import os
from Balle import Balle
from Screen import Screen
from Cercle import Cercle
from Images import GestionnaireImages  # Correction du chemin d'import
import time
import random


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

        # Ajouter les balles
        for _ in range(nb_balles):
            # Position aléatoire avec marge
            x = random.randint(marge, taille_ecran[0] - marge)
            y = random.randint(marge, taille_ecran[1] - marge)
            vitesse = [random.uniform(-200, 200), random.uniform(-200, 200)]

            balle = Balle(taille=10, couleur="white", position=(x, y), vitesse=vitesse)
            self.balles.append(balle)
            self.screen.ajouter_objet(balle)

    def demarrer(self):
        self.screen.boucle(fps=self.fps, duree=self.duree)


if __name__ == "__main__":
    jeu = Jeu(nb_balles=2, nb_cercles=2, duree=61)
    time.sleep(0.5)
    jeu.demarrer()