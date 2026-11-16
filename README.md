# Video Tracker — pointage de trajectoire sur vidéo

[![Tests](https://github.com/aleblanchard/video-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/aleblanchard/video-tracker/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)

Application de bureau en Python qui permet de relever, image par image et à la souris, la position d'un objet en mouvement dans une vidéo, puis d'afficher les courbes du mouvement et d'exporter les mesures au format CSV. Projet de groupe réalisé à l'Université de Bordeaux, avec une architecture **MVC**.

## Fonctionnalités

- Ouverture d'une vidéo (MP4, AVI, MOV, MKV) et lecture à sa vitesse réelle
- Navigation image par image : boutons ⇤ ← ▶ → ⇥, flèches du clavier, `Ctrl+←` / `Ctrl+→` pour aller au début ou à la fin, barre espace pour lecture/pause
- Affichage du numéro d'image et du temps écoulé
- **Origine du repère** : clic molette (axe x vers la droite, axe y vers le haut)
- **Échelle** : deux clics droits sur un objet de longueur connue, puis saisie de la distance réelle en mètres (`0.5` ou `0,5`)
- **Pointage** : un clic gauche par image, la vidéo avance automatiquement ; fin automatique à la dernière image ou avec `Échap`. Cliquer à nouveau sur une image déjà pointée remplace le point.
- Tableau des mesures **t (s), x, y** dans le repère choisi, en mètres (ou en pixels si aucune échelle n'est définie)
- Graphiques **y(x)**, **x(t)** et **y(t)** avec Matplotlib (zoom et export d'image possibles)
- Export **CSV** (séparateur point-virgule)
- Grandes vidéos réduites automatiquement pour tenir à l'écran, sans perte de précision sur les mesures
- Avertissement avant de quitter ou d'ouvrir une autre vidéo si des points ne sont pas enregistrés

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Tkinter doit être disponible (inclus avec Python sous Windows et macOS ; sous Debian/Ubuntu : `sudo apt install python3-tk`).

## Utilisation

```bash
python3 src/Application.py                                   # puis Fichier > Ouvrir
python3 src/Application.py resources/videos/exemple_chute.mp4  # ouvre directement une vidéo
```

Exemple de relevé avec la vidéo fournie (`exemple_chute.mp4`, la barre noire mesure 1 m) :

1. **Éditer > Mode édition**.
2. Clic molette sur l'extrémité gauche de la barre noire : c'est l'origine.
3. Clic droit sur chaque extrémité de la barre, puis saisissez `1`.
4. Clic gauche sur la balle à chaque image. Arrêtez avec `Échap` quand vous voulez.
5. **Afficher > Afficher graphiques** pour voir la trajectoire, **Fichier > Sauvegarder** (`Ctrl+S`) pour l'export.

| Raccourci | Action |
| --- | --- |
| `Ctrl+O` | Ouvrir une vidéo |
| `Ctrl+Q` | Lire / mettre en pause |
| `Ctrl+S` | Enregistrer les mesures en CSV |
| `Ctrl+X` | Quitter |
| `Espace` | Lecture / pause |
| `←` / `→` | Image précédente / suivante |
| `Ctrl+←` / `Ctrl+→` | Première / dernière image |
| `Échap` | Terminer le pointage |

Sous macOS, le clic droit et le clic molette sont gérés automatiquement (Tk les inverse sur ce système).

### Format du fichier CSV

```
t (s);x (m);y (m)
0.0000;0.0987;1.2000
0.0333;0.1493;1.2613
```

## Tests

```bash
pip install pytest
python3 -m pytest tests
```

Les tests utilisent une petite vidéo générée à la volée (lecture, navigation, échelle, pointage, mesures, export CSV).

## Structure

```
src/
├── Application.py        # point d'entrée (fenêtre Tkinter)
├── controllers/          # Controller : lien entre la vue et le modèle
├── models/               # Video, Point, FileRepo (export CSV)
└── views/                # interface Tkinter et graphiques
tests/                    # tests unitaires (pytest)
resources/videos/         # vidéo d'exemple
docs/                     # cahier des charges
```

## Auteurs

- **Alexis Blanchard**
- **Hugo Carvalho Pereira**
- **Yanis Floch**
