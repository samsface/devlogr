from multiprocessing import Pool
from media import Media, Audio, Image
from itertools import product
import os

class Options:
    scale = 640

def generate_video_scene(section, opts):
    audio_path = os.path.splitext(section.media.src)[0] + '.m4a'
    video_path = section.media.src

    audio = Audio(audio_path).ogg().remove_low_freq().denoise().compress()
    video = Media(video_path).set_scale(opts.scale).mix_in_text(section.title).mix_in_audio(audio.path, 0.1)

    return video.path

def generate(sections, opts):
    scenes = []
    with Pool() as pool:
        scenes = pool.starmap(generate_video_scene, [(s, opts) for s in sections])

    return Media.concat(scenes).mix_in_audio('music.ogg', 1.0, False).path

def generate_thumbnail(sections):
    random_frame = Media(sections[0].media.src).frame(10).path

    return Image.composite([random_frame, 'thumbnail_template.png']).mix_in_caption(sections[0].title, '/home/sam/projects/devlogr/work/nishuki_pixels.ttf').path
