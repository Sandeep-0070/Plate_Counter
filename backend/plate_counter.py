# plate_counter.py
import cv2
import numpy as np
from scipy.signal import find_peaks

def auto_rotate_image(image, debug=False):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=150)

    if lines is None:
        return image, 0

    angles = []
    for rho, theta in lines[:, 0]:
        angle = (theta - np.pi / 2) * (180 / np.pi)
        if -45 < angle < 45:
            angles.append(angle)

    if len(angles) == 0:
        return image, 0

    median_angle = np.median(angles)

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(image, rot_mat, (w, h), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)

    return rotated, median_angle

def count_plates_with_rotation(image, show_plot=False):
    rotated_img, angle = auto_rotate_image(image, debug=False)
    gray = cv2.cvtColor(rotated_img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    grad = np.abs(sobel_y)
    profile = grad.sum(axis=1)
    window = 15
    smooth = np.convolve(profile, np.ones(window)/window, mode='same')
    peaks, _ = find_peaks(smooth, height=np.max(smooth)*0.3, distance=20)
    return len(peaks)
