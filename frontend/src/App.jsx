import React, { useState } from 'react';
import './index.css';

const App = () => {
  const [image, setImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
    }
  };

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
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-purple-500 via-pink-500 to-yellow-500 text-white">
      <h1 className="text-5xl font-extrabold mb-6 animate-pulse tracking-wide">
        MNIST Digit Recognition
      </h1>
      <form
        onSubmit={handleSubmit}
        className="flex flex-col items-center bg-white text-gray-800 p-6 rounded-3xl shadow-2xl transform hover:scale-105 transition duration-500"
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          required
          className="mb-4 border-2 border-dashed border-gray-400 rounded-lg p-3 w-full text-center bg-gray-100 hover:border-purple-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className={`px-6 py-3 font-bold text-white rounded-full transition-transform duration-300 ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-700 hover:scale-110'
          }`}
        >
          {loading ? 'Processing...' : 'Upload and Predict'}
        </button>
      </form>

      {prediction !== null && (
        <div className="mt-6 bg-green-500 text-white p-4 rounded-lg shadow-lg animate-bounce">
          <h2 className="text-3xl font-semibold">
            Predicted Digit: <span className="text-yellow-300">{prediction}</span>
          </h2>
        </div>
      )}

      {error && (
        <div className="mt-6 bg-red-500 text-white p-4 rounded-lg shadow-lg animate-shake">
          <h2 className="text-2xl font-semibold">{error}</h2>
        </div>
      )}

      <footer className="absolute bottom-4 text-sm text-gray-300">
        Made with 💜 by Ishika
      </footer>
    </div>
  );
};

export default App;
