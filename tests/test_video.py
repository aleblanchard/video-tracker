import unittest
import sys
import os
from tkinter import Tk

path = os.getcwd()
sys.path.insert(0, path)
from unittest.mock import Mock, patch, MagicMock
from tkinter import Tk, Canvas
from src.models.Video import Video
import numpy as np
import cv2


def make_mock_cap(width=640, height=480, opened=True):
    """Simule un cv2.VideoCapture qui renvoie une vraie image noire."""
    props = {cv2.CAP_PROP_FRAME_WIDTH: width, cv2.CAP_PROP_FRAME_HEIGHT: height}
    cap = Mock()
    cap.isOpened.return_value = opened
    cap.get.side_effect = lambda prop: props.get(prop, 0)
    cap.read.return_value = (True, np.zeros((height, width, 3), dtype=np.uint8))
    return cap


class TestVideo(unittest.TestCase):
    
    def setUp(self):
        self.video = Video()
        self.root = Tk()
        self.canvas = Canvas(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('cv2.VideoCapture')
    @patch('tkinter.messagebox.showerror')
    def test_open_file_success(self, mock_showerror, mock_VideoCapture):
        mock_VideoCapture.return_value = make_mock_cap(640, 480)

        self.video.open_file('test_video.mp4', self.canvas, self.root)

        self.assertTrue(self.video.cap.isOpened())
        self.assertEqual(self.video.width, 640)
        self.assertEqual(self.video.height, 480)
        self.assertEqual(int(self.canvas.cget('width')), 640)
        self.assertEqual(int(self.canvas.cget('height')), 480)
        self.assertFalse(mock_showerror.called)

    @patch('cv2.VideoCapture')
    @patch('tkinter.messagebox.showerror')
    def test_open_file_failure(self, mock_showerror, mock_VideoCapture):
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_VideoCapture.return_value = mock_cap

        self.video.open_file('test_video.mp4', self.canvas, self.root)

        self.assertTrue(mock_showerror.called)

    @patch('cv2.VideoCapture')
    def test_show_frame(self, mock_VideoCapture):
        mock_VideoCapture.return_value = make_mock_cap()

        self.video.open_file('test_video.mp4', self.canvas, self.root)
        self.video.show_frame(self.canvas)

        self.assertTrue(self.video.cap.isOpened())
        self.assertIsNotNone(self.video.photo)

    def test_toggle_play_pause(self):
        self.video.pause = False
        self.video.cap = make_mock_cap()
        self.video.btn_play_pause = MagicMock()

        with patch.object(self.video, 'play_video') as mock_play_video:
            self.video.toggle_play_pause(self.canvas, self.root)
            self.assertTrue(self.video.pause)
            self.video.btn_play_pause.__setitem__.assert_called_with("text", "▶️")
            mock_play_video.assert_called_once()

        with patch.object(self.video, 'play_video') as mock_play_video:
            self.video.toggle_play_pause(self.canvas, self.root)
            self.assertFalse(self.video.pause)
            self.video.btn_play_pause.__setitem__.assert_called_with("text", "⏸️")
            mock_play_video.assert_called_once()

    def test_previous_frame(self):
        self.video.pause = True
        self.video.index_courant = 1
        self.video.cap = Mock()
        self.video.cap.isOpened.return_value = True
        self.video.cap.read.return_value = (True, MagicMock())

        with patch.object(self.video, 'show_frame') as mock_show_frame:
            self.video.previous_frame(self.canvas, self.root)
            self.assertEqual(self.video.index_courant, 0)
            mock_show_frame.assert_called_once()

    def test_next_frame(self):
        self.video.pause = True
        self.video.index_courant = 0
        self.video.cap = Mock()
        self.video.cap.isOpened.return_value = True
        self.video.cap.read.return_value = (True, MagicMock())
        self.video.cap.get.side_effect = [10] 

        with patch.object(self.video, 'show_frame') as mock_show_frame:
            self.video.next_frame(self.canvas, self.root)
            self.assertEqual(self.video.index_courant, 1)
            mock_show_frame.assert_called_once()

    @patch('tkinter.messagebox.showinfo')
    def test_first_frame(self, mock_showinfo):
        self.video.pause = True
        self.video.index_courant = 5
        self.video.cap = Mock()
        self.video.cap.isOpened.return_value = True
        self.video.cap.read.return_value = (True, MagicMock())

        with patch.object(self.video, 'show_frame') as mock_show_frame:
            self.video.first_frame(self.canvas, self.root)
            self.assertEqual(self.video.index_courant, 0)
            mock_show_frame.assert_called_once()

    @patch('tkinter.messagebox.showinfo')
    def test_last_frame(self, mock_showinfo):
        self.video.pause = True
        self.video.index_courant = 0
        self.video.cap = Mock()
        self.video.cap.isOpened.return_value = True
        self.video.cap.read.return_value = (True, MagicMock())
        self.video.cap.get.side_effect = [10]  # total frames

        with patch.object(self.video, 'show_frame') as mock_show_frame:
            self.video.last_frame(self.canvas, self.root)
            self.assertEqual(self.video.index_courant, 8)
            mock_show_frame.assert_called_once()


if __name__ == '__main__':
    unittest.main()


