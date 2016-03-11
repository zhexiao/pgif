from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import urllib.request, os, subprocess, uuid


# convert video
class ConvertVideo(APIView):    
    def __init__(self):
        self.link = None
        self.video_name = None
        self.video_path = settings.BASE_DIR + '/files/video/'
        self.gif_name = None
        self.gif_path = settings.BASE_DIR + '/files/gif/'


    def post(self, request, format=None):
        """
        convert video to gif
        ---
        parameters:
        - name: link
          description: Video Link
          required: true
          type: string
          paramType: form
        consumes:
        - application/json
        - application/xml
        produces:
        - application/json
        - application/xml
        """
        print(request.build_absolute_uri('/files/gif'))
        try:
            post_data = request.data
            self.link = post_data['link']
            self.download_video()
        except Exception as e:
            return Response('Parameters error!', status=status.HTTP_400_BAD_REQUEST)
       
        # # if do not exist download file
        if not self.video_name:
            return Response('Video link {0} is not found!'.format(self.link), status=status.HTTP_400_BAD_REQUEST)

        # # convert video to gif
        self.convert_to_gif()
            
        return Response(self.gif_name, status=status.HTTP_200_OK)


    # download video
    def download_video(self):
        try:          
            self.video_name = str(uuid.uuid4()) +'.mp4'
            urllib.request.urlretrieve(self.link, self.video_path + self.video_name)
        except Exception as e:
            self.video_name = None
        
        return self.video_name


    def convert_to_gif(self):
        try:
            self.gif_name = str(uuid.uuid4()) + '.gif'

            video_fullpath = self.video_path + self.video_name
            gif_fullpath = self.gif_path + self.gif_name

            command = 'ffmpeg -i {0} -ss 00:00:00.000 -pix_fmt rgb24 -r 10 -s 320x240 -t 00:00:10.000  {1} 2>&1'.format(video_fullpath, gif_fullpath)
            subprocess.call(command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

            # remove temporary video file
            os.remove(video_fullpath)
        except Exception as e:
            pass     