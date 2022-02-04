from sklearn.cluster import MiniBatchKMeans
import cv2
import numpy as np
import imutils
import os
import sys

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
    t, mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    cv2.imshow('reduced noise mask', mask)
    out = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow('reduced noise', out)
    return out


def quantize_image(image, n_clusters=16):
    (h, w) = image.shape[:2]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    # reshape the image into a feature vector so that k-means
    # can be applied
    image = image.reshape((image.shape[0] * image.shape[1], 3))
    # apply k-means using the specified number of clusters and
    # then create the quantized image based on the predictions
    clt = MiniBatchKMeans(n_clusters=n_clusters)
    labels = clt.fit_predict(image)
    quant = clt.cluster_centers_.astype("uint8")[labels]
    # reshape the feature vectors to images
    quant = quant.reshape((h, w, 3))
    # convert from L*a*b* to RGB
    return cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)


def get_track(track):
    s = 10
    track = reduce_noise(track)
    track = cv2.medianBlur(track, 3)
    cv2.imshow('median track', track)
    track = quantize_image(track, 16)
    cv2.imshow('quantized track', track)
    colors = list_colors(track)
    color_ranges = [
        [np.array([max(0, c - s) for c in color]), np.array([min(255, c + s) for c in color])]
        for color, _count in colors
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
        color_ranges = get_track(track)
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
            cv2.imwrite(LAST_TRACK, track)
            color_ranges = get_track(track)
        reduced = reduce_colors(frame, color_ranges)
        cv2.imshow('Quant', np.hstack([frame, reduced]))



if __name__ == "__main__":
    main(sys.argv[1])