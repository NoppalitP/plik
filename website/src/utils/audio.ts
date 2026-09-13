// Web Audio API Mechanical Keyboard Synthesizer
// Generates realistic tactile "thock" and "click" sounds natively without external MP3 files

class MechanicalSoundSynthesizer {
  private ctx: AudioContext | null = null;
  private enabled: boolean = true;

  constructor() {
    // AudioContext will be lazily initialized on first user gesture
  }

  private getContext(): AudioContext | null {
    if (typeof window === 'undefined') return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  public setEnabled(val: boolean) {
    this.enabled = val;
  }

  public isEnabled(): boolean {
    return this.enabled;
  }

  // Play mechanical key press (sharp transient + hollow body resonance)
  public playKeypress(isSpace: boolean = false) {
    if (!this.enabled) return;
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;

    // 1. High frequency transient click (noise buffer)
    const bufferSize = ctx.sampleRate * 0.005; // 5ms burst
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = ctx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;

    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(isSpace ? 1800 : 2600 + Math.random() * 400, now);
    filter.Q.setValueAtTime(3.5, now);

    const clickGain = ctx.createGain();
    clickGain.gain.setValueAtTime(0.2, now);
    clickGain.gain.exponentialRampToValueAtTime(0.001, now + 0.006);

    whiteNoise.connect(filter);
    filter.connect(clickGain);
    clickGain.connect(ctx.destination);
    whiteNoise.start(now);

    // 2. Low-mid resonance thock (sine oscillator decay)
    const osc = ctx.createOscillator();
    const oscGain = ctx.createGain();

    const baseFreq = isSpace ? 140 : 220 + Math.random() * 30;
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(baseFreq, now);
    osc.frequency.exponentialRampToValueAtTime(60, now + 0.04);

    oscGain.gain.setValueAtTime(isSpace ? 0.35 : 0.25, now);
    oscGain.gain.exponentialRampToValueAtTime(0.001, now + (isSpace ? 0.06 : 0.045));

    osc.connect(oscGain);
    oscGain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.06);
  }

  // Play celebratory flip sound (smooth rising harmonic chime)
  public playFlip() {
    if (!this.enabled) return;
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(440, now);
    osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);

    gain.gain.setValueAtTime(0.18, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.25);
  }
}

export const soundFx = new MechanicalSoundSynthesizer();
