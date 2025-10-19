import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import './App.css';

// Vercel Analytics
const initVercelAnalytics = () => {
  if (typeof window !== 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://cdn.vercel-analytics.com/v1/script.js';
    script.async = true;
    document.head.appendChild(script);
  }
};

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
  const [retryCount, setRetryCount] = useState(0);
  const [maxRetries] = useState(3);
  const [showMessage, setShowMessage] = useState(false);
  const [backendReady, setBackendReady] = useState(false);
  const [backendLoading, setBackendLoading] = useState(false);

  useEffect(() => {
    initVercelAnalytics();
    if (typeof window !== 'undefined' && window.va) {
      window.va('pageview');
    }
  }, []);

  const wakeupBackend = async () => {
    setBackendLoading(true);
    try {
      const response = await fetch('https://pdf-extraction-backend-b3bx.onrender.com/health', {
        method: 'GET',
      });
      if (response.ok) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Add delay
        setBackendReady(true);
        setErrorMessage('');
        setShowMessage(false);
        if (typeof window !== 'undefined' && window.va) {
          window.va('event', { name: 'backend_connected' });
        }
      } else {
        throw new Error(`Backend returned ${response.status}`);
      }
    } catch (error) {
      setErrorMessage('Failed to connect to backend.');
      setShowMessage(true);
      setBackendReady(false);
    } finally {
      setBackendLoading(false);
    }
  };

  const onDrop = useCallback(acceptedFiles => {
    const pdfFiles = acceptedFiles.filter(file => file.type === "application/pdf");
    setFiles(prevFiles => [...prevFiles, ...pdfFiles]);
    setShowMessage(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }
  });

  const removeFile = (fileName) => {
    setFiles(files.filter(file => file.name !== fileName));
    setShowMessage(false);
  };

  const extractWithRetry = async (formData, attempt = 0) => {
    try {
      setStatus('extracting');
      setRetryCount(attempt);

      let response;
      try {
        response = await fetch('https://pdf-extraction-backend-b3bx.onrender.com/extract/', {
          method: 'POST',
          body: formData,
          timeout: 300000,
        });
      } catch (networkError) {
        throw new Error('Cannot connect to backend server.');
      }

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
          const errData = await response.json();
          errorDetail = errData.detail || errorDetail;
        } catch (e) {
          // If response is not JSON, use default error
        }
        throw new Error(errorDetail);
      }

      setStatus('downloading');
      const blob = await response.blob();

      if (blob.size === 0) {
        throw new Error('Received empty file from server');
      }

      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'extracted_data.xlsx';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=([^;]+)/);
        if (match) {
          filename = match[1].replace(/"/g, '').trim();
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setStatus('success');
      setErrorMessage('');
      setRetryCount(0);
      setShowMessage(true);

      if (typeof window !== 'undefined' && window.va) {
        window.va('event', { name: 'extraction_success' });
      }

      // Keep showing success message for 3 seconds
      await new Promise(resolve => setTimeout(resolve, 3000));

    } catch (error) {
      console.error(`Extraction failed (Attempt ${attempt + 1}/${maxRetries}):`, error);

      const errorMsg = error.message || 'An unknown error occurred';
      setErrorMessage(errorMsg);

      const isRetryableError =
        errorMsg.includes('invalid') ||
        errorMsg.includes('incomplete') ||
        errorMsg.includes('empty') ||
        errorMsg.includes('timeout') ||
        errorMsg.includes('LLM');

      if (isRetryableError && attempt < maxRetries - 1) {
        console.log(`Retrying extraction... (Attempt ${attempt + 2}/${maxRetries})`);

        const waitTime = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, waitTime));

        return extractWithRetry(formData, attempt + 1);
      } else {
        setStatus('error');
        setShowMessage(true);
        throw error;
      }
    }
  };

  const handleExtract = async () => {
    if (files.length === 0) {
      setErrorMessage("Please upload at least one PDF file.");
      setStatus('error');
      setShowMessage(true);
      if (typeof window !== 'undefined' && window.va) {
        window.va('event', { name: 'extraction_error_no_files' });
      }
      return;
    }

    setIsProcessing(true);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      setStatus('uploading');
      setErrorMessage('');
      setRetryCount(0);
      setShowMessage(false);

      console.log(`Processing file ${i + 1}/${files.length}: ${file.name}`);

      if (typeof window !== 'undefined' && window.va) {
        window.va('event', { name: 'extraction_started', value: 1 });
      }

      const formData = new FormData();
      formData.append('files', file);
      formData.append('template_id', template);

      try {
        await extractWithRetry(formData, 0);
        console.log(`File ${i + 1} completed successfully`);
      } catch (error) {
        console.error("Extraction failed:", error);
        if (typeof window !== 'undefined' && window.va) {
          window.va('event', { name: 'extraction_failed', value: error.message });
        }
      }

      if (i < files.length - 1) {
        console.log(`Waiting before file ${i + 2}...`);
        await new Promise(resolve => setTimeout(resolve, 2500));
        // Clear message before next file
        setShowMessage(false);
      }
    }

    // Keep success message visible if last file was successful
    if (status !== 'error') {
      // Message stays visible - user will see it
      await new Promise(resolve => setTimeout(resolve, 3000));
      setShowMessage(false);
    }

    setStatus('idle');
    setIsProcessing(false);
  };

  return (
    <body>
      <div className={`app-container ${isProcessing && (status === 'uploading' || status === 'extracting' || status === 'downloading') ? 'processing' : ''}`}>
        <h1>PDF Extraction Tool</h1>
        <p>Leveraging AI to extract structured data from your documents.</p>

        <div className="backend-section">
          <div className="backend-indicator">
            <span className={`status-dot ${backendReady ? 'ready' : ''}`}></span>
            <span className="backend-label">
              {backendReady ? 'Backend Ready' : 'Backend Offline'}
            </span>
          </div>
          {!backendReady && (
            <button
              className="wakeup-button"
              onClick={wakeupBackend}
              disabled={backendLoading}
            >
              {backendLoading ? 'Connecting...' : 'Start Backend'}
            </button>
          )}
        </div>

        <div className="template-selector">
          <label>Select an Extraction Template</label>
          <select value={template} onChange={(e) => {
            setTemplate(e.target.value);
            setShowMessage(false);
          }} disabled={isProcessing || !backendReady}>
            <option value="1">Template 1 - Standard fund financial reports</option>
            <option value="2">Template 2 - Detailed portfolio company analysis</option>
          </select>
        </div>

        <div {...getRootProps()} className={`upload-area ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} id="file-input" />
          <div className="upload-icon"><UploadIcon /></div>
          <div className="upload-text">
            Drag & drop PDF files here, or <span className="upload-browse">click to browse</span>
          </div>
        </div>

        {files.length > 0 && (
          <div className="files-list">
            {files.map(file => (
              <div key={file.name} className="file-item">
                <FileIcon />
                <span className="file-name">{file.name}</span>
                <button
                  onClick={() => removeFile(file.name)}
                  className="file-remove"
                  disabled={isProcessing}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {(status === 'uploading' || status === 'extracting' || status === 'downloading') && (
          <div className="status-section">
            {status === 'uploading' && 'Uploading files...'}
            {status === 'extracting' && `Extracting data from PDFs${retryCount > 0 ? ` (Attempt ${retryCount + 1}/${maxRetries})` : ''}...`}
            {status === 'downloading' && 'Preparing your download...'}
          </div>
        )}

        {showMessage && !isProcessing && (
          <div className={`completion-message ${status === 'success' ? 'success' : 'error'}`}>
            {status === 'success' && (
              <>
                <div className="message-icon">✓</div>
                <div className="message-text">File downloaded successfully!</div>
              </>
            )}
            {status === 'error' && (
              <>
                <div className="message-icon">✕</div>
                <div className="message-text">{errorMessage || 'An error occurred'}</div>
              </>
            )}
          </div>
        )}

        <button
          className="action-button"
          onClick={handleExtract}
          disabled={isProcessing || !backendReady}
        >
          {status === 'idle' && 'Start Extraction'}
          {status === 'uploading' && 'Uploading...'}
          {status === 'extracting' && 'Extracting Data...'}
          {status === 'downloading' && 'Downloading...'}
          {status === 'success' && 'Start Extraction'}
          {status === 'error' && 'Try Again'}
        </button>
      </div>

      {isProcessing && (status === 'uploading' || status === 'extracting' || status === 'downloading') && (
        <div className="loader-overlay">
          <div className="spinner"></div>
          <p>
            {status === 'uploading' ? 'Uploading files...' :
              status === 'extracting' ? `Extracting data from PDFs${retryCount > 0 ? ` (Attempt ${retryCount + 1}/${maxRetries})` : ''}...` :
                'Preparing your download...'}
          </p>
        </div>
      )}

      <div className="footer-note">v1.0</div>
    </body>
  );
}

export default App;