import http.server
import socketserver
import os
import json
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the MNIST model
model = load_model('mnist_model.keras')

# Directory for storing uploaded files
UPLOAD_DIR = './uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def preprocess_image(filepath):
    """
    Preprocess the image to match the MNIST model's input requirements.
    """
    # Read the image
    image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

    # Handle alpha channel (if present)
    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # Convert to grayscale (if not already)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize to 28x28 pixels
    image = cv2.resize(image, (28, 28))

    # Normalize pixel values to [0, 1]
    image = image / 255.0

    # Invert colors if the background is white
    if np.mean(image) > 0.5:  # White background
        image = 1.0 - image

    # Add batch and channel dimensions
    image = np.expand_dims(image, axis=(0, -1))  # Shape (1, 28, 28, 1)

    return image

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Parse the uploaded file
            boundary = self.headers['Content-Type'].split('=')[1]
            headers_and_file = post_data.split(b'\r\n\r\n', 1)
            file_headers = headers_and_file[0]
            file_data = headers_and_file[1].split(b'\r\n--', 1)[0]

            # Detect file type from headers (default to .png if unknown)
            filename = "uploaded_image"
            if b"filename=" in file_headers:
                filename = file_headers.split(b'filename="')[1].split(b'"')[0].decode()
            extension = os.path.splitext(filename)[1].lower()
            if extension not in ['.png', '.jpeg', '.jpg']:
                extension = '.png'  # Default to PNG if no extension is provided

            filepath = os.path.join(UPLOAD_DIR, f"uploaded_image{extension}")
            with open(filepath, 'wb') as f:
                f.write(file_data)

            try:
                # Preprocess the image
                image = preprocess_image(filepath)

                # Predict using the model
                prediction = model.predict(image)
                predicted_class = int(np.argmax(prediction))

                # Remove the temporary file
                os.remove(filepath)

                # Send the response
                response = {'prediction': predicted_class}
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                # Handle any errors
                response = {'error': str(e)}
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
        else:
            # Handle invalid endpoints
            self.send_response(404)
            self.end_headers()

# Run the server
PORT = 8000
with socketserver.TCPServer(('', PORT), RequestHandler) as httpd:
    print(f"Server started at http://localhost:{PORT}")
    httpd.serve_forever()
