from pathlib import Path
from Video import Video
import sys

def get_video_id_from_argv():
    if len(sys.argv) > 1:
        return sys.argv[1]
    videos = Path('.cache/youtube')
    slugs = []
    for d in videos.iterdir():
        if d.is_dir():
            slugs.append(str(d).split('/')[-1])
    print("Please select a directory")
    for i, s in enumerate(slugs):
        print(f'{i}: {s}')
    return slugs[int(input("select a directory"))]

def get_video_from_argv():
    return Video(get_video_id_from_argv())

if __name__ == "__main__":
    print(get_video_id_from_argv())