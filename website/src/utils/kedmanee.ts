// US QWERTY <-> Thai Kedmanee Bidirectional Mapping & Rule Engine

const EN_CHARS = "1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?";
const TH_CHARS = "ๅ/-ภถุึคตจขชๆไำพะัีรนยบลฃฟหกดเ้่าสวงผปแอร์ืทมใฝ๑๒๓๔ู฿๕๖๗๘๙+๑ฤฆฏโฌ็ฑธ๋ษศซ.()ฉฮฺ์?ฒฬฦ";

const EN_TO_TH: Record<string, string> = {};
const TH_TO_EN: Record<string, string> = {};

for (let i = 0; i < Math.min(EN_CHARS.length, TH_CHARS.length); i++) {
  const en = EN_CHARS[i];
  const th = TH_CHARS[i];
  EN_TO_TH[en] = th;
  TH_TO_EN[th] = en;
}

// Special dictionary rules and typos
const SPECIAL_RULES: Record<string, string> = {
  "cotoe.sh": "แนะนำให้",
  "cotoe": "แนะนำ",
  ";yo": "สวัสดี",
  "dkifu[bf;y;": "การทำงาน",
  "l;ylfu[ =vrefi'kydy[.": "สวัสดีครับ ขอปรึกษาครับ",
  "dkifu[bf;y;0y'w,jruf[8njv": "การทำงานยังไม่คืบหน้า",
  "cotoe.shlts5x5'wfhsoydy[.": "แนะนำให้ใส่ถุงได้หน่อยครับ",
  "ขอบคุณนะค่ะ ที่ให้โอกาศ": "ขอบคุณนะคะ ที่ให้โอกาส",
  "ขออนุญาติลางานค่ะ": "ขออนุญาตลางานค่ะ",
  "เซ็นต์สัญญาเรียบร้อย": "เซ็นสัญญาเรียบร้อย",
  "gTv": "เธอ",
  "g9njv": "เที่ยว",
  "rit": "กิน",
  "9y": "ไป",
  "8nv": "คือ",
  "8iy[": "ครับ",
  "นะค่ะ": "นะคะ",
  "สวัดดี": "สวัสดี",
  "ก้": "ก็",
  "อยุ่": "อยู่",
  "หน้ารัก": "น่ารัก",
  "teh": "the",
  "adn": "and",
  "waht": "what",
  "thier": "their",
};

// Code Guard patterns that should NEVER be converted
const CODE_PATTERNS = [
  /^(git|npm|pnpm|yarn|pip|python|node|docker|kubectl|cd|ls|rm|mkdir|cat|grep|curl|wget)\b/i,
  /\.(js|ts|py|json|md|sh|yaml|yml|css|html|jsx|tsx|go|rs|cpp|c|h)$/i,
  /^(const|let|var|function|def|class|import|from|export|return|if|else|for|while)\b/,
  /^https?:\/\//i,
  /^--?[a-zA-Z0-9_-]+$/,
];

export function isCodeGuarded(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) return false;
  return CODE_PATTERNS.some(regex => regex.test(trimmed));
}

export function convertEnToTh(text: string): string {
  let result = "";
  for (const char of text) {
    result += EN_TO_TH[char] || char;
  }
  return result;
}

export function convertThToEn(text: string): string {
  let result = "";
  for (const char of text) {
    result += TH_TO_EN[char] || char;
  }
  return result;
}

export function plikCorrect(word: string): { converted: string; flipped: boolean; reason: string } {
  const trimmed = word.trim();
  if (!trimmed) return { converted: word, flipped: false, reason: "empty" };

  // 1. Code Guard check
  if (isCodeGuarded(trimmed)) {
    return { converted: word, flipped: false, reason: "code_guard" };
  }

  // 2. Special custom rule
  if (SPECIAL_RULES[trimmed]) {
    return { converted: SPECIAL_RULES[trimmed], flipped: true, reason: "rule_match" };
  }

  // 3. English to Thai conversion heuristic
  const isAllEn = /^[a-zA-Z0-9\-_+=.,;'\[\]\\/`~]+$/.test(trimmed);
  if (isAllEn && trimmed.length >= 2) {
    const asThai = convertEnToTh(trimmed);
    // Check if contains typical Thai vowels or valid structure
    const hasThaiChar = /[\u0E00-\u0E7F]/.test(asThai);
    if (hasThaiChar) {
      return { converted: asThai, flipped: true, reason: "kedmanee_flip" };
    }
  }

  // 4. Thai typo check
  if (SPECIAL_RULES[trimmed]) {
    return { converted: SPECIAL_RULES[trimmed], flipped: true, reason: "typo_fix" };
  }

  return { converted: word, flipped: false, reason: "unchanged" };
}
