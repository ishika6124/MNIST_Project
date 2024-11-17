import http.server
import socketserver
import os
import json
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the MNIST model
model = load_model('mnist_model.h5')

# Directory for storing uploaded files
UPLOAD_DIR = './uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Parse the uploaded file
            boundary = self.headers['Content-Type'].split('=')[1]
            file_data = post_data.split(b'\r\n')[4]

            # Save the uploaded file
            filepath = os.path.join(UPLOAD_DIR, 'uploaded_image.png')
            with open(filepath, 'wb') as f:
                f.write(file_data)

            try:
                # Preprocess the image
                image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                image = cv2.resize(image, (28, 28))
                image = image / 255.0
                image = np.expand_dims(image, axis=(0, -1))  # Shape (1, 28, 28, 1)

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
