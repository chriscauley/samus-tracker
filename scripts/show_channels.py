import color_ranges
import cv2
import numpy as np
from cccv import scale


def stack_many(images, text=None, border=False):
    w = int(np.ceil(len(images)**0.5))
    h = int(np.ceil(len(images)/w))
    if h < 2:
        return np.hstack(images)

    (ih, iw, ic) = images[0].shape
    result = np.zeros((h*ih, w*iw, ic), dtype=np.uint8)
    for index, image in enumerate(images):
        x0 = iw * (index % w)
        y0 = ih * int(np.floor(index / w))
        result[y0:y0+ih,x0:x0+iw,:] = image
    for index, image in enumerate(images):
        x0 = iw * (index % w)
        y0 = ih * int(np.floor(index / w))
        if text:
            pass
        if border:
            cv2.line(result, (x0+iw, y0), (x0+iw, y0+ih), border, 1)
            cv2.line(result, (x0, y0+ih), (x0+iw, y0+ih), border, 1)
    return result


def crop_ratio(image, bounds):
    ih, iw = image.shape[:2]
    x, y, w, h = bounds
    x = int(x * iw)
    w = int(w * iw)
    y = int(y * ih)
    h = int(h * ih)
    return image[y:y+h,x:x+w]

if __name__ == "__main__":
    import sys
    image = sys.argv[1]
    # images = split_channels(scale(cv2.imread(image), 0.5))
    image = scale(cv2.imread(image), 0.75)
    image = crop_ratio(image, (0.2, 0, 0.5, 0.85))
    cv2.imshow('og', image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    images, ranges = color_ranges.scan_hue(hsv, 24, saturation=[0, 255], value=[0,255])

    result = stack_many(images, border=[255, 0, 255], text=[str(r) for r in ranges])
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    cv2.imshow('result', result)
    cv2.waitKey(0)