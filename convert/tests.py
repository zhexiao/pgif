from django.test import TestCase
from .views import VideoConvertType

class ConvertTests(TestCase):
    def test_convert_video_type_correct(self):
        self.assertEqual(VideoConvertType('gif').value, 'gif')

    def test_convert_video_type_incorrect(self):
        self.assertNotEqual(VideoConvertType('gif').value, 'jpeg')