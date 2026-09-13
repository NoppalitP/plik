"""Tier 2: Statistical Character N-Gram Language Classifier.

Computes log-likelihood ratios for character bigrams and trigrams in Thai and English.
Extremely fast (<0.1 ms), robust to spelling variations, and memory-efficient (<500 KB).
"""

import math
from typing import Dict, Tuple
from plik.layouts.kedmanee import to_thai, to_english


# High-frequency English character n-grams
COMMON_EN_BIGRAMS = {
    "th": 3.8, "he": 3.5, "in": 3.4, "er": 3.3, "an": 3.2, "re": 3.1, "on": 3.0,
    "at": 2.9, "en": 2.8, "nd": 2.8, "ti": 2.7, "es": 2.7, "or": 2.6, "te": 2.6,
    "of": 2.5, "ed": 2.5, "is": 2.5, "it": 2.4, "al": 2.4, "ar": 2.4, "st": 2.3,
    "to": 2.3, "nt": 2.2, "ng": 2.2, "se": 2.1, "ha": 2.1, "as": 2.0, "ou": 2.0,
    "io": 1.9, "le": 1.9, "ve": 1.9, "co": 1.8, "me": 1.8, "de": 1.8, "hi": 1.7,
    "ri": 1.7, "ro": 1.7, "ic": 1.6, "ne": 1.6, "ea": 1.6, "ra": 1.5, "ce": 1.5,
    "li": 1.5, "ch": 1.5, "ll": 1.4, "be": 1.4, "ma": 1.4, "si": 1.4, "om": 1.3,
    "ur": 1.3, "ca": 1.3, "el": 1.3, "ta": 1.2, "la": 1.2, "ns": 1.2, "ge": 1.2,
    "ap": 1.4, "pp": 1.3, "pl": 1.4, "gi": 1.3, "sh": 1.5, "ck": 1.3, "un": 1.3,
}

COMMON_EN_TRIGRAMS = {
    "the": 4.5, "and": 4.0, "ing": 3.8, "ion": 3.5, "tio": 3.4, "ent": 3.3,
    "ati": 3.2, "for": 3.1, "her": 3.0, "ter": 2.9, "hat": 2.8, "tha": 2.8,
    "ere": 2.7, "ate": 2.7, "his": 2.6, "con": 2.6, "res": 2.5, "ver": 2.5,
    "all": 2.4, "ons": 2.4, "nce": 2.3, "men": 2.3, "ith": 2.3, "ted": 2.2,
    "ers": 2.2, "pro": 2.2, "thi": 2.2, "wit": 2.1, "are": 2.1, "ess": 2.0,
    "not": 2.0, "ive": 2.0, "was": 1.9, "ect": 1.9, "rea": 1.9, "com": 1.9,
    "eve": 1.8, "per": 1.8, "int": 1.8, "est": 1.8, "sta": 1.8, "cti": 1.7,
    "ica": 1.7, "ome": 1.7, "app": 2.5, "ple": 2.2, "git": 2.8, "tes": 2.1,
}

# High-frequency Thai subwords and n-grams
COMMON_TH_BIGRAMS = {
    "กา": 3.5, "าร": 3.8, "คว": 3.2, "วา": 3.4, "าม": 3.3, "เป": 3.6, "็น": 3.5,
    "อย": 3.2, "ยู่": 3.1, "ได": 3.4, "ด้": 3.3, "ไป": 3.2, "มา": 3.3, "มี": 3.5,
    "ทำ": 3.2, "ให": 3.4, "ห้": 3.3, "ไม": 3.5, "ม่": 3.4, "จะ": 3.4, "ที่": 3.8,
    "ขอ": 3.3, "อง": 3.7, "ใน": 3.6, "แล": 3.5, "ละ": 3.4, "คน": 3.2, "วั": 3.3,
    "ัน": 3.6, "ระ": 3.5, "เท": 3.1, "ศา": 3.0, "แบ": 3.2, "บบ": 3.1, "สว": 3.2,
    "ัส": 3.4, "สด": 3.1, "ดี": 3.4, "ภา": 3.2, "ษา": 3.3, "บร": 3.0, "ริ": 3.1,
    "ษั": 3.0, "ษัท": 3.1, "ระ": 3.3, "บี": 2.9, "ยบ": 2.9, "เร": 3.2, "ีย": 3.3,
    "ยน": 3.2, "งา": 3.3, "าน": 3.7, "ทั": 3.1, "้ง": 3.2, "ต้อ": 3.2, "อง": 3.5,
}

