import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [maskedImage, setMaskedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setMaskedImage(null);
    setProgress(0);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload an image first!");
      return;
    }

    setLoading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload", formData, {
        responseType: "blob",
        onUploadProgress: (evt) => {
          if (evt.total) {
            const percent = Math.round((evt.loaded * 100) / evt.total);
            setProgress(percent);
          }
        },
      });

      const imageUrl = URL.createObjectURL(response.data);
      setMaskedImage(imageUrl);
    } catch (err) {
      console.error(err);
      alert("Masking failed. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1 className="title">🔒 PII Masker App</h1>

      <div className="upload-box">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Processing..." : "Upload & Mask"}
        </button>
      </div>

      {loading && (
        <div className="loading-section">
          <div className="loader"></div>
          <div className="progress-bar">
            <div className="progress" style={{ width: `${progress}%` }}></div>
          </div>
          <p>{progress}%</p>
        </div>
      )}

      {maskedImage && (
        <div className="result-box">
          <h2>Masked Output</h2>
          <img src={maskedImage} alt="Masked" className="masked-img" />
          <a href={maskedImage} download="masked_output.png">
            <button className="download-btn">⬇ Download Masked Image</button>
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
