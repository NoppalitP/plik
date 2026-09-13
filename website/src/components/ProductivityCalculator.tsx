import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, TrendingUp, Delete, Calendar } from 'lucide-react';

export const ProductivityCalculator: React.FC = () => {
  const [dailyHours, setDailyHours] = useState(5);

  // Formulas derived from ergonomic typing studies:
  // Average knowledge worker makes 1 bilingual mistake per 8 minutes (7.5 mistakes/hr)
  // Each mistake takes ~6.5 seconds to realize, backspace, toggle language, re-type
  // Annual working days: 240 days
  const mistakesPerDay = Math.round(dailyHours * 7.5);
  const secondsSavedPerDay = mistakesPerDay * 6.5;
  const hoursSavedPerYear = Math.round((secondsSavedPerDay * 240) / 3600);
  const keystrokesSavedPerYear = Math.round(mistakesPerDay * 14 * 240);
  const workDaysGained = (hoursSavedPerYear / 8).toFixed(1);

  return (
    <section id="calculator" className="py-16 sm:py-24 bg-slate-50/50 border-y border-slate-200/60 relative">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-200/80 text-brand-700 text-xs font-semibold uppercase tracking-wider mb-4">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Productivity & ROI Calculator</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Plik ประหยัดเวลาให้คุณได้มากแค่ไหน?
          </h2>
          <p className="mt-3 text-slate-600 text-sm sm:text-base">
            การกด Backspace ซ้ำๆ เพื่อลบคำผิดเพราะลืมเปลี่ยนภาษา สะสมเป็นชั่วโมงทำงานมหาศาลในแต่ละปี
          </p>
        </div>

        {/* Calculator Card */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 p-6 sm:p-10 max-w-4xl mx-auto">
          {/* Slider Controls */}
          <div className="mb-10">
            <div className="flex items-center justify-between mb-4">
              <label className="text-sm sm:text-base font-bold text-slate-800 flex items-center gap-2">
                <Clock className="w-4 h-4 text-brand-600" />
                <span>คุณพิมพ์คีย์บอร์ดเฉลี่ยวันละกี่ชั่วโมง?</span>
              </label>
              <span className="text-2xl sm:text-3xl font-extrabold text-brand-600 font-mono">
                {dailyHours} <span className="text-sm font-sans font-medium text-slate-500">ชม./วัน</span>
              </span>
            </div>

            <input
              type="range"
              min="1"
              max="12"
              step="1"
              value={dailyHours}
              onChange={(e) => setDailyHours(parseInt(e.target.value))}
              className="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600 focus:outline-none"
            />
            <div className="flex justify-between text-[11px] font-semibold text-slate-400 mt-2 font-mono">
              <span>1 ชม. (พิมพ์ประปราย)</span>
              <span>6 ชม. (โปรแกรมเมอร์/พนักงานออฟฟิศ)</span>
              <span>12 ชม. (Hardcore Typist)</span>
            </div>
          </div>

          {/* Results Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-6 border-t border-slate-100">
            {/* Metric 1 */}
            <motion.div 
              key={hoursSavedPerYear}
              initial={{ scale: 0.95, opacity: 0.8 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-6 rounded-2xl bg-gradient-to-b from-brand-50/50 to-transparent border border-brand-200/70 flex flex-col items-center text-center"
            >
              <div className="w-10 h-10 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center mb-3">
                <Clock className="w-5 h-5" />
              </div>
              <span className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-mono">
                ~{hoursSavedPerYear}
              </span>
              <span className="text-xs font-bold text-brand-700 uppercase tracking-wider mt-1">
                ชั่วโมงที่ประหยัดได้ / ปี
              </span>
              <p className="text-[11px] text-slate-500 mt-2">
                เวลาที่ไม่ต้องเสียไปกับการลบแล้วพิมพ์คำเดิมซ้ำ
              </p>
            </motion.div>

            {/* Metric 2 */}
            <motion.div 
              key={keystrokesSavedPerYear}
              initial={{ scale: 0.95, opacity: 0.8 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-6 rounded-2xl bg-gradient-to-b from-slate-50 to-transparent border border-slate-200 flex flex-col items-center text-center"
            >
              <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center mb-3">
                <Delete className="w-5 h-5" />
              </div>
              <span className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-mono">
                {keystrokesSavedPerYear.toLocaleString()}
              </span>
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider mt-1">
                ครั้งการกด Backspace ที่ลดลง
              </span>
              <p className="text-[11px] text-slate-500 mt-2">
                ถนอมสวิตช์คีย์บอร์ดและลดความล้าของข้อมือ
              </p>
            </motion.div>

            {/* Metric 3 */}
            <motion.div 
              key={workDaysGained}
              initial={{ scale: 0.95, opacity: 0.8 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-6 rounded-2xl bg-gradient-to-b from-emerald-50/50 to-transparent border border-emerald-200/70 flex flex-col items-center text-center"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center mb-3">
                <Calendar className="w-5 h-5" />
              </div>
              <span className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-mono">
                +{workDaysGained}
              </span>
              <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider mt-1">
                วันทำงานที่ได้คืนมา
              </span>
              <p className="text-[11px] text-slate-500 mt-2">
                เทียบเท่าได้วันหยุดพักผ่อนเพิ่มฟรีๆ ต่อปี
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
};
