export default function Navbar() {
  return (
    <header
      style={{
        padding: "1rem 1.5rem",
        background: "var(--base-dark-lighter)",
        color: "var(--text-primary)",
        borderBottom: "1px solid var(--glass-border)",
        backdropFilter: "var(--glass-blur)",
        WebkitBackdropFilter: "var(--glass-blur)",
        boxShadow: "var(--shadow-subtle)",
      }}
    >
      <strong
        style={{
          fontSize: "1.25rem",
          fontWeight: 700,
          background: "var(--primary-gradient)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
        }}
      >
        OmniInsightIQ
      </strong>
    </header>
  );
}

