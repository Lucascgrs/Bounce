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

        # Correction du chemin des images pour plus de portabilité
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

            # Paramètres pour les arcs de cercle
            angle_ouverture = 30  # 30° d'ouverture (partie invisible) comme demandé
            angle_rotation_initial = k * 60  # Décaler la position initiale de chaque arc
            vitesse_rotation = 90 + k * 30  # Vitesse de rotation différente pour chaque arc

            arc = Cercle(
                position=self.centre,
                rayon=r,
                couleur="red",
                epaisseur=epaisseur,
                angle_ouverture=angle_ouverture,
                angle_rotation=angle_rotation_initial,
                vitesse_rotation=vitesse_rotation,
                life=40
            )
            self.cercles.append(arc)
            self.screen.ajouter_objet(arc)

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
                coef_gravite=0.6,  # Nouveau paramètre pour ajuster la gravité
                # contour=("white", 2)  # Ajout d'une bordure blanche
            )
            self.balles.append(balle)
            self.screen.ajouter_objet(balle)

    def demarrer(self):
        self.screen.boucle(fps=self.fps, duree=self.duree)


if __name__ == "__main__":
    # Test 1 : Collision traditionnelle (rebond sur l'arc visible, pas dans l'ouverture)
    jeu = Jeu(nb_balles=2, nb_cercles=1, duree=61, collision_sur_contact=True, brisure_dans_ouverture=False)

    # Test 2 : Brisure dans l'ouverture (pas de rebond, brise quand traverse l'ouverture)
    # jeu = Jeu(nb_balles=2, nb_cercles=2, duree=61, collision_sur_contact=False, brisure_dans_ouverture=True)

    time.sleep(0.5)
    jeu.demarrer()