import csv
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.getcwd())
from src.models.FileRepo import FileRepo


class TestFileRepo(unittest.TestCase):

    def setUp(self):
        self.repo = FileRepo(nb_file=0)
        self.dossier = tempfile.mkdtemp()
        self.liste_frame = [random.randint(0, 500) for _ in range(10)]
        self.liste_points = [(random.randint(-200, 500), random.randint(-200, 500)) for _ in range(10)]

    def tearDown(self):
        for f in os.listdir(self.dossier):
            os.remove(os.path.join(self.dossier, f))
        os.rmdir(self.dossier)

    def lire(self, chemin):
        with open(chemin, newline='', encoding='utf-8') as f:
            return list(csv.reader(f, delimiter=';'))

    def test_file_creation(self):
        chemin = os.path.join(self.dossier, "repo0.csv")
        self.repo.ecrire(self.liste_frame, self.liste_points, chemin)
        self.assertTrue(os.path.exists(chemin))

    def test_file_content(self):
        chemin = self.repo.ecrire(self.liste_frame, self.liste_points, os.path.join(self.dossier, "brut.csv"))
        lines = self.lire(chemin)
        self.assertEqual(lines[0], ["Frame", "x Coordinates", "y Coordinates"])
        for i in range(1, len(lines)):
            self.assertEqual(lines[i], [str(self.liste_frame[i - 1]),
                                        str(self.liste_points[i - 1][0]),
                                        str(self.liste_points[i - 1][1])])

    def test_ecrire_mesures(self):
        chemin = os.path.join(self.dossier, "mesures.csv")
        self.repo.ecrire_mesures(chemin, [(0, 0.1, 1.2), (0.0333, 0.15, 1.26)], "m")
        lines = self.lire(chemin)
        self.assertEqual(lines[0], ["t (s)", "x (m)", "y (m)"])
        self.assertEqual(lines[2], ["0.0333", "0.1500", "1.2600"])
        self.assertEqual(len(lines), 3)


if __name__ == '__main__':
    unittest.main()
