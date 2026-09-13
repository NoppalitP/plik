import React from 'react';
import { Cpu, Lock, CheckCircle2 } from 'lucide-react';

export const Features: React.FC = () => {
  const tiers = [
    {
      level: 'Tier 1',
      name: 'Code Guard',
      desc: 'ตรวจจับคำสั่ง CLI (git, npm, pip), ส่วนขยายไฟล์ (.sh, .py, .js) และ syntax โค้ด เพื่อไม่ให้ระบบเข้าไปแก้ไขโค้ดโปรแกรมมิ่งของคุณโดยเด็ดขาด',
      badge: 'Protected',
      badgeColor: 'text-blue-700 bg-blue-50 border-blue-200',
    },
    {
      level: 'Tier 2',
      name: 'Deterministic Rules',
      desc: 'ตารางแมปคู่คำสลับภาษาที่มีความแม่นยำ 100% เช่น คำเฉพาะ, คำศัพท์เชื่อมประโยค และคำผิดยอดนิยม (นะค่ะ -> นะคะ)',
      badge: 'O(1) Direct',
      badgeColor: 'text-emerald-700 bg-emerald-50 border-emerald-200',
    },
    {
      level: 'Tier 3',
      name: 'Dictionary Trie Cache',
      desc: 'โครงสร้างต้นไม้ค้นหาคำภาษาไทยกว่า 3,000+ คำที่ใช้บ่อยที่สุด ค้นหาแบบ Sub-string ได้เร็วระดับไมโครวินาที',
      badge: 'Sub-ms Speed',
      badgeColor: 'text-teal-700 bg-teal-50 border-teal-200',
    },
    {
      level: 'Tier 4',
      name: 'Bigram Transition Matrix',
      desc: 'โมเดลความน่าจะเป็นของสระและพยัญชนะไทย ตรวจจับการเรียงตัวของอักขระที่ไม่เป็นธรรมชาติในภาษาเดิมเพื่อตัดสินใจสลับภาษาอย่างแม่นยำ',
      badge: 'Context-Aware',
      badgeColor: 'text-purple-700 bg-purple-50 border-purple-200',
    },
  ];

  return (
    <section id="features" className="py-20 sm:py-28 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold uppercase tracking-wider mb-4">
            <Cpu className="w-3.5 h-3.5 text-brand-600" />
            <span>Under The Hood</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            CHA Engine: สถาปัตยกรรมอัจฉริยะ 4 ระดับ
          </h2>
          <p className="mt-4 text-slate-600 text-base sm:text-lg">
            ไม่ใช่แค่การแมปปุ่มตรงๆ แต่เป็นระบบคัดกรองบริบทหลายชั้น เพื่อความแม่นยำสูงสุดโดยไม่รบกวนการทำงานปกติ
          </p>
        </div>

        {/* 4 Tiers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {tiers.map((tier, idx) => (
            <div 
              key={idx}
              className="p-6 rounded-3xl bg-white border border-slate-200 hover:border-brand-300 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-mono font-bold text-slate-400">
                    {tier.level}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${tier.badgeColor}`}>
                    {tier.badge}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">
                  {tier.name}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {tier.desc}
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center text-xs font-semibold text-brand-600">
                <CheckCircle2 className="w-4 h-4 mr-1.5" />
                <span>Zero False Positive</span>
              </div>
            </div>
          ))}
        </div>

        {/* Security & Offline Banner */}
        <div className="mt-12 p-8 sm:p-10 rounded-3xl bg-slate-950 text-white shadow-2xl relative overflow-hidden">
          {/* Subtle glow */}
          <div className="absolute right-0 top-0 w-96 h-96 bg-brand-500/10 blur-3xl pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center relative z-10">
            <div className="lg:col-span-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-brand-400 text-xs font-semibold uppercase tracking-wider mb-4 border border-slate-700">
                <Lock className="w-3.5 h-3.5" />
                <span>Privacy First by Design</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                ข้อมูลการพิมพ์ของคุณ จะไม่หลุดออกนอกเครื่องแม้แต่ตัวอักษรเดียว
              </h3>
              <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
                Plik ทำงานแบบ Offline 100% ไม่มีโมดูล Network Egress, ไม่มี Analytics, ไม่มี Telemetry ดักเก็บข้อมูล 
                ปลอดภัยสำหรับรหัสผ่าน, เอกสารความลับทางธุรกิจ และรหัสความปลอดภัยขององค์กร
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-2xl font-extrabold text-brand-400 font-mono">0 KB</span>
                <p className="text-xs text-slate-400 mt-1">Network Outbound</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-2xl font-extrabold text-brand-400 font-mono">&lt; 15 MB</span>
                <p className="text-xs text-slate-400 mt-1">RAM Consumption</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-2xl font-extrabold text-brand-400 font-mono">&lt; 0.5 ms</span>
                <p className="text-xs text-slate-400 mt-1">Processing Latency</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-center">
                <span className="text-2xl font-extrabold text-brand-400 font-mono">100%</span>
                <p className="text-xs text-slate-400 mt-1">Windows Native Hook</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
