import unittest
import sys
import os

path = os.getcwd()  
sys.path.insert(0, path)

from src.models.Point import Point
import random


class testPoint(unittest.TestCase):

    def setUp(self):
        self.test_x = random.randint(-200,500)
        self.test_y = random.randint(-200,500)
        self.testPoint = Point(self.test_x,self.test_y)

    def tearDown(self):
        pass

    def test_getx(self):
        self.assertTrue(self.test_x == self.testPoint.get_x())

    def test_gety(self):
        self.assertTrue(self.test_y == self.testPoint.get_y())

if __name__ == '__main__':
    unittest.main(verbosity=2)
    tester = testPoint()
    tester.setUp()
    tester.test_getx()
    tester.test_gety()