import cv2
from tkinter import *
from tkinter import messagebox, simpledialog
from math import sqrt
import PIL.Image, PIL.ImageTk

class Video:
    def __init__(self):
        self.delay = 15
        self.pause = False
        self.cap = None
        self.index_courant = 0
        self.start_frame = 0
        self.photo = None
        self.button_frame = None
        self.origin_point = (0,0)
        self.liste_frame = []
        self.liste_points = []
        self.echelle = 1


    def open_file(self, path, canv, wind):
        self.pause = True
        self.filename = path
        self.cap = cv2.VideoCapture(self.filename)

        if not self.cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier vidéo.")
            return

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        canv.config(width=self.width, height=self.height)
        self.index_courant = 0
        self.show_frame(canv)

        if not self.button_frame:
            self.create_buttons(wind, canv)
        else:
            self.btn_play_pause.config(text="▶️")
            self.button_frame.pack(side='bottom', pady=(0, 10))



    def create_buttons(self, wind, canv):
        self.button_frame = Frame(wind)
        self.button_frame.pack(side='bottom', pady=(0, 10))

        self.btn_first = Button(self.button_frame, text="⏪", command=lambda: self.first_frame(canv, wind), height=2, width=5)
        self.btn_previous = Button(self.button_frame, text="⬅", command=lambda: self.previous_frame(canv, wind), height=2, width=5)
        self.btn_play_pause = Button(self.button_frame, text="▶️", command=lambda: self.toggle_play_pause(canv, wind), height=2, width=5)
        self.btn_next = Button(self.button_frame, text="➡", command=lambda: self.next_frame(canv, wind), height=2, width=5)
        self.btn_last = Button(self.button_frame, text="⏩", command=lambda: self.last_frame(canv, wind), height=2, width=5)

        self.btn_first.pack(side='left')
        self.btn_previous.pack(side='left')
        self.btn_play_pause.pack(side='left')
        self.btn_next.pack(side='left')
        self.btn_last.pack(side='right')

        # Bind des boutons
        wind.bind("<Control-Left>", lambda event: self.first_frame(canv, wind))
        wind.bind("<Left>", lambda event: self.previous_frame(canv, wind))
        wind.bind("<space>", lambda event: self.toggle_play_pause(canv, wind))
        wind.bind("<Right>", lambda event: self.next_frame(canv, wind))
        wind.bind("<Control-Right>", lambda event: self.last_frame(canv, wind))

    def show_frame(self, canv):
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index_courant)
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame_rgb))
                canv.create_image(0, 0, image=self.photo, anchor=NW)
                if self.origin_point:
                    self.origin(canv)
                self.place_points(canv)

    def play_video(self, canv, wind):
        ret, frame = self.cap.read()
        if ret and not self.pause:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame_rgb))
            canv.create_image(0, 0, image=self.photo, anchor=NW)
            if self.origin_point:
                self.origin(canv)
            self.place_points(canv)
            wind.after(self.delay, lambda: self.play_video(canv, wind))
        elif not ret:
            if self.cap.isOpened():
                answer = messagebox.askquestion("Fin de la vidéo", "Voulez-vous rejouer la vidéo ?")
                if answer == "yes":
                    self.restart_video()
                    self.btn_play_pause["text"] = "⏸️"
                    self.play_video(canv, wind)

    def restart_video(self):
        self.index_courant = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index_courant)
        self.btn_play_pause["text"] = "▶️"

    def toggle_play_pause(self, canv, wind):
        self.pause = not self.pause
        self.play_video(canv, wind)
        self.index_courant = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

        if self.pause:
            self.btn_play_pause["text"] = "▶️"  # Quand la vidéo est en pause le bouton affiche jouer la vidéo
        else:
            self.btn_play_pause["text"] = "⏸️"  # Quand la vidéo n'est pas pausée le bouton affiche pause

    def previous_frame(self, canv, wind):
        if not self.pause: 
            self.toggle_play_pause(canv, wind)

        if self.index_courant > 0:
            self.index_courant -= 1
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index_courant)
            self.cap.read()
            self.show_frame(canv)
        else:
            messagebox.showinfo("Début de la vidéo", "Début de la vidéo atteint.")

    def next_frame(self, canv, wind):
        if not self.pause:
            self.toggle_play_pause(canv, wind)

        if self.cap.isOpened():
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if self.index_courant < total_frames - 1:
                self.index_courant += 1
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index_courant)
                self.cap.read()
                self.show_frame(canv)
            else:
                messagebox.showinfo("Fin de la vidéo", "Fin de la vidéo atteint.")
                canv.unbind("<Button-1>")

    def first_frame(self, canv, wind):
        if not self.pause:
            self.toggle_play_pause(canv, wind)

        if self.cap.isOpened():
            self.index_courant = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index_courant)
            self.cap.read()
            self.show_frame(canv)

    def last_frame(self, canv, wind):
        if not self.pause:  # Met en pause la vidéo et va à la dernière frame
            self.toggle_play_pause(canv, wind)

        if self.cap.isOpened():
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.index_courant = total_frames - 2
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.index_courant)
            self.cap.read()
            self.show_frame(canv)

    def origin(self, canv):
        if self.origin_point:
            x, y = self.origin_point
            canv.create_oval(x-5, y-5, x+5, y+5, fill="blue",tags="point")
    
    def set_origin(self, canv, event):
        self.origin_point = (event.x, event.y)
        self.show_frame(canv)

    def place_points(self, canv):
        for x, y in self.liste_points:
            canv.create_oval(x-5, y-5, x+5, y+5, fill="red",tags="point")

    def place_point_next_frame(self, canv, wind, event):
        if self.origin_point is None:
            messagebox.showwarning("Attention", "Veuillez d'abord définir l'origine.")
            return
        self.liste_points.append((event.x, event.y))
        self.liste_frame.append(self.start_frame + self.index_courant)
        self.next_frame(canv, wind)

    def resetList(self, canv):
        self.start_frame = self.index_courant
        self.liste_points.clear()
        self.liste_frame.clear()
        canv.delete("point", "echelle")
        canv.bind("<Button-3>", lambda event: self.echelle1(canv,event))


    def echelle1(self,canv,event):
        x0 = event.x
        y0 = event.y
        canv.create_oval(x0-3, y0-3, x0+3, y0+3, fill="green", tags = "echelle")
        canv.bind("<Button-3>", lambda event: self.echelle2(x0,y0,canv,event))

    def echelle2(self,x0,y0,canv,event):
        canv.unbind("<Button-3>")
        x1 = event.x
        y1 = event.y
        canv.create_line(x0, y0, x1, y1, fill='green', width=2,tags = "echelle")
        canv.create_oval(x1-3, y1-3, x1+3, y1+3, fill="green",tags = "echelle")
        distance = simpledialog.askstring("échelle des longueurs","Donnez la distance réelle entre les deux points en mètre")
        
        if distance is None:
            messagebox.showwarning("Attention", "Veuillez d'abord définir l'origine.")
            canv.delete("echelle")
            canv.bind("<Button-3>", lambda event: self.echelle1(canv,event))
        else:
            self.echelle = int(distance)/(sqrt((y1-y0)**2+(x1-x0)**2))

    
    def get_points_data(self):
        return [(x, y, frame) for (x, y), frame in zip(self.liste_points, self.liste_frame)]

    def __del__(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()