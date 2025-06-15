import random
import pygame


class Particule:
    def __init__(self, position):
        self.position = list(position)
        angle = random.uniform(0, 2 * 3.1415)
        vitesse = random.uniform(2, 5)
        self.vitesse = [vitesse * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
                        vitesse * pygame.math.Vector2(1, 0).rotate_rad(angle).y]
        self.vie = random.uniform(0.5, 1.0)
        self.taille = random.randint(2, 4)
        self.couleur = (255, 255, 255)

    def mettre_a_jour(self, dt):
        self.position[0] += self.vitesse[0]
        self.position[1] += self.vitesse[1]
        self.vie -= dt

    def afficher(self, surface):
        if self.vie > 0:
            alpha = int(255 * self.vie)
            surf = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.couleur, alpha), (self.taille, self.taille), self.taille)
            surface.blit(surf, (self.position[0] - self.taille, self.position[1] - self.taille))
