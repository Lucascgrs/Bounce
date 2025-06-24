 ```markdown
# 🎮 Bounce Game

Un jeu de rebonds de balles avec éditeur de configuration graphique intégré !

## 📋 Table des matières

- [🚀 Installation](#-installation)
- [🎯 Lancement rapide](#-lancement-rapide)
- [🎨 Éditeur de configuration](#-éditeur-de-configuration)
- [⚙️ Configurations](#️-configurations)
- [📁 Structure des fichiers](#-structure-des-fichiers)
- [🎮 Commandes](#-commandes)
- [🔧 Personnalisation](#-personnalisation)

---

## 🚀 Installation

### Prérequis
- Python 3.7+
- Pygame
- Tkinter (inclus avec Python)
- PIL/Pillow (pour l'éditeur)

### Installation des dépendances
```bash
pip install pygame pillow
```

### Téléchargement
```bash
git clone https://github.com/Lucascgrs/Bounce.git
cd Bounce
```

---

## 🎯 Lancement rapide

### 🎮 Jouer immédiatement
```bash
python Main.py
```
Puis choisir l'option **1** pour les configurations rapides.

### 🎨 Éditeur de configuration
```bash
python Main.py editor
```

### 🚀 Lancement direct
```bash
# Configurations rapides
python Main.py classique
python Main.py arcade

# Configuration personnalisée
python Main.py ma_config.json
```

---

## 🎨 Éditeur de configuration

L'éditeur graphique permet de créer des configurations de jeu personnalisées.

### Interface principale

#### 🖥️ Onglet Écran
- **Taille** : Largeur et hauteur de la fenêtre
- **Titre** : Titre affiché dans la barre
- **FPS** : Images par seconde (30-120)
- **Couleur de fond** : Sélecteur RGB avec historique
- **Options de gameplay** :
  - Collision sur contact
  - Brisure dans ouverture
  - Mode debug

#### ⚽ Onglet Balles
- **Position** : Coordonnées X,Y de départ
- **Vitesse** : Vecteur de déplacement
- **Taille** : Rayon de la balle
- **Apparence** :
  - Couleur RGB (avec sélecteur)
  - Image (depuis le dossier `Images/`)
- **Actions** :
  - ➕ Ajouter
  - ❌ Supprimer
  - 📋 Dupliquer
  - 🎯 Centrer

#### ⭕ Onglet Cercles
- **Position** : Centre du cercle
- **Propriétés** :
  - Rayon
  - Points de vie
- **Angles** :
  - Ouverture (0° = cercle complet)
  - Rotation initiale
  - Vitesse de rotation
- **Couleur** : Sélecteur RGB

#### 👁️ Onglet Aperçu
- Visualisation JSON de la configuration
- Rafraîchissement en temps réel

### Barre d'outils
- **📁 Nouveau** : Configuration vierge
- **💾 Sauvegarder** : Exporter en JSON
- **📂 Charger** : Importer une config
- **🔄 Rafraîchir** : Actualiser les listes
- **🚀 Lancer le jeu** : Test immédiat

---

## ⚙️ Configurations

### 🏃‍♂️ Configurations rapides (intégrées)

#### Classique
- 2 balles, 2 cercles
- Mode normal avec rebonds
- 800x600, 60 FPS

#### Arcade
- 3+ balles rapides
- Cercles variés
- 1000x700, action intense

### 📄 Configurations JSON (personnalisées)

Stockées dans le dossier `CONFIGS/`. Format :

```json
{
  "ecran": {
    "taille": [1200, 800],
    "couleur_fond": [0, 0, 0],
    "titre": "Ma Configuration",
    "fps": 60,
    "collision_sur_contact": true,
    "brisure_dans_ouverture": false
  },
  "balles": [
    {
      "position": [100, 100],
      "vitesse": [200, 150],
      "taille": 15,
      "type_apparence": "couleur",
      "couleur": [255, 255, 255]
    }
  ],
  "cercles": [
    {
      "position": [400, 300],
      "rayon": 80,
      "couleur": [255, 0, 0],
      "life": 3,
      "angle_ouverture": 60,
      "vitesse_rotation": 30
    }
  ]
}
```

---

## 📁 Structure des fichiers

```
Bounce/
├── 📄 Main.py              # Point d'entrée principal
├── 📄 Launcher.py          # Lanceur de jeu
├── 📄 ConfigEditor.py      # Éditeur graphique
├── 📄 Screen.py            # Gestion de l'écran
├── 📄 Balle.py             # Classe Balle
├── 📄 Cercle.py            # Classe Cercle
├── 📄 Particule.py         # Effets de particules
├── 📄 README.md            # Ce fichier
├── 📁 CONFIGS/             # Configurations JSON
│   ├── config1.json
│   └── config2.json
├── 📁 Images/              # Images pour les balles
│   ├── ball1.png
│   └── ball2.png
└── 📁 conf_app/            # Données de l'éditeur
    └── colors.json         # Historique des couleurs
