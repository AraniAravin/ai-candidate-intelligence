import { createContext, useContext, useState } from "react";

const JobContext = createContext(null);

export function JobProvider({ children }) {
  const [selectedJobId, setSelectedJobId] = useState(null);
  return (
    <JobContext.Provider value={{ selectedJobId, setSelectedJobId }}>
      {children}
    </JobContext.Provider>
  );
}

export function useJobContext() {
  const context = useContext(JobContext);
  if (!context) {
    throw new Error("useJobContext must be used within a JobProvider");
  }
  return context;
}