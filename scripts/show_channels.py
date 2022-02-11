import cv2
import numpy as np
import urcv


def stack_many(images, text=None, border=False, text_color=(255,255,255)):
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
            cv2.putText(result, text[index], (x0+5, y0+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color)
        if border:
            cv2.line(result, (x0+iw, y0), (x0+iw, y0+ih), border, 1)
            cv2.line(result, (x0, y0+ih), (x0+iw, y0+ih), border, 1)
    return result


if __name__ == "__main__":
    import sys
    image = sys.argv[1]
    image = cv2.imread(image)
    image = urcv.transform.scale(image, 0.75)
    image = urcv.transform.crop_ratio(image, (0.2, 0.25, 0.5, 0.5))
    cv2.imshow('og', urcv.transform.scale(image, 4))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    images, ranges = urcv.hsv.scan_hue(hsv, 48, saturation=[0, 255], value=[0,255])

    result = stack_many(images, border=[255, 0, 255], text=[str(r) for r in ranges])
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    result2 = urcv.hsv.filter(hsv, hue=[161, 168])
    result2 = cv2.cvtColor(result2, cv2.COLOR_HSV2BGR)
    result2 = urcv.transform.scale(result2, 4)
    cv2.imshow('result', result)
    cv2.imshow('result2', result2)
    cv2.waitKey(0)