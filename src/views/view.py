from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename 
from models.Video import Video
import matplotlib.pyplot as plt
import numpy as np

class View(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.window = parent
        self.canvas = Canvas(width=100, height=100)
        self.canvas.pack()

        self.video = Video()

        self.menu_bar = Menu(self)
        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_editer = Menu(self.menu_bar, tearoff=0)
        self.menu_aide = Menu(self.menu_bar, tearoff=0)
        self.menu_afficher = Menu(self.menu_bar, tearoff=0)
        self.menu_afficher_valeurs = Menu(self.menu_afficher, tearoff=0)

        self.new_callback = None
        self.ouvrir_fichier_callback = None
        self.save_callback = None
        self.about_callback = None
        self.exit_callback = None
        self.origine_callback = None
        self.tableau_callback = None
        self.resetpoint_callback = None
        
        self.create_menu()
        self.window.config(menu=self.menu_bar)
        self.button_frame = Frame(self)
        self.button_frame.pack()

        self.Milieu = Canvas(self.window)
        self.text_id = self.Milieu.create_text((150, 50), text="Chargez une vidéo")
        self.Milieu.pack()

        self.fig, self.axs = plt.subplots(1, 3, figsize=(15, 10))

    def create_menu(self):
        self.menu_bar.add_cascade(label="Fichier", menu=self.menu_file)
        self.menu_bar.add_cascade(label="Afficher", menu=self.menu_afficher)
        self.menu_bar.add_cascade(label="Éditer", menu=self.menu_editer)
        self.menu_bar.add_cascade(label="Aide", menu=self.menu_aide)
        


    def set_menu_callbacks(self, ouvrir_fichier_callback, save_callback,exit_callback, edition_callback,about_callback, resetpoint_callback, tableau_callback,affiche_graphs_callback):
        self.ouvrir_fichier_callback = ouvrir_fichier_callback
        self.save_callback = save_callback
        self.about_callback = about_callback
        self.exit_callback = exit_callback
        self.edition_callback = edition_callback
        self.resetpoint_callback = resetpoint_callback
        self.tableau_callback = tableau_callback
        self.affiche_graphs_callback = affiche_graphs_callback

        self.menu_file.add_command(label="Ouvrir", command=self.ouvrir_fichier_callback)
        self.menu_file.add_command(label="Sauvegarder", command=self.save_callback)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Quitter", command=self.exit_callback)

        self.menu_editer.add_command(label="Mode Édition", command=self.edition_callback)
        self.menu_editer.add_command(label="Réinitialiser les points", command=self.resetpoint_callback)

        self.menu_afficher.add_command(label="Afficher tableau valeurs", command=self.tableau_callback)
        self.menu_afficher.add_command(label="Afficher graphiques", command=self.affiche_graphs_callback)

        self.menu_aide.add_command(label="À Propos", command=self.about_callback)
    
    def setController(self, controller):
        self.controller = controller

    def delete_text(self):
        self.Milieu.delete(self.text_id)

    def editionModeOFF(self):
        messagebox.showinfo("Information", "Vous avez quitté le mode édition.")

    def afficher_tab(self, liste_points):
        table_window = Toplevel(self.window)
        table_window.title("Tableau des valeurs")

        table_canvas = Canvas(table_window)
        vbar = Scrollbar(table_window, orient=VERTICAL, command=table_canvas.yview)
        hbar = Scrollbar(table_window, orient=HORIZONTAL, command=table_canvas.xview)
        table_canvas.config(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        vbar.pack(side=RIGHT, fill=Y)
        hbar.pack(side=BOTTOM, fill=X)
        table_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        table_frame = Frame(table_canvas)
        table_canvas.create_window((0, 0), window=table_frame, anchor="nw")


        def on_configure(event):
            table_canvas.configure(scrollregion=table_canvas.bbox('all'))

        table_frame.bind("<Configure>", on_configure)

        if not liste_points:
            aucun_point = Label(table_frame, text="Vous n'avez placé aucun point")
            aucun_point.pack()
        else:
            titre = ("x", "y", "Frame")
            for c, colonne in enumerate(titre):
                tab = Entry(table_frame, width=20, fg='black', font=('Arial', 16, 'bold'))
                tab.grid(row=0, column=c)
                tab.insert(END, colonne)

            for i, (x, y, frame) in enumerate(liste_points, start=1):
                tab_x = Entry(table_frame, width=20, fg='black', font=('Arial', 16, 'bold'))
                tab_x.grid(row=i, column=0)
                tab_x.insert(END, x)
                
                tab_y = Entry(table_frame, width=20, fg='black', font=('Arial', 16, 'bold'))
                tab_y.grid(row=i, column=1)
                tab_y.insert(END, y)
                
                tab_frame = Entry(table_frame, width=20, fg='black', font=('Arial', 16, 'bold'))
                tab_frame.grid(row=i, column=2)
                tab_frame.insert(END, frame)          



    def affiche_graphs(self, t, xarr, yarr):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        graph_window = Toplevel(self.window)
        graph_window.title("Graphiques")

        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        axs[0].plot(t, xarr, marker='o', linestyle='-', color='r')
        axs[0].set_title('Graphe x(t)')
        axs[0].set_xlabel('t')
        axs[0].set_ylabel('x')

        axs[1].plot(t, yarr, marker='o', linestyle='-', color='b')
        axs[1].set_title('Graphe y(t)')
        axs[1].set_xlabel('t')
        axs[1].set_ylabel('y')

        axs[2].plot(xarr, yarr, marker='o', linestyle='-', color='g')
        axs[2].set_title('Graphe y(x)')
        axs[2].set_xlabel('x')
        axs[2].set_ylabel('y')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def affiche_graphs_callback(self):
        data = self.video.get_points_data()
        t = np.arange(len(data))
        xarr = np.array([point[0] for point in data])
        yarr = np.array([self.video.height - point[1] for point in data])
        self.affiche_graphs(t, xarr, yarr)




