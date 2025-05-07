from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from watermark import process_video_robust  # Move your processing logic to watermark.py
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = f"{uuid.uuid4()}.mp4"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(PROCESSED_FOLDER, f"processed_{filename}")
    file.save(input_path)

    process_video_robust(input_path, output_path, sensitivity=0.9)

    return send_file(output_path, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
