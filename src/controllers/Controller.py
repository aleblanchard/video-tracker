from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os

from models.FileRepo import FileRepo


AIDE = """Utilisation :

1. Fichier > Ouvrir (Ctrl+O) pour charger une vidéo.
2. Éditer > Mode édition, puis sur la vidéo :
   • clic molette : définir l'origine du repère ;
   • deux clics droits : tracer l'échelle, puis saisir la distance réelle ;
   • clic gauche : pointer l'objet (la vidéo avance d'une image).
   Échap termine le pointage (il s'arrête aussi à la dernière image).
3. Afficher > tableau ou graphiques pour voir les mesures.
4. Fichier > Sauvegarder (Ctrl+S) pour exporter en CSV.

Navigation : boutons ⇤ ← ▶ → ⇥, flèches du clavier (Ctrl+flèche : début/fin) et barre espace."""


class Controller:

    def __init__(self, video, view):
        self.video = video
        self.view = view
        self.file_repo = FileRepo()
        self.editionMode = False
        self.unsaved = False
        self.video.on_pointing_end = self.pointing_finished

        self.view.set_menu_callbacks(
            ouvrir_fichier_callback=self.ouvrir_fichier,
            save_callback=self.save,
            exit_callback=self.on_exit,
            edition_callback=self.edition,
            about_callback=self.about,
            resetpoint_callback=self.resetPoint,
            tableau_callback=self.tableau,
            affiche_graphs_callback=self.affiche_graphs
        )

        self.view.window.bind_all("<Control-o>", self.ouvrir_fichier_shortcut)
        self.view.window.bind_all("<Control-s>", self.save_shortcut)
        self.view.window.bind_all("<Control-x>", self.exit_program_shortcut)
        self.view.window.bind_all("<Control-q>", self.loadplay_file_shortcut)

        # Boutons de la souris : sous macOS, clic droit et clic molette sont inversés
        aqua = self.view.window.tk.call("tk", "windowingsystem") == "aqua"
        self.btn_droit = "<Button-2>" if aqua else "<Button-3>"
        self.btn_molette = "<Button-3>" if aqua else "<Button-2>"

        self.bind_escape_key()
        self.bind_edit_mode_shortcuts()

    # ------------------------------------------------------------------ #
    # Mode édition (origine, échelle, pointage)
    # ------------------------------------------------------------------ #
    def bind_escape_key(self):
        if self.editionMode:
            self.view.window.bind_all('<Escape>', self.switchEditionOff)
        else:
            self.view.window.unbind_all('<Escape>')

    def bind_edit_mode_shortcuts(self):
        canvas = self.view.canvas
        if self.editionMode:
            canvas.bind("<Button-1>", self.on_left_click)
            canvas.bind(self.btn_molette, lambda event: self.video.set_origin(canvas, event))
            canvas.bind(self.btn_droit, lambda event: self.video.scale_click(canvas, event))
            canvas.config(cursor="crosshair")
        else:
            for b in ("<Button-1>", "<Button-2>", "<Button-3>"):
                canvas.unbind(b)
            canvas.config(cursor="")
        self.view.set_edition_status(self.editionMode)

    def on_left_click(self, event):
        nb = len(self.video.liste_points)
        self.video.place_point_next_frame(self.view.canvas, self.view.window, event)
        if len(self.video.liste_points) >= nb and self.video.liste_points:
            self.unsaved = True

    def switchEditionOn(self):
        self.editionMode = True
        self.bind_escape_key()
        self.bind_edit_mode_shortcuts()

    def switchEditionOff(self, event=None, message="Vous avez quitté le mode édition."):
        if not self.editionMode:
            return
        self.editionMode = False
        self.bind_escape_key()
        self.bind_edit_mode_shortcuts()
        self.view.editionModeOFF(message)

    def pointing_finished(self):
        self.switchEditionOff(message="Dernière image atteinte : le pointage est terminé.")

    def edition(self):
        if self.editionMode:
            self.switchEditionOff()
            return
        if not self.video.is_loaded:
            messagebox.showwarning("Édition", "Chargez d'abord une vidéo (Fichier > Ouvrir).")
            return
        messagebox.showinfo("Édition",
                            "Vous êtes en mode édition :\n"
                            "- Clic molette pour définir l'origine.\n"
                            "- Deux clics droits pour définir l'échelle.\n"
                            "- Clic gauche pour placer des points.\n"
                            "- Appuyez sur Échap pour quitter le mode édition.")
        self.switchEditionOn()

    # ------------------------------------------------------------------ #
    # Fichier
    # ------------------------------------------------------------------ #
    def loadplay_file_shortcut(self, event):
        self.loadplay_file()

    def ouvrir_fichier_shortcut(self, event):
        self.ouvrir_fichier()

    def save_shortcut(self, event):
        self.save()

    def exit_program_shortcut(self, event):
        self.on_exit()

    def loadplay_file(self):
        """Ctrl+Q : lit la vidéo (en demandant d'abord un fichier si aucun n'est chargé)."""
        if not self.video.is_loaded and not self.ouvrir_fichier():
            return
        self.video.toggle_play_pause(self.view.canvas, self.view.window)

    def ouvrir_fichier(self):
        if self.unsaved and not self.confirm_discard():
            return False
        file = askopenfilename(title="Choisissez le fichier à ouvrir",
                               filetypes=[("Vidéos", "*.mp4 *.avi *.mov *.mkv *.MP4 *.AVI *.MOV"),
                                          ("Tous les fichiers", "*.*")])
        if not file:
            return False
        return self.open_path(file)

    def open_path(self, file):
        if self.editionMode:
            self.switchEditionOff(message="Nouvelle vidéo chargée : mode édition désactivé.")
        self.video.max_display_size = self.view.available_video_size()
        if self.video.open_file(file, self.view.canvas, self.view.window):
            self.view.delete_text()
            self.view.window.title(f"Video Tracker — {os.path.basename(file)}")
            self.unsaved = False
            return True
        return False

    def confirm_discard(self):
        """Demande quoi faire des points non enregistrés. Renvoie False si l'utilisateur annule."""
        choice = messagebox.askyesnocancel("Points non enregistrés",
                                           "Voulez-vous enregistrer les points relevés ?")
        if choice is None:
            return False
        if choice:
            return self.save()
        return True

    def save(self):
        if not self.video.liste_points:
            messagebox.showwarning("Sauvegarde", "Aucun point à enregistrer.")
            return False
        base = os.path.splitext(os.path.basename(self.video.filename or "mesures"))[0]
        filename = asksaveasfilename(title="Enregistrer les mesures",
                                     defaultextension=".csv",
                                     initialfile=f"{base}_mesures.csv",
                                     filetypes=[("Fichier CSV", "*.csv")])
        if not filename:
            return False
        try:
            self.file_repo.ecrire_mesures(filename, self.video.get_measures(), self.video.unite)
        except OSError as e:
            messagebox.showerror("Sauvegarde", f"Impossible d'écrire le fichier :\n{e}")
            return False
        self.unsaved = False
        messagebox.showinfo("Sauvegardé", f"Les mesures ont été enregistrées dans :\n{filename}")
        return True

    def on_exit(self):
        if self.unsaved and self.video.liste_points:
            if not self.confirm_discard():
                return
        else:
            if not messagebox.askokcancel("Quitter", "Voulez-vous quitter Video Tracker ?"):
                return
        self.video.stop(self.view.window)
        self.video.release()
        self.view.window.destroy()

    # Ancien nom conservé
    exit_program = on_exit

    def about(self):
        messagebox.showinfo("Video Tracker", AIDE)

    # ------------------------------------------------------------------ #
    # Données
    # ------------------------------------------------------------------ #
    def resetPoint(self):
        if self.video.liste_points and not messagebox.askyesno(
                "Réinitialiser", "Supprimer tous les points relevés ?"):
            return
        self.video.resetList(self.view.canvas)
        self.unsaved = False

    def tableau(self):
        self.view.afficher_tab(self.video.get_measures(), self.video.unite)

    def affiche_graphs(self):
        mesures = self.video.get_measures()
        if len(mesures) < 2:
            messagebox.showinfo("Graphiques", "Placez au moins deux points pour afficher les graphiques.")
            return
        t = [m[0] for m in mesures]
        xarr = [m[1] for m in mesures]
        yarr = [m[2] for m in mesures]
        self.view.affiche_graphs(t, xarr, yarr, self.video.unite)
