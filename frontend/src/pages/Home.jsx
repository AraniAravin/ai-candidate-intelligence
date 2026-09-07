import { useNavigate } from "react-router-dom";
import "./Home.css";

function Home() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Welcome 👋</h1>
      <p className="home-subtitle">
        Manage job descriptions, analyse candidates, and get AI-powered ranking explanations — all in one place.
      </p>

      <div className="home-cards">
        <div className="home-card" onClick={() => navigate("/jobs")}>
          <div className="home-card-icon">📋</div>
          <h3>Upload a New Job Description</h3>
          <p>Create a job posting and let AI extract the role, required skills, and experience level.</p>
          <span className="home-card-cta">Go to Jobs →</span>
        </div>

        <div className="home-card" onClick={() => navigate("/candidates")}>
          <div className="home-card-icon">🧑‍💼</div>
          <h3>Upload Candidates to Analyse</h3>
          <p>Upload CV PDFs and let AI extract skills, experience, and education automatically.</p>
          <span className="home-card-cta">Go to Candidates →</span>
        </div>
      </div>
    </div>
  );
}

export default Home;