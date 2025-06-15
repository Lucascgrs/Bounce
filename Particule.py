import random
import pygame
import math
import colorsys
from enum import Enum


class StyleExplosion(Enum):
    NORMAL = "normal"  # Une seule couleur de la palette
    MULTICOLOR = "multicolor"  # Mélange de couleurs de la palette
    RAINBOW = "rainbow"  # Dégradé complet
    FIREWORK = "firework"  # Style feu d'artifice avec traînées colorées


class Particule:
    # Palettes de couleurs prédéfinies (RGB)
    PALETTES = {
        "festif": [
            (255, 215, 0),  # Or
            (255, 0, 0),  # Rouge
            (0, 255, 127),  # Vert printemps
            (138, 43, 226),  # Bleu violet
            (255, 69, 0)  # Rouge-orange
        ],
        "froid": [
            (0, 191, 255),  # Bleu ciel profond
            (135, 206, 250),  # Bleu ciel clair
            (70, 130, 180),  # Bleu acier
            (100, 149, 237),  # Bleu cornflower
            (176, 224, 230)  # Bleu poudre
        ],
        "chaud": [
            (255, 69, 0),  # Rouge-orange
            (255, 140, 0),  # Orange foncé
            (255, 215, 0),  # Or
            (255, 99, 71),  # Rouge tomate
            (255, 127, 80)  # Corail
        ],
        "magique": [
            (148, 0, 211),  # Violet
            (75, 0, 130),  # Indigo
            (255, 0, 255),  # Magenta
            (238, 130, 238),  # Violet clair
            (218, 112, 214)  # Orchidée
        ],
        "celebration": [
            (255, 215, 0),  # Or
            (255, 255, 255),  # Blanc
            (192, 192, 192),  # Argent
            (218, 165, 32),  # GoldenRod
            (240, 230, 140)  # Kaki clair
        ]
    }

    def __init__(self, position, style=StyleExplosion.NORMAL, palette_name="festif",
                 couleur=None, vitesse_min=100, vitesse_max=300, direction_angle=None):
        self.position = list(position)
        self.style = style
        self.palette = self.PALETTES.get(palette_name, self.PALETTES["festif"])

        # Configuration de la couleur selon le style
        if couleur:
            self.couleur_base = couleur
            self.couleurs = [couleur]
        else:
            self.couleur_base = random.choice(self.palette)
            if style == StyleExplosion.MULTICOLOR:
                # Sélection de 2-3 couleurs aléatoires de la palette
                self.couleurs = random.sample(self.palette, random.randint(2, 3))
            elif style == StyleExplosion.RAINBOW:
                # Création d'un dégradé
                self.couleurs = self._creer_degrade()
            elif style == StyleExplosion.FIREWORK:
                # Couleurs spécifiques pour l'effet feu d'artifice
                self.couleurs = [self.couleur_base] + [self._ajuster_luminosite(self.couleur_base, i / 5) for i in
                                                       range(4)]
            else:
                self.couleurs = [self.couleur_base]

        # Direction et vitesse
        if direction_angle is not None:
            angle = direction_angle
        else:
            angle = random.uniform(0, 2 * math.pi)

        vitesse = random.uniform(vitesse_min, vitesse_max)
        self.vitesse = [
            vitesse * math.cos(angle),
            vitesse * math.sin(angle)
        ]

        self.vie = random.uniform(0.5, 1.5)
        self.vie_initiale = self.vie
        self.taille = random.randint(2, 4)

        # Paramètres physiques
        self.gravite = 400 if style != StyleExplosion.FIREWORK else 200  # Gravité réduite pour les feux d'artifice
        self.friction = 0.98

        # Paramètres visuels
        self.angle = random.uniform(0, 360)
        self.vitesse_rotation = random.uniform(-360, 360)
        self.positions_precedentes = []
        self.max_trail_length = 8 if style == StyleExplosion.FIREWORK else 5

    def _creer_degrade(self, steps=5):
        """Crée un dégradé de couleurs"""
        degrade = []
        for i in range(steps):
            factor = i / (steps - 1)
            r = int(self.couleur_base[0] * (1 - factor))
            g = int(self.couleur_base[1] * (1 - factor))
            b = int(self.couleur_base[2] * (1 - factor))
            degrade.append((r, g, b))
        return degrade

    def _ajuster_luminosite(self, couleur, factor):
        """Ajuste la luminosité d'une couleur"""
        return tuple(int(c * factor) for c in couleur)

    def mettre_a_jour(self, dt):
        self.positions_precedentes.append(list(self.position))
        if len(self.positions_precedentes) > self.max_trail_length:
            self.positions_precedentes.pop(0)

        self.vitesse[1] += self.gravite * dt
        self.vitesse[0] *= self.friction
        self.vitesse[1] *= self.friction

        self.position[0] += self.vitesse[0] * dt
        self.position[1] += self.vitesse[1] * dt

        self.angle += self.vitesse_rotation * dt
        self.vie -= dt

    def afficher(self, surface):
        if self.vie <= 0:
            return

        alpha = int(255 * (self.vie / self.vie_initiale))

        # Affichage du trail avec effet selon le style
        for i, pos in enumerate(self.positions_precedentes):
            trail_alpha = int(alpha * (i + 1) / len(self.positions_precedentes) * 0.5)
            trail_surface = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)

            # Sélection de la couleur selon le style
            if self.style == StyleExplosion.FIREWORK:
                couleur = self.couleurs[min(i, len(self.couleurs) - 1)]
            elif self.style == StyleExplosion.MULTICOLOR:
                couleur = random.choice(self.couleurs)
            elif self.style == StyleExplosion.RAINBOW:
                couleur = self.couleurs[min(i, len(self.couleurs) - 1)]
            else:
                couleur = self.couleur_base

            pygame.draw.circle(trail_surface, (*couleur, trail_alpha),
                               (self.taille, self.taille),
                               self.taille * (i + 1) / len(self.positions_precedentes))
            surface.blit(trail_surface, (pos[0] - self.taille, pos[1] - self.taille))

        # Particule principale
        particule_surface = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)
        pygame.draw.circle(particule_surface, (*self.couleur_base, alpha),
                           (self.taille, self.taille), self.taille)

        rotated_surface = pygame.transform.rotate(particule_surface, self.angle)
        new_rect = rotated_surface.get_rect(center=(self.position[0], self.position[1]))
        surface.blit(rotated_surface, new_rect)