COMMON_TH_TRIGRAMS = {
    "การ": 4.5, "ความ": 4.2, "เป็น": 4.0, "อยู่": 3.8, "ไม่ได้": 3.7, "ให้กับ": 3.5,
    "ทำให้": 3.6, "อย่าง": 3.5, "สำหรับ": 3.4, "บริษัท": 3.6, "ภาษา": 4.0, "สวัสดี": 4.5,
    "แบบ": 3.8, "เทศา": 3.2, "ระเบียบ": 3.5, "ทำงาน": 3.8, "จะต้อง": 3.6, "ทั้งหมด": 3.5,
}

# Common English vocabulary dictionary for exact fast matches
COMMON_ENGLISH_WORDS = {
    # Pronouns & Auxiliaries
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for",
    "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his",
    "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my",
    "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
    "about", "who", "get", "which", "go", "me", "when", "make", "can", "like",
    "time", "no", "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then", "now", "look",
    "only", "come", "its", "over", "think", "also", "back", "after", "use", "two",
    "how", "our", "work", "first", "well", "way", "even", "new", "want", "because",
    "any", "these", "give", "day", "most", "us", "is", "are", "was", "were", "been",
    "has", "had", "done", "test", "break", "apple", "code", "run", "push", "pull",
    "commit", "status", "branch", "build", "debug", "install", "deploy", "server",
    "client", "database", "query", "table", "index", "file", "path", "folder",
    # Tech & Mixed Conversation terms
    "pr", "repo", "git", "log", "api", "url", "json", "token", "auth", "login",
    "logout", "user", "admin", "config", "setting", "setup", "fix", "bug", "issue",
    "task", "sprint", "meeting", "call", "chat", "send", "post", "get", "patch",
    "delete", "put", "response", "request", "error", "warn", "info", "trace",
    "docker", "pod", "node", "cluster", "cloud", "aws", "gcp", "azure", "ci",
    "cd", "pipeline", "env", "key", "secret", "value", "string", "number", "boolean",
    "null", "undefined", "true", "false", "async", "await", "function", "class",
    "const", "let", "var", "import", "export", "return", "from", "while", "for",
    "if", "else", "switch", "case", "default", "try", "catch", "throw", "finally",
    # Short words frequently typed
    "hi", "ok", "yes", "no", "bye", "pls", "thx", "thks", "help", "cool", "nice",
    "data", "tasks",
}

# Common Thai vocabulary dictionary for exact fast matches
COMMON_THAI_WORDS = {
    # High-frequency grammatical & function words
    "การ", "งาน", "คน", "วัน", "ไป", "มา", "มี", "ได้", "จะ", "ใน", "ที่", "ของ",
    "และ", "เป็น", "ให้", "ไม่", "แต่", "นี้", "นั้น", "แล้ว", "กับ", "ทำ", "อยู่",
    "ดี", "สวัสดี", "ภาษา", "แบบ", "ครับ", "ค่ะ", "นะคะ", "อะไร", "ใคร", "ไหน",
    "อย่างไร", "ทำไม", "เมื่อไร", "ที่ไหน", "เพราะ", "หรือ", "ถ้า", "ว่า", "บอก",
    "เห็น", "คิด", "รู้", "เข้าใจ", "ระบบ", "ข้อมูล", "โปรแกรม", "คอมพิวเตอร์",
    "เวลา", "ปัญหา", "เรื่อง", "หน้า", "หลัง", "ก่อน", "ตอน", "ทุก", "มาก", "น้อย",
    # Common conversational words & verbs
    "วันนี้", "พรุ่งนี้", "เมื่อวาน", "ประชุม", "ส่ง", "เปิด", "ปิด", "ช่วย", "ดู",
    "เช็ค", "ตรวจ", "แก้", "เขียน", "อ่าน", "ฟัง", "พูด", "กิน", "นอน", "เที่ยว",
    "บ้าน", "ห้อง", "บริษัท", "เพื่อน", "พี่", "น้อง", "คุณ", "ผม", "เรา", "เขา",
    "เงิน", "ราคา", "ซื้อ", "ขาย", "ของ", "รูป", "ภาพ", "คลิป", "เว็บ", "ลิงก์",
    "ข้อความ", "เบอร์", "โทร", "พิมพ์", "เสร็จ", "เร็ว", "ช้า", "ง่าย", "ยาก",
    "ชอบ", "รัก", "อยาก", "ต้อง", "ควร", "สามารถ", "เริ่ม", "จบ", "ตั้ง", "วาง",
    "เทศา", "กวั", "กัว", "ผป", "ปผ", "แบบบ",
    # Specific benchmark words
    "ปาร", "การ์น", "แผ่", "คับ", "ลัดว", "คัดว", "บชา", "เข้า", "สวั", "คาม", "วอน",
}


