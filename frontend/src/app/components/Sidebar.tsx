const linkStyle: React.CSSProperties = { display: "block", padding: "0.5rem 0" };

export default function Sidebar() {
  return (
    <aside style={{ width: 240, padding: "1rem", background: "#f8fafc", borderRight: "1px solid #e2e8f0" }}>
      <nav>
        <a href="#" style={linkStyle}>Dashboard</a>
        <a href="#" style={linkStyle}>Sales</a>
        <a href="#" style={linkStyle}>Marketing</a>
        <a href="#" style={linkStyle}>Analytics</a>
        <a href="#" style={linkStyle}>Insights</a>
      </nav>
    </aside>
  );
}

