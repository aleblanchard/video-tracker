import os
import sys
import tkinter as tk

# Permet de lancer l'application depuis n'importe quel dossier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.view import View
from models.Video import Video
from controllers.Controller import Controller


class Application(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Video Tracker')
        self.geometry("1280x800")
        self.minsize(700, 500)
        try:
            if self.tk.call("tk", "windowingsystem") == "x11":
                self.attributes('-zoomed', True)
            else:
                self.state('zoomed')
        except tk.TclError:
            pass   # gestionnaire de fenêtres sans mode « agrandi »

        self.video = Video()
        self.view = View(self)
        self.controller = Controller(self.video, self.view)
        self.view.setController(self.controller)

        self.protocol("WM_DELETE_WINDOW", self.controller.on_exit)


def main():
    app = Application()
    if len(sys.argv) > 1:   # vidéo passée en argument : python Application.py ma_video.mp4
        app.after(100, lambda: app.controller.open_path(sys.argv[1]))
    app.mainloop()


if __name__ == '__main__':
    main()
