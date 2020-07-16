import os, argparse
from script import Script
import videogenerator
import emailgenerator

def clean_tmp_dirs():
    os.system('rm -rf tmp')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Misc batch jobs for Conan upkeep')
    ap.add_argument('path',       help='path of project', nargs='?', default=os.getcwd())
    ap.add_argument('--generate', help='material to generate', choices=['email', 'video', 'youtube-thumbnail'])
    ap.add_argument('--clean',    help='post & publish all output in "out" dir', default=False)
    ap.add_argument('--preview',  help='output smaller lesser quality media', default=False)
    args = ap.parse_args()

    os.chdir(args.path)

    if args.clean:
        clean_tmp_dirs()
        exit(0)

    os.system('mkdir -p tmp')
    os.system('mkdir -p out')

    script = Script.get_script()

    if args.generate == 'email':
        emailgenerator.generate(script)

    if args.generate == 'video':
        opts = videogenerator.Options()

        if args.preview:
            opts.preview = args.scale = 200
        else:
            opts.preview = args.scale = 1024

        video_path = videogenerator.generate(script, opts)
        os.rename(video_path, 'out/video.mp4')

    if args.generate == 'youtube-thumbnail':
        video_thumbnail_path = videogenerator.generate_thumbnail(script)
        os.rename(video_thumbnail_path, 'out/video_thumbnail.png')

    clean_tmp_dirs()
