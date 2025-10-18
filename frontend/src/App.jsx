// src/App.jsx
import React, { useState, useRef } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState('Please select a PDF file to begin.');
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) setSelectedFile(file);
  };

  const handleUploadAreaClick = () => fileInputRef.current.click();

  const handleUpload = async () => {
    if (!selectedFile) {
      setStatusMessage('Error: You must select a file first.');
      return;
    }

    setIsProcessing(true);
    setStatusMessage('Processing PDF... This may take a moment.');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/generate-detailed-excel/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Server-side extraction failed.');
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `extracted_${selectedFile.name}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setStatusMessage('✅ Success! Your Excel file has been downloaded.');
      setSelectedFile(null);
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      {isProcessing && (
        <div className="loader-overlay">
          <div className="spinner"></div>
          <p>{statusMessage}</p>
        </div>
      )}

      <div className={`app-container ${isProcessing ? 'processing' : ''}`}>
        <div className="glass-card">
          <h1>PDF Extraction Tool</h1>
          <p className="subtitle">Upload a PDF and get a structured Excel file in seconds.</p>

          <input
            id="file-input"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            ref={fileInputRef}
          />

          <div className="upload-area" onClick={handleUploadAreaClick}>
            <span className="upload-icon">📄</span>
            <p className="upload-text">
              Click to upload or <span className="upload-browse">browse files</span>
            </p>
          </div>

          {selectedFile ? (
            <div className="attached-file">
              <strong>Attached File:</strong> {selectedFile.name}
            </div>
          ) : (
            <p className="status-section">{statusMessage}</p>
          )}

          <button
            className="action-button"
            onClick={handleUpload}
            disabled={!selectedFile || isProcessing}
          >
            {isProcessing ? 'PROCESSING...' : 'EXTRACT & DOWNLOAD'}
          </button>
        </div>
      </div>
      <footer className="footer-note">Made by 'me' Rahul Sharma</footer>
    </>
  );
}

export default App;
