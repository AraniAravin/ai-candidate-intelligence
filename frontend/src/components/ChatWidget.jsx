import { useState } from "react";
import { API_BASE } from "../api";
import { useJobContext } from "../context/JobContext";
import "./ChatWidget.css";

function ChatWidget() {
  const { selectedJobId } = useJobContext();
  const [open, setOpen] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

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
    <>
      <button className="chat-fab" onClick={() => setOpen((o) => !o)}>
        {open ? "✕" : "💬"}
      </button>

      {open && (
        <div className="chat-panel">
          <div className="chat-panel-header">
            AI Recruitment Assistant
            {selectedJobId && <span className="chat-panel-job"> · Job #{selectedJobId}</span>}
          </div>

          <div className="chat-history">
            {chatHistory.length === 0 && !chatLoading && (
              <p className="chat-empty">
                Ask things like "Why is Candidate A better than Candidate B?"
              </p>
            )}
            {chatHistory.map((entry, index) => (
              <div key={index} className="chat-entry">
                <p className="chat-question">{entry.question}</p>
                <p className="chat-answer">{entry.answer}</p>
              </div>
            ))}
            {chatLoading && <p>Thinking...</p>}
          </div>

          <input
            type="text"
            value={chatQuestion}
            onChange={(e) => setChatQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
            placeholder="Ask the AI recruitment assistant..."
          />
          <button onClick={handleAskQuestion} disabled={chatLoading}>Ask</button>
        </div>
      )}
    </>
  );
}

export default ChatWidget;