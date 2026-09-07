import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const navItems = [
  { to: "/", label: "Home", icon: "🏠" },
  { to: "/jobs", label: "Jobs", icon: "📋" },
  { to: "/candidates", label: "Candidates", icon: "🧑‍💼" },
  { to: "/analyse", label: "Analyse", icon: "🎯" }
];

function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">AI Candidate Intelligence</div>
      <ul className="sidebar-nav">
        {navItems.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Sidebar;