import pygame
import sys
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass
from Circle import Circle


@dataclass
class ScreenParams:
    """Paramètres de configuration de l'écran"""
    width: int = 800
    height: int = 600
    title: str = "Animation"
    background_color: Tuple[int, int, int] = (0, 0, 0)  # Noir par défaut
    fps: int = 60
    fullscreen: bool = False
    vsync: bool = True
    resizable: bool = False


class Screen:
    def __init__(self, params: Optional[ScreenParams] = None):
        """Initialise la fenêtre avec les paramètres donnés"""
        if params is None:
            params = ScreenParams()

        # Initialisation de Pygame
        pygame.init()

        # Paramètres de base
        self.width = params.width
        self.height = params.height
        self.background_color = params.background_color
        self.title = params.title
        self.fps = params.fps
        self.running = False

        # Horloge pour le contrôle FPS
        self.clock = pygame.time.Clock()

        # Création de la fenêtre
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if params.fullscreen:
            flags |= pygame.FULLSCREEN
        if params.resizable:
            flags |= pygame.RESIZABLE
        if params.vsync:
            flags |= pygame.VSYNC

        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self.title)

        # Gestion des objets
        self.shapes: Dict[str, List[Any]] = {
            'circles': [],
            # Ajoutez d'autres types de formes ici au besoin
        }

        # Variables de debug
        self.show_fps = False
        self.debug_mode = False
        self.font = pygame.font.Font(None, 36)

        # Variables de contrôle
        self.paused = False
        self.mouse_pos = (0, 0)
        self.delta_time = 0

    def add_shape(self, shape: Any, shape_type: str = 'circles'):
        """Ajoute une forme à l'écran"""
        if shape_type in self.shapes:
            self.shapes[shape_type].append(shape)

    def remove_shape(self, shape: Any, shape_type: str = 'circles'):
        """Retire une forme de l'écran"""
        if shape_type in self.shapes and shape in self.shapes[shape_type]:
            self.shapes[shape_type].remove(shape)

    def clear_shapes(self, shape_type: Optional[str] = None):
        """Efface toutes les formes ou celles d'un type spécifique"""
        if shape_type:
            if shape_type in self.shapes:
                self.shapes[shape_type].clear()
        else:
            for shapes_list in self.shapes.values():
                shapes_list.clear()

    def toggle_pause(self):
        """Active/désactive la pause"""
        self.paused = not self.paused

    def toggle_debug(self):
        """Active/désactive le mode debug"""
        self.debug_mode = not self.debug_mode

    def toggle_fps_display(self):
        """Active/désactive l'affichage des FPS"""
        self.show_fps = not self.show_fps

    def handle_events(self) -> bool:
        """Gère les événements Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif event.key == pygame.K_F3:
                    self.toggle_debug()
                elif event.key == pygame.K_F4:
                    self.toggle_fps_display()

            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                if not pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                    self.screen = pygame.display.set_mode((self.width, self.height),
                                                          pygame.RESIZABLE)

            # Mettez à jour la position de la souris
            self.mouse_pos = pygame.mouse.get_pos()

        return True

    def update(self):
        """Met à jour l'état de tous les objets"""
        if self.paused:
            return

        # Mise à jour des cercles
        for circle in self.shapes['circles']:
            circle.update(self.delta_time, self.width, self.height)

        # Ajoutez ici la mise à jour d'autres types de formes

    def draw(self):
        """Dessine tous les objets à l'écran"""
        # Effacement de l'écran
        self.screen.fill(self.background_color)

        # Dessin des cercles
        for circle in self.shapes['circles']:
            circle.draw(self.screen)

            # Affichage des hitbox en mode debug
            if self.debug_mode:
                pygame.draw.rect(self.screen, (255, 0, 0), circle.rect, 1)

        # Affichage des informations de debug
        if self.debug_mode:
            debug_info = [
                f"FPS: {int(self.clock.get_fps())}",
                f"Objects: {sum(len(shapes) for shapes in self.shapes.values())}",
                f"Mouse: {self.mouse_pos}",
                f"Paused: {self.paused}"
            ]

            for i, text in enumerate(debug_info):
                text_surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, 10 + i * 30))

        # Affichage FPS si activé
        elif self.show_fps:
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 10))

        # Mise à jour de l'affichage
        pygame.display.flip()

    def run(self):
        """Boucle principale"""
        self.running = True

        while self.running:
            # Calcul du delta time
            self.delta_time = self.clock.tick(self.fps) / 1000.0

            # Gestion des événements
            self.running = self.handle_events()

            # Mise à jour et dessin
            self.update()
            self.draw()

        # Nettoyage
        self.quit()

    def quit(self):
        """Ferme proprement la fenêtre"""
        pygame.quit()
        sys.exit()

    def get_mouse_position(self) -> Tuple[int, int]:
        """Retourne la position actuelle de la souris"""
        return self.mouse_pos

    def is_mouse_pressed(self) -> Tuple[bool, bool, bool]:
        """Retourne l'état des boutons de la souris"""
        return pygame.mouse.get_pressed()

    def set_background_color(self, color: Tuple[int, int, int]):
        """Change la couleur de fond"""
        self.background_color = color

    def set_title(self, title: str):
        """Change le titre de la fenêtre"""
        self.title = title
        pygame.display.set_caption(title)

    def set_fps(self, fps: int):
        """Change la limite de FPS"""
        self.fps = fps