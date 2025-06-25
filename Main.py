# -*- coding: utf-8 -*-
"""
Point d'entrée ultra-simple pour lancer le jeu Bounce
"""
import sys
import os


def main():
    """Point d'entrée principal avec choix simple"""
    print("🎮 Bounce Game - Lanceur")
    print("=" * 30)

    if len(sys.argv) > 1:
        # Si un argument est fourni, essayer de le lancer directement
        arg = sys.argv[1].lower()

        if arg == "editor":
            # Lancer l'éditeur
            try:
                from ConfigEditor import main as editor_main
                editor_main()
            except ImportError:
                print("❌ Éditeur non disponible (ConfigEditor.py manquant)")
        else:
            # Lancer le jeu avec l'argument fourni
            from Launcher import main as launcher_main
            launcher_main()
    else:
        # Mode interactif simplifié
        print("Que voulez-vous faire ?")
        print("1. 🎯 Jouer (configurations JSON)")
        print("2. 🎨 Éditeur de configuration")
        print("3. ❌ Quitter")

        choix = input("\nVotre choix [1-3]: ").strip()

        if choix == "1":
            from Launcher import main as launcher_main
            launcher_main()

        elif choix == "2":
            try:
                from ConfigEditor import main as editor_main
                editor_main()
            except ImportError:
                print("❌ Éditeur non disponible (ConfigEditor.py manquant)")

        elif choix == "3":
            print("👋 Au revoir !")

        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    main()