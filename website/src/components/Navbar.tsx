import React, { useState, useEffect } from 'react';
import { Download, Github } from 'lucide-react';

export const Navbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled 
        ? 'bg-white/80 backdrop-blur-xl border-b border-slate-200/80 shadow-sm py-3' 
        : 'bg-transparent py-5'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Brand Logo */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="relative w-9 h-9 rounded-xl overflow-hidden shadow-md shadow-emerald-500/10 border border-slate-200/80 group-hover:scale-105 transition-transform duration-200">
            <img 
              src="./app_icon.png" 
              alt="Plik Logo" 
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-xl tracking-tight text-slate-900">Plik</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200/60">
                v1.0.0
              </span>
            </div>
            <span className="text-[10px] text-slate-500 font-medium -mt-0.5 tracking-wider uppercase">
              Bilingual Typing Engine
            </span>
          </div>
        </a>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          <a href="#demo" className="hover:text-slate-900 transition-colors">ทดลองใช้งาน</a>
          <a href="#calculator" className="hover:text-slate-900 transition-colors">คำนวณเวลาที่ประหยัด</a>
          <a href="#features" className="hover:text-slate-900 transition-colors">สถาปัตยกรรม</a>
          <a href="#comparison" className="hover:text-slate-900 transition-colors">เปรียบเทียบ</a>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            title="GitHub Repository"
          >
            <Github className="w-5 h-5" />
          </a>

          <a
            href="#download"
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-sm hover:shadow transition-all duration-200 active:scale-95"
          >
            <Download className="w-4 h-4 text-brand-400" />
            <span>ดาวน์โหลด v1.0</span>
          </a>
        </div>
      </div>
    </header>
  );
};
