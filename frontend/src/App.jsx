import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './App.css';

const UploadIcon = () => (
  <svg className="w-12 h-12 mx-auto text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const FileIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

function App() {
  const [files, setFiles] = useState([]);
  const [template, setTemplate] = useState('1');
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const onDrop = useCallback(acceptedFiles => {
    const pdfFiles = acceptedFiles.filter(file => file.type === "application/pdf");
    setFiles(prevFiles => [...prevFiles, ...pdfFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }
  });

  const removeFile = (fileName) => {
    setFiles(files.filter(file => file.name !== fileName));
  };

  const handleExtract = async () => {
    if (files.length === 0) {
      setErrorMessage("Please upload at least one PDF file.");
      setStatus('error');
      return;
    }

    setIsProcessing(true);
    setStatus('uploading');
    setErrorMessage('');

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('template_id', template);

    try {
      setStatus('extracting');
      const response = await fetch('http://127.0.0.1:8000/extract/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
      }

      setStatus('success');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'extracted_data.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error("Extraction failed:", error);
      setErrorMessage(`Extraction failed: ${error.message}`);
      setStatus('error');
    } finally {
      setTimeout(() => {
        setStatus('idle');
        setIsProcessing(false);
      }, 5000);
    }
  };

  return (
    <body>
      <div className={`app-container ${isProcessing ? 'processing' : ''}`}>
        <h1>PDF Extraction Tool</h1>
        <p>Leveraging AI to extract structured data from your documents.</p>

        {/* Template Selection */}
        <div className="template-selector">
          <label>Select an Extraction Template</label>
          <select value={template} onChange={(e) => setTemplate(e.target.value)}>
            <option value="1">Template 1 - Standard fund financial reports</option>
            <option value="2">Template 2 - Detailed portfolio company analysis</option>
          </select>
        </div>

        {/* Upload Area */}
        <div {...getRootProps()} className={`upload-area ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} id="file-input" />
          <div className="upload-icon"><UploadIcon /></div>
          <div className="upload-text">
            Drag & drop PDF files here, or <span className="upload-browse">click to browse</span>
          </div>
        </div>

        {/* Selected Files */}
        {files.length > 0 && (
          <div className="files-list">
            {files.map(file => (
              <div key={file.name} className="file-item">
                <FileIcon />
                <span className="file-name">{file.name}</span>
                <button
                  onClick={() => removeFile(file.name)}
                  className="file-remove"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Status */}
        {status !== 'idle' && (
          <div className="status-section">
            {status === 'uploading' && 'Uploading files...'}
            {status === 'extracting' && 'Extracting data from PDFs...'}
            {status === 'success' && 'Success! Your file is downloading...'}
            {status === 'error' && errorMessage}
          </div>
        )}

        {/* Extract Button */}
        <button
          className="action-button"
          onClick={handleExtract}
          disabled={status === 'uploading' || status === 'extracting'}
        >
          {status === 'idle' && 'Start Extraction'}
          {status === 'uploading' && 'Uploading...'}
          {status === 'extracting' && 'Extracting Data...'}
          {status === 'success' && 'Download Complete'}
          {status === 'error' && 'Try Again'}
        </button>
      </div>

      {/* Loader Overlay */}
      {isProcessing && (
        <div className="loader-overlay">
          <div className="spinner"></div>
          <p>Processing your files...</p>
        </div>
      )}

      <div className="footer-note">v1.0  Made by Rahul</div>
    </body>
  );
}

export default App;