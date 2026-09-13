import React from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { Hero3DFlipDemo } from './components/Hero3DFlipDemo';
import { ProductivityCalculator } from './components/ProductivityCalculator';
import { Features } from './components/Features';
import { Comparison } from './components/Comparison';
import { DownloadSection } from './components/DownloadSection';
import { Footer } from './components/Footer';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#FCFCFD] text-slate-900 bg-grid-pattern relative selection:bg-brand-500 selection:text-white">
      {/* Top Ambient Glow */}
      <div className="absolute top-0 inset-x-0 h-[600px] bg-radial-glow pointer-events-none -z-10" />

      {/* Navigation */}
      <Navbar />

      {/* Main Content */}
      <main>
        {/* Hero Section */}
        <Hero />

        {/* 3D Flip Demo (The Centerpiece) */}
        <Hero3DFlipDemo />

        {/* Productivity Calculator */}
        <ProductivityCalculator />

        {/* 4-Tier CHA Engine Architecture & Security */}
        <Features />

        {/* Feature Comparison */}
        <Comparison />

        {/* Download Section */}
        <DownloadSection />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default App;
