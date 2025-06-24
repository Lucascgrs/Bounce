# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from typing import Dict, List, Any
import copy
from PIL import Image, ImageTk
import colorsys


class ColorManager:
    """Gestionnaire des couleurs avec historique"""

    def __init__(self):
        self.config_app_dir = "conf_app"
        self.colors_file = os.path.join(self.config_app_dir, "colors.json")
        self.images_dir = "Images"

        # Créer les dossiers s'ils n'existent pas
        os.makedirs(self.config_app_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

        self.colors_history = self.load_colors_history()

    def load_colors_history(self):
        """Charge l'historique des couleurs"""
        if os.path.exists(self.colors_file):
            try:
                with open(self.colors_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        # Couleurs par défaut
        return [
            {"name": "Blanc", "rgb": [255, 255, 255]},
            {"name": "Rouge", "rgb": [255, 0, 0]},
            {"name": "Vert", "rgb": [0, 255, 0]},
            {"name": "Bleu", "rgb": [0, 0, 255]},
            {"name": "Jaune", "rgb": [255, 255, 0]},
            {"name": "Cyan", "rgb": [0, 255, 255]},
            {"name": "Magenta", "rgb": [255, 0, 255]},
            {"name": "Orange", "rgb": [255, 165, 0]}
        ]

    def save_colors_history(self):
        """Sauvegarde l'historique des couleurs"""
        try:
            with open(self.colors_file, 'w', encoding='utf-8') as f:
                json.dump(self.colors_history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des couleurs: {e}")

    def add_color(self, name, rgb):
        """Ajoute une couleur à l'historique"""
        # Vérifier si la couleur existe déjà
        for color in self.colors_history:
            if color["rgb"] == rgb:
                return False

        self.colors_history.append({"name": name, "rgb": rgb})
        self.save_colors_history()
        return True

    def get_images_list(self):
        """Retourne la liste des images disponibles"""
        images = []
        if os.path.exists(self.images_dir):
            for file in os.listdir(self.images_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    images.append(file)
        return sorted(images)


class ColorPicker:
    """Widget personnalisé pour choisir les couleurs"""

    def __init__(self, parent, color_manager, callback=None):
        self.parent = parent
        self.color_manager = color_manager
        self.callback = callback
        self.current_rgb = [255, 255, 255]

        self.frame = ttk.LabelFrame(parent, text="Sélecteur de couleur", padding=5)

        # Variables pour les sliders
        self.rgb_vars = [tk.IntVar(value=255), tk.IntVar(value=255), tk.IntVar(value=255)]

        self.create_widgets()
        self.update_color_preview()

    def create_widgets(self):
        """Crée les widgets du sélecteur de couleur"""
        # Aperçu de la couleur
        self.color_preview = tk.Frame(self.frame, width=60, height=60, relief="sunken", bd=2)
        self.color_preview.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="nsew")
        self.color_preview.pack_propagate(False)

        # Sliders RGB
        colors = ["Rouge", "Vert", "Bleu"]
        slider_colors = ["red", "green", "blue"]

        for i, (color_name, slider_color) in enumerate(zip(colors, slider_colors)):
            tk.Label(self.frame, text=f"{color_name}:").grid(row=i, column=1, sticky="w", padx=5)

            slider = tk.Scale(self.frame, from_=0, to=255, orient="horizontal",
                              variable=self.rgb_vars[i], command=self.on_slider_change,
                              bg=slider_color, length=200)
            slider.grid(row=i, column=2, padx=5, pady=2)

            # Champ d'entrée pour valeur exacte
            entry = tk.Spinbox(self.frame, from_=0, to=255, width=5,
                               textvariable=self.rgb_vars[i], command=self.on_slider_change)
            entry.grid(row=i, column=3, padx=5)
            entry.bind('<KeyRelease>', self.on_slider_change)

        # Boutons
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(buttons_frame, text="💾 Sauver couleur", command=self.save_color, bg="lightblue").pack(side="left",
                                                                                                        padx=2)
        tk.Button(buttons_frame, text="🎨 Pipette", command=self.use_color_chooser, bg="lightyellow").pack(side="left",
                                                                                                          padx=2)

        # Liste des couleurs sauvegardées
        history_frame = ttk.LabelFrame(self.frame, text="Couleurs sauvegardées", padding=5)
        history_frame.grid(row=4, column=0, columnspan=4, pady=10, sticky="ew")

        # Frame avec scroll pour la liste des couleurs
        list_frame = tk.Frame(history_frame)
        list_frame.pack(fill="both", expand=True)

        self.colors_listbox = tk.Listbox(list_frame, height=6, font=("Arial", 9))
        scrollbar_colors = ttk.Scrollbar(list_frame, orient="vertical", command=self.colors_listbox.yview)
        self.colors_listbox.configure(yscrollcommand=scrollbar_colors.set)

        self.colors_listbox.pack(side="left", fill="both", expand=True)
        scrollbar_colors.pack(side="right", fill="y")

        self.colors_listbox.bind("<<ListboxSelect>>", self.on_color_selected)

        self.refresh_colors_list()

    def on_slider_change(self, event=None):
        """Appelé quand un slider change"""
        self.current_rgb = [var.get() for var in self.rgb_vars]
        self.update_color_preview()
        if self.callback:
            self.callback(self.current_rgb)

    def update_color_preview(self):
        """Met à jour l'aperçu de la couleur"""
        color_hex = f"#{self.current_rgb[0]:02x}{self.current_rgb[1]:02x}{self.current_rgb[2]:02x}"
        self.color_preview.configure(bg=color_hex)

    def set_color(self, rgb):
        """Définit la couleur actuelle"""
        self.current_rgb = rgb
        for i, value in enumerate(rgb):
            self.rgb_vars[i].set(value)
        self.update_color_preview()

    def get_color(self):
        """Retourne la couleur actuelle en RGB"""
        return self.current_rgb.copy()

    def get_color_hex(self):
        """Retourne la couleur actuelle en hexadécimal"""
        return f"#{self.current_rgb[0]:02x}{self.current_rgb[1]:02x}{self.current_rgb[2]:02x}"

    def save_color(self):
        """Sauvegarde la couleur actuelle"""
        name = tk.simpledialog.askstring("Nom de la couleur", "Entrez un nom pour cette couleur:")
        if name:
            if self.color_manager.add_color(name, self.current_rgb):
                self.refresh_colors_list()
                messagebox.showinfo("Succès", f"Couleur '{name}' sauvegardée!")
            else:
                messagebox.showwarning("Attention", "Cette couleur existe déjà!")

    def use_color_chooser(self):
        """Utilise le sélecteur de couleur système"""
        color = colorchooser.askcolor(color=self.get_color_hex())
        if color[0]:  # Si une couleur a été choisie
            rgb = [int(c) for c in color[0]]
            self.set_color(rgb)
            if self.callback:
                self.callback(rgb)

    def refresh_colors_list(self):
        """Rafraîchit la liste des couleurs"""
        self.colors_listbox.delete(0, tk.END)
        for color in self.color_manager.colors_history:
            rgb = color["rgb"]
            color_hex = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.colors_listbox.insert(tk.END, f"{color['name']} - RGB({rgb[0]},{rgb[1]},{rgb[2]})")
            # Colorer l'item (approximativement)
            self.colors_listbox.itemconfig(tk.END, bg=color_hex,
                                           fg="white" if sum(rgb) < 400 else "black")

    def on_color_selected(self, event):
        """Appelé quand une couleur est sélectionnée dans la liste"""
        selection = self.colors_listbox.curselection()
        if selection:
            color = self.color_manager.colors_history[selection[0]]
            self.set_color(color["rgb"])
            if self.callback:
                self.callback(color["rgb"])


class ConfigEditor:
    """Éditeur graphique de configuration pour le jeu de balles"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Éditeur de Configuration - Bounce Game")
        self.root.geometry("1200x800")

        # Créer le dossier CONFIGS s'il n'existe pas
        self.config_dir = "CONFIGS"
        os.makedirs(self.config_dir, exist_ok=True)

        # Gestionnaire de couleurs
        self.color_manager = ColorManager()

        # Configuration par défaut
        self.config = {
            "ecran": {
                "taille": [1200, 800],
                "couleur_fond": [0, 0, 0],  # RGB au lieu de string
                "titre": "Bounce Game",
                "fps": 60,
                "collision_sur_contact": True,
                "brisure_dans_ouverture": False,
                "marge_suppression": 100,
                "debug": False
            },
            "balles": [],
            "cercles": []
        }

        # Variables pour les éléments sélectionnés
        self.selected_balle_index = None
        self.selected_cercle_index = None

        # Importer tkinter.simpledialog
        import tkinter.simpledialog
        tk.simpledialog = tkinter.simpledialog

        self.create_interface()
        self.refresh_all_lists()

    def create_interface(self):
        """Crée l'interface principale"""
        # Barre d'outils
        self.create_toolbar()

        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Créer les onglets
        self.create_screen_tab()
        self.create_balles_tab()
        self.create_cercles_tab()
        self.create_preview_tab()

    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = tk.Frame(self.root, relief="raised", bd=1)
        toolbar.pack(side="top", fill="x")

        # Boutons de fichier
        tk.Button(toolbar, text="📁 Nouveau", command=self.new_config).pack(side="left", padx=2)
        tk.Button(toolbar, text="💾 Sauvegarder", command=self.save_config).pack(side="left", padx=2)
        tk.Button(toolbar, text="📂 Charger", command=self.load_config).pack(side="left", padx=2)

        # Séparateur
        tk.Label(toolbar, text="|").pack(side="left", padx=10)

        # Liste des configs disponibles
        tk.Label(toolbar, text="Configs:").pack(side="left", padx=2)
        self.config_listbox = ttk.Combobox(toolbar, width=20, state="readonly")
        self.config_listbox.pack(side="left", padx=2)
        self.config_listbox.bind("<<ComboboxSelected>>", self.on_config_selected)

        # Bouton de rafraîchissement
        tk.Button(toolbar, text="🔄", command=self.refresh_config_list).pack(side="left", padx=2)

        # Séparateur
        tk.Label(toolbar, text="|").pack(side="left", padx=10)

        # Bouton de lancement
        tk.Button(toolbar, text="🚀 Lancer le jeu", command=self.launch_game,
                  bg="green", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=2)

    def create_screen_tab(self):
        """Crée l'onglet de configuration de l'écran"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🖥️ Écran")

        # Variables pour les champs
        self.screen_vars = {}

        # Frame principal avec scroll
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configuration de l'écran
        screen_frame = ttk.LabelFrame(scrollable_frame, text="Configuration de l'écran", padding=10)
        screen_frame.pack(fill="x", padx=10, pady=5)

        row = 0

        # Taille
        tk.Label(screen_frame, text="Largeur:").grid(row=row, column=0, sticky="w")
        self.screen_vars['largeur'] = tk.IntVar(value=self.config['ecran']['taille'][0])
        tk.Spinbox(screen_frame, from_=400, to=2000, textvariable=self.screen_vars['largeur'], width=10).grid(row=row,
                                                                                                              column=1,
                                                                                                              padx=5)

        tk.Label(screen_frame, text="Hauteur:").grid(row=row, column=2, sticky="w", padx=(20, 0))
        self.screen_vars['hauteur'] = tk.IntVar(value=self.config['ecran']['taille'][1])
        tk.Spinbox(screen_frame, from_=300, to=1500, textvariable=self.screen_vars['hauteur'], width=10).grid(row=row,
                                                                                                              column=3,
                                                                                                              padx=5)
        row += 1

        # Titre
        tk.Label(screen_frame, text="Titre:").grid(row=row, column=0, sticky="w")
        self.screen_vars['titre'] = tk.StringVar(value=self.config['ecran']['titre'])
        tk.Entry(screen_frame, textvariable=self.screen_vars['titre'], width=30).grid(row=row, column=1, columnspan=3,
                                                                                      padx=5, sticky="w")
        row += 1

        # FPS
        tk.Label(screen_frame, text="FPS:").grid(row=row, column=0, sticky="w")
        self.screen_vars['fps'] = tk.IntVar(value=self.config['ecran']['fps'])
        tk.Spinbox(screen_frame, from_=30, to=120, textvariable=self.screen_vars['fps'], width=10).grid(row=row,
                                                                                                        column=1,
                                                                                                        padx=5)
        row += 1

        # Sélecteur de couleur de fond
        self.screen_color_picker = ColorPicker(screen_frame, self.color_manager, self.on_screen_color_change)
        self.screen_color_picker.frame.grid(row=row, column=0, columnspan=4, pady=10, sticky="ew")
        self.screen_color_picker.set_color(self.config['ecran']['couleur_fond'])
        row += 1

        # Options booléennes
        self.screen_vars['collision_sur_contact'] = tk.BooleanVar(value=self.config['ecran']['collision_sur_contact'])
        tk.Checkbutton(screen_frame, text="Collision sur contact",
                       variable=self.screen_vars['collision_sur_contact']).grid(row=row, column=0, columnspan=2,
                                                                                sticky="w")
        row += 1

        self.screen_vars['brisure_dans_ouverture'] = tk.BooleanVar(value=self.config['ecran']['brisure_dans_ouverture'])
        tk.Checkbutton(screen_frame, text="Brisure dans ouverture",
                       variable=self.screen_vars['brisure_dans_ouverture']).grid(row=row, column=0, columnspan=2,
                                                                                 sticky="w")
        row += 1

        self.screen_vars['debug'] = tk.BooleanVar(value=self.config['ecran']['debug'])
        tk.Checkbutton(screen_frame, text="Mode debug", variable=self.screen_vars['debug']).grid(row=row, column=0,
                                                                                                 columnspan=2,
                                                                                                 sticky="w")
        row += 1

        # Marge de suppression
        tk.Label(screen_frame, text="Marge suppression:").grid(row=row, column=0, sticky="w")
        self.screen_vars['marge_suppression'] = tk.IntVar(value=self.config['ecran']['marge_suppression'])
        tk.Spinbox(screen_frame, from_=50, to=500, textvariable=self.screen_vars['marge_suppression'], width=10).grid(
            row=row, column=1, padx=5)

        # Bouton d'application
        tk.Button(screen_frame, text="Appliquer les modifications", command=self.apply_screen_config,
                  bg="lightblue").grid(row=row + 1, column=0, columnspan=4, pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def on_screen_color_change(self, rgb):
        """Appelé quand la couleur de fond change"""
        pass  # Mise à jour en temps réel pas nécessaire pour l'écran

    def create_balles_tab(self):
        """Crée l'onglet de gestion des balles"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚽ Balles")

        # Frame gauche - Liste des balles
        left_frame = ttk.LabelFrame(frame, text="Balles existantes", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Liste des balles
        self.balles_listbox = tk.Listbox(left_frame, height=15)
        self.balles_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.balles_listbox.bind("<<ListboxSelect>>", self.on_balle_selected)

        # Boutons de gestion des balles
        balles_buttons_frame = tk.Frame(left_frame)
        balles_buttons_frame.pack(fill="x", padx=5, pady=5)

        tk.Button(balles_buttons_frame, text="➕ Ajouter", command=self.add_balle, bg="lightgreen").pack(side="left",
                                                                                                        padx=2)
        tk.Button(balles_buttons_frame, text="❌ Supprimer", command=self.delete_balle, bg="lightcoral").pack(
            side="left", padx=2)
        tk.Button(balles_buttons_frame, text="📋 Dupliquer", command=self.duplicate_balle, bg="lightyellow").pack(
            side="left", padx=2)

        # Frame droite - Édition de balle
        right_frame = ttk.LabelFrame(frame, text="Édition de balle", padding=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Canvas avec scrollbar pour l'édition
        canvas_balle = tk.Canvas(right_frame)
        scrollbar_balle = ttk.Scrollbar(right_frame, orient="vertical", command=canvas_balle.yview)
        scrollable_balle_frame = ttk.Frame(canvas_balle)

        scrollable_balle_frame.bind(
            "<Configure>",
            lambda e: canvas_balle.configure(scrollregion=canvas_balle.bbox("all"))
        )

        canvas_balle.create_window((0, 0), window=scrollable_balle_frame, anchor="nw")
        canvas_balle.configure(yscrollcommand=scrollbar_balle.set)

        # Variables pour l'édition de balle
        self.balle_vars = {}

        row = 0

        # Position
        position_frame = ttk.LabelFrame(scrollable_balle_frame, text="Position", padding=5)
        position_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(position_frame, text="X:").grid(row=0, column=0, sticky="w")
        self.balle_vars['pos_x'] = tk.DoubleVar()
        tk.Spinbox(position_frame, from_=0, to=2000, textvariable=self.balle_vars['pos_x'], width=10).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=5)

        tk.Label(position_frame, text="Y:").grid(row=0, column=2, sticky="w")
        self.balle_vars['pos_y'] = tk.DoubleVar()
        tk.Spinbox(position_frame, from_=0, to=1500, textvariable=self.balle_vars['pos_y'], width=10).grid(row=0,
                                                                                                           column=3,
                                                                                                           padx=5)

        tk.Button(position_frame, text="🎯 Centrer", command=self.center_balle, bg="lightcyan").grid(row=1, column=0,
                                                                                                    columnspan=4,
                                                                                                    pady=5)
        row += 1

        # Vitesse
        vitesse_frame = ttk.LabelFrame(scrollable_balle_frame, text="Vitesse", padding=5)
        vitesse_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(vitesse_frame, text="X:").grid(row=0, column=0, sticky="w")
        self.balle_vars['vit_x'] = tk.DoubleVar()
        tk.Spinbox(vitesse_frame, from_=-500, to=500, textvariable=self.balle_vars['vit_x'], width=10).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=5)

        tk.Label(vitesse_frame, text="Y:").grid(row=0, column=2, sticky="w")
        self.balle_vars['vit_y'] = tk.DoubleVar()
        tk.Spinbox(vitesse_frame, from_=-500, to=500, textvariable=self.balle_vars['vit_y'], width=10).grid(row=0,
                                                                                                            column=3,
                                                                                                            padx=5)
        row += 1

        # Taille
        tk.Label(scrollable_balle_frame, text="Taille:").grid(row=row, column=0, sticky="w")
        self.balle_vars['taille'] = tk.DoubleVar()
        tk.Spinbox(scrollable_balle_frame, from_=5, to=50, textvariable=self.balle_vars['taille'], width=10).grid(
            row=row, column=1, padx=5)
        row += 1

        # Type d'apparence (couleur ou image)
        apparence_frame = ttk.LabelFrame(scrollable_balle_frame, text="Apparence", padding=5)
        apparence_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        self.balle_vars['type_apparence'] = tk.StringVar(value="couleur")
        tk.Radiobutton(apparence_frame, text="Couleur", variable=self.balle_vars['type_apparence'],
                       value="couleur", command=self.on_balle_apparence_change).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(apparence_frame, text="Image", variable=self.balle_vars['type_apparence'],
                       value="image", command=self.on_balle_apparence_change).grid(row=0, column=1, sticky="w")
        row += 1

        # Sélecteur de couleur pour balle
        self.balle_color_frame = tk.Frame(scrollable_balle_frame)
        self.balle_color_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        self.balle_color_picker = ColorPicker(self.balle_color_frame, self.color_manager, self.on_balle_color_change)
        self.balle_color_picker.frame.pack(fill="both", expand=True)
        row += 1

        # Sélecteur d'image pour balle
        self.balle_image_frame = ttk.LabelFrame(scrollable_balle_frame, text="Sélection d'image", padding=5)
        self.balle_image_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(self.balle_image_frame, text="Image:").grid(row=0, column=0, sticky="w")
        self.balle_vars['image'] = tk.StringVar()
        self.balle_image_combo = ttk.Combobox(self.balle_image_frame, textvariable=self.balle_vars['image'],
                                              values=self.color_manager.get_images_list(), width=20)
        self.balle_image_combo.grid(row=0, column=1, padx=5)

        tk.Button(self.balle_image_frame, text="🔄 Actualiser", command=self.refresh_images_list).grid(row=0, column=2,
                                                                                                      padx=5)

        self.balle_image_frame.grid_remove()  # Masquer par défaut
        row += 1

        # Boutons d'action
        buttons_frame = tk.Frame(scrollable_balle_frame)
        buttons_frame.grid(row=row, column=0, columnspan=4, pady=10)

        tk.Button(buttons_frame, text="💾 Sauvegarder balle", command=self.save_balle_changes, bg="lightblue").pack(
            side="left", padx=5)
        tk.Button(buttons_frame, text="🔄 Annuler", command=self.cancel_balle_changes, bg="lightgray").pack(side="left",
                                                                                                           padx=5)

        canvas_balle.pack(side="left", fill="both", expand=True)
        scrollbar_balle.pack(side="right", fill="y")

    def create_cercles_tab(self):
        """Crée l'onglet de gestion des cercles"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⭕ Cercles")

        # Frame gauche - Liste des cercles
        left_frame = ttk.LabelFrame(frame, text="Cercles existants", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Liste des cercles
        self.cercles_listbox = tk.Listbox(left_frame, height=15)
        self.cercles_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.cercles_listbox.bind("<<ListboxSelect>>", self.on_cercle_selected)

        # Boutons de gestion des cercles
        cercles_buttons_frame = tk.Frame(left_frame)
        cercles_buttons_frame.pack(fill="x", padx=5, pady=5)

        tk.Button(cercles_buttons_frame, text="➕ Ajouter", command=self.add_cercle, bg="lightgreen").pack(side="left",
                                                                                                          padx=2)
        tk.Button(cercles_buttons_frame, text="❌ Supprimer", command=self.delete_cercle, bg="lightcoral").pack(
            side="left", padx=2)
        tk.Button(cercles_buttons_frame, text="📋 Dupliquer", command=self.duplicate_cercle, bg="lightyellow").pack(
            side="left", padx=2)

        # Frame droite - Édition de cercle
        right_frame = ttk.LabelFrame(frame, text="Édition de cercle", padding=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Canvas avec scrollbar pour l'édition
        canvas_cercle = tk.Canvas(right_frame)
        scrollbar_cercle = ttk.Scrollbar(right_frame, orient="vertical", command=canvas_cercle.yview)
        scrollable_cercle_frame = ttk.Frame(canvas_cercle)

        scrollable_cercle_frame.bind(
            "<Configure>",
            lambda e: canvas_cercle.configure(scrollregion=canvas_cercle.bbox("all"))
        )

        canvas_cercle.create_window((0, 0), window=scrollable_cercle_frame, anchor="nw")
        canvas_cercle.configure(yscrollcommand=scrollbar_cercle.set)

        # Variables pour l'édition de cercle
        self.cercle_vars = {}

        row = 0

        # Position
        position_frame = ttk.LabelFrame(scrollable_cercle_frame, text="Position", padding=5)
        position_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(position_frame, text="X:").grid(row=0, column=0, sticky="w")
        self.cercle_vars['pos_x'] = tk.DoubleVar()
        tk.Spinbox(position_frame, from_=0, to=2000, textvariable=self.cercle_vars['pos_x'], width=10).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=5)

        tk.Label(position_frame, text="Y:").grid(row=0, column=2, sticky="w")
        self.cercle_vars['pos_y'] = tk.DoubleVar()
        tk.Spinbox(position_frame, from_=0, to=1500, textvariable=self.cercle_vars['pos_y'], width=10).grid(row=0,
                                                                                                            column=3,
                                                                                                            padx=5)

        tk.Button(position_frame, text="🎯 Centrer", command=self.center_cercle, bg="lightcyan").grid(row=1, column=0,
                                                                                                     columnspan=4,
                                                                                                     pady=5)
        row += 1

        # Propriétés du cercle
        props_frame = ttk.LabelFrame(scrollable_cercle_frame, text="Propriétés", padding=5)
        props_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(props_frame, text="Rayon:").grid(row=0, column=0, sticky="w")
        self.cercle_vars['rayon'] = tk.DoubleVar()
        tk.Spinbox(props_frame, from_=20, to=200, textvariable=self.cercle_vars['rayon'], width=10).grid(row=0,
                                                                                                         column=1,
                                                                                                         padx=5)

        tk.Label(props_frame, text="Vie:").grid(row=0, column=2, sticky="w")
        self.cercle_vars['life'] = tk.IntVar()
        tk.Spinbox(props_frame, from_=1, to=10, textvariable=self.cercle_vars['life'], width=10).grid(row=0, column=3,
                                                                                                      padx=5)
        row += 1

        # Angles
        angles_frame = ttk.LabelFrame(scrollable_cercle_frame, text="Angles", padding=5)
        angles_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(angles_frame, text="Ouverture:").grid(row=0, column=0, sticky="w")
        self.cercle_vars['angle_ouverture'] = tk.DoubleVar()
        tk.Spinbox(angles_frame, from_=0, to=360, textvariable=self.cercle_vars['angle_ouverture'], width=10).grid(
            row=0, column=1, padx=5)
        tk.Label(angles_frame, text="°").grid(row=0, column=2, sticky="w")

        tk.Label(angles_frame, text="Rotation initiale:").grid(row=1, column=0, sticky="w")
        self.cercle_vars['angle_rotation_initial'] = tk.DoubleVar()
        tk.Spinbox(angles_frame, from_=0, to=360, textvariable=self.cercle_vars['angle_rotation_initial'],
                   width=10).grid(row=1, column=1, padx=5)
        tk.Label(angles_frame, text="°").grid(row=1, column=2, sticky="w")

        tk.Label(angles_frame, text="Vitesse rotation:").grid(row=2, column=0, sticky="w")
        self.cercle_vars['vitesse_rotation'] = tk.DoubleVar()
        tk.Spinbox(angles_frame, from_=-180, to=180, textvariable=self.cercle_vars['vitesse_rotation'], width=10).grid(
            row=2, column=1, padx=5)
        tk.Label(angles_frame, text="°/s").grid(row=2, column=2, sticky="w")
        row += 1

        # Sélecteur de couleur pour cercle
        self.cercle_color_picker = ColorPicker(scrollable_cercle_frame, self.color_manager, self.on_cercle_color_change)
        self.cercle_color_picker.frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)
        row += 1

        # Boutons d'action
        buttons_frame = tk.Frame(scrollable_cercle_frame)
        buttons_frame.grid(row=row, column=0, columnspan=4, pady=10)

        tk.Button(buttons_frame, text="💾 Sauvegarder cercle", command=self.save_cercle_changes, bg="lightblue").pack(
            side="left", padx=5)
        tk.Button(buttons_frame, text="🔄 Annuler", command=self.cancel_cercle_changes, bg="lightgray").pack(side="left",
                                                                                                            padx=5)

        canvas_cercle.pack(side="left", fill="both", expand=True)
        scrollbar_cercle.pack(side="right", fill="y")

    def create_preview_tab(self):
        """Crée l'onglet de prévisualisation"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👁️ Aperçu")

        # Zone de texte pour afficher la configuration JSON
        text_frame = ttk.LabelFrame(frame, text="Configuration JSON", padding=5)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Zone de texte avec scrollbar
        text_area_frame = tk.Frame(text_frame)
        text_area_frame.pack(fill="both", expand=True)

        self.preview_text = tk.Text(text_area_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar_preview = ttk.Scrollbar(text_area_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar_preview.set)

        self.preview_text.pack(side="left", fill="both", expand=True)
        scrollbar_preview.pack(side="right", fill="y")

        # Bouton de rafraîchissement
        tk.Button(text_frame, text="🔄 Rafraîchir l'aperçu", command=self.refresh_preview, bg="lightblue").pack(pady=5)

    # === MÉTHODES UTILITAIRES ===

    def center_balle(self):
        """Centre la balle sélectionnée dans la fenêtre"""
        largeur = self.screen_vars['largeur'].get()
        hauteur = self.screen_vars['hauteur'].get()

        self.balle_vars['pos_x'].set(largeur / 2)
        self.balle_vars['pos_y'].set(hauteur / 2)

    def center_cercle(self):
        """Centre le cercle sélectionné dans la fenêtre"""
        largeur = self.screen_vars['largeur'].get()
        hauteur = self.screen_vars['hauteur'].get()

        self.cercle_vars['pos_x'].set(largeur / 2)
        self.cercle_vars['pos_y'].set(hauteur / 2)

    def on_balle_apparence_change(self):
        """Gère le changement de type d'apparence de la balle"""
        if self.balle_vars['type_apparence'].get() == "couleur":
            self.balle_color_frame.grid()
            self.balle_image_frame.grid_remove()
        else:
            self.balle_color_frame.grid_remove()
            self.balle_image_frame.grid()

    def on_balle_color_change(self, rgb):
        """Appelé quand la couleur de la balle change"""
        pass  # Mise à jour en temps réel pas nécessaire

    def on_cercle_color_change(self, rgb):
        """Appelé quand la couleur du cercle change"""
        pass  # Mise à jour en temps réel pas nécessaire

    def refresh_images_list(self):
        """Rafraîchit la liste des images"""
        images = self.color_manager.get_images_list()
        self.balle_image_combo['values'] = images

    # === MÉTHODES DE GESTION DES BALLES ===

    def add_balle(self):
        """Ajoute une nouvelle balle"""
        nouvelle_balle = {
            "position": [100, 100],
            "vitesse": [150, 100],
            "taille": 15,
            "type_apparence": "couleur",
            "couleur": [255, 255, 255],
            "image": ""
        }
        self.config["balles"].append(nouvelle_balle)
        self.refresh_balles_list()

        # Sélectionner la nouvelle balle
        self.balles_listbox.selection_set(len(self.config["balles"]) - 1)
        self.on_balle_selected(None)

    def delete_balle(self):
        """Supprime la balle sélectionnée"""
        if self.selected_balle_index is not None:
            if messagebox.askyesno("Confirmation", "Supprimer cette balle ?"):
                del self.config["balles"][self.selected_balle_index]
                self.refresh_balles_list()
                self.clear_balle_fields()

    def duplicate_balle(self):
        """Duplique la balle sélectionnée"""
        if self.selected_balle_index is not None:
            balle_originale = copy.deepcopy(self.config["balles"][self.selected_balle_index])
            # Décaler légèrement la position
            balle_originale["position"][0] += 20
            balle_originale["position"][1] += 20
            self.config["balles"].append(balle_originale)
            self.refresh_balles_list()

    def on_balle_selected(self, event):
        """Gère la sélection d'une balle dans la liste"""
        selection = self.balles_listbox.curselection()
        if selection:
            self.selected_balle_index = selection[0]
            balle = self.config["balles"][self.selected_balle_index]

            # Remplir les champs d'édition
            self.balle_vars['pos_x'].set(balle["position"][0])
            self.balle_vars['pos_y'].set(balle["position"][1])
            self.balle_vars['vit_x'].set(balle["vitesse"][0])
            self.balle_vars['vit_y'].set(balle["vitesse"][1])
            self.balle_vars['taille'].set(balle["taille"])

            # Gestion du type d'apparence
            type_apparence = balle.get("type_apparence", "couleur")
            self.balle_vars['type_apparence'].set(type_apparence)

            if type_apparence == "couleur":
                couleur = balle.get("couleur", [255, 255, 255])
                if isinstance(couleur, str):
                    # Convertir les anciennes couleurs string en RGB
                    couleur_map = {
                        "white": [255, 255, 255], "black": [0, 0, 0], "red": [255, 0, 0],
                        "green": [0, 255, 0], "blue": [0, 0, 255], "yellow": [255, 255, 0],
                        "cyan": [0, 255, 255], "magenta": [255, 0, 255], "orange": [255, 165, 0]
                    }
                    couleur = couleur_map.get(couleur, [255, 255, 255])
                self.balle_color_picker.set_color(couleur)
            else:
                self.balle_vars['image'].set(balle.get("image", ""))

            self.on_balle_apparence_change()

    def save_balle_changes(self):
        """Sauvegarde les modifications de la balle"""
        if self.selected_balle_index is not None:
            balle = self.config["balles"][self.selected_balle_index]
            balle["position"] = [self.balle_vars['pos_x'].get(), self.balle_vars['pos_y'].get()]
            balle["vitesse"] = [self.balle_vars['vit_x'].get(), self.balle_vars['vit_y'].get()]
            balle["taille"] = self.balle_vars['taille'].get()
            balle["type_apparence"] = self.balle_vars['type_apparence'].get()

            if balle["type_apparence"] == "couleur":
                balle["couleur"] = self.balle_color_picker.get_color()
                balle["image"] = ""
            else:
                balle["image"] = self.balle_vars['image'].get()
                balle["couleur"] = [255, 255, 255]  # Couleur par défaut

            self.refresh_balles_list()
            messagebox.showinfo("Succès", "Modifications sauvegardées !")

    def cancel_balle_changes(self):
        """Annule les modifications de la balle"""
        if self.selected_balle_index is not None:
            self.on_balle_selected(None)

    def clear_balle_fields(self):
        """Vide les champs d'édition de balle"""
        for var_name, var in self.balle_vars.items():
            if isinstance(var, tk.StringVar):
                var.set("")
            else:
                var.set(0)
        self.selected_balle_index = None

    def refresh_balles_list(self):
        """Rafraîchit la liste des balles"""
        self.balles_listbox.delete(0, tk.END)
        for i, balle in enumerate(self.config["balles"]):
            type_app = balle.get("type_apparence", "couleur")
            if type_app == "couleur":
                couleur = balle.get("couleur", [255, 255, 255])
                if isinstance(couleur, list):
                    app_info = f"RGB({couleur[0]},{couleur[1]},{couleur[2]})"
                else:
                    app_info = str(couleur)
            else:
                app_info = f"Image: {balle.get('image', 'None')}"

            text = f"Balle {i + 1}: pos=({balle['position'][0]:.0f},{balle['position'][1]:.0f}) " \
                   f"v=({balle['vitesse'][0]:.0f},{balle['vitesse'][1]:.0f}) " \
                   f"taille={balle['taille']:.0f} {app_info}"
            self.balles_listbox.insert(tk.END, text)

    # === MÉTHODES DE GESTION DES CERCLES ===

    def add_cercle(self):
        """Ajoute un nouveau cercle"""
        nouveau_cercle = {
            "position": [400, 300],
            "rayon": 80,
            "couleur": [255, 0, 0],
            "life": 2,
            "angle_ouverture": 60,
            "angle_rotation_initial": 0,
            "vitesse_rotation": 30
        }
        self.config["cercles"].append(nouveau_cercle)
        self.refresh_cercles_list()

        # Sélectionner le nouveau cercle
        self.cercles_listbox.selection_set(len(self.config["cercles"]) - 1)
        self.on_cercle_selected(None)

    def delete_cercle(self):
        """Supprime le cercle sélectionné"""
        if self.selected_cercle_index is not None:
            if messagebox.askyesno("Confirmation", "Supprimer ce cercle ?"):
                del self.config["cercles"][self.selected_cercle_index]
                self.refresh_cercles_list()
                self.clear_cercle_fields()

    def duplicate_cercle(self):
        """Duplique le cercle sélectionné"""
        if self.selected_cercle_index is not None:
            cercle_original = copy.deepcopy(self.config["cercles"][self.selected_cercle_index])
            # Décaler légèrement la position
            cercle_original["position"][0] += 50
            cercle_original["position"][1] += 50
            self.config["cercles"].append(cercle_original)
            self.refresh_cercles_list()

    def on_cercle_selected(self, event):
        """Gère la sélection d'un cercle dans la liste"""
        selection = self.cercles_listbox.curselection()
        if selection:
            self.selected_cercle_index = selection[0]
            cercle = self.config["cercles"][self.selected_cercle_index]

            # Remplir les champs d'édition
            self.cercle_vars['pos_x'].set(cercle["position"][0])
            self.cercle_vars['pos_y'].set(cercle["position"][1])
            self.cercle_vars['rayon'].set(cercle["rayon"])
            self.cercle_vars['life'].set(cercle["life"])
            self.cercle_vars['angle_ouverture'].set(cercle["angle_ouverture"])
            self.cercle_vars['angle_rotation_initial'].set(cercle["angle_rotation_initial"])
            self.cercle_vars['vitesse_rotation'].set(cercle["vitesse_rotation"])

            # Couleur
            couleur = cercle.get("couleur", [255, 0, 0])
            if isinstance(couleur, str):
                # Convertir les anciennes couleurs string en RGB
                couleur_map = {
                    "white": [255, 255, 255], "black": [0, 0, 0], "red": [255, 0, 0],
                    "green": [0, 255, 0], "blue": [0, 0, 255], "yellow": [255, 255, 0],
                    "cyan": [0, 255, 255], "magenta": [255, 0, 255], "orange": [255, 165, 0],
                    "purple": [128, 0, 128], "brown": [165, 42, 42], "pink": [255, 192, 203],
                    "gray": [128, 128, 128]
                }
                couleur = couleur_map.get(couleur, [255, 0, 0])
            self.cercle_color_picker.set_color(couleur)

    def save_cercle_changes(self):
        """Sauvegarde les modifications du cercle"""
        if self.selected_cercle_index is not None:
            cercle = self.config["cercles"][self.selected_cercle_index]
            cercle["position"] = [self.cercle_vars['pos_x'].get(), self.cercle_vars['pos_y'].get()]
            cercle["rayon"] = self.cercle_vars['rayon'].get()
            cercle["life"] = self.cercle_vars['life'].get()
            cercle["couleur"] = self.cercle_color_picker.get_color()
            cercle["angle_ouverture"] = self.cercle_vars['angle_ouverture'].get()
            cercle["angle_rotation_initial"] = self.cercle_vars['angle_rotation_initial'].get()
            cercle["vitesse_rotation"] = self.cercle_vars['vitesse_rotation'].get()

            self.refresh_cercles_list()
            messagebox.showinfo("Succès", "Modifications sauvegardées !")

    def cancel_cercle_changes(self):
        """Annule les modifications du cercle"""
        if self.selected_cercle_index is not None:
            self.on_cercle_selected(None)

    def clear_cercle_fields(self):
        """Vide les champs d'édition de cercle"""
        for var in self.cercle_vars.values():
            if isinstance(var, tk.StringVar):
                var.set("")
            else:
                var.set(0)
        self.selected_cercle_index = None

    def refresh_cercles_list(self):
        """Rafraîchit la liste des cercles"""
        self.cercles_listbox.delete(0, tk.END)
        for i, cercle in enumerate(self.config["cercles"]):
            couleur = cercle.get("couleur", [255, 0, 0])
            if isinstance(couleur, list):
                couleur_info = f"RGB({couleur[0]},{couleur[1]},{couleur[2]})"
            else:
                couleur_info = str(couleur)

            text = f"Cercle {i + 1}: pos=({cercle['position'][0]:.0f},{cercle['position'][1]:.0f}) " \
                   f"r={cercle['rayon']:.0f} vie={cercle['life']} " \
                   f"ouv={cercle['angle_ouverture']:.0f}° {couleur_info}"
            self.cercles_listbox.insert(tk.END, text)

    # === MÉTHODES DE GESTION DE L'ÉCRAN ===

    def apply_screen_config(self):
        """Applique la configuration de l'écran"""
        self.config["ecran"]["taille"] = [self.screen_vars['largeur'].get(), self.screen_vars['hauteur'].get()]
        self.config["ecran"]["titre"] = self.screen_vars['titre'].get()
        self.config["ecran"]["fps"] = self.screen_vars['fps'].get()
        self.config["ecran"]["couleur_fond"] = self.screen_color_picker.get_color()
        self.config["ecran"]["collision_sur_contact"] = self.screen_vars['collision_sur_contact'].get()
        self.config["ecran"]["brisure_dans_ouverture"] = self.screen_vars['brisure_dans_ouverture'].get()
        self.config["ecran"]["debug"] = self.screen_vars['debug'].get()
        self.config["ecran"]["marge_suppression"] = self.screen_vars['marge_suppression'].get()

        messagebox.showinfo("Succès", "Configuration de l'écran appliquée !")

    # === MÉTHODES DE GESTION DES FICHIERS ===

    def new_config(self):
        """Crée une nouvelle configuration"""
        if messagebox.askyesno("Confirmation",
                               "Créer une nouvelle configuration ? (Les modifications non sauvegardées seront perdues)"):
            self.config = {
                "ecran": {
                    "taille": [1200, 800],
                    "couleur_fond": [0, 0, 0],
                    "titre": "Bounce Game",
                    "fps": 60,
                    "collision_sur_contact": True,
                    "brisure_dans_ouverture": False,
                    "marge_suppression": 100,
                    "debug": False
                },
                "balles": [],
                "cercles": []
            }
            self.refresh_all_lists()
            self.load_screen_config()

    def save_config(self):
        """Sauvegarde la configuration"""
        filename = filedialog.asksaveasfilename(
            initialdir=self.config_dir,
            title="Sauvegarder la configuration",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Succès", f"Configuration sauvegardée dans {os.path.basename(filename)}")
                self.refresh_config_list()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")

    def load_config(self):
        """Charge une configuration"""
        filename = filedialog.askopenfilename(
            initialdir=self.config_dir,
            title="Charger une configuration",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )

        if filename:
            self.load_config_from_file(filename)

    def load_config_from_file(self, filename):
        """Charge une configuration depuis un fichier"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            self.refresh_all_lists()
            self.load_screen_config()
            messagebox.showinfo("Succès", f"Configuration chargée depuis {os.path.basename(filename)}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")

    def load_screen_config(self):
        """Charge la configuration de l'écran dans l'interface"""
        ecran = self.config["ecran"]
        self.screen_vars['largeur'].set(ecran["taille"][0])
        self.screen_vars['hauteur'].set(ecran["taille"][1])
        self.screen_vars['titre'].set(ecran["titre"])
        self.screen_vars['fps'].set(ecran["fps"])

        # Couleur de fond
        couleur_fond = ecran.get("couleur_fond", [0, 0, 0])
        if isinstance(couleur_fond, str):
            # Convertir string en RGB pour compatibilité
            couleur_map = {"black": [0, 0, 0], "white": [255, 255, 255], "gray": [128, 128, 128]}
            couleur_fond = couleur_map.get(couleur_fond, [0, 0, 0])
        self.screen_color_picker.set_color(couleur_fond)

        self.screen_vars['collision_sur_contact'].set(ecran["collision_sur_contact"])
        self.screen_vars['brisure_dans_ouverture'].set(ecran["brisure_dans_ouverture"])
        self.screen_vars['debug'].set(ecran["debug"])
        self.screen_vars['marge_suppression'].set(ecran["marge_suppression"])

    def refresh_config_list(self):
        """Rafraîchit la liste des configurations disponibles"""
        configs = []
        if os.path.exists(self.config_dir):
            for file in os.listdir(self.config_dir):
                if file.endswith('.json'):
                    configs.append(file)

        self.config_listbox['values'] = configs

    def on_config_selected(self, event):
        """Gère la sélection d'une configuration dans la liste"""
        selected = self.config_listbox.get()
        if selected:
            filepath = os.path.join(self.config_dir, selected)
            if messagebox.askyesno("Confirmation", f"Charger la configuration '{selected}' ?"):
                self.load_config_from_file(filepath)

    def refresh_preview(self):
        """Rafraîchit l'aperçu JSON"""
        self.preview_text.delete(1.0, tk.END)
        json_text = json.dumps(self.config, indent=4, ensure_ascii=False)
        self.preview_text.insert(1.0, json_text)

    def refresh_all_lists(self):
        """Rafraîchit toutes les listes"""
        self.refresh_balles_list()
        self.refresh_cercles_list()
        self.refresh_config_list()
        self.refresh_preview()
        self.refresh_images_list()

    def launch_game(self):
        """Lance le jeu avec la configuration actuelle"""
        try:
            # Sauvegarder temporairement la config actuelle
            temp_config_path = os.path.join(self.config_dir, "_temp_config.json")

            # Appliquer d'abord la config de l'écran si elle n'a pas été appliquée
            self.apply_screen_config()

            # Sauvegarder la configuration temporaire
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            # Importer et lancer le jeu
            try:
                from Launcher import lancer_jeu_depuis_fichier

                # Minimiser l'éditeur pendant le jeu
                self.root.iconify()

                # Lancer le jeu
                lancer_jeu_depuis_fichier(temp_config_path)

                # Restaurer l'éditeur après le jeu
                self.root.deiconify()

            except ImportError:
                messagebox.showerror("Erreur",
                                     "Impossible d'importer le module Launcher.\n"
                                     "Assurez-vous que Launcher.py est présent dans le même dossier.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du lancement du jeu: {e}")
                self.root.deiconify()  # Restaurer en cas d'erreur

            # Nettoyer le fichier temporaire
            try:
                if os.path.exists(temp_config_path):
                    os.remove(temp_config_path)
            except:
                pass  # Ignore les erreurs de suppression

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la préparation du jeu: {e}")

    def run(self):
        """Lance l'éditeur de configuration"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Éditeur fermé par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur dans l'éditeur: {e}")


def main():
    """Point d'entrée principal pour l'éditeur"""
    print("🎨 Lancement de l'éditeur de configuration Bounce")

    try:
        editor = ConfigEditor()
        editor.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        input("Appuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()