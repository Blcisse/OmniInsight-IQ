import "./globals.css";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Footer from "./components/Footer";
import React from "react";

export const metadata = {
  title: "OmniInsightIQ",
  description: "Analytics and insights platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <div style={{ display: "flex", minHeight: "80vh" }}>
          <Sidebar />
          <main style={{ flex: 1, padding: "1rem" }}>{children}</main>
        </div>
        <Footer />
      </body>
    </html>
  );
}