```

---

## 🎮 Commandes

### En jeu
- **❌ Fermer** : Quitter le jeu
- **Souris** : Observer les interactions

### Dans l'éditeur
- **Ctrl+S** : Sauvegarder
- **Ctrl+O** : Ouvrir
- **Ctrl+N** : Nouveau
- **F5** : Lancer le jeu

---

## 🔧 Personnalisation

### 🎨 Ajouter des images de balles
1. Placez vos images dans le dossier `Images/`
2. Formats supportés : PNG, JPG, JPEG, GIF, BMP
3. Dans l'éditeur : onglet **Balles** → **Image** → 🔄 Actualiser

### 🎯 Créer une configuration
1. Lancez l'éditeur : `python Main.py editor`
2. Configurez l'écran, ajoutez balles et cercles
3. Sauvegardez : **💾 Sauvegarder**
4. Testez : **🚀 Lancer le jeu**

### 🌈 Couleurs personnalisées
- Utilisez le sélecteur RGB
- Sauvegardez vos couleurs favorites
- Historique automatique dans `conf_app/colors.json`

### ⚡ Configurations de gameplay

#### Mode Perçage
```json
"collision_sur_contact": false,
"brisure_dans_ouverture": true
```
Les balles percent les cercles.

#### Mode Contact
```json
"collision_sur_contact": true,
"brisure_dans_ouverture": false
```
Les balles rebondissent sur les cercles.

---

## 🎯 Exemples d'utilisation

### Scénario 1 : Découverte
```bash
python Main.py
# Choisir option 1 → "classique"
```

### Scénario 2 : Création personnalisée
```bash
python Main.py editor
# Créer sa config → Sauvegarder → Lancer
```

### Scénario 3 : Partage de configuration
```bash
# Créer ma_config.json avec l'éditeur
python Main.py ma_config.json
```

---

## 🐛 Dépannage

### Erreur "Module not found"
```bash
pip install pygame pillow
```

### L'éditeur ne se lance pas
Vérifiez que Tkinter est installé :
```python
import tkinter
print("Tkinter OK")
```

### Images non affichées
- Vérifiez le dossier `Images/`
- Formats supportés : PNG, JPG, JPEG, GIF, BMP
- Cliquez sur 🔄 Actualiser dans l'éditeur

### Configuration corrompue
Supprimez le fichier JSON problématique et recréez-le.

---

## 🎉 Astuces pro

### 🎨 Design efficace
- Utilisez des couleurs contrastées
- Évitez trop d'objets (performance)
- Testez différentes vitesses

### ⚡ Performance
- FPS optimal : 60-75
- Taille écran raisonnable : 800x600 à 1200x800
- Limiter les particules si lag

### 🎯 Gameplay intéressant
- Mélangez cercles pleins et arcs
- Variez les vitesses de rotation
- Créez des "labyrinthes" avec les ouvertures

---

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/Lucascgrs/Bounce/issues)
- **Créateur** : @Lucascgrs
- **Version** : 2024.1

---

**🎮 Amusez-vous bien avec Bounce Game ! 🎯**
```