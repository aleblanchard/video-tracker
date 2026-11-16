import tkinter as tk


from views.view import *
from models.Video import *
from controllers.Controller import *
import platform

platform.system()
class Application(tk.Tk):

    def __init__(self):

        super().__init__()
        self.title('Video Tracker')
        self.geometry("1600x800")
        if platform.system() == "Linux" :
            self.attributes('-zoomed', True)
        else:
            self.state('zoomed')
            
        self.video = Video()
        self.view = View(self)
        self.controller = Controller(self.video, self.view)
        
        self.view.pack()
        self.view.setController(self.controller)

        button_frame_container = tk.Frame(self)
        button_frame_container.pack()
        
        self.button_frame = tk.Frame(button_frame_container)
        self.button_frame.grid(row=0, column=0, columnspan=3)

        self.protocol("WM_DELETE_WINDOW", self.controller.on_exit)


if __name__ == '__main__':
    app = Application()
    app.mainloop()