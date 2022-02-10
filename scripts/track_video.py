from sklearn.cluster import MiniBatchKMeans
import cv2
import numpy as np
import imutils
import os
import sys

from quantize import quantize
from unrest.image.list_colors import list_colors

def show(image, name="unnamed"):
    cv2.imshow(name, image)
    cv2.waitKey(0)

def reduce_colors(image, color_ranges):
    result = None
    for r in color_ranges:
        reduced = cv2.inRange(image, r[0], r[1])
        if result is not None:
            result = result | reduced
        else:
            result = reduced
    return cv2.bitwise_and(image, image, mask=result)


def reduce_noise(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('reduced noise gray', gray)
    t, mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    cv2.imshow('reduced noise thresh mask', mask)
    out = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow('reduced noise', out)
    return out


def get_color_ranges(track):
    s = 20
    track = quantize(track, 16)
    cv2.imshow('quantized track', track)
    colors = list_colors(track)
    color_ranges = [
        [np.array([max(0, c - s) for c in color]), np.array([min(255, c + s) for c in color])]
        for color, _count in colors
        if sum(color) > 50
    ]
    print(f'using {len(color_ranges)} ranges')
    print(color_ranges)
    return color_ranges


def main(video):
    LAST_TRACK = '.cache/_last-track.png'
    video = cv2.VideoCapture(video)
    color_ranges = None
    if os.path.exists(LAST_TRACK):
        track = cv2.imread(LAST_TRACK)
        track_gray = cv2.cvtColor(track, cv2.COLOR_BGR2GRAY)
        color_ranges = get_color_ranges(track)
    while True:
        key = cv2.waitKey(1) & 0xff
        if key == ord(' '):
            key = cv2.waitKey(0)
        if key == ord('t'):
            color_ranges = None
        elif key == ord('q'):
            break
        elif key != 0xff:
            print(key)
        _, frame = video.read()
        # frame = imutils.resize(frame,width=720)
        if color_ranges is None:
            x, y, w, h = cv2.selectROI(frame,False)
            track = frame[y:y+h,x:x+w]
            track_gray = cv2.cvtColor(track, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(LAST_TRACK, track)
            color_ranges = get_color_ranges(track)
        reduced = reduce_colors(frame, color_ranges)
        # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # result = cv2.matchTemplate(frame, track, cv2.TM_CCOEFF_NORMED)
        # (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
        # (startX, startY) = maxLoc
        # endX = startX + track.shape[1]
        # endY = startY + track.shape[0]
        # cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 3)
        cv2.imshow('doot', np.hstack([frame, reduced]))



if __name__ == "__main__":
    main(sys.argv[1])