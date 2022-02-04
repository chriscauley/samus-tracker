from sklearn.cluster import MiniBatchKMeans
import cv2
import numpy as np
import imutils
import os
import sys

from unrest.image.list_colors import list_colors

def reduce_colors(image, color_ranges):
    result = None
    for r in color_ranges:
        reduced = cv2.inRange(image, r[0], r[1])
        if result is not None:
            result = result | reduced
        else:
            result = reduced
    return result

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


def main(video, image):
    video = cv2.VideoCapture(video)
    colors = list_colors(image)
    color_ranges = [
        [np.array([max(0, c - 20) for c in color]), np.array([min(255, c+20) for c in color])]
        for color, _count in colors
    ]
    while True:
        _, frame = video.read()
        frame = imutils.resize(frame,width=720)
        # reduced = reduce_colors(frame, color_ranges)
        # cv2.imshow('reduced', reduced)
        quant = quantize_image(frame)
        cv2.imshow('Quant', np.hstack([frame, quant]))

        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])