import os
import sys
import shutil
import tempfile
import unittest
from tkinter import Tk, Canvas
from unittest.mock import patch

import cv2
import numpy as np

sys.path.insert(0, os.getcwd())
from src.models.Video import Video

FPS = 10
NB_IMAGES = 12
LARGEUR, HAUTEUR = 160, 120


def creer_video(chemin):
    """Petite vidéo de test : un carré blanc qui avance de 10 px par image."""
    out = cv2.VideoWriter(chemin, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (LARGEUR, HAUTEUR))
    for i in range(NB_IMAGES):
        img = np.zeros((HAUTEUR, LARGEUR, 3), np.uint8)
        cv2.rectangle(img, (10 * i, 50), (10 * i + 9, 59), (255, 255, 255), -1)
        out.write(img)
    out.release()


class Clic:
    def __init__(self, x, y):
        self.x, self.y = x, y


class TestVideo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dossier = tempfile.mkdtemp()
        cls.chemin = os.path.join(cls.dossier, "test.mp4")
        creer_video(cls.chemin)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dossier, ignore_errors=True)

    def setUp(self):
        self.root = Tk()
        self.canvas = Canvas(self.root)
        self.video = Video()
        patcher = patch('src.models.Video.messagebox')
        self.messagebox = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.video.release()
        self.root.destroy()

    def ouvrir(self):
        self.assertTrue(self.video.open_file(self.chemin, self.canvas, self.root))

    def test_open_file_success(self):
        self.ouvrir()
        self.assertTrue(self.video.is_loaded)
        self.assertEqual((self.video.width, self.video.height), (LARGEUR, HAUTEUR))
        self.assertEqual(int(self.canvas.cget('width')), LARGEUR)
        self.assertEqual(int(self.canvas.cget('height')), HAUTEUR)
        self.assertAlmostEqual(self.video.fps, FPS)
        self.assertEqual(self.video.index_courant, 0)
        self.assertIsNotNone(self.video.photo)
        self.messagebox.showerror.assert_not_called()

    def test_open_file_failure(self):
        self.assertFalse(self.video.open_file(os.path.join(self.dossier, "absent.mp4"), self.canvas, self.root))
        self.messagebox.showerror.assert_called_once()

    def test_zoom_si_video_trop_grande(self):
        self.video.max_display_size = (80, 1000)
        self.ouvrir()
        self.assertAlmostEqual(self.video.zoom, 0.5)
        self.assertEqual(int(self.canvas.cget('width')), 80)
        self.assertEqual(self.video.canvas_to_video(40, 30), (80, 60))

    def test_navigation(self):
        self.ouvrir()
        self.video.next_frame(self.canvas, self.root)
        self.video.next_frame(self.canvas, self.root)
        self.assertEqual(self.video.index_courant, 2)
        self.video.previous_frame(self.canvas, self.root)
        self.assertEqual(self.video.index_courant, 1)
        self.video.last_frame(self.canvas, self.root)
        self.assertEqual(self.video.index_courant, NB_IMAGES - 1)
        self.assertFalse(self.video.next_frame(self.canvas, self.root))
        self.assertEqual(self.video.index_courant, NB_IMAGES - 1)
        self.video.first_frame(self.canvas, self.root)
        self.assertEqual(self.video.index_courant, 0)
        self.video.previous_frame(self.canvas, self.root)
        self.assertEqual(self.video.index_courant, 0)
        self.messagebox.showinfo.assert_called()

    def test_image_affichee_correspond_a_l_index(self):
        self.ouvrir()
        for _ in range(5):
            self.video.next_frame(self.canvas, self.root)
        self.video.previous_frame(self.canvas, self.root)
        # le carré blanc de l'image 4 commence à x = 40
        colonnes = np.where(self.video._frame_rgb[55, :, 0] > 128)[0]
        self.assertTrue(38 <= colonnes[0] <= 42)

    def test_toggle_play_pause(self):
        self.ouvrir()
        with patch.object(self.video, 'play_video') as mock_play_video:
            self.video.toggle_play_pause(self.canvas, self.root)
            self.assertFalse(self.video.pause)
            self.assertEqual(self.video.btn_play_pause["text"], "❚❚")
            mock_play_video.assert_called_once()
        self.video.toggle_play_pause(self.canvas, self.root)
        self.assertTrue(self.video.pause)
        self.assertEqual(self.video.btn_play_pause["text"], "▶")

    def test_lecture_avance(self):
        self.ouvrir()
        self.video.pause = False
        self.video.play_video(self.canvas, self.root)
        self.assertEqual(self.video.index_courant, 1)
        self.video.stop(self.root)
        self.assertIsNone(self.video._after_id)

    def test_echelle(self):
        self.ouvrir()
        with patch('src.models.Video.simpledialog.askstring', return_value="0,5"):
            self.video.scale_click(self.canvas, Clic(10, 100))
            self.video.scale_click(self.canvas, Clic(110, 100))
        self.assertTrue(self.video.echelle_definie)
        self.assertAlmostEqual(self.video.echelle, 0.005)

    def test_echelle_saisie_invalide_puis_annulee(self):
        self.ouvrir()
        with patch('src.models.Video.simpledialog.askstring', side_effect=["abc", None]):
            self.video.scale_click(self.canvas, Clic(10, 100))
            self.video.scale_click(self.canvas, Clic(110, 100))
        self.assertFalse(self.video.echelle_definie)
        self.assertEqual(self.video.echelle, 1.0)
        self.messagebox.showerror.assert_called_once()

    def test_pointage_sans_origine(self):
        self.ouvrir()
        self.video.place_point_next_frame(self.canvas, self.root, Clic(5, 5))
        self.assertEqual(self.video.liste_points, [])
        self.messagebox.showwarning.assert_called_once()

    def test_pointage_et_mesures(self):
        self.ouvrir()
        self.video.set_origin(self.canvas, Clic(0, 100))
        self.video.echelle, self.video.echelle_definie = 0.01, True
        for i in range(3):
            self.video.place_point_next_frame(self.canvas, self.root, Clic(10 * i + 5, 55))
        self.assertEqual(self.video.index_courant, 3)
        self.assertEqual(self.video.liste_frame, [0, 1, 2])
        mesures = self.video.get_measures()
        self.assertEqual(len(mesures), 3)
        t, x, y = mesures[2]
        self.assertAlmostEqual(t, 2 / FPS)
        self.assertAlmostEqual(x, 0.25)
        self.assertAlmostEqual(y, 0.45)       # axe y orienté vers le haut
        self.assertEqual(self.video.get_points_data()[0], (5, 55, 0))

    def test_pointage_s_arrete_a_la_derniere_image(self):
        self.ouvrir()
        fin = []
        self.video.on_pointing_end = lambda: fin.append(True)
        self.video.set_origin(self.canvas, Clic(0, 100))
        self.video.last_frame(self.canvas, self.root)
        self.video.place_point_next_frame(self.canvas, self.root, Clic(50, 50))
        self.assertEqual(fin, [True])
        self.assertEqual(len(self.video.liste_points), 1)

    def test_reset(self):
        self.ouvrir()
        self.video.set_origin(self.canvas, Clic(0, 100))
        self.video.place_point_next_frame(self.canvas, self.root, Clic(5, 5))
        self.video.resetList(self.canvas)
        self.assertEqual(self.video.liste_points, [])
        self.assertEqual(self.video.liste_frame, [])


if __name__ == '__main__':
    unittest.main()
