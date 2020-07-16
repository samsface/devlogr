import glob, os, mistune, pprint, subprocess, argparse, praw, getpass
from mako.template import Template
import uuid

def tmp_path(path):
    return os.path.join('tmp', str(uuid.uuid4()) + os.path.splitext(path)[1])

def cmd(cmd_str):
    print(cmd_str)
    return subprocess.check_output(cmd_str.split(' '))

def cmd_(cmd_str):
    print(cmd_str)
    return subprocess.check_output(cmd_str)

def ffmpeg(cmd_str):
    cmd('ffmpeg -nostdin -hide_banner -loglevel warning ' + cmd_str)

def convert(cmd_str):
    cmd_(['convert'] + cmd_str)

class Image:
    path = ''

    def __init__(self, path):
        self.path = path

    @staticmethod
    def composite(paths, gravity='west'):
        output_path  = tmp_path(paths[0])
        convert(['-size', '1280x720', 'xc:transparent', output_path])

        for path in paths:
            working_path = tmp_path(paths[0])
            convert([output_path, path, '-gravity', gravity, '-composite', working_path])
            output_path = working_path

        return Image(output_path)

    @staticmethod
    def caption(text, font):
        output_path  = tmp_path('file.png')
        convert(['-background', 'black', '-fill', 'white', '-font', font, '-size', '1280x150', 'caption:{0}'.format(text), output_path])
        return Image(output_path)

    def mix_in_caption(self, text, font):
        return Image.composite([self.path, Image.caption(text, font).path], 'south')

class Media:
    path = ''

    @staticmethod
    def concat(paths):
        output_path = tmp_path(paths[0])

        list_path = tmp_path('file.txt')
        with open(list_path, 'w') as f: 
            for path in paths:
                f.write('file {0}\n'.format(path).replace('tmp/', ''))

        ffmpeg('-y -f concat -i {0} -c copy {1}'.format(list_path, output_path))

        return Media(output_path)

    def __init__(self, path):
        self.path = path

    def duration(self):
        return float(cmd('ffprobe -nostdin -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {0}'.format(self.path)))

    def gif(self):
        output_path = tmp_path('file.gif')
        ffmpeg('-y -i {0} -vf fps=24,scale=320:-1 -loop 0 {1}'.format(self.path, output_path))
        return 'data:image/gif;base64,' + cmd('base64 {0}'.format(output_path)).decode('utf-8')

    def frame(self, number):
        output_path = tmp_path('file.png')
        ffmpeg('-i {0} -r {1}/{2} {3}%03d.png'.format(self.path, number, number + 1, output_path))
        return Media(output_path + '001.png')

    def cut(self, duration):
        output_path = tmp_path(self.path)
        ffmpeg('-y -i {0} -c copy -t {1} {2}'.format(self.path, duration, output_path))
        return Media(output_path)

    def set_volume(self, value):
        output_path = tmp_path(self.path)
        ffmpeg('-y -i {0} -filter:a volume={1} {2}'.format(self.path, value, output_path))
        return Media(output_path)
    
    def set_scale(self, width):
        output_path = tmp_path(self.path)
        ffmpeg('-y -i {0} -filter:v scale={1}:-1 -c:a copy {2}'.format(self.path, width, output_path))
        return Media(output_path)

    def loop(self, loop_duration):
        loops = 1 if self.duration() > loop_duration else int(loop_duration / self.duration()) + 1
        return Media.concat([self.path for i in range(loops)]).cut(loop_duration)

    def mix_in_audio(self, audio_path, volume, loop=True):
        output_path = tmp_path(self.path)
        working_media = self

        if volume < 1.0:
            working_media = working_media.set_volume(volume)
        if loop:
            working_media = working_media.loop(Media(audio_path).duration())

        ffmpeg('-y -i {0} -i {1} -filter_complex amix=inputs=2:duration=shortest {2}'.format(working_media.path, audio_path, output_path))

        return Media(output_path)

    def mix_in_text(self, text):
        output_path = tmp_path(self.path)
        cmd_(['ffmpeg', '-nostdin', '-y', '-i', self.path, '-vf', """drawtext="fontfile='/home/sam/projects/marketing-generater/work/Pixelmania.ttf': text='{0}': fontcolor=white: fontsize=24: box=1: boxcolor=black@1.0: boxborderw=5: x=(w-text_w)/2: y=(h - text_h - 16)""".format(text), '-codec:a', 'copy', output_path])
        return Media(output_path)

class Audio:
    path = ''

    def __init__(self, path):
        self.path = path

    def ogg(self):
        output_path = tmp_path('file.ogg')
        ffmpeg('-i {0} -acodec libvorbis {1}'.format(self.path, output_path))
        return Audio(output_path)

    def denoise(self):
        output_path = tmp_path(self.path)
        noise_path  = tmp_path(self.path)
        noise_profile_path = tmp_path('file.prof')
        cmd('sox {0} {1} trim 0 0.900'.format(self.path, noise_path))
        cmd('sox {0} -n noiseprof {1}'.format(noise_path, noise_profile_path))
        cmd('sox {0} {1} noisered {2} 0.01'.format(self.path, output_path, noise_profile_path))
        return Audio(output_path)

    def remove_low_freq(self):
        output_path = tmp_path(self.path)
        cmd('sox {0} {1} sinc 200-20000'.format(self.path, output_path))
        return Audio(output_path)

    def compress(self):
        output_path = tmp_path(self.path)
        cmd('sox {0} {1} compand 0.01,1 -90,-90,-70,-70,-60,-20,0,0 -5'.format(self.path, output_path))
        return Audio(output_path)

