from pytube import YouTube
from unrest.utils import mkdir
import urllib.parse
import sys

SAVE_PATH = mkdir('.cache', 'youtube')

def download(v):
    if 'v=' in v:
        v = v.split('v=')[-1].split("&")[0]
    link = f"https://www.youtube.com/watch?v={v}"
    print(link)
    yt = YouTube(link)
    print(dir(yt))
    print(yt.length)

    # filters out all the files with "mp4" extension
    streams = yt.streams
    streams = streams.filter(progressive=True, file_extension='mp4')
    first = streams.order_by('resolution').desc().first()
    first.download()


if __name__ == "__main__":
    download(sys.argv[1])