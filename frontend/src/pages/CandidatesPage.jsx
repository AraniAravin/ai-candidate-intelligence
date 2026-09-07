import { useState, useEffect } from "react";
import CvUploadForm from "../CvUploadForm";
import { API_BASE } from "../api";

function CandidatesPage() {
  const [candidates, setCandidates] = useState([]);

  useEffect(() => {
    fetchCandidates();
  }, []);

  async function fetchCandidates() {
    const response = await fetch(`${API_BASE}/candidates`);
    const data = await response.json();
    setCandidates(data);
  }

  return (
    <div>
      <h1>Candidates</h1>
      <CvUploadForm onCandidatesProcessed={fetchCandidates} />

      <h2>All Candidates</h2>
      <ul className="plain-list">
        {candidates.map((c) => (
          <li key={c.id} className="list-card">
            <strong>{c.name || "Unnamed"}</strong>{" "}
            <span className={`status-badge status-${c.status}`}>{c.status}</span>
            <div className="tag-row">
              {c.skills.map((s) => (
                <span key={s} className="tag">{s}</span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CandidatesPage;