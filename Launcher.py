# -*- coding: utf-8 -*-
"""
Lanceur simple pour le jeu Bounce
"""
from Screen import Screen
from Balle import Balle
from Cercle import Cercle
import sys
import json
import os


def creer_objets_depuis_config_json(screen, config):
    """Crée les objets du jeu à partir d'une configuration JSON"""
    # Créer les balles
    for balle_config in config.get("balles", []):
        # Gestion de la couleur (RGB ou string)
        couleur = balle_config.get("couleur", [255, 255, 255])
        if isinstance(couleur, str):
            # Convertir les couleurs string en RGB
            couleur_map = {
                "white": [255, 255, 255], "black": [0, 0, 0], "red": [255, 0, 0],
                "green": [0, 255, 0], "blue": [0, 0, 255], "yellow": [255, 255, 0],
                "cyan": [0, 255, 255], "magenta": [255, 0, 255], "orange": [255, 165, 0]
            }
            couleur = couleur_map.get(couleur, [255, 255, 255])

        # Gestion de l'apparence
        type_apparence = balle_config.get("type_apparence", "couleur")
        image = balle_config.get("image", "") if type_apparence == "image" else None

        balle = Balle(
            position=balle_config["position"],
            vitesse=balle_config["vitesse"],
            taille=balle_config["taille"],
            couleur=couleur,
            image=image
        )
        screen.ajouter_objet(balle)

    # Créer les cercles
    for cercle_config in config.get("cercles", []):
        # Gestion de la couleur (RGB ou string)
        couleur = cercle_config.get("couleur", [255, 0, 0])
        if isinstance(couleur, str):
            couleur_map = {
                "white": [255, 255, 255], "black": [0, 0, 0], "red": [255, 0, 0],
                "green": [0, 255, 0], "blue": [0, 0, 255], "yellow": [255, 255, 0],
                "cyan": [0, 255, 255], "magenta": [255, 0, 255], "orange": [255, 165, 0],
                "purple": [128, 0, 128], "brown": [165, 42, 42], "pink": [255, 192, 203],
                "gray": [128, 128, 128]
            }
            couleur = couleur_map.get(couleur, [255, 0, 0])

        cercle = Cercle(
            position=cercle_config["position"],
            rayon=cercle_config["rayon"],
            angle_ouverture=cercle_config.get("angle_ouverture", 0),
            couleur=couleur,
            life=cercle_config.get("life", 1),
            angle_rotation_initial=cercle_config.get("angle_rotation_initial", 0),
            vitesse_rotation=cercle_config.get("vitesse_rotation", 0)
        )
        screen.ajouter_objet(cercle)


def creer_objets_depuis_config_simple(screen, objets_config):
    """Crée les objets du jeu à partir de l'ancienne configuration simple"""
    for obj_config in objets_config:
        if obj_config["type"] == "balle":
            balle = Balle(
                position=obj_config["position"],
                vitesse=obj_config["vitesse"],
                taille=obj_config["taille"],
                couleur=obj_config["couleur"]
            )
            screen.ajouter_objet(balle)

        elif obj_config["type"] == "cercle":
            cercle = Cercle(
                position=obj_config["position"],
                rayon=obj_config["rayon"],
                angle_ouverture=obj_config.get("angle_ouverture", 0),
                couleur=obj_config["couleur"],
                life=obj_config.get("life", 1)
            )
            screen.ajouter_objet(cercle)


