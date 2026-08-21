import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function CvUploadForm({ onCandidatesProcessed }) {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(""); // human-readable progress text
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (files.length === 0) return;

    setSubmitting(true);
    setStatus("Uploading...");

    try {
      const formData = new FormData();
      for (const file of files) {
        formData.append("files", file);
      }

      const uploadResponse = await fetch(`${API_BASE}/candidates/upload`, {
        method: "POST",
        body: formData, // no Content-Type header — browser sets it automatically for FormData
      });

      if (!uploadResponse.ok) throw new Error(`Upload failed: ${uploadResponse.status}`);

      setStatus("Analyzing (this can take a while per CV)...");

      const analyzeResponse = await fetch(`${API_BASE}/candidates/analyze`, {
        method: "POST",
      });
      const analyzeData = await analyzeResponse.json();

      setStatus(
        `Done. Processed: ${analyzeData.processed.length}, Failed: ${analyzeData.failed.length}`
      );
      setFiles([]);
      onCandidatesProcessed(); // tell the parent something changed
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
      <h3>Upload CVs</h3>
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />
      <button type="submit" disabled={submitting || files.length === 0} style={{ marginLeft: "8px" }}>
        {submitting ? "Working..." : "Upload & Analyze"}
      </button>
      {status && <p>{status}</p>}
    </form>
  );
}

export default CvUploadForm;