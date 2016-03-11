from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pprint import pprint
import urllib.request, os, subprocess, uuid


# convert video
class ConvertVideo(APIView):    
    def __init__(self):
        self.link = None
        self.tmp_video_name = None
        self.response_video_name = None

    # process data
    def post(self, request, link, format=None):
        self.link = link
        self.download_video()

        # if do not exist download file
        if not self.tmp_video_name:
            return Response('Video link {0} is not found!'.format(self.link), status=status.HTTP_404_NOT_FOUND)


        # convert video to gif
        self.convert_to_gif()
            
        return Response(link, status=status.HTTP_200_OK)


    # download video
    def download_video(self):
        try:          
            self.tmp_video_name = './files/video/'+ str(uuid.uuid4()) +'.mp4'
            urllib.request.urlretrieve(self.link, self.tmp_video_name)
        except Exception as e:
            self.tmp_video_name = None
        
        return self.tmp_video_name


    def convert_to_gif(self):
        try:
            self.response_video_name = './files/gif/' + str(uuid.uuid4()) + '.gif'

            command = 'ffmpeg -i {0} -ss 00:00:00.000 -pix_fmt rgb24 -r 10 -s 320x240 -t 00:00:10.000  {1} 2>&1'.format(self.tmp_video_name, self.response_video_name)
            subprocess.call(command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        except Exception as e:
            pass     