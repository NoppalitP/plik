import React from 'react';
import { motion } from 'framer-motion';
import { Download, Sparkles, ShieldCheck, Zap, ArrowRight } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section className="relative pt-32 pb-12 sm:pt-40 sm:pb-16 overflow-hidden">
      {/* Background Radial Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-gradient-to-b from-brand-100/40 via-brand-50/20 to-transparent blur-3xl pointer-events-none -z-10" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Release Badge */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-slate-200 shadow-sm text-xs font-medium text-slate-700 mb-8 hover:border-brand-300 transition-colors cursor-default"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
          </span>
          <span className="font-semibold text-brand-700">Plik v1.0.0</span>
          <span className="text-slate-300">|</span>
          <span>Offline 100% • Zero Cloud • Sub-millisecond</span>
          <Sparkles className="w-3.5 h-3.5 text-amber-500 ml-0.5" />
        </motion.div>

        {/* Headline */}
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.1, ease: "easeOut" }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 leading-[1.12]"
        >
          พิมพ์ผิดภาษา? <br className="hidden sm:inline" />
          ให้ <span className="relative inline-block text-transparent bg-clip-text bg-gradient-to-r from-brand-600 via-emerald-600 to-teal-700">
            Plik พลิกให้
            <svg className="absolute left-0 -bottom-2 w-full h-3 text-brand-400/40" viewBox="0 0 200 12" fill="none">
              <path d="M2 9C50 2 150 2 198 9" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
            </svg>
          </span> ทันทีใน 0ms
        </motion.h1>

        {/* Subtitle */}
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.2, ease: "easeOut" }}
          className="mt-6 text-lg sm:text-xl text-slate-600 max-w-3xl mx-auto font-normal leading-relaxed"
        >
          ลืมสลับแป้นพิมพ์ภาษาอังกฤษ-ไทยใช่ไหม? ไม่ต้องกดลบทีละตัวให้เสียเวลา 
          Plik ตรวจจับคำที่คุณตั้งใจพิมพ์และพลิกคำให้อัตโนมัติทันทีที่เคาะเว้นวรรค
        </motion.p>

        {/* Action Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.3, ease: "easeOut" }}
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="#download"
            className="w-full sm:w-auto flex items-center justify-center gap-3 px-8 py-4 text-base font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-2xl shadow-lg shadow-slate-900/10 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200 active:scale-95"
          >
            <Download className="w-5 h-5 text-brand-400" />
            <span>ดาวน์โหลดสำหรับ Windows</span>
            <span className="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md font-mono">
              v1.0.0
            </span>
          </a>

          <a
            href="#demo"
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-4 text-base font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200/90 rounded-2xl shadow-sm hover:shadow transition-all duration-200"
          >
            <span>ดูแอนิเมชันจำลองสด</span>
            <ArrowRight className="w-4 h-4 text-slate-400" />
          </a>
        </motion.div>

        {/* Feature Pills */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-12 flex flex-wrap items-center justify-center gap-6 sm:gap-10 text-xs sm:text-sm font-medium text-slate-500"
        >
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-brand-600" />
            <span>100% Offline (ไม่ส่งข้อมูลออกนอกเครื่อง)</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-500" />
            <span>Latency &lt; 1ms (ไม่หน่วงการพิมพ์)</span>
          </div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-500" />
            <span>Code Guard (ไม่แปลงโค้ดโปรแกรมมิ่ง)</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
