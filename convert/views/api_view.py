from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pprint import pprint
from enum import Enum
import simplejson as json
import urllib.request, os, subprocess, uuid, re
import cloudinary, cloudinary.uploader, cloudinary.api


# video convert type enum
class VideoConvertType(Enum):
    link = 'link'
    video = 'video'
    youtube = 'youtube'


# convert video
class ConvertVideo(APIView):    
    def __init__(self):
        self.video_path = settings.BASE_DIR + '/files/video/'
        self.gif_path = settings.BASE_DIR + '/files/gif/'
        self.response_data = {'error':False}
        self.init_cloundinary()


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
        self.post_data = request.data

        try:
            self.type = self.post_data['type']
        except Exception as e:
            return Response('Parameters error, type is required!', status=status.HTTP_400_BAD_REQUEST)

        try:
            # check video type
            VideoConvertType(self.type)
        except Exception as e:
            return Response('Parameter value of Type is invalid!', status=status.HTTP_400_BAD_REQUEST)

        # dispatch video type
        self.video_type_dispatch()

        # get the response data
        self.parse_response_data(request)
        
        # response to client
        return Response(self.response_data, status=status.HTTP_200_OK, content_type='application/json')


    # init cloundinary
    def init_cloundinary(self):
        cloudinary.config( 
            cloud_name = settings.CLOUDINARY_CLOUND_NAME,
            api_key = settings.CLOUDINARY_API_KEY,
            api_secret = settings.CLOUDINARY_API_SECRECT
        )


    # upload image to cloundinary
    def upload_to_cloundinary(self, file):
        try:
            res = cloudinary.uploader.upload(file)
            self.clound_gif_url = res['url']
        except Exception as e:
            self.clound_gif_url = None
        

    # dispatch video type
    def video_type_dispatch(self):
        # check whether exist local file
        self.video_name = self.post_data['local_file']
        self.video_fullpath = self.video_path + self.video_name

        if not os.path.isfile(self.video_fullpath):
            # download new file to local
            if self.type == 'video':
                self.file_handle = self.post_data['file']
                self.save_uploaded_file()
            elif self.type == 'youtube':
                self.get_youtube_video_link()
                self.download_video()
            elif self.type == 'link':
                # download a video from a link
                self.link = self.post_data['link']
                self.download_video()
                self.analysis_video()


    # operate response data
    def parse_response_data(self, request):
        # convert video to gif
        if self.type == 'video' or self.type == 'youtube':        
            self.convert_to_gif()
            self.response_file = self.clound_gif_url
            # self.response_file = request.build_absolute_uri('/files/gif/') + self.gif_name
            self.response_data['local_file'] = self.video_name    

        # format video by new requirement
        elif self.type == 'link':          
            self.format_to_video()
            self.response_file = request.build_absolute_uri('/files/video/') + self.new_video_name

        self.response_data['response_file'] = self.response_file    


    def get_youtube_video_link(self):
        try:
            request_link = 'https://rxjthjm1pofte.com/info?url=https://www.youtube.com/watch?v={0}'.format(self.post_data['youtube_id'])
            res = urllib.request.urlopen(request_link)
            content = res.read().decode('utf8')
            json_data = json.loads(content)
            self.link = json_data['url']
        except Exception as e:
            raise e
        

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
                self.start_timestamps = 0
                self.gif_duration = 5
 
            self.generate_high_quality_gif()
            # upload to clound
            self.upload_to_cloundinary(self.gif_fullpath)
        except Exception as e:
            pass     


    # generate high quality gif
    def generate_high_quality_gif(self):
        # most high quality
        palette="/tmp/{0}.png".format( str(uuid.uuid4()) )

        palette_command = 'ffmpeg -v warning -ss {0} -t {1} -i {2} -vf "fps=12,scale=320:-1:flags=lanczos,palettegen" -y {3}'.format(self.start_timestamps, self.gif_duration, self.video_fullpath, palette)
        subprocess.call(palette_command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

        gif_command = 'ffmpeg -v warning -ss {0} -t {1} -i {2} -i {3} -lavfi "fps=12,scale=320:-1:flags=lanczos [x]; [x][1:v] paletteuse" -y {4}'.format(self.start_timestamps, self.gif_duration, self.video_fullpath, palette, self.gif_fullpath)
        subprocess.call(gif_command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)


    # generate low quality gif
    def generate_low_quality_gif(self):
        # low quality
        command = 'ffmpeg -v warning -ss {0} -t {1} -i {2} -r 12 -vf scale=320:-1 -gifflags +transdiff -y {3} 2>&1'.format(self.start_timestamps, self.gif_duration, self.video_fullpath, self.gif_fullpath)

        subprocess.call(command, shell=True,  stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)


    # format video with new requirement
    def format_to_video(self):
        try: 
            self.new_video_name = str(uuid.uuid4()) +'.mp4'
            new_video_fullpath = self.video_path + self.new_video_name

            # set default video parameters
            self.frameRate = 20
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
            