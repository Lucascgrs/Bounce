# -*- coding: utf-8 -*-
import pygame
from Balle import Balle
from Cercle import Cercle
from Particule import Particule, StyleExplosion
import random
import math


class Screen:
    def __init__(self, taille=(800, 600), couleur_fond="black", titre="Bounce",
                 collision_sur_contact=True, brisure_dans_ouverture=False, marge_suppression=100, debug=False):
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
        self.debug = debug

        # Paramètres de collision globaux
        self.collision_sur_contact = collision_sur_contact
        self.brisure_dans_ouverture = brisure_dans_ouverture

    def log_debug(self, message):
        """Affiche les messages de debug si activé"""
        if self.debug:
            print(f"[DEBUG] {message}")

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
            self.log_debug(
                f"Objet retiré hors écran: {type(obj).__name__} à {getattr(obj, 'position', 'position inconnue')}")

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
            if objets_retires > 0:
                self.log_debug(f"{objets_retires} objets retirés de l'écran")

            # Gestion des collisions entre balles
            for i in range(len(balles)):
                for j in range(i + 1, len(balles)):
                    balles[i].collision_avec_balle(balles[j])

            # Gestion des collisions balle-cercle avec nouvelle logique
            for balle in balles:
                for cercle in cercles[:]:
                    collision_point = self._gerer_collision_balle_cercle(balle, cercle)

                    if cercle.life <= 0:
                        self.log_debug(f"Cercle détruit! Création d'explosion à {collision_point}")
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

            self.log_debug("\n")

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

        # Vérifier si la balle est à l'intérieur ou à l'extérieur du cercle
        balle_a_l_interieur = distance <= rayon_cercle - balle.taille
        balle_a_l_exterieur = distance >= rayon_cercle + balle.taille

        # Calculer la direction du mouvement de la balle par rapport au cercle
        vitesse_vec = np.array(balle.vitesse)
        s_approche = np.dot(vitesse_vec, normal) < 0  # True si la balle s'approche du centre
        s_eloigne = np.dot(vitesse_vec, normal) > 0  # True si la balle s'éloigne du centre

        # Logs détaillés
        self.log_debug(f"Balle pos: {[round(x, 2) for x in balle.position]}, Cercle pos: {cercle.position}")
        self.log_debug(f"Distance: {distance:.2f}, Rayon: {rayon_cercle}, Taille balle: {balle.taille}")
        self.log_debug(
            f"Proche du cercle: {balle_pres_du_cercle}, À l'intérieur: {balle_a_l_interieur}, À l'extérieur: {balle_a_l_exterieur}")
        self.log_debug(f"S'approche: {s_approche}, S'éloigne: {s_eloigne}")
        self.log_debug(
            f"Mode collision_sur_contact: {self.collision_sur_contact}, Mode brisure: {self.brisure_dans_ouverture}")

        if balle_pres_du_cercle:
            collision_detectee = False
            point_collision = None
            brisure_detectee = False

            # Vérifier d'abord la brisure dans l'ouverture (priorité plus haute)
            if self.brisure_dans_ouverture and cercle.angle_ouverture > 0:
                self.log_debug("Vérification: BRISURE DANS OUVERTURE")
                balle_entierement_dans_ouverture = self._est_entierement_dans_ouverture(balle, cercle)
                self.log_debug(f"Balle entièrement dans ouverture: {balle_entierement_dans_ouverture}")

                # Conditions pour la brisure : balle dans l'ouverture ET proche du cercle
                if balle_entierement_dans_ouverture and balle_pres_du_cercle:
                    # La balle traverse l'ouverture : brise le cercle directement
                    cercle.life = 0  # Brise immédiatement
                    point_collision = list(position)  # Point d'impact = position de la balle
                    brisure_detectee = True
                    self.log_debug(f"BRISURE! Cercle brisé à la position: {[round(x, 2) for x in point_collision]}")
                    # Pas de rebond, la balle continue sa trajectoire
                else:
                    self.log_debug("Conditions de brisure non remplies")

            # Si pas de brisure, vérifier les collisions normales
            if not brisure_detectee and self.collision_sur_contact:
                self.log_debug("Vérification: COLLISION SUR CONTACT")
                if cercle.angle_ouverture == 0:
                    # Cercle complet - collision normale
                    collision_detectee = True
                    self.log_debug("Cercle complet - collision détectée")
                else:
                    # Arc : logique d'ouverture avec vérification de direction
                    balle_entierement_dans_ouverture = self._est_entierement_dans_ouverture(balle, cercle)
                    self.log_debug(
                        f"Angle ouverture: {cercle.angle_ouverture}°, Rotation: {cercle.angle_rotation:.1f}°")
                    self.log_debug(f"Balle entièrement dans ouverture: {balle_entierement_dans_ouverture}")

                    if balle_entierement_dans_ouverture:
                        # Balle dans l'ouverture - pas de collision
                        collision_detectee = False
                        self.log_debug("Balle dans l'ouverture - PAS DE COLLISION")
                    elif balle_a_l_exterieur and s_eloigne:
                        # Balle à l'extérieur qui s'éloigne - pas de collision (évite la re-téléportation)
                        collision_detectee = False
                        self.log_debug("Balle à l'extérieur qui s'éloigne - PAS DE COLLISION (anti re-téléportation)")
                    elif balle_a_l_interieur and s_approche:
                        # Balle à l'intérieur qui s'approche du bord - collision normale
                        collision_detectee = True
                        self.log_debug("Balle à l'intérieur qui s'approche - COLLISION")
                    elif not balle_a_l_interieur and not balle_a_l_exterieur:
                        # Balle en intersection avec le cercle - collision normale
                        collision_detectee = True
                        self.log_debug("Balle en intersection avec le cercle - COLLISION")
                    elif balle_a_l_exterieur and s_approche:
                        # Balle à l'extérieur qui s'approche - collision normale
                        collision_detectee = True
                        self.log_debug("Balle à l'extérieur qui s'approche - COLLISION")
                    else:
                        # Autres cas - pas de collision
                        collision_detectee = False
                        self.log_debug("Autres cas - PAS DE COLLISION")

                if collision_detectee:
                    # Rebond traditionnel
                    cercle.life -= 1
                    point_collision = centre_cercle + normal * rayon_cercle
                    self.log_debug(f"REBOND! Vie du cercle: {cercle.life}")

                    vitesse_vec = np.array(balle.vitesse, dtype=float)
                    nouvelle_vitesse = vitesse_vec - 2 * np.dot(vitesse_vec, normal) * normal
                    balle.vitesse = list(nouvelle_vitesse)

                    # Repositionner selon la position d'origine
                    if balle_a_l_interieur:
                        # Balle vient de l'intérieur - la placer à l'intérieur
                        nouvelle_position = centre_cercle + normal * (rayon_cercle - balle.taille)
                        balle.position = list(nouvelle_position)
                        self.log_debug(f"Repositionnement INTÉRIEUR: {[round(x, 2) for x in balle.position]}")
                    self.log_debug(f"Nouvelle vitesse: {[round(x, 2) for x in balle.vitesse]}")

            # S'assurer que point_collision est toujours une liste ou None
            if point_collision is not None and hasattr(point_collision, 'tolist'):
                point_collision = point_collision.tolist()

            return point_collision

        return None

    def _creer_explosion(self, cercle, collision_point):
        """Crée l'animation d'explosion pour un cercle détruit"""
        self.log_debug(f"Création explosion avec {75} particules")

        # Choisir un style d'explosion
        style = random.choice([
            StyleExplosion.NORMAL,
            StyleExplosion.MULTICOLOR,
            StyleExplosion.RAINBOW,
            StyleExplosion.FIREWORK
        ])

        # Choisir une palette de couleurs
        palette = random.choice(list(Particule.PALETTES.keys()))

        self.log_debug(f"Style explosion: {style}, Palette: {palette}")

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