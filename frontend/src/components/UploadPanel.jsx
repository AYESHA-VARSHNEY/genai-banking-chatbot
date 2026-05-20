import { useState } from "react";

export default function UploadPanel({ apiBase }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setStatus(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${apiBase}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setStatus({ type: "success", message: data.message });
      } else {
        setStatus({ type: "error", message: data.detail });
      }
    } catch (err) {
      setStatus({ type: "error", message: "Upload failed. Server might be down." });
    } finally {
      setLoading(false);
      setFile(null);
    }
  };

  return (
    <div className="upload-panel">
      <h2>📄 Upload Banking Documents</h2>
      <p>Upload PDF or TXT files to expand the chatbot's knowledge base.</p>

      <div className="upload-box">
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={(e) => setFile(e.target.files[0])}
          id="file-input"
          style={{ display: "none" }}
        />
        <label htmlFor="file-input" className="file-label">
          {file ? `📎 ${file.name}` : "Click to select a file (PDF or TXT)"}
        </label>
        <button className="upload-btn" onClick={handleUpload} disabled={!file || loading}>
          {loading ? "Uploading..." : "Upload & Ingest"}
        </button>
      </div>

      {status && (
        <div className={`status-msg ${status.type}`}>
          {status.type === "success" ? "✅" : "❌"} {status.message}
        </div>
      )}

      <div className="upload-tips">
        <h3>Supported File Types:</h3>
        <ul>
          <li>📄 PDF — Loan agreements, credit card T&C, policy documents</li>
          <li>📝 TXT — FAQs, banking guides, support manuals</li>
        </ul>
      </div>
    </div>
  );
}