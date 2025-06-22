# jeu.py
import os
from Balle import Balle
from Screen import Screen
from Cercle import Cercle
from Images import GestionnaireImages
import time
import random
import math


class Jeu:
    def __init__(self, nb_balles=1, nb_cercles=1, taille_ecran=(800, 600), couleur_fond="black", titre="Balles",
                 duree=30, fps=120, marge=10, collision_sur_contact=True, brisure_dans_ouverture=False):
        self.taille_ecran = taille_ecran
        self.couleur_fond = couleur_fond
        self.titre = titre
        self.duree = duree
        self.fps = fps
        self.balles = []
        self.cercles = []
        self.gestionnaire_images = GestionnaireImages(os.path.join(os.getcwd(), "Images"))

        # Calcul du centre de l'écran
        centre_x = taille_ecran[0] // 2
        centre_y = taille_ecran[1] // 2
        self.centre = (centre_x, centre_y)

        rayon = (min(taille_ecran[0], taille_ecran[1]) - 2 * marge) // 2

        # Créer l'écran avec les paramètres de collision
        self.screen = Screen(
            taille=taille_ecran,
            couleur_fond=couleur_fond,
            titre=titre,
            collision_sur_contact=collision_sur_contact,
            brisure_dans_ouverture=brisure_dans_ouverture
        )

        epaisseur = 5
        decalage = 15

        # Créer les arcs de cercle avec 30° d'ouverture qui tournent
        for k in range(nb_cercles):
            r = rayon - k * (epaisseur + decalage)
            if r <= 0:
                break

            angle_ouverture = 30
            angle_rotation_initial = k * 60
            vitesse_rotation = 90 + k * 30

            arc = Cercle(
                position=self.centre,
                rayon=r,
                couleur="red",
                epaisseur=epaisseur,
                angle_ouverture=angle_ouverture,
                angle_rotation=angle_rotation_initial,
                vitesse_rotation=vitesse_rotation
            )
            self.cercles.append(arc)
            self.screen.ajouter_objet(arc)

        # Reste du code pour créer les balles...
        # (copie le code de création des balles de ta version actuelle)

    def demarrer(self):
        self.screen.boucle(fps=self.fps, duree=self.duree)


if __name__ == "__main__":
    # Test 1 : Collision traditionnelle (rebond sur l'arc visible)
    # jeu = Jeu(nb_balles=2, nb_cercles=2, duree=61, collision_sur_contact=True, brisure_dans_ouverture=False)

    # Test 2 : Brisure dans l'ouverture (pas de rebond, brise quand traverse)
    jeu = Jeu(nb_balles=2, nb_cercles=2, duree=61, collision_sur_contact=False, brisure_dans_ouverture=True)

    time.sleep(0.5)
    jeu.demarrer()