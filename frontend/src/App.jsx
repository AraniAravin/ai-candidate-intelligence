import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [rankedCandidates, setRankedCandidates] = useState([]);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (selectedJobId) {
      fetchRankedCandidates(selectedJobId);
    }
  }, [selectedJobId]);

  async function fetchJobs() {
    const response = await fetch(`${API_BASE}/jobs`);
    const data = await response.json();
    setJobs(data);
  }

  async function fetchRankedCandidates(jobId) {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/ranked-candidates`);
    const data = await response.json();
    setRankedCandidates(data.ranked_candidates);
  }

  return (
    <div style={{ fontFamily: "sans-serif", padding: "20px" }}>
      <h1>AI Candidate Intelligence</h1>

      <h2>Jobs</h2>
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <button onClick={() => setSelectedJobId(job.id)}>
              {job.role || "Untitled role"} (ID: {job.id})
            </button>
          </li>
        ))}
      </ul>

      {selectedJobId && (
        <>
          <h2>Ranked Candidates for Job #{selectedJobId}</h2>
          <ul>
            {rankedCandidates.map((candidate, index) => (
              <li key={index}>
                {candidate.name} — {(candidate.score * 100).toFixed(1)}%
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;