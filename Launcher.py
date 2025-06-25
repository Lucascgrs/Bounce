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
        if type_apparence == "image" and balle_config.get("image"):
            image = os.path.join("Images", balle_config.get("image"))
        else:
            image = None

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

        # CORRECTION : Mapper angle_rotation_initial du JSON vers angle_rotation de la classe
        cercle = Cercle(
            position=cercle_config["position"],
            rayon=cercle_config["rayon"],
            angle_ouverture=cercle_config.get("angle_ouverture", 0),
            couleur=couleur,
            life=cercle_config.get("life", 1),
            angle_rotation=cercle_config.get("angle_rotation_initial", 0),  # Mapping JSON → classe
            vitesse_rotation=cercle_config.get("vitesse_rotation", 0)
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
            print(f"❌ Format de fichier non supporté. Utilisez un fichier .json")
    else:
        # Mode interactif - seulement les configs JSON
        configs_json = lister_configs_disponibles()

        if not configs_json:
            print("❌ Aucune configuration JSON trouvée dans le dossier CONFIGS/")
            return

        print("\n📁 Configurations JSON disponibles:")
        for i, config in enumerate(configs_json, 1):
            print(f"   {i}. {config}")

        try:
            num = int(input("\nNuméro de la configuration à lancer: ")) - 1
            if 0 <= num < len(configs_json):
                fichier = os.path.join("CONFIGS", configs_json[num])
                lancer_jeu_depuis_fichier(fichier)
            else:
                print("❌ Numéro invalide")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide")
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")


if __name__ == "__main__":
    main()