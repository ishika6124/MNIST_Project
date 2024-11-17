import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [image, setImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle file upload
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      alert('Please upload an image');
      return;
    }

    const formData = new FormData();
    formData.append('file', image);

    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to get a response from the server');
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setPrediction(data.prediction);
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>MNIST Digit Recognition</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Upload and Predict'}
        </button>
      </form>

      {prediction !== null && (
        <div className="result">
          <h2>Predicted Digit: {prediction}</h2>
        </div>
      )}

      {error && (
        <div className="error">
          <h2>{error}</h2>
        </div>
      )}
    </div>
  );
};

export default App;
