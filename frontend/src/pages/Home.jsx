
import React from "react";
import { Link } from "react-router-dom";
import "../App.css";
import "./Home.css";

export default function Home() {
  return (
    <main className="medi-home">
      {/* Navigation */}
      <header className="medi-nav">
        <Link to="/" className="medi-brand">
          <span className="medi-brand-icon">M</span>
          <span>
            <strong>MediAI</strong>
            <small>MEDICAL IMAGE INTELLIGENCE</small>
          </span>
        </Link>

        <nav className="medi-nav-links">
          <Link to="/" className="medi-nav-active">
            Home
          </Link>
          <Link to="/detector">Detector</Link>
          <Link to="/about">About</Link>
        </nav>

        <Link to="/login" className="medi-login">
          Login <span aria-hidden="true">↗</span>
        </Link>
      </header>

      {/* Main hero section */}
      <section className="medi-hero">
        <div className="medi-hero-content">
          <div className="medi-eyebrow">
            <span className="medi-status-dot" />
            AI-POWERED MEDICAL IMAGE ANALYSIS
          </div>

          <h1>
            See beyond
            <br />
            the scan.
            <br />
            <span>Trust the evidence.</span>
          </h1>

          <p className="medi-hero-description">
            Detect potential manipulations in medical images with
            AI-powered analysis. Explore suspicious regions and
            understand your results through one simple interface.
          </p>

          <div className="medi-hero-actions">
            <Link to="/detector" className="medi-primary-button">
              Open Image Detector <span aria-hidden="true">→</span>
            </Link>

            <Link to="/about" className="medi-secondary-button">
              Learn about MediAI
            </Link>
          </div>

          <div className="medi-trust-note">
            <span className="medi-trust-check">✓</span>
            <span>Image analysis support</span>
            <span className="medi-trust-separator">·</span>
            <span>Visual result insights</span>
          </div>
        </div>

        {/* Brain MRI image */}
        <div className="medi-hero-visual">
          <div className="medi-scan-card">
            <div className="medi-scan-top">
              <div>
                <span className="medi-scan-label">SCAN VIEWER</span>
                <span className="medi-scan-subtitle">
                  Brain MRI · Axial view
                </span>
              </div>

              <span className="medi-scan-live">
                <span className="medi-status-dot" />
                AI READY
              </span>
            </div>

            <div className="medi-scan-image-wrap">
              <img
                src="/brain img.jpeg"
                alt="Black and white brain MRI scan"
                className="medi-scan-image"
              />

              <div className="medi-scan-image-shade" />

              <div className="medi-scan-corner-label">
                MRI / BRAIN
              </div>

              <div className="medi-scan-bottom-label">
                MEDICAL IMAGE ANALYSIS
              </div>
            </div>

            <div className="medi-scan-footer">
              <div className="medi-scan-footer-icon">✳</div>
              <div>
                <strong>AI-assisted screening</strong>
                <p>Review image integrity and flagged regions</p>
              </div>
              <span className="medi-scan-arrow">↗</span>
            </div>
          </div>

          <p className="medi-image-disclaimer">
            Illustrative scan display · Not a clinical diagnosis
          </p>
        </div>
      </section>

      {/* Bottom information strip */}
      <section className="medi-info-strip">
        <div>
          <span className="medi-info-number">01</span>
          <div>
            <strong>Upload</strong>
            <p>Choose a medical image</p>
          </div>
        </div>

        <div>
          <span className="medi-info-number">02</span>
          <div>
            <strong>Analyze</strong>
            <p>Run AI-assisted detection</p>
          </div>
        </div>

        <div>
          <span className="medi-info-number">03</span>
          <div>
            <strong>Review</strong>
            <p>Inspect the returned results</p>
          </div>
        </div>
      </section>

      <footer className="medi-footer">
        <span>© MediAI · Medical Image Integrity</span>
        <span>Designed for research and demonstration</span>
      </footer>
    </main>
  );
}