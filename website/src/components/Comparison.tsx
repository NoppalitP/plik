import React from 'react';
import { Check, X } from 'lucide-react';

export const Comparison: React.FC = () => {
  const features = [
    { name: 'สลับภาษาคำผิดให้อัตโนมัติทันทีที่เคาะ Space', plik: true, others: 'ช้า/ต้องกดคีย์ลัด', defaultWin: false },
    { name: 'Code Guard ป้องกันคำสั่ง Git, CLI, Code File', plik: true, others: false, defaultWin: false },
    { name: 'แก้ไขคำผิดภาษาไทยในตัว (เช่น นะค่ะ -> นะคะ)', plik: true, others: false, defaultWin: false },
    { name: 'ทำงานออฟไลน์ 100% ไม่ส่งข้อมูลออกนอกเครื่อง', plik: true, others: 'บางตัวต่อ Cloud', defaultWin: true },
    { name: 'กินแรมน้อย ไม่ทำให้เครื่องหน่วง (< 15 MB)', plik: true, others: false, defaultWin: true },
    { name: 'Single-Instance Win32 Mutex ป้องกันเปิดโปรแกรมซ้ำ', plik: true, others: false, defaultWin: false },
    { name: 'คีย์ลัด Pause / Resume ชั่วคราวได้ทันที', plik: true, others: true, defaultWin: false },
    { name: 'Open Source ตรวจสอบซอร์สโค้ดได้ 100%', plik: true, others: false, defaultWin: false },
  ];

  return (
    <section id="comparison" className="py-20 sm:py-28 bg-slate-50/50 border-t border-slate-200/60">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            ทำไมต้อง Plik?
          </h2>
          <p className="mt-3 text-slate-600 text-sm sm:text-base">
            เปรียบเทียบฟีเจอร์ของ Plik กับโปรแกรมสลับภาษาแบบเดิมๆ และ Windows ปกติ
          </p>
        </div>

        {/* Table Container */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/60">
                  <th className="py-5 px-6 text-sm font-bold text-slate-700 w-1/2">
                    ฟังก์ชันการทำงาน
                  </th>
                  <th className="py-5 px-4 text-center text-sm font-extrabold text-brand-700 bg-brand-50/50 border-x border-brand-200/60">
                    <div className="flex items-center justify-center gap-1.5">
                      <span>Plik (พลิก)</span>
                      <span className="text-[10px] bg-brand-600 text-white px-1.5 py-0.5 rounded-full font-sans">
                        แนะนำ
                      </span>
                    </div>
                  </th>
                  <th className="py-5 px-4 text-center text-sm font-semibold text-slate-500">
                    โปรแกรมทั่วไป / RightLang
                  </th>
                  <th className="py-5 px-4 text-center text-sm font-semibold text-slate-500">
                    Windows ทั่วไป
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs sm:text-sm">
                {features.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-4 px-6 font-medium text-slate-800">
                      {item.name}
                    </td>

                    {/* Plik */}
                    <td className="py-4 px-4 text-center bg-brand-50/20 border-x border-brand-200/40">
                      {item.plik === true ? (
                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-brand-100 text-brand-700">
                          <Check className="w-4 h-4" />
                        </div>
                      ) : (
                        <span className="font-semibold text-brand-700">{item.plik}</span>
                      )}
                    </td>

                    {/* Traditional */}
                    <td className="py-4 px-4 text-center text-slate-500">
                      {item.others === true ? (
                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-600">
                          <Check className="w-4 h-4" />
                        </div>
                      ) : item.others === false ? (
                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-rose-50 text-rose-500">
                          <X className="w-4 h-4" />
                        </div>
                      ) : (
                        <span className="text-xs text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
                          {item.others}
                        </span>
                      )}
                    </td>

                    {/* Windows Default */}
                    <td className="py-4 px-4 text-center text-slate-400">
                      {item.defaultWin === true ? (
                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-600">
                          <Check className="w-4 h-4" />
                        </div>
                      ) : (
                        <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-rose-50 text-rose-500">
                          <X className="w-4 h-4" />
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
};
