import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function JobForm({ onJobCreated }) {
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!description.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      setDescription("");
      onJobCreated(); // tell the parent to refresh the jobs list
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
      <h3>Create a Job</h3>
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Paste the job description here..."
        rows={5}
        style={{ width: "100%", padding: "8px" }}
      />
      <button type="submit" disabled={submitting} style={{ marginTop: "8px" }}>
        {submitting ? "Creating..." : "Create Job"}
      </button>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
    </form>
  );
}

export default JobForm;