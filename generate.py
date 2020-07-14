import os, argparse
from script import Script
import videogenerator
import emailgenerator

def clean_tmp_dirs():
    os.system('rm -rf tmp')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Misc batch jobs for Conan upkeep')
    ap.add_argument('--generate', help='material to generate', choices=['email', 'video'])
    ap.add_argument('--clean',    help='post & publish all output in "out" dir', default=False)
    args = ap.parse_args()

    os.chdir('work')

    if args.clean:
        clean_tmp_dirs()
        exit(0)

    os.system('mkdir -p tmp')
    os.system('mkdir -p out')

    script = Script.get_script()

    if args.generate == 'email':
        emailgenerator.generate(script)

    if args.generate == 'video':
        video_path = videogenerator.generate(script)
        os.rename(video_path, 'out/youtube.mp4')

    clean_tmp_dirs()
