from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
from plate_counter import crop_by_horizontal_bands, edge_based_plate_count_refined

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Health check
@app.route("/")
def index():
    return "API is running."

@app.route("/count-plates", methods=["POST"])
def count_plates():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    image = cv2.imread(filepath)
    if image is None:
        return jsonify({"error": "Invalid image"}), 400

    try:
        cropped_img = crop_by_horizontal_bands(image)
        resized_img = cropped_img
        h, w = cropped_img.shape[:2]
        max_dim = 600
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            resized_img = cv2.resize(cropped_img, (int(w * scale), int(h * scale)))

        count = edge_based_plate_count_refined(resized_img, visualize=False)
        return jsonify({"count": count})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)