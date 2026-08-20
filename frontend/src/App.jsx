import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [rankedCandidates, setRankedCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [matchDetails, setMatchDetails] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]); // list of {question, answer}
  const [chatLoading, setChatLoading] = useState(false);


  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (selectedJobId) {
      fetchRankedCandidates(selectedJobId);
      //setSelectedCandidate(null); // clear details when switching jobs
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

  // async function handleCandidateClick(candidateId) {
  //   const response = await fetch(`${API_BASE}/candidates/${candidateId}`);
  //   const data = await response.json();
  //   setSelectedCandidate(data);
  // }
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

async function handleAskQuestion() {
  if (!chatQuestion.trim()) return;

  setChatLoading(true);
  const questionText = chatQuestion;
  setChatQuestion("");

  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: questionText, job_id: selectedJobId }),
  });
  const data = await response.json();

  setChatHistory((prev) => [...prev, { question: questionText, answer: data.answer }]);
  setChatLoading(false);
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
          <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Candidate</th>
                <th>Match</th>
              </tr>
            </thead>
            <tbody>
              {rankedCandidates.map((candidate, index) => (
                <tr
                  key={candidate.id}
                  onClick={() => handleCandidateClick(candidate.id)}
                  style={{ cursor: "pointer" }}
                >
                  <td>{index + 1}</td>
                  <td>{candidate.name}</td>
                  <td>{(candidate.score * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {/* {selectedCandidate && (
        <div style={{ marginTop: "20px", padding: "12px", border: "1px solid #ccc" }}>
          <h3>{selectedCandidate.name}</h3>
          <p><strong>Status:</strong> {selectedCandidate.status}</p>
          <p><strong>Experience:</strong> {selectedCandidate.experience_years ?? "Not specified"} years</p>
          <p><strong>Education:</strong> {selectedCandidate.education ?? "Not specified"}</p>
          <p><strong>Skills:</strong> {selectedCandidate.skills?.join(", ") || "None extracted"}</p>
        </div>
      )} */}
      {loadingExplanation && <p>Loading match details...</p>}

{matchDetails && (
  <div style={{ marginTop: "20px", padding: "12px", border: "1px solid #ccc", maxWidth: "500px" }}>
    <h3>{matchDetails.candidate_name}</h3>
    <p><strong>Match Score:</strong> {matchDetails.score}%</p>

    <p><strong>Strong Matches</strong></p>
    <ul>
      {matchDetails.matching_skills.length > 0 ? (
        matchDetails.matching_skills.map((skill) => <li key={skill}>{skill}</li>)
      ) : (
        <li>None</li>
      )}
    </ul>

    <p><strong>Missing</strong></p>
    <ul>
      {matchDetails.missing_skills.length > 0 ? (
        matchDetails.missing_skills.map((skill) => <li key={skill}>{skill}</li>)
      ) : (
        <li>None</li>
      )}
    </ul>

    <p><strong>Experience</strong></p>
    <p>{matchDetails.experience_years ?? "Not specified"} years relevant experience</p>

    <p><strong>AI Explanation</strong></p>
    <p>{matchDetails.explanation}</p>
  </div>
)}

<div style={{ marginTop: "30px", padding: "12px", border: "1px solid #999", maxWidth: "600px" }}>
  <h2>Ask the AI Recruitment Assistant</h2>

  <div style={{ maxHeight: "300px", overflowY: "auto", marginBottom: "10px" }}>
    {chatHistory.map((entry, index) => (
      <div key={index} style={{ marginBottom: "12px" }}>
        <p><strong>Q:</strong> {entry.question}</p>
        <p><strong>A:</strong> {entry.answer}</p>
      </div>
    ))}
    {chatLoading && <p>Thinking...</p>}
  </div>

  <input
    type="text"
    value={chatQuestion}
    onChange={(e) => setChatQuestion(e.target.value)}
    onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
    placeholder="e.g. Which candidates know Python and AWS?"
    style={{ width: "100%", padding: "8px" }}
  />
  <button onClick={handleAskQuestion} disabled={chatLoading} style={{ marginTop: "8px" }}>
    Ask
  </button>
</div>
      
    </div>
  );
}

export default App;