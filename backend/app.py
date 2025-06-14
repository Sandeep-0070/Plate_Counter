from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from plate_counter import count_plates_with_rotation

app = Flask(__name__)
CORS(app)

@app.route('/count-plates', methods=['POST'])
def count_plates():
    file = request.files['file']
    img = Image.open(file.stream).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    count = count_plates_with_rotation(img_cv)
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(debug=True)
