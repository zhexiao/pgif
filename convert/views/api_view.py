from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pprint import pprint
from enum import Enum
import urllib.request, os, subprocess, uuid, re


# video convert type enum
class VideoConvertType(Enum):
    gif = 'gif'
    video = 'video'
    upload = 'upload'


# convert video
class ConvertVideo(APIView):    
    def __init__(self):
        self.video_path = settings.BASE_DIR + '/files/video/'
        self.gif_path = settings.BASE_DIR + '/files/gif/'
        self.response_data = {'error':False}


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
        - name: type
          description: Video Convert Type
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
        try:
            self.post_data = request.data
            self.type = self.post_data['type']

            try:
                # check convert video type
                VideoConvertType(self.type)
            except Exception as e:
                return Response('Convert type error!', status=status.HTTP_400_BAD_REQUEST)


            # if type is upload, then upload video to disk
            if self.type=='upload':
                self.file_handle = request.data['file']
                self.save_uploaded_file()
            # download a video from a link
            else:
                self.link = self.post_data['link']
                self.download_video()
        except Exception as e:
            return Response('Parameters error!', status=status.HTTP_400_BAD_REQUEST)
       

        if not self.video_name:
            # if not exist file, then return an error message
            return Response('Video can not save in our system, please try it later!', status=status.HTTP_400_BAD_REQUEST)
        else:
            # if exist video file, analysis this video and get video basic info
            self.analysis_video()


        if VideoConvertType(self.type).value == 'gif':
            # convert video to gif
            self.convert_to_gif()
            self.response_file = request.build_absolute_uri('/files/gif/') + self.gif_name
        elif VideoConvertType(self.type).value == 'video':
            # format video by new requirement
            self.format_to_video()
            self.response_file = request.build_absolute_uri('/files/video/') + self.new_video_name
        elif VideoConvertType(self.type).value == 'upload':
            # format video by new requirement
            self.format_to_video()
            self.response_file = request.build_absolute_uri('/files/video/') + self.new_video_name

        self.response_data['response_file'] = self.response_file    
        return Response(self.response_data, status=status.HTTP_200_OK)


    # save uploaded file
    def save_uploaded_file(self):
        self.video_name = str(uuid.uuid4()) +'.mp4'
        self.video_fullpath = self.video_path + self.video_name

        with open(self.video_fullpath, 'wb+') as v_f:
            for chunk in self.file_handle.chunks():
                v_f.write(chunk)


    # download video
    def download_video(self):
        try:          
            self.video_name = str(uuid.uuid4()) +'.mp4'
            self.video_fullpath = self.video_path + self.video_name
            urllib.request.urlretrieve(self.link, self.video_fullpath)
        except Exception as e:
            self.video_name = None
        
        return self.video_name

    # analysis video info
    def analysis_video(self):
        self.metadata = {}
        try:
            result = subprocess.Popen(["ffprobe", self.video_fullpath], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

            for ldt in result.stdout.readlines():
                ldt = ldt.strip().decode('utf-8')

                # duration info
                if  ldt.startswith('Duration'):
                    self.metadata['duration'] = re.search('Duration: (.*?),', ldt).group(0).split(':',1)[1].strip(' ,')
                    self.metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", ldt).group(0).split(':')[1].strip()

                # video info
                elif ldt.startswith('Stream #0:') and 'Video:' in ldt:
                    self.metadata['video'] = {}
                    self.metadata['video']['codec'], self.metadata['video']['profile'] = [e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', ldt).group(0).split(':')[1].split('(')]
                    self.metadata['video']['bitrate'] = re.search('(\d+ kb/s)', ldt).group(1)
                    self.metadata['video']['fps'] = re.search('(\d+ fps)', ldt).group(1)
                    self.metadata['video']['width'], self.metadata['video']['height'] = re.search('([1-9]\d+x\d+)', ldt).group(1).split('x')

                # audio info
                elif ldt.startswith('Stream #0:') and 'Audio:' in ldt:
                    self.metadata['audio'] = {}
                    self.metadata['audio']['codec'] = re.search('Audio: (.*?) ', ldt).group(1)
                    self.metadata['audio']['frequency'] = re.search(', (.*? Hz),', ldt).group(1)
                    self.metadata['audio']['bitrate'] = re.search(', (\d+ kb/s)', ldt).group(1)
        except Exception as e:
            print(e)


    # convert video to gif image
    def convert_to_gif(self):
        try:
            self.gif_name = str(uuid.uuid4()) + '.gif'
            self.gif_fullpath = self.gif_path + self.gif_name

            try:
                self.start_timestamps = self.post_data['start_timestamps']
                self.gif_duration = self.post_data['gif_duration']
            except Exception as e:
                self.start_timestamps = 5
                self.gif_duration = 20

            # default gif parameters
            self.gif_width = 320
            self.gif_height = 240
            self.frameRate = 15

            command = 'ffmpeg -i {0} -ss {1} -pix_fmt rgb24 -r {2} -s {3}x{4} -t {5} {6} 2>&1'.format(self.video_fullpath, self.start_timestamps, self.frameRate, self.gif_width, self.gif_height, self.gif_duration, self.gif_fullpath)
            subprocess.call(command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

            # remove temporary video file
            os.remove(self.video_fullpath)
        except Exception as e:
            pass     


    # format video with new requirement
    def format_to_video(self):
        try: 
            self.new_video_name = str(uuid.uuid4()) +'.mp4'
            new_video_fullpath = self.video_path + self.new_video_name

            # set default video parameters
            self.frameRate = 24
            self.newWidth = 640
            self.newHeight = 320
            self.videoRate = '200k'
            self.audioRate = '64k'

            command = 'ffmpeg -i '+self.video_fullpath+'  -ac 1  -b:a '+self.audioRate+' -b:v '+self.videoRate+' -r '+str(self.frameRate)+' -flags +aic+mv4 -s '+str(self.newWidth)+'x'+str(self.newHeight)+' -y -movflags faststart '+new_video_fullpath+' 2>&1'

            subprocess.call(command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
            # remove temporary video file
            os.remove(self.video_fullpath)
        except Exception as e:
            print(e)
            