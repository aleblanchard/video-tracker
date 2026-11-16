from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from models.FileRepo import FileRepo
import numpy as np


class Controller:

    def __init__(self, video, view):
        self.video = video
        self.view = view
        self.file_repo = FileRepo()
        self.editionMode = False


        self.view.set_menu_callbacks(
            ouvrir_fichier_callback=self.ouvrir_fichier,
            save_callback=self.save,
            exit_callback=self.exit_program,
            edition_callback=self.edition,
            about_callback=self.about,
            resetpoint_callback=self.resetPoint,
            tableau_callback=self.tableau,
            affiche_graphs_callback = self.affiche_graphs
        )

        self.view.window.bind_all("<Control-o>", self.ouvrir_fichier_shortcut)
        self.view.window.bind_all("<Control-s>", self.save_shortcut)
        self.view.window.bind_all("<Control-x>", self.exit_program_shortcut)
        self.view.window.bind_all("<Control-q>", self.loadplay_file_shortcut)


        self.bind_escape_key()
        self.bind_edit_mode_shortcuts()
    
    def bind_escape_key(self):
        if self.editionMode:
            self.view.window.bind_all('<Escape>', self.switchEditionOff)
        else:
            self.view.window.unbind_all('<Escape>')

    def bind_edit_mode_shortcuts(self):
        if self.editionMode:
            self.view.canvas.bind("<Button-1>", lambda event: self.video.place_point_next_frame(self.view.canvas, self.view.window, event))
            self.view.canvas.bind("<Button-2>", lambda event: self.video.set_origin(self.view.canvas, event))
            self.view.canvas.bind("<Button-3>", lambda event: self.video.echelle1(self.view.canvas,event))

        else:
            self.view.canvas.unbind("<Button-1>")
            self.view.canvas.unbind("<Button-2>")
            self.view.canvas.unbind("<Button-3>")




    def switchEditionOff(self, event=None) : 
        self.view.editionModeOFF()
        self.editionMode = False
        self.bind_escape_key()
        self.bind_edit_mode_shortcuts()


    def loadplay_file_shortcut(self, event):
        self.loadplay_file()

    def ouvrir_fichier_shortcut(self, event):
        self.ouvrir_fichier()

    def save_shortcut(self, event):
        self.save()

    def exit_program_shortcut(self, event):
        self.on_exit()


    def loadplay_file(self):
        self.ouvrir_fichier()
        if self.video.cap.isOpened():
            self.view.window.event_generate('<space>')
    
    def ouvrir_fichier(self):
        file = askopenfilename(title="Choisissez le fichier à ouvrir",
                               filetypes=[("Vidéo MP4", ".mp4"), ("Vidéo AVI", ".avi"), ("Vidéo MOV", ".mov"), ("All files", ".*")])
        if file:
            self.view.delete_text()
            self.video.open_file(file, self.view.canvas, self.view.window)

    def save(self):
        self.file_repo.ecrire(self.video.liste_frame, self.video.liste_points)
        messagebox.showinfo("Sauvegardé", "Les données d'acquisition ont été sauvegardées avec succès.")

    def on_exit(self):
        choice = messagebox.askyesnocancel("Quitter", "Voulez-vous enregistrer avant de quitter?")
        if choice is None:
            return
        elif choice:
            self.save()
        self.view.quit()

    def exit_program(self):
        result = messagebox.askquestion("Exit", "Êtes-vous sûr de vouloir quitter l'application ?", icon='warning')
        if result == 'yes':
            self.view.window.destroy()

    def edition(self):
        if self.editionMode:
            self.switchEditionOff()
        else:
            messagebox.showinfo("Édition",
            """Vous êtes en mode édition :
- Clic molette pour définir l'origine.
- Clic gauche pour placer des points.
- Deux clics droits pour définir l'échelle
- Appuyez sur Échap pour quitter le mode édition""")
            self.editionMode = True
            self.bind_escape_key()
            self.bind_edit_mode_shortcuts()

    def about(self):
        messagebox.showinfo("Video Tracker", "Voici comment utiliser ce programme :\n Clic droit = Définir l'echelle ;Clic du milieu = Définir l'origine ; Clic gauche = Place les points")



    def resetPoint(self):
        self.video.resetList(self.view.canvas)

    def tableau(self):
        data = self.video.get_points_data()
        self.view.afficher_tab(data)

    def affiche_graphs(self):
        data = self.video.get_points_data()
        ech = self.video.echelle
        org = self.video.origin_point
        t = np.arange(len(data))
        xarr = np.array([ech*(point[0] - org[0]) for point in data])
        yarr = np.array([ech*((self.video.height - point[1])-org[1]) for point in data])
        self.view.affiche_graphs(t, xarr, yarr)