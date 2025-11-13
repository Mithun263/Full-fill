import React, { useState, useEffect } from "react";
import axios from "axios";
import ProgressBar from "./ProgressBar";

const API_URL = "http://127.0.0.1:8000/import";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const uploadFile = async () => {
    if (!file) return alert("Please select a CSV file!");
    setProgress(0);
    setStatus("Uploading...");
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          const percent = Math.round((event.loaded * 100) / event.total);
          setProgress(percent);
        },
      });
      setJobId(res.data.job_id);
      setStatus(res.data.message || "Processing file...");
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Upload failed");
      setStatus("");
    }
  };

  // Poll for backend import progress
  useEffect(() => {
    if (!jobId) return;
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/status/${jobId}`);
        if (res.data.progress !== undefined) {
          setProgress(res.data.progress);
          setStatus(res.data.message);
        }
        if (res.data.progress === 100) clearInterval(interval);
      } catch (err) {
        console.error(err);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div className="upload-container">
      <h3>📤 Upload Product CSV</h3>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={uploadFile} disabled={!file}>
        Upload
      </button>

      {progress > 0 && <ProgressBar progress={progress} />}
      {status && <p className="status-text">{status}</p>}
      {error && <p className="error-text">❌ {error}</p>}
    </div>
  );
}

export default FileUpload;
