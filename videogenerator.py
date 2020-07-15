from multiprocessing import Pool
from media import Media, Audio
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
