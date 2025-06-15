# jeu.py
from Balle import Balle
from Screen import Screen
from Cercle import Cercle
from PROJECT.Bounce.Images import GestionnaireImages
import time
import random


class Jeu:
    def __init__(self, nb_balles=1, nb_cercles=1, taille_ecran=(800, 600), couleur_fond="black", titre="Balles", duree=30, fps=120, marge=10):
        self.taille_ecran = taille_ecran
        self.couleur_fond = couleur_fond
        self.titre = titre
        self.duree = duree
        self.fps = fps
        self.balles = []
        self.cercles = []
        self.gestionnaire_images = GestionnaireImages("C:\\Users\\lucas\\PycharmProjects\\PROJECT\\TikTok\\Images")

        # Calcul du centre de l'écran
        centre_x = taille_ecran[0] // 2
        centre_y = taille_ecran[1] // 2
        self.centre = (centre_x, centre_y)

        rayon = (min(taille_ecran[0], taille_ecran[1]) - 2 * marge) // 2

        # Créer l'écran
        self.screen = Screen(taille=taille_ecran, couleur_fond=couleur_fond, titre=titre)

        epaisseur = 5
        decalage = 15  # Décalage visuel entre chaque cercle

        # Créer les cercles imbriqués du plus grand au plus petit
        for k in range(nb_cercles):
            r = rayon - k * (epaisseur + decalage)
            if r <= 0:
                break  # On arrête si le rayon devient non visible

            cercle = Cercle(position=self.centre, rayon=r, couleur="red", epaisseur=epaisseur)
            self.cercles.append(cercle)
            self.screen.ajouter_objet(cercle)

        for k in range(nb_balles):

            # Créer la balle centrée dans le cercle
            offset_x = random.randint(-int(rayon / 2), int(rayon / 2))
            offset_y = random.randint(-int(rayon / 2), int(rayon / 2))
            position = (self.centre[0] + offset_x, self.centre[1] + offset_y)

            balle = Balle(taille=20, couleur="white", contour=("white", 2), position=position, vitesse=(0, 0), gravite=0.3, image=self.gestionnaire_images.images[list(self.gestionnaire_images.images.keys())[k]])
            self.balles.append(balle)
            self.screen.ajouter_objet(balle)

    def demarrer(self):
        self.screen.boucle(fps=self.fps, duree=self.duree)


if __name__ == "__main__":
    jeu = Jeu(nb_balles=2, nb_cercles=2, duree=61)
    time.sleep(0.5)
    jeu.demarrer()
