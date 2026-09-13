import React, { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { Volume2, VolumeX, Sparkles, RefreshCw, Terminal, Keyboard, ShieldCheck, Play, Pause } from 'lucide-react';
import confetti from 'canvas-confetti';
import { soundFx } from '../utils/audio';
import { plikCorrect } from '../utils/kedmanee';

interface DemoStep {
  typed: string;
  expected: string;
  desc: string;
  type: 'thai_flip' | 'typo_fix' | 'code_guard';
}

const DEMO_STEPS: DemoStep[] = [
  { typed: 'cotoe.sh', expected: 'แนะนำให้', desc: 'เผลอพิมพ์ภาษาอังกฤษบนแป้นเกษมณี', type: 'thai_flip' },
  { typed: ';yo', expected: 'สวัสดี', desc: 'ทักทายยอดนิยมที่ลืมเปลี่ยนภาษา', type: 'thai_flip' },
  { typed: 'dkifu[bf;y;', expected: 'การทำงาน', desc: 'พิมพ์ยาวต่อเนื่องโดยไม่รู้ตัว', type: 'thai_flip' },
  { typed: 'นะค่ะ', expected: 'นะคะ', desc: 'แก้ไขคำผิดภาษาไทยอัตโนมัติ', type: 'typo_fix' },
  { typed: 'git push origin main', expected: 'git push origin main', desc: 'Code Guard ป้องกันคำสั่งโค้ดและ Git', type: 'code_guard' },
];

export const Hero3DFlipDemo: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'auto' | 'interactive'>('auto');
  const [stepIndex, setStepIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState('');
  const [isFlipping, setIsFlipping] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);
  const [autoPlaying, setAutoPlaying] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [activeKey, setActiveKey] = useState<string | null>(null);

  // Interactive state
  const [userQuery, setUserQuery] = useState('');
  const [userResult, setUserResult] = useState<{ converted: string; flipped: boolean; reason: string } | null>(null);

  // 3D Tilt Motion Values
  const cardRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { damping: 25, stiffness: 200 };
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [8, -8]), springConfig);
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-8, 8]), springConfig);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const x = (e.clientX - rect.left) / width - 0.5;
    const y = (e.clientY - rect.top) / height - 0.5;
    mouseX.set(x);
    mouseY.set(y);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  const toggleSound = () => {
    const next = !soundEnabled;
    setSoundEnabled(next);
    soundFx.setEnabled(next);
    if (next) soundFx.playKeypress();
  };

  // Auto-playing typing sequence effect
  useEffect(() => {
    if (activeTab !== 'auto' || !autoPlaying) return;

    let timeoutId: ReturnType<typeof setTimeout>;
    const currentDemo = DEMO_STEPS[stepIndex];
    const fullText = currentDemo.typed;

    let charIdx = 0;
    setDisplayedText('');
    setIsFlipped(false);
    setIsFlipping(false);

    const typeNextChar = () => {
      if (charIdx < fullText.length) {
        const nextChar = fullText[charIdx];
        setDisplayedText(fullText.slice(0, charIdx + 1));
        setActiveKey(nextChar);
        if (soundEnabled) soundFx.playKeypress(nextChar === ' ');
        charIdx++;
        timeoutId = setTimeout(typeNextChar, 110 + Math.random() * 40);
      } else {
        // Finished typing word, simulate spacebar press & flip!
        setActiveKey('Space');
        if (soundEnabled) soundFx.playKeypress(true);

        timeoutId = setTimeout(() => {
          setActiveKey(null);
          if (currentDemo.type !== 'code_guard') {
            setIsFlipping(true);
            if (soundEnabled) soundFx.playFlip();

            // Mid-flip change text
            setTimeout(() => {
              setIsFlipped(true);
              setDisplayedText(currentDemo.expected);
            }, 250);

            setTimeout(() => {
              setIsFlipping(false);
            }, 600);
          } else {
            // Code Guard protected - no flip
            setIsFlipped(false);
          }

          // Wait on result before moving to next step
          timeoutId = setTimeout(() => {
            setStepIndex((prev) => (prev + 1) % DEMO_STEPS.length);
          }, 2400);
        }, 350);
      }
    };

    timeoutId = setTimeout(typeNextChar, 500);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [stepIndex, activeTab, autoPlaying, soundEnabled]);

  // Handle interactive live input
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setUserQuery(val);
    if (val.endsWith(' ') || val.length > 0) {
      if (soundEnabled) soundFx.playKeypress(val.endsWith(' '));
    }
    const res = plikCorrect(val);
    setUserResult(res);
  };

  const handleApplyPreset = (preset: string) => {
    setUserQuery(preset);
    if (soundEnabled) soundFx.playKeypress();
    const res = plikCorrect(preset);
    setUserResult(res);
    if (res.flipped) {
      if (soundEnabled) soundFx.playFlip();
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.7 },
        colors: ['#10b981', '#059669', '#34d399', '#6ee7b7']
      });
    }
  };

  const currentStepData = DEMO_STEPS[stepIndex];

  return (
    <section id="demo" className="py-12 sm:py-20 relative">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Controls Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          {/* Tab Switcher */}
          <div className="inline-flex p-1 bg-slate-100/90 rounded-xl border border-slate-200/80">
            <button
              onClick={() => setActiveTab('auto')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'auto'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${activeTab === 'auto' && autoPlaying ? 'animate-spin-slow text-brand-600' : ''}`} />
              <span>Cinematic 3D Demo</span>
            </button>
            <button
              onClick={() => setActiveTab('interactive')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'interactive'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              <Keyboard className="w-3.5 h-3.5 text-brand-600" />
              <span>Interactive Playground</span>
            </button>
          </div>

          {/* Sound & Play/Pause Controls */}
          <div className="flex items-center gap-2">
            {activeTab === 'auto' && (
              <button
                onClick={() => setAutoPlaying(!autoPlaying)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 hover:border-slate-300 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors shadow-sm"
                title={autoPlaying ? "หยุดชั่วคราว" : "เล่นต่อ"}
              >
                {autoPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-brand-600" />}
                <span className="hidden sm:inline">{autoPlaying ? "Pause" : "Play"}</span>
              </button>
            )}

            <button
              onClick={toggleSound}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors shadow-sm ${
                soundEnabled 
                  ? 'bg-brand-50 border-brand-200 text-brand-700' 
                  : 'bg-white border-slate-200 text-slate-400 hover:text-slate-700'
              }`}
              title="สลับเสียงพิมพ์ Mechanical Keyboard"
            >
              {soundEnabled ? <Volume2 className="w-3.5 h-3.5 text-brand-600" /> : <VolumeX className="w-3.5 h-3.5" />}
              <span className="hidden sm:inline">{soundEnabled ? "Mechanical Sound: On" : "Sound: Off"}</span>
            </button>
          </div>
        </div>

        {/* 3D PERSPECTIVE CARD CONTAINER */}
        <div 
          className="perspective-1000 w-full"
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          <motion.div
            ref={cardRef}
            style={{ rotateX, rotateY }}
            className="relative w-full rounded-3xl bg-white border border-slate-200/90 shadow-2xl shadow-slate-200/60 overflow-hidden transform-style-3d p-6 sm:p-10"
          >
            {/* Ambient Corner Badge */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-5 mb-8">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-400" />
                  <div className="w-3 h-3 rounded-full bg-amber-400" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400" />
                </div>
                <span className="text-xs font-mono text-slate-400 ml-2 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Plik Core Pipeline • WH_KEYBOARD_LL</span>
                </span>
              </div>

              {activeTab === 'auto' ? (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 hidden sm:inline">{currentStepData.desc}</span>
                  <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                    currentStepData.type === 'thai_flip' 
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                      : currentStepData.type === 'typo_fix'
                      ? 'bg-purple-50 text-purple-700 border border-purple-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}>
                    {currentStepData.type === 'thai_flip' ? 'Kedmanee Flip' : currentStepData.type === 'typo_fix' ? 'Typo Correction' : 'Code Guard'}
                  </span>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 text-xs text-brand-700 font-semibold bg-brand-50 px-2.5 py-1 rounded-full border border-brand-200">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Live Conversion Mode</span>
                </div>
              )}
            </div>

            {/* MAIN DEMO AREA */}
            {activeTab === 'auto' ? (
              <div className="flex flex-col items-center justify-center py-8 sm:py-14">
                {/* 3D FLIPPING DISPLAY BOX */}
                <div className="perspective-1000 w-full max-w-xl">
                  <motion.div
                    animate={{
                      rotateX: isFlipping ? 360 : 0,
                      scale: isFlipping ? 1.05 : 1,
                    }}
                    transition={{
                      duration: 0.6,
                      ease: [0.34, 1.56, 0.64, 1], // Spring overshoot curve
                    }}
                    className={`w-full py-8 sm:py-12 px-6 rounded-2xl text-center flex flex-col items-center justify-center transition-all duration-300 border-2 ${
                      isFlipped 
                        ? 'bg-gradient-to-b from-brand-50/70 to-white border-brand-400 shadow-glow-md' 
                        : currentStepData.type === 'code_guard'
                        ? 'bg-gradient-to-b from-blue-50/50 to-white border-blue-300 shadow-sm'
                        : 'bg-slate-50/80 border-slate-200 shadow-sm'
                    }`}
                  >
                    <div className="text-xs font-mono font-medium text-slate-400 mb-2 uppercase tracking-widest flex items-center gap-2">
                      {isFlipped ? (
                        <>
                          <Sparkles className="w-4 h-4 text-brand-600" />
                          <span className="text-brand-700 font-bold">ผลลัพธ์ที่ Plik พลิกให้อัตโนมัติ:</span>
                        </>
                      ) : currentStepData.type === 'code_guard' ? (
                        <>
                          <ShieldCheck className="w-4 h-4 text-blue-600" />
                          <span className="text-blue-700 font-bold">Code Guard คุ้มครองคำสั่งโค้ด:</span>
                        </>
                      ) : (
                        <span>กำลังตรวจจับสิ่งที่คุณพิมพ์...</span>
                      )}
                    </div>

                    <div className="min-h-[70px] flex items-center justify-center">
                      <span className={`text-3xl sm:text-5xl font-extrabold tracking-tight transition-colors ${
                        isFlipped 
                          ? 'text-brand-700 font-sans' 
                          : currentStepData.type === 'code_guard'
                          ? 'text-blue-700 font-mono'
                          : 'text-slate-800 font-mono'
                      }`}>
                        {displayedText}
                        {!isFlipping && (
                          <span className="inline-block w-1 h-8 sm:h-10 ml-1.5 bg-brand-500 animate-pulse-subtle align-middle rounded-full" />
                        )}
                      </span>
                    </div>

                    {/* Status pill under display */}
                    <div className="mt-4">
                      {isFlipped ? (
                        <motion.div 
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-brand-100 text-brand-800 border border-brand-300/80"
                        >
                          <span>✓ สลับภาษาและแปลงข้อความใน 0.4ms</span>
                        </motion.div>
                      ) : currentStepData.type === 'code_guard' ? (
                        <div className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                          <span>✓ ละเว้นอัตโนมัติ ไม่แปลงโค้ดเสียหาย</span>
                        </div>
                      ) : (
                        <div className="text-xs text-slate-400 font-mono">
                          กด Spacebar เพื่อพลิกคำ ➔
                        </div>
                      )}
                    </div>
                  </motion.div>
                </div>

                {/* VISUAL KEYCAPS & TIMELINE */}
                <div className="mt-10 flex items-center gap-3">
                  <div className={`keycap px-4 py-2 bg-white rounded-xl border border-slate-200 font-mono text-xs font-bold text-slate-700 flex items-center gap-2 ${
                    activeKey ? 'keycap-pressed bg-brand-50 border-brand-300 text-brand-700' : ''
                  }`}>
                    <span>คีย์ล่าสุด:</span>
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-900 border border-slate-300">
                      {activeKey || 'Ready'}
                    </span>
                  </div>

                  {/* Step Selector Dots */}
                  <div className="flex items-center gap-1.5 ml-4">
                    {DEMO_STEPS.map((step, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setStepIndex(idx);
                          if (soundEnabled) soundFx.playKeypress();
                        }}
                        className={`h-2.5 rounded-full transition-all duration-300 ${
                          idx === stepIndex 
                            ? 'w-7 bg-brand-600' 
                            : 'w-2.5 bg-slate-200 hover:bg-slate-300'
                        }`}
                        title={step.typed}
                      />
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              /* INTERACTIVE LIVE PLAYGROUND */
              <div className="py-6 sm:py-10 max-w-2xl mx-auto">
                <div className="text-center mb-6">
                  <h3 className="text-lg font-bold text-slate-900">ทดลองพิมพ์ด้วยตัวคุณเอง</h3>
                  <p className="text-xs sm:text-sm text-slate-500 mt-1">
                    ลองพิมพ์คำอังกฤษที่ลืมเปลี่ยนภาษา หรือพิมพ์คำผิดภาษาไทย แล้วดูการพลิกคำแบบ Real-time
                  </p>
                </div>

                {/* Input box */}
                <div className="relative">
                  <input
                    type="text"
                    value={userQuery}
                    onChange={handleInputChange}
                    placeholder="เช่น ลองพิมพ์ 'cotoe.sh' หรือ ';yo' หรือ 'นะค่ะ'..."
                    className="w-full px-5 py-4 text-lg font-mono rounded-2xl bg-slate-50 border-2 border-slate-200 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-100 transition-all text-slate-900 placeholder:text-slate-400 placeholder:font-sans shadow-inner"
                  />
                  {userQuery && (
                    <button
                      onClick={() => setUserQuery('')}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-semibold px-2.5 py-1 bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-lg transition-colors"
                    >
                      ล้าง
                    </button>
                  )}
                </div>

                {/* Live conversion card */}
                {userQuery && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mt-4 p-5 rounded-2xl border ${
                      userResult?.flipped 
                        ? 'bg-brand-50/60 border-brand-300 text-brand-900' 
                        : userResult?.reason === 'code_guard'
                        ? 'bg-blue-50/60 border-blue-200 text-blue-900'
                        : 'bg-slate-50 border-slate-200 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-medium text-slate-500 mb-1">
                      <span>สถานะการประมวลผล:</span>
                      <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-white border border-slate-200">
                        {userResult?.reason}
                      </span>
                    </div>

                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-3">
                        <span className="text-xl font-bold font-sans">
                          {userResult?.converted}
                        </span>
                        {userResult?.flipped && (
                          <span className="text-xs px-2.5 py-0.5 rounded-full bg-brand-600 text-white font-semibold">
                            Flipped!
                          </span>
                        )}
                      </div>

                      {userResult?.flipped && (
                        <button
                          onClick={() => {
                            if (soundEnabled) soundFx.playFlip();
                            confetti({
                              particleCount: 50,
                              spread: 70,
                              origin: { y: 0.6 }
                            });
                          }}
                          className="text-xs font-semibold text-brand-700 hover:text-brand-800 underline"
                        >
                          ยินดีด้วย! พลิกสำเร็จ 🎉
                        </button>
                      )}
                    </div>
                  </motion.div>
                )}

                {/* Preset Chips */}
                <div className="mt-8">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    กดลองคำทดสอบยอดนิยม:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { key: 'cotoe.sh', label: 'cotoe.sh ➔ แนะนำให้' },
                      { key: ';yo', label: ';yo ➔ สวัสดี' },
                      { key: 'dkifu[bf;y;', label: 'dkifu[bf;y; ➔ การทำงาน' },
                      { key: 'นะค่ะ', label: 'นะค่ะ ➔ นะคะ' },
                      { key: 'teh', label: 'teh ➔ the' },
                      { key: 'deploy.sh', label: 'deploy.sh (Code Guard)' },
                    ].map((preset) => (
                      <button
                        key={preset.key}
                        onClick={() => handleApplyPreset(preset.key)}
                        className="px-3.5 py-1.5 text-xs font-medium bg-white hover:bg-slate-50 border border-slate-200 hover:border-brand-300 rounded-xl text-slate-700 hover:text-brand-700 shadow-sm transition-all active:scale-95"
                      >
                        {preset.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
};