def lancer_jeu_depuis_fichier(fichier_config):
    """Lance le jeu à partir d'un fichier de configuration JSON"""
    try:
        with open(fichier_config, 'r', encoding='utf-8') as f:
            config = json.load(f)

        ecran_config = config.get("ecran", {})

        # Gestion de la couleur de fond
        couleur_fond = ecran_config.get("couleur_fond", [0, 0, 0])
        if isinstance(couleur_fond, str):
            couleur_map = {"black": [0, 0, 0], "white": [255, 255, 255], "gray": [128, 128, 128]}
            couleur_fond = couleur_map.get(couleur_fond, [0, 0, 0])

        print(f"\n🚀 Lancement depuis: {os.path.basename(fichier_config)}")
        print(f"   Titre: {ecran_config.get('titre', 'Bounce Game')}")
        print(f"   Taille: {ecran_config.get('taille', [800, 600])}")
        print(f"   Balles: {len(config.get('balles', []))}")
        print(f"   Cercles: {len(config.get('cercles', []))}")
        print("   Appuyez sur la croix pour quitter")
        print("   Bon jeu ! 🎯\n")

        # Créer l'écran de jeu
        screen = Screen(
            taille=ecran_config.get("taille", [800, 600]),
            couleur_fond=couleur_fond,
            titre=ecran_config.get("titre", "Bounce Game"),
            collision_sur_contact=ecran_config.get("collision_sur_contact", True),
            brisure_dans_ouverture=ecran_config.get("brisure_dans_ouverture", False)
        )

        # Ajouter les objets
        creer_objets_depuis_config_json(screen, config)

        # Lancer la boucle de jeu
        screen.boucle(fps=ecran_config.get("fps", 60))

    except FileNotFoundError:
        print(f"❌ Fichier de configuration '{fichier_config}' introuvable")
    except json.JSONDecodeError:
        print(f"❌ Erreur de format JSON dans '{fichier_config}'")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")


def lancer_jeu_depuis_config_rapide(nom_config=None):
    """Lance le jeu avec les configurations rapides (anciennes)"""
    # Configurations rapides intégrées
    CONFIGS = {
        "classique": {
            "titre": "Bounce - Classique",
            "taille_ecran": (800, 600),
            "couleur_fond": "black",
            "collision_sur_contact": True,
            "brisure_dans_ouverture": False,
            "fps": 60,
            "objets": [
                {"type": "balle", "position": [100, 100], "vitesse": [200, 150], "taille": 10, "couleur": "white"},
                {"type": "balle", "position": [200, 200], "vitesse": [-150, 200], "taille": 8, "couleur": "yellow"},
                {"type": "cercle", "position": [400, 300], "rayon": 80, "angle_ouverture": 0, "couleur": "red",
                 "life": 3},
                {"type": "cercle", "position": [600, 200], "rayon": 60, "angle_ouverture": 90, "couleur": "blue",
                 "life": 2},
            ]
        },

        "arcade": {
            "titre": "Bounce - Arcade",
            "taille_ecran": (1000, 700),
            "couleur_fond": "navy",
            "collision_sur_contact": True,
            "brisure_dans_ouverture": False,
            "fps": 60,
            "objets": [
                {"type": "balle", "position": [50, 50], "vitesse": [300, 200], "taille": 12, "couleur": "lime"},
                {"type": "balle", "position": [100, 150], "vitesse": [250, -180], "taille": 10, "couleur": "cyan"},
                {"type": "balle", "position": [150, 250], "vitesse": [-200, 250], "taille": 8, "couleur": "magenta"},
                {"type": "cercle", "position": [500, 200], "rayon": 100, "angle_ouverture": 60, "couleur": "red",
                 "life": 5},
                {"type": "cercle", "position": [300, 400], "rayon": 70, "angle_ouverture": 120, "couleur": "green",
                 "life": 3},
            ]
        }
    }

    def afficher_configs():
        print("\n🎮 Configurations rapides disponibles:")
        print("=" * 40)
        for nom, config in CONFIGS.items():
            nb_balles = len([obj for obj in config["objets"] if obj["type"] == "balle"])
            nb_cercles = len([obj for obj in config["objets"] if obj["type"] == "cercle"])
            print(f"• {nom.upper():<12} - {nb_balles} balle(s), {nb_cercles} cercle(s)")
        print("=" * 40)

    def choisir_config():
        afficher_configs()
        while True:
            choix = input("\nQuelle configuration voulez-vous ? ").strip().lower()
            if choix in CONFIGS:
                return choix
            elif choix in ['quit', 'q', 'exit']:
                return None
            else:
                configs_dispo = ", ".join(CONFIGS.keys())
                print(f"❌ Configuration inconnue. Choisissez parmi: {configs_dispo}")

    # Si aucune config spécifiée, demander à l'utilisateur
    if nom_config is None:
        nom_config = choisir_config()
        if nom_config is None:
            print("👋 Au revoir !")
            return

    # Vérifier que la config existe
    if nom_config not in CONFIGS:
        print(f"❌ Configuration '{nom_config}' introuvable. Utilisation de 'classique'.")
        nom_config = "classique"

    # Récupérer la configuration
    config = CONFIGS[nom_config]

    print(f"\n🚀 Lancement de: {config['titre']}")
    print(f"   Taille: {config['taille_ecran']}")
    print(f"   Mode collision: {'Contact' if config['collision_sur_contact'] else 'Perçage'}")
    print("   Appuyez sur la croix pour quitter")
    print("   Bon jeu ! 🎯\n")

    # Créer l'écran de jeu
    screen = Screen(
        taille=config["taille_ecran"],
        couleur_fond=config["couleur_fond"],
        titre=config["titre"],
        collision_sur_contact=config["collision_sur_contact"],
        brisure_dans_ouverture=config["brisure_dans_ouverture"]
    )

    # Ajouter les objets
    creer_objets_depuis_config_simple(screen, config["objets"])

    # Lancer la boucle de jeu
    try:
        screen.boucle(fps=config["fps"])
    except KeyboardInterrupt:
        print("\n👋 Jeu interrompu par l'utilisateur")


