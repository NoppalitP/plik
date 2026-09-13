import React, { useState } from 'react';
import { Download, Package, Terminal, Copy, Check, Sparkles } from 'lucide-react';

export const DownloadSection: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const handleCopyPip = () => {
    navigator.clipboard.writeText('pip install plik');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="download" className="py-20 sm:py-28 relative">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold uppercase tracking-wider mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ready for Windows 10 & 11</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            เริ่มต้นใช้งาน Plik ได้ฟรี วันนี้
          </h2>
          <p className="mt-4 text-slate-600 text-base sm:text-lg">
            เลือกรูปแบบการติดตั้งที่เหมาะกับการใช้งานของคุณ — ทั้งแบบ Installer และ Portable ไร้รอยต่อ
          </p>
        </div>

        {/* Download Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Official Installer */}
          <div className="p-8 rounded-3xl bg-white border-2 border-brand-500/80 shadow-xl shadow-brand-500/5 relative flex flex-col justify-between">
            <div className="absolute -top-3.5 right-6 px-3 py-0.5 rounded-full bg-brand-600 text-white text-[11px] font-bold tracking-wide uppercase">
              แนะนำสำหรับทุกคน
            </div>

            <div>
              <div className="w-12 h-12 rounded-2xl bg-brand-50 border border-brand-200 text-brand-700 flex items-center justify-center mb-6">
                <Download className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                Windows Setup Installer
              </h3>
              <p className="text-xs text-slate-500 font-mono mt-1">Plik_Setup_v1.0.exe</p>
              <p className="text-xs sm:text-sm text-slate-600 mt-4 leading-relaxed">
                ติดตั้งลงใน Program Files อัตโนมัติ พร้อมสร้าง Shortcut และตั้งค่าเปิดตอนเปิดเครื่อง (Run on Startup)
              </p>
            </div>

            <div className="mt-8">
              <a
                href="./installer/Plik_Setup_v1.0.exe"
                download
                className="w-full flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-2xl shadow-md shadow-brand-600/20 hover:shadow-lg transition-all duration-200 active:scale-95"
              >
                <Download className="w-4 h-4" />
                <span>ดาวน์โหลดตัวติดตั้ง (.exe)</span>
              </a>
              <span className="block text-center text-[11px] text-slate-400 mt-2">
                ขนาด ~15 MB • Windows 10/11 x64
              </span>
            </div>
          </div>

          {/* Card 2: Portable Standalone */}
          <div className="p-8 rounded-3xl bg-white border border-slate-200 hover:border-slate-300 shadow-md hover:shadow-xl transition-all duration-300 flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center mb-6">
                <Package className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                Portable Standalone
              </h3>
              <p className="text-xs text-slate-500 font-mono mt-1">Plik.exe (Zero Install)</p>
              <p className="text-xs sm:text-sm text-slate-600 mt-4 leading-relaxed">
                ไม่ต้องติดตั้งใดๆ เหมาะสำหรับใส่ Flash Drive หรือใช้งานในเครื่องที่ไม่ได้รับสิทธิ์ Admin เพียงดับเบิลคลิกก็ใช้งานได้ทันที
              </p>
            </div>

            <div className="mt-8">
              <a
                href="./Plik.exe"
                download
                className="w-full flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-2xl transition-all duration-200 active:scale-95"
              >
                <Download className="w-4 h-4 text-slate-600" />
                <span>ดาวน์โหลด Portable (.exe)</span>
              </a>
              <span className="block text-center text-[11px] text-slate-400 mt-2">
                ขนาด ~14 MB • ไม่ต้องติดตั้ง
              </span>
            </div>
          </div>

          {/* Card 3: Developer CLI */}
          <div className="p-8 rounded-3xl bg-white border border-slate-200 hover:border-slate-300 shadow-md hover:shadow-xl transition-all duration-300 flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center mb-6">
                <Terminal className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                Python Package (CLI)
              </h3>
              <p className="text-xs text-slate-500 font-mono mt-1">pip install plik</p>
              <p className="text-xs sm:text-sm text-slate-600 mt-4 leading-relaxed">
                สำหรับนักพัฒนาที่ใช้ Python สามารถติดตั้งและปรับแต่งโมเดล หรือรันผ่านคำสั่ง Terminal ได้โดยตรง
              </p>
            </div>

            <div className="mt-8">
              <div 
                onClick={handleCopyPip}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-900 hover:bg-slate-800 text-slate-200 rounded-2xl font-mono text-xs cursor-pointer transition-colors"
                title="คลิกเพื่อคัดลอกคำสั่ง"
              >
                <span className="text-brand-400">$ pip install plik</span>
                <button className="text-slate-400 hover:text-white">
                  {copied ? <Check className="w-4 h-4 text-brand-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
              <span className="block text-center text-[11px] text-slate-400 mt-2">
                {copied ? 'คัดลอกแล้ว!' : 'Python 3.10 - 3.13'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
