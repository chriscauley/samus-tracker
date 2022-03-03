import cv2
import numpy as np
import urcv


if __name__ == "__main__":
    import sys
    image = sys.argv[1]
    image = cv2.imread(image)
    # image = urcv.transform.scale(image, 0.75)
    # image = urcv.transform.crop_ratio(image, (0.2, 0.25, 0.5, 0.5))
    cv2.imshow('og', urcv.transform.scale(image, 4))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    images, ranges = urcv.hsv.scan_hue(hsv, 48, saturation=[0, 255], value=[0,255])

    result = urcv.stack.many(images, border=[255, 0, 255], text=[str(r) for r in ranges])
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    result2 = urcv.hsv.filter(hsv, hue=[161, 168])
    result2 = cv2.cvtColor(result2, cv2.COLOR_HSV2BGR)
    result2 = urcv.transform.scale(result2, 4)
    cv2.imshow('result', result)
    cv2.imshow('result2', result2)
    cv2.waitKey(0)