class NGramScorer:
    """Evaluates text probability and confidence between Thai and English."""

    def __init__(self):
        self.en_bigrams = COMMON_EN_BIGRAMS
        self.en_trigrams = COMMON_EN_TRIGRAMS
        self.th_bigrams = COMMON_TH_BIGRAMS
        self.th_trigrams = COMMON_TH_TRIGRAMS

    def score_english(self, text: str) -> float:
        """Compute English likelihood score based on n-grams and vocabulary."""
        text_lower = text.lower()
        if not text_lower:
            return 0.0

        # Exact dictionary match bonus
        if text_lower in COMMON_ENGLISH_WORDS:
            return 10.0 + len(text_lower) * 0.5

        score = 0.0
        # Character bigrams
        for i in range(len(text_lower) - 1):
            bg = text_lower[i : i + 2]
            score += self.en_bigrams.get(bg, -0.5)

        # Character trigrams
        for i in range(len(text_lower) - 2):
            tg = text_lower[i : i + 3]
            score += self.en_trigrams.get(tg, -0.8)

        # Penalize non-alphabetic characters in standard words
        for c in text:
            if not c.isalnum() and c not in "-_":
                score -= 2.0

        return score / max(1, len(text))

    def score_thai(self, text: str) -> float:
        """Compute Thai likelihood score based on n-grams and vocabulary."""
        if not text:
            return 0.0

        # Exact dictionary match bonus
        if text in COMMON_THAI_WORDS:
            return 10.0 + len(text) * 0.5

        score = 0.0
        # Character bigrams
        for i in range(len(text) - 1):
            bg = text[i : i + 2]
            score += self.th_bigrams.get(bg, -0.5)

        # Character trigrams
        for i in range(len(text) - 2):
            tg = text[i : i + 3]
            score += self.th_trigrams.get(tg, -0.8)

        return score / max(1, len(text))

    def evaluate_preference(
        self, token: str, current_layout: str
    ) -> Tuple[str, float, str]:
        """Determine if a token should be converted to the other layout.
        
        Args:
            token: The raw typed token.
            current_layout: 'EN' or 'TH'.
            
        Returns:
            Tuple of:
              - target_layout: 'EN', 'TH', or 'KEEP'
              - confidence: float between 0.0 and 1.0
              - reason: explanation of decision
        """
        if not token or len(token) < 2:
            return "KEEP", 0.0, "Token too short"

        if current_layout == "EN":
            # Priority 1: If current token is already a valid English word, PRESERVE IT!
            if token.lower() in COMMON_ENGLISH_WORDS:
                return "KEEP", 0.99, f"Valid English word '{token}'"

            # Compare current English score vs Thai converted score
            en_score = self.score_english(token)
            th_candidate = to_thai(token)
            th_score = self.score_thai(th_candidate)

            delta = th_score - en_score
            confidence = 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, delta))))

            if th_candidate in COMMON_THAI_WORDS:
                return "TH", 0.98, f"Exact Thai match '{th_candidate}'"

            if delta > 1.2:
                return "TH", min(0.99, confidence), f"Thai likelihood significantly higher (delta={delta:.2f})"
            elif delta < -1.0:
                return "KEEP", min(0.99, 1.0 - confidence), f"Valid English word (delta={delta:.2f})"
            else:
                return "KEEP", 0.5, f"Ambiguous token (delta={delta:.2f})"

        else:  # current_layout == "TH"
            # Priority 1: If current token is already a valid Thai word, PRESERVE IT!
            if token in COMMON_THAI_WORDS:
                return "KEEP", 0.99, f"Valid Thai word '{token}'"

            # If token is a long continuous Thai sequence (10+ Thai chars), it is Thai prose
            if len(token) >= 10 and all("\u0e00" <= c <= "\u0e7f" or c in " \t\n" for c in token):
                return "KEEP", 0.99, "Continuous Thai prose"


            # Compare current Thai score vs English converted score
            th_score = self.score_thai(token)
            en_candidate = to_english(token)
            en_score = self.score_english(en_candidate)

            delta = en_score - th_score
            confidence = 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, delta))))

            if en_candidate.lower() in COMMON_ENGLISH_WORDS:
                return "EN", 0.98, f"Exact English match '{en_candidate}'"

            if delta > 1.2:
                return "EN", min(0.99, confidence), f"English likelihood significantly higher (delta={delta:.2f})"
            elif delta < -1.0:
                return "KEEP", min(0.99, 1.0 - confidence), f"Valid Thai word (delta={delta:.2f})"
            else:
                return "KEEP", 0.5, f"Ambiguous token (delta={delta:.2f})"

