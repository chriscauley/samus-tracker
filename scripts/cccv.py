import cv2

def scale(image, scale):
    w = int(image.shape[1] * scale)
    h = int(image.shape[0] * scale)
    return cv2.resize(image, (w, h))