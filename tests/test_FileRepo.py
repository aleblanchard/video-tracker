import unittest
import sys
import os
import csv

path = os.getcwd()  
sys.path.insert(0, path)

from src.models.FileRepo import FileRepo
from src.models.Point import Point
import random

class TestFileRepo(unittest.TestCase):

    def setUp(self):
        self.repo = FileRepo(nb_file=0)
        self.liste_frame = [random.randint(-200, 500) for _ in range(10)]
        self.liste_points = [(random.randint(-200, 500), random.randint(-200, 500)) for _ in range(10)]
        self.filename = "repo0.csv"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_file_creation(self):
        self.repo.ecrire(self.liste_frame, self.liste_points)
        self.assertTrue(os.path.exists(self.filename))

    def test_file_content(self):
        self.repo.ecrire(self.liste_frame, self.liste_points)
        
        with open(self.filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            lines = list(reader)

        self.assertEqual(lines[0], ["Frame", "x Coordinates", "y Coordinates"])

        for i in range(1, len(lines)):
            self.assertEqual(lines[i], [str(self.liste_frame[i-1]), str(self.liste_points[i-1][0]), str(self.liste_points[i-1][1])])

if __name__ == '__main__':
    unittest.main()