from tkinter import Frame, Canvas, Menu, Label, Toplevel, Scrollbar, messagebox, VERTICAL, RIGHT, Y, BOTH, LEFT
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class View(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.window = parent

        self.status = Label(self.window, anchor="w", padx=8)
        self.status.pack(side="top", fill="x")

        self.canvas = Canvas(self.window, width=640, height=360, highlightthickness=0, bg="#202020")
        self.canvas.pack(pady=(4, 6))
        self.text_id = self.canvas.create_text(
            320, 180, fill="white", font=("TkDefaultFont", 14),
            text="Chargez une vidéo : Fichier > Ouvrir (Ctrl+O)")

        self.menu_bar = Menu(self.window)
        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_editer = Menu(self.menu_bar, tearoff=0)
        self.menu_aide = Menu(self.menu_bar, tearoff=0)
        self.menu_afficher = Menu(self.menu_bar, tearoff=0)

        self.controller = None
        self.create_menu()
        self.window.config(menu=self.menu_bar)
        self.set_edition_status(False)

    def create_menu(self):
        self.menu_bar.add_cascade(label="Fichier", menu=self.menu_file)
        self.menu_bar.add_cascade(label="Afficher", menu=self.menu_afficher)
        self.menu_bar.add_cascade(label="Éditer", menu=self.menu_editer)
        self.menu_bar.add_cascade(label="Aide", menu=self.menu_aide)

    def set_menu_callbacks(self, ouvrir_fichier_callback, save_callback, exit_callback, edition_callback,
                           about_callback, resetpoint_callback, tableau_callback, affiche_graphs_callback):
        self.menu_file.add_command(label="Ouvrir", accelerator="Ctrl+O", command=ouvrir_fichier_callback)
        self.menu_file.add_command(label="Sauvegarder", accelerator="Ctrl+S", command=save_callback)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Quitter", accelerator="Ctrl+X", command=exit_callback)

        self.menu_editer.add_command(label="Mode édition", command=edition_callback)
        self.menu_editer.add_command(label="Réinitialiser les points", command=resetpoint_callback)

        self.menu_afficher.add_command(label="Afficher tableau valeurs", command=tableau_callback)
        self.menu_afficher.add_command(label="Afficher graphiques", command=affiche_graphs_callback)

        self.menu_aide.add_command(label="À propos", command=about_callback)

    def setController(self, controller):
        self.controller = controller

    def available_video_size(self):
        """Place disponible pour la vidéo (écran moins menus, boutons et marges)."""
        self.window.update_idletasks()
        return (self.window.winfo_screenwidth() - 80, self.window.winfo_screenheight() - 220)

    def delete_text(self):
        self.canvas.delete(self.text_id)

    def set_edition_status(self, active):
        if active:
            self.status.config(text="MODE ÉDITION — clic molette : origine · 2 clics droits : échelle · "
                                    "clic gauche : pointer · Échap : terminer",
                               bg="#ffe082", fg="black")
        else:
            self.status.config(text="Lecture — Éditer > Mode édition pour relever des points",
                               bg=self.window.cget("bg"), fg="black")

    def editionModeOFF(self, message="Vous avez quitté le mode édition."):
        messagebox.showinfo("Information", message)

    def afficher_tab(self, mesures, unite="m"):
        table_window = Toplevel(self.window)
        table_window.title("Tableau des valeurs")
        table_window.geometry("460x420")

        if not mesures:
            Label(table_window, text="Vous n'avez placé aucun point", padx=20, pady=20).pack()
            return

        colonnes = ("t", "x", "y")
        tree = ttk.Treeview(table_window, columns=colonnes, show="headings")
        for col, titre in zip(colonnes, ("t (s)", f"x ({unite})", f"y ({unite})")):
            tree.heading(col, text=titre)
            tree.column(col, anchor="e", width=140)
        for t, x, y in mesures:
            tree.insert("", "end", values=(f"{t:.3f}", f"{x:.4f}", f"{y:.4f}"))

        vbar = Scrollbar(table_window, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vbar.set)
        vbar.pack(side=RIGHT, fill=Y)
        tree.pack(side=LEFT, fill=BOTH, expand=True)

    def affiche_graphs(self, t, xarr, yarr, unite="m"):
        graph_window = Toplevel(self.window)
        graph_window.title("Graphiques")

        fig = Figure(figsize=(14, 4.5), dpi=90)
        axs = fig.subplots(1, 3)

        axs[0].plot(xarr, yarr, marker='o', linestyle='-', color='g')
        axs[0].set_title('y(x)')
        axs[0].set_xlabel(f'x ({unite})')
        axs[0].set_ylabel(f'y ({unite})')

        axs[1].plot(t, xarr, marker='o', linestyle='-', color='r')
        axs[1].set_title('x(t)')
        axs[1].set_xlabel('t (s)')
        axs[1].set_ylabel(f'x ({unite})')

        axs[2].plot(t, yarr, marker='o', linestyle='-', color='b')
        axs[2].set_title('y(t)')
        axs[2].set_xlabel('t (s)')
        axs[2].set_ylabel(f'y ({unite})')

        for ax in axs:
            ax.grid(True, alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        NavigationToolbar2Tk(canvas, graph_window).update()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