def lister_configs_disponibles():
    """Liste les configurations JSON disponibles"""
    config_dir = "CONFIGS"
    if not os.path.exists(config_dir):
        print("❌ Dossier CONFIGS introuvable")
        return []

    configs = []
    for file in os.listdir(config_dir):
        if file.endswith('.json') and not file.startswith('_'):
            configs.append(file)

    return sorted(configs)


def main():
    """Point d'entrée principal"""
    print("🎮 Bienvenue dans Bounce!")

    # Vérifier si un fichier de config a été passé en argument
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Si c'est un fichier JSON, le charger directement
        if arg.endswith('.json'):
            if os.path.exists(arg):
                lancer_jeu_depuis_fichier(arg)
            else:
                # Essayer dans le dossier CONFIGS
                fichier_dans_configs = os.path.join("CONFIGS", arg)
                if os.path.exists(fichier_dans_configs):
                    lancer_jeu_depuis_fichier(fichier_dans_configs)
                else:
                    print(f"❌ Fichier '{arg}' introuvable")
        else:
            # Configuration rapide
            lancer_jeu_depuis_config_rapide(arg.lower())
    else:
        # Mode interactif
        print("\nOptions disponibles:")
        print("1. Configurations rapides (classique, arcade)")
        print("2. Configurations JSON personnalisées")

        configs_json = lister_configs_disponibles()
        if configs_json:
            print("\nConfigurations JSON disponibles:")
            for i, config in enumerate(configs_json, 1):
                print(f"   {i}. {config}")

        choix = input("\nVoulez-vous utiliser une config rapide (r) ou JSON (j) ? [r/j]: ").strip().lower()

        if choix == 'j' and configs_json:
            print("\nConfigurations JSON:")
            for i, config in enumerate(configs_json, 1):
                print(f"{i}. {config}")

            try:
                num = int(input("Numéro de la configuration: ")) - 1
                if 0 <= num < len(configs_json):
                    fichier = os.path.join("CONFIGS", configs_json[num])
                    lancer_jeu_depuis_fichier(fichier)
                else:
                    print("❌ Numéro invalide")
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")
        else:
            lancer_jeu_depuis_config_rapide()


if __name__ == "__main__":
    main()