# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from typing import Dict, List, Any
import copy
from PIL import Image, ImageTk
import colorsys
import math


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


class CercleCloneDialog:
    """Dialogue pour le clonage avancé de cercles"""

    def __init__(self, parent, cercle_original):
        self.parent = parent
        self.cercle_original = copy.deepcopy(cercle_original)
        self.result = None

        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title("Clonage avancé de cercle")
        self.dialog.geometry("580x650")  # Augmenter encore la hauteur
        self.dialog.resizable(False, False)
        self.dialog.transient(parent.root)
        self.dialog.grab_set()

        self.vars = {}
        self.create_widgets()
        self.center_dialog()

    def save_and_apply_to_original(self):
        """Sauvegarde et applique les modifications à l'original avant clonage"""
        try:
            # Récupérer les valeurs modifiées
            nb_clones = self.vars['nb_clones'].get()
            distance = self.vars['decalage_distance'].get()
            rotation = self.vars['decalage_rotation'].get()

            # Modifier l'original selon les paramètres choisis
            if self.vars['mode_disposition'].get() == "cercle" and nb_clones > 0:
                # Appliquer une rotation au cercle original
                angle_rotation_original = math.radians(rotation * -1)  # Rotation inverse pour équilibrer
                self.cercle_original["angle_rotation_initial"] = (
                                                                         self.cercle_original.get(
                                                                             "angle_rotation_initial",
                                                                             0) + math.degrees(angle_rotation_original)
                                                                 ) % 360

            # Appliquer les modifications au cercle original dans la configuration
            cercle_index = self.parent.selected_cercle_index
            if cercle_index is not None:
                self.parent.config["cercles"][cercle_index] = copy.deepcopy(self.cercle_original)
                self.parent.refresh_cercles_list()
                self.parent.on_cercle_selected(None)  # Recharger l'affichage

            messagebox.showinfo("Succès", "Modifications appliquées au cercle original !")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")

    def create_widgets(self):
        """Crée les widgets du dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Titre
        title_label = tk.Label(main_frame, text="Clonage avancé de cercle",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Nombre de clones
        clone_frame = ttk.LabelFrame(main_frame, text="Nombre de clones", padding=10)
        clone_frame.pack(fill="x", pady=5)

        tk.Label(clone_frame, text="Nombre de cercles à créer:").grid(row=0, column=0, sticky="w")
        self.vars['nb_clones'] = tk.IntVar(value=3)
        tk.Spinbox(clone_frame, from_=1, to=20, textvariable=self.vars['nb_clones'],
                   width=10, command=self.update_preview).grid(row=0, column=1, padx=(10, 0))

        # Décalages
        offset_frame = ttk.LabelFrame(main_frame, text="Décalages", padding=10)
        offset_frame.pack(fill="x", pady=5)

        # Décalage de rotation
        tk.Label(offset_frame, text="Décalage rotation (degrés):").grid(row=0, column=0, sticky="w")
        self.vars['decalage_rotation'] = tk.DoubleVar(value=30.0)
        rotation_spinbox = tk.Spinbox(offset_frame, from_=-180, to=180,
                                      textvariable=self.vars['decalage_rotation'],
                                      width=10, increment=15, command=self.update_preview)
        rotation_spinbox.grid(row=0, column=1, padx=(10, 0))
        rotation_spinbox.bind('<KeyRelease>', lambda e: self.update_preview())

        # Décalage de distance
        tk.Label(offset_frame, text="Décalage distance (pixels):").grid(row=1, column=0, sticky="w")
        self.vars['decalage_distance'] = tk.DoubleVar(value=100.0)
        distance_spinbox = tk.Spinbox(offset_frame, from_=0, to=500,
                                      textvariable=self.vars['decalage_distance'],
                                      width=10, increment=10, command=self.update_preview)
        distance_spinbox.grid(row=1, column=1, padx=(10, 0))
        distance_spinbox.bind('<KeyRelease>', lambda e: self.update_preview())

        # Mode de disposition
        layout_frame = ttk.LabelFrame(main_frame, text="Disposition", padding=10)
        layout_frame.pack(fill="x", pady=5)

        self.vars['mode_disposition'] = tk.StringVar(value="cercle")
        tk.Radiobutton(layout_frame, text="En cercle autour de l'original",
                       variable=self.vars['mode_disposition'], value="cercle",
                       command=self.update_preview).pack(anchor="w")
        tk.Radiobutton(layout_frame, text="En ligne droite",
                       variable=self.vars['mode_disposition'], value="ligne",
                       command=self.update_preview).pack(anchor="w")
        tk.Radiobutton(layout_frame, text="En grille",
                       variable=self.vars['mode_disposition'], value="grille",
                       command=self.update_preview).pack(anchor="w")

        # Décalage de couleur AMÉLIORÉ
        color_frame = ttk.LabelFrame(main_frame, text="Dégradé de couleur", padding=10)
        color_frame.pack(fill="x", pady=5)

        self.vars['fondu_couleur'] = tk.BooleanVar(value=True)
        tk.Checkbutton(color_frame, text="Activer le dégradé de couleur",
                       variable=self.vars['fondu_couleur'],
                       command=self.update_preview).pack(anchor="w")

        # Frame pour les couleurs
        colors_frame = tk.Frame(color_frame)
        colors_frame.pack(fill="x", pady=10)

        # Couleur source (couleur du cercle original)
        tk.Label(colors_frame, text="Couleur source:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        couleur_orig = self.cercle_original.get("couleur", [255, 0, 0])
        self.source_color_display = tk.Frame(colors_frame, width=40, height=25,
                                             bg=f"#{couleur_orig[0]:02x}{couleur_orig[1]:02x}{couleur_orig[2]:02x}",
                                             relief="sunken", bd=2)
        self.source_color_display.grid(row=0, column=1, padx=(0, 20))
        self.source_color_display.pack_propagate(False)

        # Couleur cible (sélectionnable)
        tk.Label(colors_frame, text="Couleur cible:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.vars['couleur_cible'] = [0, 255, 255]  # Cyan par défaut
        self.target_color_display = tk.Frame(colors_frame, width=40, height=25,
                                             bg="#00ffff", relief="sunken", bd=2)
        self.target_color_display.grid(row=0, column=3, padx=(0, 10))
        self.target_color_display.pack_propagate(False)

        tk.Button(colors_frame, text="🎨 Choisir", command=self.choose_target_color).grid(row=0, column=4)

        # Intensité du dégradé
        tk.Label(color_frame, text="Intensité du dégradé:").pack(anchor="w", pady=(10, 0))
        self.vars['intensite_fondu'] = tk.DoubleVar(value=0.8)
        intensity_scale = tk.Scale(color_frame, from_=0.0, to=1.0, resolution=0.05, orient="horizontal",
                                   variable=self.vars['intensite_fondu'], length=400,
                                   command=lambda x: self.update_preview())
        intensity_scale.pack(fill="x")

        # Aperçu
        preview_frame = ttk.LabelFrame(main_frame, text="Aperçu", padding=5)
        preview_frame.pack(fill="x", pady=10)

        self.preview_canvas = tk.Canvas(preview_frame, width=500, height=140, bg="black")
        self.preview_canvas.pack()

        # Boutons (version modifiée)
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="💾 Sauvegarder sur original",
                  command=self.save_and_apply_to_original,
                  bg="lightblue", font=("Arial", 9)).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="✅ Créer les clones", command=self.create_clones,
                  bg="lightgreen", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="❌ Annuler", command=self.cancel,
                  bg="lightcoral").pack(side="left", padx=5)

        # Initialiser l'aperçu
        self.dialog.after(100, self.update_preview)

    def choose_target_color(self):
        """Ouvre un sélecteur de couleur pour la couleur cible"""
        current_color = f"#{self.vars['couleur_cible'][0]:02x}{self.vars['couleur_cible'][1]:02x}{self.vars['couleur_cible'][2]:02x}"
        color = colorchooser.askcolor(color=current_color, title="Choisir la couleur cible du dégradé")
        if color[0]:  # Si une couleur a été choisie
            rgb = [int(c) for c in color[0]]
            self.vars['couleur_cible'] = rgb
            # Mettre à jour l'affichage
            color_hex = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.target_color_display.configure(bg=color_hex)
            self.update_preview()

    def center_dialog(self):
        """Centre le dialogue sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (580 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def update_preview(self, *args):
        """Met à jour l'aperçu visuel"""
        try:
            self.preview_canvas.delete("all")

            # Centre du canvas
            cx, cy = 250, 70

            # Dessiner l'original
            couleur_orig = self.cercle_original.get("couleur", [255, 0, 0])
            orig_color = f"#{couleur_orig[0]:02x}{couleur_orig[1]:02x}{couleur_orig[2]:02x}"
            self.preview_canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12,
                                            fill="", outline=orig_color, width=3)
            self.preview_canvas.create_text(cx, cy - 30, text="Original", fill="white", font=("Arial", 9, "bold"))

            nb_clones = self.vars['nb_clones'].get()
            mode = self.vars['mode_disposition'].get()
            distance = self.vars['decalage_distance'].get() * 0.15  # Échelle réduite pour l'aperçu
            rotation = self.vars['decalage_rotation'].get()

            for i in range(min(nb_clones, 12)):  # Limiter l'aperçu à 12 cercles
                if mode == "cercle":
                    angle = math.radians(rotation * i)
                    x = cx + distance * math.cos(angle)
                    y = cy + distance * math.sin(angle)
                elif mode == "ligne":
                    angle = math.radians(rotation)
                    x = cx + (distance * (i + 1)) * math.cos(angle)
                    y = cy + (distance * (i + 1)) * math.sin(angle)
                else:  # grille
                    cols = int(math.sqrt(nb_clones)) + 1
                    row = i // cols
                    col = i % cols
                    x = cx + col * (distance * 0.8) - (cols * distance * 0.4)
                    y = cy + row * (distance * 0.8) - 30

                # Calculer la couleur avec dégradé entre couleur source et cible
                if self.vars['fondu_couleur'].get():
                    intensite = self.vars['intensite_fondu'].get()
                    factor = (i / max(1, nb_clones - 1)) * intensite

                    couleur_cible = self.vars['couleur_cible']

                    # Interpolation linéaire entre couleur source et cible
                    r = int(couleur_orig[0] * (1 - factor) + couleur_cible[0] * factor)
                    g = int(couleur_orig[1] * (1 - factor) + couleur_cible[1] * factor)
                    b = int(couleur_orig[2] * (1 - factor) + couleur_cible[2] * factor)

                    color = f"#{r:02x}{g:02x}{b:02x}"
                else:
                    color = orig_color

                # S'assurer que le cercle reste dans le canvas
                if 20 <= x <= 480 and 20 <= y <= 120:
                    self.preview_canvas.create_oval(x - 10, y - 10, x + 10, y + 10,
                                                    fill="", outline=color, width=2)
                    self.preview_canvas.create_text(x, y + 18, text=f"{i + 1}", fill="white", font=("Arial", 8))

            # Afficher le nombre total si > 12
            if nb_clones > 12:
                self.preview_canvas.create_text(250, 125, text=f"... et {nb_clones - 12} autres",
                                                fill="yellow", font=("Arial", 9))
        except Exception as e:
            print(f"Erreur dans update_preview: {e}")

    def create_clones(self):
        """Crée les cercles clonés"""
        try:
            nb_clones = self.vars['nb_clones'].get()
            mode = self.vars['mode_disposition'].get()
            distance = self.vars['decalage_distance'].get()
            rotation = self.vars['decalage_rotation'].get()

            clones = []
            couleur_orig = self.cercle_original.get("couleur", [255, 0, 0])
            couleur_cible = self.vars['couleur_cible']
            pos_orig = self.cercle_original["position"]

            for i in range(nb_clones):
                clone = copy.deepcopy(self.cercle_original)

                # Calculer la nouvelle position
                if mode == "cercle":
                    angle = math.radians(rotation * i)
                    clone["position"][0] = pos_orig[0] + distance * math.cos(angle)
                    clone["position"][1] = pos_orig[1] + distance * math.sin(angle)
                elif mode == "ligne":
                    angle = math.radians(rotation)
                    clone["position"][0] = pos_orig[0] + (distance * (i + 1)) * math.cos(angle)
                    clone["position"][1] = pos_orig[1] + (distance * (i + 1)) * math.sin(angle)
                else:  # grille
                    cols = int(math.sqrt(nb_clones)) + 1
                    row = i // cols
                    col = i % cols
                    clone["position"][0] = pos_orig[0] + col * distance
                    clone["position"][1] = pos_orig[1] + row * distance

                # CORRECTION : Appliquer le dégradé de couleur entre source et cible
                if self.vars['fondu_couleur'].get() and nb_clones > 1:
                    intensite = self.vars['intensite_fondu'].get()
                    # Factor de 0 (premier clone = couleur originale) à 1 (dernier clone = couleur cible)
                    factor = (i / (nb_clones - 1)) * intensite

                    # Interpolation linéaire entre couleur source et cible
                    r = int(couleur_orig[0] * (1 - factor) + couleur_cible[0] * factor)
                    g = int(couleur_orig[1] * (1 - factor) + couleur_cible[1] * factor)
                    b = int(couleur_orig[2] * (1 - factor) + couleur_cible[2] * factor)

                    # S'assurer que les valeurs sont dans la plage valide
                    clone["couleur"] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))]

                # Décaler légèrement la rotation initiale
                clone["angle_rotation_initial"] = (clone["angle_rotation_initial"] + rotation * i) % 360

                clones.append(clone)

            self.result = clones
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création des clones: {e}")
            print(f"Erreur détaillée: {e}")

    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy()


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

        # Options booléennes avec callbacks
        self.screen_vars['collision_sur_contact'] = tk.BooleanVar(value=self.config['ecran']['collision_sur_contact'])
        self.screen_vars['collision_sur_contact'].trace('w', self.on_screen_setting_changed)
        tk.Checkbutton(screen_frame, text="Collision sur contact",
                       variable=self.screen_vars['collision_sur_contact']).grid(row=row, column=0, columnspan=2,
                                                                                sticky="w")
        row += 1

        self.screen_vars['brisure_dans_ouverture'] = tk.BooleanVar(value=self.config['ecran']['brisure_dans_ouverture'])
        self.screen_vars['brisure_dans_ouverture'].trace('w', self.on_screen_setting_changed)
        tk.Checkbutton(screen_frame, text="Brisure dans ouverture",
                       variable=self.screen_vars['brisure_dans_ouverture']).grid(row=row, column=0, columnspan=2,
                                                                                 sticky="w")
        row += 1

        self.screen_vars['debug'] = tk.BooleanVar(value=self.config['ecran']['debug'])
        self.screen_vars['debug'].trace('w', self.on_screen_setting_changed)
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

        # Coefficients physiques
        physics_frame = ttk.LabelFrame(scrollable_balle_frame, text="Coefficients physiques", padding=5)
        physics_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)

        tk.Label(physics_frame, text="Coefficient rebondissement:").grid(row=0, column=0, sticky="w")
        self.balle_vars['coef_rebondissement'] = tk.DoubleVar(value=0.8)
        tk.Scale(physics_frame, from_=0.0, to=1.0, resolution=0.01, orient="horizontal",
                 variable=self.balle_vars['coef_rebondissement'], length=150).grid(row=0, column=1, padx=5)

        tk.Label(physics_frame, text="Coefficient gravité:").grid(row=1, column=0, sticky="w")
        self.balle_vars['coef_gravite'] = tk.DoubleVar(value=1.0)
        tk.Scale(physics_frame, from_=0.0, to=3.0, resolution=0.01, orient="horizontal",
                 variable=self.balle_vars['coef_gravite'], length=150).grid(row=1, column=1, padx=5)

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
        tk.Button(cercles_buttons_frame, text="🎭 Cloner avancé", command=self.duplicate_cercle,
                  bg="lightblue").pack(side="left", padx=2)

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
        """Crée l'onglet de prévisualisation amélioré"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👁️ Aperçu")

        # Créer un notebook pour séparer JSON et visualisation
        preview_notebook = ttk.Notebook(frame)
        preview_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Onglet JSON
        json_frame = ttk.Frame(preview_notebook)
        preview_notebook.add(json_frame, text="📄 Configuration JSON")

        # Zone de texte pour afficher la configuration JSON
        text_frame = ttk.LabelFrame(json_frame, text="Configuration JSON", padding=5)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Zone de texte avec scrollbar
        text_area_frame = tk.Frame(text_frame)
        text_area_frame.pack(fill="both", expand=True)

        self.preview_text = tk.Text(text_area_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar_preview = ttk.Scrollbar(text_area_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar_preview.set)

        self.preview_text.pack(side="left", fill="both", expand=True)
        scrollbar_preview.pack(side="right", fill="y")

        # Bouton de rafraîchissement JSON
        tk.Button(text_frame, text="🔄 Rafraîchir JSON", command=self.refresh_preview,
                  bg="lightblue").pack(pady=5)

        # Onglet Visualisation
        visual_frame = ttk.Frame(preview_notebook)
        preview_notebook.add(visual_frame, text="🎮 Visualisation t=0")

        # Frame pour la visualisation
        viz_frame = ttk.LabelFrame(visual_frame, text="Aperçu visuel de la configuration", padding=5)
        viz_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Canvas pour dessiner la prévisualisation
        canvas_frame = tk.Frame(viz_frame)
        canvas_frame.pack(fill="both", expand=True)

        self.visual_canvas = tk.Canvas(canvas_frame, bg="black", width=600, height=400)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.visual_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.visual_canvas.xview)

        self.visual_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.visual_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Contrôles de la visualisation
        controls_frame = tk.Frame(viz_frame)
        controls_frame.pack(fill="x", pady=5)

        tk.Button(controls_frame, text="🔄 Rafraîchir visualisation",
                  command=self.refresh_visual_preview, bg="lightgreen").pack(side="left", padx=5)

        # Échelle
        tk.Label(controls_frame, text="Échelle:").pack(side="left", padx=(20, 5))
        self.scale_var = tk.DoubleVar(value=0.5)
        tk.Scale(controls_frame, from_=0.1, to=2.0, resolution=0.1, orient="horizontal",
                 variable=self.scale_var, command=self.on_scale_change, length=150).pack(side="left")

        # Options d'affichage
        tk.Label(controls_frame, text="Affichage:").pack(side="left", padx=(20, 5))
        self.show_trajectories = tk.BooleanVar(value=True)
        tk.Checkbutton(controls_frame, text="Trajectoires",
                       variable=self.show_trajectories,
                       command=self.refresh_visual_preview).pack(side="left")

        self.show_vectors = tk.BooleanVar(value=True)
        tk.Checkbutton(controls_frame, text="Vecteurs vitesse",
                       variable=self.show_vectors,
                       command=self.refresh_visual_preview).pack(side="left")

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

    def on_scale_change(self, value=None):
        """Appelé quand l'échelle change"""
        self.refresh_visual_preview()

    def refresh_visual_preview(self):
        """Rafraîchit la prévisualisation visuelle"""
        self.visual_canvas.delete("all")

        # Récupérer les dimensions de l'écran configuré
        largeur_ecran = self.config["ecran"]["taille"][0]
        hauteur_ecran = self.config["ecran"]["taille"][1]
        couleur_fond = self.config["ecran"]["couleur_fond"]

        scale = self.scale_var.get()

        # Redimensionner le canvas
        canvas_width = int(largeur_ecran * scale)
        canvas_height = int(hauteur_ecran * scale)
        self.visual_canvas.configure(width=min(600, canvas_width),
                                     height=min(400, canvas_height),
                                     scrollregion=(0, 0, canvas_width, canvas_height))

        # Couleur de fond
        fond_hex = f"#{couleur_fond[0]:02x}{couleur_fond[1]:02x}{couleur_fond[2]:02x}"
        self.visual_canvas.configure(bg=fond_hex)

        # Dessiner les cercles
        for i, cercle in enumerate(self.config["cercles"]):
            x = cercle["position"][0] * scale
            y = cercle["position"][1] * scale
            rayon = cercle["rayon"] * scale
            couleur = cercle["couleur"]
            couleur_hex = f"#{couleur[0]:02x}{couleur[1]:02x}{couleur[2]:02x}"

            # Calculer les angles pour l'ouverture
            angle_rot = math.radians(cercle["angle_rotation_initial"])
            angle_ouverture = math.radians(cercle["angle_ouverture"])

            if cercle["angle_ouverture"] >= 360:
                # Cercle complet
                self.visual_canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon,
                                               outline=couleur_hex, width=3, fill="")
            else:
                # Dessiner le cercle complet en arrière-plan avec une couleur plus sombre
                dark_color = f"#{couleur[0] // 3:02x}{couleur[1] // 3:02x}{couleur[2] // 3:02x}"
                self.visual_canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon,
                                               outline=dark_color, width=1, fill="")

                # Dessiner la partie PLEINE (visible) - c'est la partie où les balles peuvent rebondir
                start_angle = math.degrees(angle_rot - angle_ouverture / 2)
                extent_angle = math.degrees(angle_ouverture)

                # La partie visible est celle qui n'est PAS l'ouverture
                if extent_angle < 360:
                    # Dessiner deux arcs pour représenter la partie solide
                    # Arc 1: de la fin de l'ouverture au début (dans le sens horaire)
                    solid_start = start_angle + extent_angle
                    solid_extent = 360 - extent_angle

                    if solid_extent > 0:
                        self.visual_canvas.create_arc(x - rayon, y - rayon, x + rayon, y + rayon,
                                                      start=solid_start, extent=solid_extent,
                                                      outline=couleur_hex, width=4, style="arc")

            # Marquer l'ouverture avec des lignes rouges si elle existe
            if cercle["angle_ouverture"] < 360:
                start_angle_rad = angle_rot - angle_ouverture / 2
                end_angle_rad = angle_rot + angle_ouverture / 2

                # Ligne de début d'ouverture
                start_x = x + rayon * math.cos(start_angle_rad)
                start_y = y + rayon * math.sin(start_angle_rad)
                self.visual_canvas.create_line(x, y, start_x, start_y, fill="red", width=2)

                # Ligne de fin d'ouverture
                end_x = x + rayon * math.cos(end_angle_rad)
                end_y = y + rayon * math.sin(end_angle_rad)
                self.visual_canvas.create_line(x, y, end_x, end_y, fill="red", width=2)

            # Étiquette du cercle avec info sur la vie
            life_info = f"C{i + 1} (vie:{cercle.get('life', 2)})"
            self.visual_canvas.create_text(x, y - rayon - 15, text=life_info,
                                           fill="white", font=("Arial", 8, "bold"))

        # Dessiner les balles (reste identique)
        for i, balle in enumerate(self.config["balles"]):
            x = balle["position"][0] * scale
            y = balle["position"][1] * scale
            taille = balle["taille"] * scale

            # Couleur ou image
            if balle.get("type_apparence", "couleur") == "couleur":
                couleur = balle["couleur"]
                couleur_hex = f"#{couleur[0]:02x}{couleur[1]:02x}{couleur[2]:02x}"
                self.visual_canvas.create_oval(x - taille, y - taille, x + taille, y + taille,
                                               fill=couleur_hex, outline="white", width=1)
            else:
                # Pour les images, dessiner un cercle avec motif
                self.visual_canvas.create_oval(x - taille, y - taille, x + taille, y + taille,
                                               fill="gray", outline="white", width=1)
                self.visual_canvas.create_text(x, y, text="IMG", fill="black", font=("Arial", 6))

            # Étiquette de la balle avec coefficients
            coef_r = balle.get("coef_rebondissement", 0.8)
            coef_g = balle.get("coef_gravite", 1.0)
            balle_info = f"B{i + 1} (r:{coef_r:.1f} g:{coef_g:.1f})"
            self.visual_canvas.create_text(x, y + taille + 10, text=balle_info,
                                           fill="white", font=("Arial", 8, "bold"))

            # Vecteur vitesse si activé
            if self.show_vectors.get():
                vx, vy = balle["vitesse"]
                # Normaliser le vecteur pour l'affichage
                factor = scale * 0.1
                end_x = x + vx * factor
                end_y = y + vy * factor

                self.visual_canvas.create_line(x, y, end_x, end_y,
                                               fill="yellow", width=2, arrow=tk.LAST)

            # Trajectoire approximative si activée
            if self.show_trajectories.get():
                vx, vy = balle["vitesse"]
                coef_grav = balle.get("coef_gravite", 1.0)

                # Simuler quelques points de trajectoire
                points = [x, y]
                curr_x, curr_y = x, y
                curr_vx, curr_vy = vx * scale * 0.1, vy * scale * 0.1

                for step in range(20):
                    curr_x += curr_vx
                    curr_y += curr_vy
                    curr_vy += coef_grav * 0.5  # Gravité approximative

                    points.extend([curr_x, curr_y])

                    # Arrêter si on sort de l'écran
                    if (curr_x < 0 or curr_x > canvas_width or
                            curr_y < 0 or curr_y > canvas_height):
                        break

                if len(points) > 4:
                    self.visual_canvas.create_line(points, fill="cyan", width=1,
                                                   dash=(2, 2), smooth=True)

        # Légende améliorée
        legend_y = 10
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text=f"Échelle: {scale:.1f}x",
                                       fill="white", font=("Arial", 10, "bold"))

        legend_y += 20
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text=f"Écran: {largeur_ecran}x{hauteur_ecran}",
                                       fill="white", font=("Arial", 8))

        legend_y += 15
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text=f"Balles: {len(self.config['balles'])}",
                                       fill="white", font=("Arial", 8))

        legend_y += 15
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text=f"Cercles: {len(self.config['cercles'])}",
                                       fill="white", font=("Arial", 8))

        # Légende des couleurs
        legend_y += 25
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text="Légende:", fill="yellow", font=("Arial", 8, "bold"))
        legend_y += 15
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text="• Trait épais: partie solide", fill="white", font=("Arial", 7))
        legend_y += 12
        self.visual_canvas.create_text(10, legend_y, anchor="nw",
                                       text="• Lignes rouges: ouverture", fill="red", font=("Arial", 7))

    # === MÉTHODES DE GESTION DES BALLES ===

    def add_balle(self):
        """Ajoute une nouvelle balle"""
        nouvelle_balle = {
            "position": [100, 100],
            "vitesse": [150, 100],
            "taille": 15,
            "type_apparence": "couleur",
            "couleur": [255, 255, 255],
            "image": "",
            "coef_rebondissement": 0.8,
            "coef_gravite": 1.0
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
            # S'assurer que les nouveaux coefficients sont présents
            if "coef_rebondissement" not in balle_originale:
                balle_originale["coef_rebondissement"] = 0.8
            if "coef_gravite" not in balle_originale:
                balle_originale["coef_gravite"] = 1.0
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

            # Coefficients physiques (avec valeurs par défaut)
            self.balle_vars['coef_rebondissement'].set(balle.get("coef_rebondissement", 0.8))
            self.balle_vars['coef_gravite'].set(balle.get("coef_gravite", 1.0))

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

            # S'assurer que les coefficients sont bien sauvegardés
            balle["coef_rebondissement"] = float(self.balle_vars['coef_rebondissement'].get())
            balle["coef_gravite"] = float(self.balle_vars['coef_gravite'].get())

            if balle["type_apparence"] == "couleur":
                balle["couleur"] = self.balle_color_picker.get_color()
                balle["image"] = ""
            else:
                balle["image"] = self.balle_vars['image'].get()
                balle["couleur"] = [255, 255, 255]  # Couleur par défaut

            self.refresh_balles_list()
            self.refresh_visual_preview()  # Mettre à jour la visualisation
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
            elif var_name == 'coef_rebondissement':
                var.set(0.8)
            elif var_name == 'coef_gravite':
                var.set(1.0)
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

            coef_r = balle.get("coef_rebondissement", 0.8)
            coef_g = balle.get("coef_gravite", 1.0)

            text = f"Balle {i + 1}: pos=({balle['position'][0]:.0f},{balle['position'][1]:.0f}) " \
                   f"v=({balle['vitesse'][0]:.0f},{balle['vitesse'][1]:.0f}) " \
                   f"taille={balle['taille']:.0f} rebond={coef_r:.2f} grav={coef_g:.2f} {app_info}"
            self.balles_listbox.insert(tk.END, text)

    # === MÉTHODES DE GESTION DES CERCLES ===

    def add_cercle(self):
        """Ajoute un nouveau cercle"""
        nouveau_cercle = {
            "position": [400, 300],
            "rayon": 80,
            "couleur": [255, 0, 0],
            "life": 2,  # Valeur par défaut correcte
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
        """Ouvre le dialogue de clonage avancé pour le cercle sélectionné"""
        if self.selected_cercle_index is not None:
            # IMPORTANT: Sauvegarder d'abord les modifications en cours
            self.save_cercle_changes()

            cercle_original = self.config["cercles"][self.selected_cercle_index]

            # S'assurer que la vie est définie
            if "life" not in cercle_original:
                cercle_original["life"] = 2

            # Ouvrir le dialogue de clonage
            dialog = CercleCloneDialog(self, cercle_original)
            self.root.wait_window(dialog.dialog)

            # Si des clones ont été créés, les ajouter
            if dialog.result:
                for clone in dialog.result:
                    # S'assurer que chaque clone a une vie définie
                    if "life" not in clone:
                        clone["life"] = cercle_original.get("life", 2)
                    self.config["cercles"].append(clone)

                self.refresh_cercles_list()
                messagebox.showinfo("Succès",
                                    f"{len(dialog.result)} cercle(s) cloné(s) avec succès !")

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
            cercle["life"] = int(self.cercle_vars['life'].get())  # S'assurer que c'est un entier
            cercle["couleur"] = self.cercle_color_picker.get_color()
            cercle["angle_ouverture"] = self.cercle_vars['angle_ouverture'].get()
            cercle["angle_rotation_initial"] = self.cercle_vars['angle_rotation_initial'].get()
            cercle["vitesse_rotation"] = self.cercle_vars['vitesse_rotation'].get()

            self.refresh_cercles_list()
            self.refresh_visual_preview()  # Mettre à jour la visualisation
            messagebox.showinfo("Succès", "Modifications sauvegardées !")

    def cancel_cercle_changes(self):
        """Annule les modifications du cercle"""
        if self.selected_cercle_index is not None:
            self.on_cercle_selected(None)

    def clear_cercle_fields(self):
        """Vide les champs d'édition de cercle"""
        for var_name, var in self.cercle_vars.items():
            if isinstance(var, tk.StringVar):
                var.set("")
            elif var_name == 'life':
                var.set(2)  # Valeur par défaut pour la vie
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

    def apply_screen_config(self, show_message=True):
        """Applique la configuration de l'écran"""
        self.config["ecran"]["taille"] = [self.screen_vars['largeur'].get(), self.screen_vars['hauteur'].get()]
        self.config["ecran"]["titre"] = self.screen_vars['titre'].get()
        self.config["ecran"]["fps"] = self.screen_vars['fps'].get()
        self.config["ecran"]["couleur_fond"] = self.screen_color_picker.get_color()
        self.config["ecran"]["collision_sur_contact"] = self.screen_vars['collision_sur_contact'].get()
        self.config["ecran"]["brisure_dans_ouverture"] = self.screen_vars['brisure_dans_ouverture'].get()
        self.config["ecran"]["debug"] = self.screen_vars['debug'].get()
        self.config["ecran"]["marge_suppression"] = self.screen_vars['marge_suppression'].get()

        if show_message:
            messagebox.showinfo("Succès", "Configuration de l'écran appliquée !")

    def on_screen_setting_changed(self, *args):
        """Appelé quand un paramètre d'écran change"""
        self.apply_screen_config(show_message=False)
        self.refresh_visual_preview()

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
        self.refresh_visual_preview()

    def launch_game(self):
        """Lance le jeu avec la configuration actuelle"""
        try:
            # Sauvegarder temporairement la config actuelle
            temp_config_path = os.path.join(self.config_dir, "_temp_config.json")

            # Appliquer TOUTES les modifications en cours
            self.apply_screen_config(show_message=False)

            # Appliquer les modifications de balle si une est sélectionnée
            if self.selected_balle_index is not None:
                self.save_balle_changes()

            # Appliquer les modifications de cercle si un est sélectionné
            if self.selected_cercle_index is not None:
                self.save_cercle_changes()

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