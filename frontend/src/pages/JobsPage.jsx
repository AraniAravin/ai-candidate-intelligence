import { useState, useEffect } from "react";
import JobForm from "../JobForm";
import { API_BASE } from "../api";

function JobsPage() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    fetchJobs();
  }, []);

  async function fetchJobs() {
    const response = await fetch(`${API_BASE}/jobs`);
    const data = await response.json();
    setJobs(data);
  }

  return (
    <div>
      <h1>Jobs</h1>
      <JobForm onJobCreated={fetchJobs} />

      <h2>All Jobs</h2>
      <ul className="plain-list">
        {jobs.map((job) => (
          <li key={job.id} className="list-card">
            <strong>{job.role || "Untitled role"}</strong> 
            {/* (ID: {job.id}) */}
            <div className="tag-row">
              {job.required_skills.map((s) => (
                <span key={s} className="tag">{s}</span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default JobsPage;