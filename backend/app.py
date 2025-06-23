from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains


def auto_crop_plate_band(image, edge_threshold=50, kernel_size=15):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edges = np.abs(edges).astype(np.uint8)
    smoothed = cv2.GaussianBlur(edges, (1, kernel_size), 0)
    row_sum = np.sum(smoothed, axis=1)
    threshold = np.max(row_sum) * 0.4
    band_indices = np.where(row_sum > threshold)[0]
    if band_indices.size == 0:
        return image, (0, image.shape[0])
    top, bottom = band_indices[0], band_indices[-1]
    cropped = image[top:bottom, :]
    return cropped, (top, bottom)


def extract_strip(img, region='middle', width=20):
    h, w = img.shape[:2]
    if region == 'left':
        return img[:, :width]
    elif region == 'right':
        return img[:, -width:]
    else:
        center = w // 2
        return img[:, center - width // 2:center + width // 2]


def count_black_chunks(strip_img, black_threshold=0.6, min_chunk_height=2):
    gray = cv2.cvtColor(strip_img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inverted = (binary == 0).astype(np.uint8)
    h, w = inverted.shape
    row_density = inverted.sum(axis=1) / w

    in_black = False
    chunk_count = 0
    current_height = 0

    for val in row_density:
        if val > black_threshold:
            if not in_black:
                in_black = True
                current_height = 1
            else:
                current_height += 1
        else:
            if in_black and current_height >= min_chunk_height:
                chunk_count += 1
            in_black = False
            current_height = 0

    if in_black and current_height >= min_chunk_height:
        chunk_count += 1

    return chunk_count


def process_image(image):
    cropped, _ = auto_crop_plate_band(image)
    strip_regions = ['left', 'middle', 'right']
    chunk_counts = {}

    for region in strip_regions:
        strip = extract_strip(cropped, region=region)
        count = count_black_chunks(strip)
        chunk_counts[region] = count

    counts_list = list(chunk_counts.values())
    most_common = max(set(counts_list), key=counts_list.count)
    is_consistent = counts_list.count(most_common) >= 2

    if is_consistent:
        return most_common
    else:
        return None


@app.route('/count-plates', methods=['POST'])
def count_plates():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    img_bytes = file.read()
    img = Image.open(BytesIO(img_bytes)).convert('RGB')
    img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    result = process_image(img_np)

    return jsonify({"count": result})


# Health check
@app.route("/")
def index():
    return "API is running."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)






