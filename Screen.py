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

        # Compteur pour limiter les logs
        self.log_counter = 0

        # Stockage des positions précédentes pour détecter les téléportations
        self.previous_positions = {}

        # Marge pour la suppression des balles hors écran
        self.marge_suppression = 500  # pixels au-delà de l'écran

    def ajouter_objet(self, objet):
        self.objets.append(objet)

    def retirer_objet(self, objet):
        if objet in self.objets:
            self.objets.remove(objet)

    def _est_hors_ecran_avec_marge(self, balle):
        """Vérifie si une balle est sortie de l'écran avec une marge"""
        x, y = balle.position
        marge = self.marge_suppression

        # Vérifier si la balle est complètement hors des limites avec marge
        hors_gauche = x < -marge
        hors_droite = x > self.taille[0] + marge
        hors_haut = y < -marge
        hors_bas = y > self.taille[1] + marge

        return hors_gauche or hors_droite or hors_haut or hors_bas

    def _supprimer_balles_hors_ecran(self):
        """Supprime les balles qui sont sorties de l'écran avec marge"""
        balles_a_supprimer = []

        for obj in self.objets:
            if isinstance(obj, Balle) and self._est_hors_ecran_avec_marge(obj):
                balles_a_supprimer.append(obj)
                print(f"🗑️ Suppression balle hors écran: position ({obj.position[0]:.1f}, {obj.position[1]:.1f})")

        for balle in balles_a_supprimer:
            self.objets.remove(balle)

        if balles_a_supprimer:
            print(
                f"🗑️ {len(balles_a_supprimer)} balle(s) supprimée(s), {len([obj for obj in self.objets if isinstance(obj, Balle)])} restante(s)")

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

            # LOG: Sauvegarder les positions AVANT mise à jour (seulement pour balles à l'écran)
            positions_avant = {}
            for i, balle in enumerate(balles):
                # Ne surveiller les téléportations que pour les balles visibles ou proches de l'écran
                if not self._est_hors_ecran_avec_marge(balle):
                    positions_avant[i] = balle.position.copy()

            # Mise à jour des objets
            for obj in self.objets:
                if hasattr(obj, 'mettre_a_jour'):
                    obj.mettre_a_jour(dt)

            # LOG: Vérifier les téléportations après mise à jour (seulement pour balles surveillées)
            for i, balle in enumerate(balles):
                if i in positions_avant:
                    distance_mouvement = ((balle.position[0] - positions_avant[i][0]) ** 2 + (
                            balle.position[1] - positions_avant[i][1]) ** 2) ** 0.5
                    if distance_mouvement > 500:  # Seuil augmenté pour éviter les faux positifs en chute libre
                        print(f"🚨 TÉLÉPORTATION détectée dans mise à jour! Balle {i}")
                        print(f"   Avant mise à jour: ({positions_avant[i][0]:.1f}, {positions_avant[i][1]:.1f})")
                        print(f"   Après mise à jour: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")
                        print(f"   Distance: {distance_mouvement:.1f}")

            # Supprimer les balles hors écran
            self._supprimer_balles_hors_ecran()

            # Mettre à jour la liste après suppression
            balles = [obj for obj in self.objets if isinstance(obj, Balle)]

            # LOG: Sauvegarder les positions AVANT collisions balles
            positions_avant_collision_balles = {}
            for i, balle in enumerate(balles):
                positions_avant_collision_balles[i] = balle.position.copy()

            # Gestion des collisions entre balles
            for i in range(len(balles)):
                for j in range(i + 1, len(balles)):
                    balles[i].collision_avec_balle(balles[j])

            # LOG: Vérifier les téléportations après collisions balles
            for i, balle in enumerate(balles):
                if i in positions_avant_collision_balles:
                    distance_mouvement = ((balle.position[0] - positions_avant_collision_balles[i][0]) ** 2 + (
                            balle.position[1] - positions_avant_collision_balles[i][1]) ** 2) ** 0.5
                    if distance_mouvement > 50:  # Mouvement suspect > 50 pixels
                        print(f"🚨 TÉLÉPORTATION détectée dans collision balles! Balle {i}")
                        print(
                            f"   Avant collision balles: ({positions_avant_collision_balles[i][0]:.1f}, {positions_avant_collision_balles[i][1]:.1f})")
                        print(f"   Après collision balles: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")
                        print(f"   Distance: {distance_mouvement:.1f}")

            # LOG: Sauvegarder les positions AVANT collisions cercles
            positions_avant_collision_cercles = {}
            for i, balle in enumerate(balles):
                positions_avant_collision_cercles[i] = balle.position.copy()

            # Gestion des collisions balle-cercle avec nouvelle logique
            for i, balle in enumerate(balles):
                for j, cercle in enumerate(cercles[:]):
                    collision_point = self._gerer_collision_balle_cercle(balle, cercle, i, j)

                    if cercle.life <= 0:
                        self._creer_explosion(cercle, collision_point)
                        # Suppression du cercle
                        if cercle in self.objets:
                            self.objets.remove(cercle)
                        if cercle in cercles:
                            cercles.remove(cercle)

            # LOG: Vérifier les téléportations après collisions cercles
            for i, balle in enumerate(balles):
                if i in positions_avant_collision_cercles:
                    distance_mouvement = ((balle.position[0] - positions_avant_collision_cercles[i][0]) ** 2 + (
                            balle.position[1] - positions_avant_collision_cercles[i][1]) ** 2) ** 0.5
                    if distance_mouvement > 50:  # Mouvement suspect > 50 pixels
                        print(f"🚨 TÉLÉPORTATION détectée dans collision cercles! Balle {i}")
                        print(
                            f"   Avant collision cercles: ({positions_avant_collision_cercles[i][0]:.1f}, {positions_avant_collision_cercles[i][1]:.1f})")
                        print(f"   Après collision cercles: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")
                        print(f"   Distance: {distance_mouvement:.1f}")

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

            # Incrémenter le compteur de logs
            self.log_counter += 1

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
        result = False
        if angle_balle_min <= angle_balle_max:
            result = angle_dans_ouverture(angle_balle_min) and angle_dans_ouverture(angle_balle_max)
        else:
            # Cas où la balle traverse 0°
            points_a_verifier = 5
            result = True
            for i in range(points_a_verifier + 1):
                if i == 0:
                    angle_test = angle_balle_min
                elif i == points_a_verifier:
                    angle_test = angle_balle_max
                else:
                    angle_test = (angle_balle_min + (
                            360 + angle_balle_max - angle_balle_min) * i / points_a_verifier) % 360

                if not angle_dans_ouverture(angle_test):
                    result = False
                    break

        return result

    def _gerer_collision_balle_cercle(self, balle, cercle, balle_id, cercle_id):
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

        # ⚠️ CORRECTION PRINCIPALE : Vérifier la collision réelle, pas juste la proximité
        # La balle doit être dans la zone de collision (rayon ± taille de balle)
        distance_collision = abs(distance - rayon_cercle)
        balle_touche_cercle = distance_collision <= balle.taille

        # LOG: Afficher seulement quand il y a vraiment collision ou proximité très proche
        if balle_touche_cercle or distance_collision <= balle.taille * 2:
            print(f"\n🔍 COLLISION CHECK - Frame {self.log_counter} - Balle {balle_id} / Cercle {cercle_id}")
            print(f"   Position balle: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")
            print(f"   Distance du centre: {distance:.1f}")
            print(f"   Rayon cercle: {rayon_cercle:.1f}")
            print(f"   Distance de collision: {distance_collision:.1f} (seuil: {balle.taille:.1f})")
            print(f"   Balle touche cercle: {balle_touche_cercle}")

            # Calculer l'angle de la balle pour debug
            dx = balle.position[0] - cercle.position[0]
            dy = balle.position[1] - cercle.position[1]
            angle_balle = math.degrees(math.atan2(dy, dx))
            angle_balle = (angle_balle + 360) % 360

            angle_ouverture_debut = (cercle.angle_rotation - cercle.angle_ouverture / 2) % 360
            angle_ouverture_fin = (cercle.angle_rotation + cercle.angle_ouverture / 2) % 360

            print(f"   Angle balle: {angle_balle:.1f}°")
            print(f"   Ouverture: {angle_ouverture_debut:.1f}° → {angle_ouverture_fin:.1f}°")

        # Ne traiter la collision que si la balle touche réellement le cercle
        if balle_touche_cercle:
            collision_detectee = False
            point_collision = None
            old_position = balle.position.copy()

            # Cas 1 : Collision sur contact avec l'arc visible
            if self.collision_sur_contact:
                if cercle.angle_ouverture == 0:
                    # Cercle complet
                    collision_detectee = True
                    print(f"   ✅ CERCLE COMPLET - Collision détectée")
                else:
                    # Arc : vérifier si la balle est ENTIÈREMENT dans l'ouverture
                    est_entierement_dans_ouverture = self._est_entierement_dans_ouverture(balle, cercle)
                    collision_detectee = not est_entierement_dans_ouverture

                    print(f"   🎯 ARC - Entièrement dans ouverture: {est_entierement_dans_ouverture}")
                    print(f"   🎯 ARC - Collision détectée: {collision_detectee}")

                if collision_detectee:
                    # LOG: Position avant rebond
                    print(f"   💥 REBOND IMMINENT!")
                    print(f"   Position AVANT rebond: ({old_position[0]:.1f}, {old_position[1]:.1f})")

                    # Rebond traditionnel
                    cercle.life -= 1
                    point_collision = centre_cercle + normal * rayon_cercle

                    vitesse_vec = np.array(balle.vitesse, dtype=float)
                    balle.vitesse = list(vitesse_vec - 2 * np.dot(vitesse_vec, normal) * normal)

                    # Repositionner la balle pour éviter qu'elle reste coincée
                    if distance < rayon_cercle:
                        # La balle est à l'intérieur, la pousser vers l'extérieur
                        balle.position = list(centre_cercle + normal * (rayon_cercle + balle.taille))
                        print(
                            f"   🔄 Balle repoussée VERS L'EXTÉRIEUR: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")
                    else:
                        # La balle est à l'extérieur, la pousser un peu plus loin pour éviter la répétition
                        balle.position = list(centre_cercle + normal * (rayon_cercle + balle.taille + 1))
                        print(f"   🔄 Balle éloignée légèrement: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")

                    # LOG: Position après rebond
                    print(f"   Position APRÈS rebond: ({balle.position[0]:.1f}, {balle.position[1]:.1f})")
                    print(f"   Vitesse APRÈS rebond: ({balle.vitesse[0]:.1f}, {balle.vitesse[1]:.1f})")
                else:
                    print(f"   ✅ PAS de collision - la balle passe librement dans l'ouverture")

            # Cas 2 : Brisure dans l'ouverture (sans rebond)
            elif self.brisure_dans_ouverture and cercle.angle_ouverture > 0:
                est_entierement_dans_ouverture = self._est_entierement_dans_ouverture(balle, cercle)

                print(f"   🔥 MODE BRISURE - Entièrement dans ouverture: {est_entierement_dans_ouverture}")

                if est_entierement_dans_ouverture:
                    # La balle traverse l'ouverture : brise le cercle directement
                    print(f"   💥 BRISURE du cercle!")
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