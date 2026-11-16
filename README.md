# Video Tracker — pointage de trajectoire sur vidéo

[![Tests](https://github.com/aleblanchard/video-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/aleblanchard/video-tracker/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)

Application de bureau en Python qui permet de relever, image par image et à la souris, la position d'un objet en mouvement dans une vidéo, puis d'afficher les courbes du mouvement et d'exporter les mesures au format CSV. Projet de groupe réalisé à l'Université de Bordeaux, avec une architecture **MVC**.

## Fonctionnalités

- Ouverture et lecture d'une vidéo, navigation image par image (⏪ ⬅ ▶ ➡ ⏩)
- **Échelle** : deux clics droits sur la vidéo, puis saisie de la distance réelle entre les deux points
- **Origine du repère** : clic molette (axe X vers la droite, axe Y vers le haut)
- **Pointage** : un clic gauche par image, la vidéo avance automatiquement ; fin automatique à la dernière image ou avec `Échap`
- Graphiques **y(x)**, **x(t)** et **y(t)** avec Matplotlib
- Tableau des valeurs (temps, X, Y) dans une fenêtre séparée
- Export **CSV** (séparateur point-virgule)
- Raccourcis clavier : `Ctrl+O` ouvrir, `Ctrl+Q` lire, `Ctrl+S` enregistrer, `Ctrl+X` quitter

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Tkinter doit être disponible (inclus avec Python sous Windows et macOS ; sous Debian/Ubuntu : `sudo apt install python3-tk`).

## Utilisation

```bash
cd src
python3 Application.py
```

Ouvrez ensuite une vidéo via **Fichier → Ouvrir** (`Ctrl+O`). Le dossier `resources/videos/` est prévu pour y déposer vos propres vidéos.

## Tests

```bash
pip install pytest
python3 -m pytest tests
```

## Structure

```
src/
├── Application.py        # point d'entrée (fenêtre Tkinter)
├── controllers/          # Controller : lien entre la vue et le modèle
├── models/               # Video, Point, FileRepo (export CSV)
└── views/                # interface Tkinter et graphiques
tests/                    # tests unitaires (unittest / pytest)
docs/                     # cahier des charges
```

## Auteurs

- **Alexis Blanchard**
- **Hugo Carvalho Pereira**
- **Yanis Floch**
