import React from 'react';
import { Github } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="py-12 border-t border-slate-200/80 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <img src="./app_icon.png" alt="Plik" className="w-7 h-7 rounded-lg" />
          <span className="font-extrabold text-slate-800 tracking-tight">Plik (พลิก)</span>
          <span className="text-xs text-slate-400">© 2026 Plik Software. Released under MIT License.</span>
        </div>

        <div className="flex items-center gap-6 text-xs font-medium text-slate-500">
          <a href="#features" className="hover:text-slate-900 transition-colors">สถาปัตยกรรม</a>
          <a href="#calculator" className="hover:text-slate-900 transition-colors">เครื่องคำนวณ</a>
          <a href="#download" className="hover:text-slate-900 transition-colors">ดาวน์โหลด</a>
          <a 
            href="https://github.com" 
            target="_blank" 
            rel="noreferrer"
            className="flex items-center gap-1.5 hover:text-slate-900 transition-colors"
          >
            <Github className="w-4 h-4" />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </footer>
  );
};
