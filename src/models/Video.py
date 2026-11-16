from math import hypot
from tkinter import Frame, Button, NW, messagebox, simpledialog

import time

import cv2
import PIL.Image
import PIL.ImageTk


class Video:
    """Modèle de la vidéo : lecture, navigation image par image, repère,
    échelle et points relevés.

    Toutes les coordonnées stockées (origine, échelle, points) sont en pixels
    de la vidéo d'origine. L'affichage peut être réduit (``self.zoom``) pour
    que la vidéo tienne à l'écran : les clics sont convertis avec
    ``canvas_to_video``.
    """

    def __init__(self):
        self.cap = None
        self.filename = None
        self.width = 0
        self.height = 0
        self.fps = 25.0
        self.delay = 40
        self.total_frames = 0
        self.zoom = 1.0
        self.max_display_size = None   # (largeur, hauteur) disponibles à l'écran

        self.pause = True
        self.index_courant = 0
        self._next_pos = 0             # index de l'image que renverra cap.read()
        self._after_id = None
        self._frame_rgb = None
        self.photo = None

        self.button_frame = None
        self.btn_play_pause = None
        self.on_pointing_end = None    # appelé quand le pointage atteint la fin

        self.origin_point = None
        self.echelle = 1.0             # unités réelles par pixel
        self.echelle_definie = False
        self.scale_points = []         # 0, 1 ou 2 points (en pixels vidéo)

        self.liste_points = []
        self.liste_frame = []

    # ------------------------------------------------------------------ #
    # Ouverture et lecture des images
    # ------------------------------------------------------------------ #
    @property
    def is_loaded(self):
        return self.cap is not None and self.cap.isOpened()

    def open_file(self, path, canv, wind):
        """Ouvre une vidéo et affiche sa première image. Renvoie True si OK."""
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier vidéo.")
            return False

        self.stop(wind)
        self.release()
        self.cap = cap
        self.filename = path
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        self.fps = float(fps) if fps and fps > 0 else 25.0
        self.delay = max(1, int(round(1000 / self.fps)))
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Nouvelle vidéo : on repart de zéro
        self.pause = True
        self.index_courant = 0
        self._next_pos = 0
        self.origin_point = None
        self.echelle = 1.0
        self.echelle_definie = False
        self.scale_points = []
        self.liste_points = []
        self.liste_frame = []

        self.zoom = self._compute_zoom()
        canv.config(width=int(self.width * self.zoom), height=int(self.height * self.zoom))

        if not self.button_frame:
            self.create_buttons(wind, canv)
        self._set_play_button(playing=False)
        self.show_frame(canv)
        return True

    def _compute_zoom(self):
        if not self.max_display_size or not self.width or not self.height:
            return 1.0
        max_w, max_h = self.max_display_size
        return min(1.0, max_w / self.width, max_h / self.height)

    def _read_frame(self, index):
        """Lit l'image ``index`` (lecture séquentielle quand c'est possible, plus rapide)."""
        if not self.is_loaded or index < 0:
            return None
        if index != self._next_pos:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self._next_pos = -1        # position inconnue : on se repositionnera
            return None
        self._next_pos = index + 1
        return frame

    def show_frame(self, canv, index=None):
        """Affiche l'image ``index`` (par défaut l'image courante). Renvoie False si illisible."""
        if index is None:
            index = self.index_courant
        frame = self._read_frame(index)
        if frame is None:
            return False
        self.index_courant = index
        self._frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.redraw(canv)
        return True

    def redraw(self, canv):
        """Redessine l'image courante et les annotations (repère, échelle, points)."""
        canv.delete("all")
        if self._frame_rgb is not None:
            image = PIL.Image.fromarray(self._frame_rgb)
            if self.zoom != 1.0:
                size = (max(1, int(self.width * self.zoom)), max(1, int(self.height * self.zoom)))
                image = image.resize(size, PIL.Image.BILINEAR)
            self.photo = PIL.ImageTk.PhotoImage(image=image)
            canv.create_image(0, 0, image=self.photo, anchor=NW)
        self.draw_scale(canv)
        self.origin(canv)
        self.place_points(canv)
        total = f"/{self.total_frames}" if self.total_frames else ""
        canv.create_text(9, 9, anchor=NW, fill="black", font=("TkDefaultFont", 11, "bold"),
                         text=f"Image {self.index_courant + 1}{total}   t = {self.frame_time(self.index_courant):.3f} s",
                         tags="info")
        canv.create_text(8, 8, anchor=NW, fill="white", font=("TkDefaultFont", 11, "bold"),
                         text=f"Image {self.index_courant + 1}{total}   t = {self.frame_time(self.index_courant):.3f} s",
                         tags="info")

    # ------------------------------------------------------------------ #
    # Boutons et lecture
    # ------------------------------------------------------------------ #
    def create_buttons(self, wind, canv):
        self.button_frame = Frame(wind)
        self.button_frame.pack(side='bottom', pady=(0, 10))

        def bouton(texte, action):
            # takefocus=0 : sinon la barre espace « clique » aussi le bouton qui a le focus
            return Button(self.button_frame, text=texte, command=action,
                          width=4, font=("TkDefaultFont", 16), takefocus=0)

        self.btn_first = bouton("⇤", lambda: self.first_frame(canv, wind))
        self.btn_previous = bouton("←", lambda: self.previous_frame(canv, wind))
        self.btn_play_pause = bouton("▶", lambda: self.toggle_play_pause(canv, wind))
        self.btn_next = bouton("→", lambda: self.next_frame(canv, wind))
        self.btn_last = bouton("⇥", lambda: self.last_frame(canv, wind))
        for b in (self.btn_first, self.btn_previous, self.btn_play_pause, self.btn_next, self.btn_last):
            b.pack(side='left')

        wind.bind("<Control-Left>", lambda event: self.first_frame(canv, wind))
        wind.bind("<Left>", lambda event: self.previous_frame(canv, wind))
        wind.bind("<space>", lambda event: self.toggle_play_pause(canv, wind))
        wind.bind("<Right>", lambda event: self.next_frame(canv, wind))
        wind.bind("<Control-Right>", lambda event: self.last_frame(canv, wind))

    def _set_play_button(self, playing):
        if self.btn_play_pause is not None:
            # En pause, le bouton propose de lire la vidéo ; pendant la lecture, de la mettre en pause
            self.btn_play_pause["text"] = "❚❚" if playing else "▶"

    def stop(self, wind=None):
        """Met la vidéo en pause et annule la lecture programmée."""
        self.pause = True
        if self._after_id is not None and wind is not None:
            try:
                wind.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None
        self._set_play_button(playing=False)

    def toggle_play_pause(self, canv, wind):
        if not self.is_loaded:
            return
        if self.pause:
            if self.is_last_frame():
                self.restart_video()   # relance depuis le début si on est à la fin
            self.pause = False
            self._set_play_button(playing=True)
            self.play_video(canv, wind)
        else:
            self.stop(wind)

    def play_video(self, canv, wind):
        """Affiche l'image suivante puis se reprogramme tant que la lecture continue."""
        self._after_id = None
        if self.pause or not self.is_loaded:
            return
        debut = time.perf_counter()
        if self.show_frame(canv, self.index_courant + 1):
            # on retire le temps de décodage/affichage pour respecter la cadence de la vidéo
            ecoule = int((time.perf_counter() - debut) * 1000)
            self._after_id = wind.after(max(1, self.delay - ecoule), lambda: self.play_video(canv, wind))
            return
        # Plus d'image : fin de la vidéo
        self._fix_total_frames()
        self.stop(wind)
        if messagebox.askquestion("Fin de la vidéo", "Voulez-vous rejouer la vidéo ?") == "yes":
            self.restart_video()
            self.toggle_play_pause(canv, wind)

    def restart_video(self):
        """Revient juste avant la première image (la lecture affichera l'image 0)."""
        self.index_courant = -1

    def _fix_total_frames(self):
        # Le nombre d'images annoncé par certains fichiers est faux : on le corrige
        if self.total_frames == 0 or self.index_courant + 1 < self.total_frames:
            self.total_frames = self.index_courant + 1

    # ------------------------------------------------------------------ #
    # Navigation image par image
    # ------------------------------------------------------------------ #
    def previous_frame(self, canv, wind):
        if not self.is_loaded:
            return
        self.stop(wind)
        if self.index_courant > 0:
            self.show_frame(canv, self.index_courant - 1)
        else:
            messagebox.showinfo("Début de la vidéo", "Début de la vidéo atteint.")

    def next_frame(self, canv, wind, silent=False):
        """Passe à l'image suivante. Renvoie False si la fin est atteinte."""
        if not self.is_loaded:
            return False
        self.stop(wind)
        if self.show_frame(canv, self.index_courant + 1):
            return True
        self._fix_total_frames()
        self.show_frame(canv)
        if not silent:
            messagebox.showinfo("Fin de la vidéo", "Fin de la vidéo atteinte.")
        return False

    def is_last_frame(self):
        return bool(self.total_frames) and self.index_courant >= self.total_frames - 1

    def first_frame(self, canv, wind):
        if not self.is_loaded:
            return
        self.stop(wind)
        self.show_frame(canv, 0)

    def last_frame(self, canv, wind):
        if not self.is_loaded:
            return
        self.stop(wind)
        index = self.total_frames - 1
        # On recule tant que l'image n'est pas lisible (nombre d'images parfois surestimé)
        while index > self.index_courant and not self.show_frame(canv, index):
            index -= 1
            self.total_frames = index + 1

    # ------------------------------------------------------------------ #
    # Repère, échelle et points
    # ------------------------------------------------------------------ #
    def canvas_to_video(self, x, y):
        return x / self.zoom, y / self.zoom

    def video_to_canvas(self, x, y):
        return x * self.zoom, y * self.zoom

    def origin(self, canv):
        if self.origin_point:
            x, y = self.video_to_canvas(*self.origin_point)
            bleu = "#1e90ff"
            canv.create_line(x, y, x + 40, y, fill=bleu, width=2, arrow="last", tags="origine")
            canv.create_line(x, y, x, y - 40, fill=bleu, width=2, arrow="last", tags="origine")
            canv.create_text(x + 46, y, text="x", fill=bleu, anchor="w", tags="origine")
            canv.create_text(x, y - 48, text="y", fill=bleu, tags="origine")
            canv.create_oval(x - 4, y - 4, x + 4, y + 4, fill=bleu, outline="white", tags="origine")

    def set_origin(self, canv, event):
        if not self.is_loaded:
            return
        self.origin_point = self.canvas_to_video(event.x, event.y)
        self.redraw(canv)

    def draw_scale(self, canv):
        vert = "#00c853"
        pts = [self.video_to_canvas(*p) for p in self.scale_points]
        if len(pts) == 2:
            (x0, y0), (x1, y1) = pts
            canv.create_line(x0, y0, x1, y1, fill=vert, width=2, tags="echelle")
            if self.echelle_definie:
                longueur = self.echelle * self.pixel_distance(*self.scale_points)
                canv.create_text((x0 + x1) / 2, (y0 + y1) / 2 - 12, fill=vert,
                                 text=f"{longueur:g} m", font=("TkDefaultFont", 11, "bold"),
                                 tags="echelle")
        for x, y in pts:
            canv.create_oval(x - 3, y - 3, x + 3, y + 3, fill=vert, outline="white", tags="echelle")

    @staticmethod
    def pixel_distance(p0, p1):
        return hypot(p1[0] - p0[0], p1[1] - p0[1])

    def scale_click(self, canv, event):
        """Clic droit : 1er clic = premier point, 2e clic = second point puis saisie de la distance."""
        if not self.is_loaded:
            return
        point = self.canvas_to_video(event.x, event.y)
        if len(self.scale_points) != 1:
            # nouveau tracé d'échelle (remplace l'éventuel précédent)
            self.scale_points = [point]
            self.redraw(canv)
            return

        self.scale_points.append(point)
        self.redraw(canv)
        pixels = self.pixel_distance(*self.scale_points)
        if pixels == 0:
            messagebox.showwarning("Échelle", "Les deux points sont confondus : recommencez.")
            self.scale_points = []
            self.redraw(canv)
            return

        distance = self.ask_distance()
        if distance is None:          # annulé : on garde l'échelle précédente
            self.scale_points = []
        else:
            self.echelle = distance / pixels
            self.echelle_definie = True
        self.redraw(canv)

    def ask_distance(self):
        """Demande la longueur réelle ; renvoie un nombre > 0, ou None si l'utilisateur annule."""
        while True:
            saisie = simpledialog.askstring(
                "Échelle des longueurs",
                "Distance réelle entre les deux points (en mètres) :")
            if saisie is None:
                return None
            try:
                distance = float(saisie.strip().replace(",", "."))
            except ValueError:
                distance = 0
            if distance > 0:
                return distance
            messagebox.showerror("Échelle", "Entrez un nombre positif, par exemple 1.5")

    def place_points(self, canv):
        coords = [self.video_to_canvas(x, y) for x, y in self.liste_points]
        if len(coords) > 1:
            canv.create_line(*[c for xy in coords for c in xy], fill="#ff5252", width=1, tags="point")
        for frame, (x, y) in zip(self.liste_frame, coords):
            couleur = "yellow" if frame == self.index_courant else "#ff1744"
            canv.create_oval(x - 4, y - 4, x + 4, y + 4, fill=couleur, outline="white", tags="point")

    def place_point_next_frame(self, canv, wind, event):
        """Clic gauche en mode édition : relève la position puis avance d'une image."""
        if not self.is_loaded:
            return
        if self.origin_point is None:
            messagebox.showwarning("Attention",
                                   "Définissez d'abord l'origine du repère (clic molette).")
            return
        point = self.canvas_to_video(event.x, event.y)
        if self.index_courant in self.liste_frame:
            # l'image a déjà un point : on le remplace
            self.liste_points[self.liste_frame.index(self.index_courant)] = point
        else:
            self.liste_frame.append(self.index_courant)
            self.liste_points.append(point)
            # garde les points dans l'ordre chronologique
            ordre = sorted(range(len(self.liste_frame)), key=self.liste_frame.__getitem__)
            self.liste_frame = [self.liste_frame[i] for i in ordre]
            self.liste_points = [self.liste_points[i] for i in ordre]

        if self.is_last_frame() or not self.next_frame(canv, wind, silent=True):
            self.redraw(canv)
            if self.on_pointing_end:
                self.on_pointing_end()

    def resetList(self, canv):
        self.liste_points.clear()
        self.liste_frame.clear()
        if self.is_loaded:
            self.redraw(canv)

    # ------------------------------------------------------------------ #
    # Données
    # ------------------------------------------------------------------ #
    def frame_time(self, frame):
        return max(frame, 0) / self.fps if self.fps else 0.0

    @property
    def unite(self):
        return "m" if self.echelle_definie else "px"

    def to_real(self, x, y):
        """Pixels vidéo -> coordonnées dans le repère (x vers la droite, y vers le haut)."""
        ox, oy = self.origin_point if self.origin_point else (0, self.height)
        return (x - ox) * self.echelle, (oy - y) * self.echelle

    def get_points_data(self):
        """Points bruts : (x en pixels, y en pixels, numéro d'image)."""
        return [(x, y, frame) for (x, y), frame in zip(self.liste_points, self.liste_frame)]

    def get_measures(self):
        """Mesures dans le repère choisi : liste de (t en s, x, y)."""
        mesures = []
        for (x, y), frame in zip(self.liste_points, self.liste_frame):
            rx, ry = self.to_real(x, y)
            mesures.append((self.frame_time(frame), rx, ry))
        return mesures

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __del__(self):
        try:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
