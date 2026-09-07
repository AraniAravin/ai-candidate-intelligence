import { useState, useEffect } from "react";
import { API_BASE } from "../api";
import { useJobContext } from "../context/JobContext";

function AnalysePage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [rankedCandidates, setRankedCandidates] = useState([]);
  const [matchDetails, setMatchDetails] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (selectedJobId) {
      fetchRankedCandidates(selectedJobId);
      setMatchDetails(null);
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

  async function handleCandidateClick(candidateId) {
    setLoadingExplanation(true);
    setMatchDetails(null);

    const response = await fetch(
      `${API_BASE}/jobs/${selectedJobId}/candidates/${candidateId}/match-details`
    );
    const data = await response.json();

    setMatchDetails(data);
    setLoadingExplanation(false);
  }

  return (
    <div>
      <h1>Analyse Candidates</h1>

      <div style={{ marginBottom: "20px" }}>
        <label htmlFor="job-select"><strong>Select a job:</strong></label>
        <br />
        <select
          id="job-select"
          value={selectedJobId ?? ""}
          onChange={(e) => setSelectedJobId(Number(e.target.value))}
          style={{ marginTop: "6px", minWidth: "300px" }}
        >
          <option value="" disabled>Choose a job...</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.role || "Untitled role"} 
              {/* (ID: {job.id}) */}
            </option>
          ))}
        </select>
      </div>

      {selectedJobId && (
        <>
          <h2>Ranked Candidates</h2>
          <table className="styled-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Candidate</th>
                <th>Match</th>
              </tr>
            </thead>
            <tbody>
              {rankedCandidates.map((candidate, index) => (
                <tr key={candidate.id} onClick={() => handleCandidateClick(candidate.id)}>
                  <td>{index + 1}</td>
                  <td>{candidate.name}</td>
                  <td>{(candidate.score * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {loadingExplanation && <p>Loading match details...</p>}

      {matchDetails && (
        <div className="match-card">
          <h3>{matchDetails.candidate_name}</h3>
          <p><strong>Match Score:</strong> {matchDetails.score}%</p>

          <p><strong>Strong Matches</strong></p>
          <div className="tag-row">
            {matchDetails.matching_skills.length > 0 ? (
              matchDetails.matching_skills.map((s) => (
                <span key={s} className="tag tag-good">{s}</span>
              ))
            ) : (
              <span>None</span>
            )}
          </div>

          <p><strong>Missing</strong></p>
          <div className="tag-row">
            {matchDetails.missing_skills.length > 0 ? (
              matchDetails.missing_skills.map((s) => (
                <span key={s} className="tag tag-bad">{s}</span>
              ))
            ) : (
              <span>None</span>
            )}
          </div>

          <p><strong>Experience:</strong> {matchDetails.experience_years ?? "Not specified"} years</p>

          <p><strong>AI Explanation</strong></p>
          <p>{matchDetails.explanation}</p>
        </div>
      )}
    </div>
  );
}

export default AnalysePage;