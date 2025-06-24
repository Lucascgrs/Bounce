# -*- coding: utf-8 -*-
"""
Lanceur simple pour le jeu Bounce
"""
from Screen import Screen
from Balle import Balle
from Cercle import Cercle
import sys


def creer_objets_depuis_config(screen, objets_config):
    """Crée les objets du jeu à partir de la configuration"""
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


def lancer_jeu(nom_config=None):
    """Lance le jeu avec la configuration choisie"""

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
    config = get_config(nom_config)

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
    creer_objets_depuis_config(screen, config["objets"])

    # Lancer la boucle de jeu
    try:
        screen.boucle(fps=config["fps"])
    except KeyboardInterrupt:
        print("\n👋 Jeu interrompu par l'utilisateur")


def main():
    """Point d'entrée principal"""
    print("🎮 Bienvenue dans Bounce!")

    # Vérifier si une config a été passée en argument
    if len(sys.argv) > 1:
        nom_config = sys.argv[1].lower()
        lancer_jeu(nom_config)
    else:
        lancer_jeu()


if __name__ == "__main__":
    main()