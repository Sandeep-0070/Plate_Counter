import cv2
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d


def crop_by_horizontal_bands(image: np.ndarray,
                             clahe_clip_limit: float = 2.0,
                             clahe_grid_size: tuple = (8, 8),
                             gaussian_ksize: tuple = (5, 5),
                             sobel_ksize: int = 3,
                             profile_sigma: float = 3,
                             threshold_ratio: float = 0.3,
                             padding: int = 10) -> np.ndarray:
    if image is None or image.size == 0:
        return image

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=clahe_grid_size).apply(gray)
    blurred = cv2.GaussianBlur(clahe, gaussian_ksize, 0)

    sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=sobel_ksize)
    vertical_edges = np.abs(sobel_y)

    edge_profile = vertical_edges.sum(axis=1)
    smoothed_profile = gaussian_filter1d(edge_profile, sigma=profile_sigma)

    max_profile_value = np.max(smoothed_profile)
    if max_profile_value == 0:
        return image

    threshold = max_profile_value * threshold_ratio
    band_indices = np.where(smoothed_profile > threshold)[0]

    if len(band_indices) == 0:
        return image

    top = band_indices[0]
    bottom = band_indices[-1]

    top_cropped = max(0, top - padding)
    bottom_cropped = min(image.shape[0], bottom + padding)

    return image[top_cropped:bottom_cropped, :]


def edge_based_plate_count_refined(img: np.ndarray,
                                   visualize: bool = True,
                                   clahe_clip_limit: float = 2.0,
                                   clahe_grid_size: tuple = (8, 8),
                                   gaussian_ksize: tuple = (5, 5),
                                   sobel_ksize: int = 3,
                                   profile_sigma: float = 1.2,
                                   zone_width_ratio: float = 0.2,  # Ratio for left/right zones
                                   peak_height: float = 0.1,
                                   peak_distance: int = 8,
                                   peak_prominence: float = 0.08,
                                   min_peak_separation: int = 5) -> int:
    if img is None or img.size == 0:
        return 0

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=clahe_grid_size).apply(gray)
    blurred = cv2.GaussianBlur(clahe, gaussian_ksize, 0)

    sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=sobel_ksize)
    edge_map = np.abs(sobel_y)

    h, w = edge_map.shape
    if w == 0:
        return 0

    zone_width = max(1, int(w * zone_width_ratio))
    left_zone = edge_map[:, :zone_width]
    right_zone = edge_map[:, -zone_width:]

    edge_strength_profile = np.minimum(left_zone.mean(axis=1), right_zone.mean(axis=1))
    smoothed_profile = gaussian_filter1d(edge_strength_profile, sigma=profile_sigma)
    max_profile_val = np.max(smoothed_profile)
    normalized_profile = smoothed_profile / max_profile_val if max_profile_val > 0 else smoothed_profile

    peaks, _ = find_peaks(normalized_profile,
                          height=peak_height,
                          distance=peak_distance,
                          prominence=peak_prominence)

    refined_peaks = []
    if len(peaks) > 0:
        refined_peaks.append(peaks[0])
        for i in range(1, len(peaks)):
            if (peaks[i] - refined_peaks[-1]) > min_peak_separation:
                refined_peaks.append(peaks[i])

    return len(refined_peaks)
