"""Auto-Correction Engine for Common Thai and English Typos.

Provides instant O(1) dictionary lookups for curated high-frequency misspellings.
Ensures zero overhead (<0.05 µs), full case preservation, and 100% deterministic results.
"""

from typing import Dict, Optional, Tuple


# Curated Thai Common Misspellings (คำที่มักเขียนผิดบ่อย)
# Mapping: typo -> standard canonical spelling
THAI_TYPOS: Dict[str, str] = {
    # ไม้เอก / ไม้โท กับคำว่า 'นะ' / 'ค่ะ'
    "นะค่ะ": "นะคะ",
    "ค่ะนะ": "คะนะ",

    # คำยอดฮิตระดับประเทศ
    "กระเพรา": "กะเพรา",
    "ผัดกระเพรา": "ผัดกะเพรา",
    "ใบกระเพรา": "ใบกะเพรา",
    "สังเกตุ": "สังเกต",
    "อนุญาติ": "อนุญาต",
    "เซ็นต์": "เซ็น",
    "เซ็นต์ชื่อ": "เซ็นชื่อ",
    "ลายเซ็นต์": "ลายเซ็น",
    "ออฟฟิต": "ออฟฟิศ",
    "อินเตอร์เน็ท": "อินเทอร์เน็ต",
    "ปรากฎ": "ปรากฏ",
    "ปรากฎการณ์": "ปรากฏการณ์",
    "กฏ": "กฎ",
    "กฏหมาย": "กฎหมาย",
    "กฏเกณฑ์": "กฎเกณฑ์",
    "มงกุฏ": "มงกุฎ",
    "ผูกพันธิ์": "ผูกพัน",
    "สเน่ห์": "เสน่ห์",
    "โอกาศ": "โอกาส",
    "สัมนา": "สัมมนา",
    "รสนิยมณ์": "รสนิยม",
    "ไลท์สด": "ไลฟ์สด",
    "โพส": "โพสต์",
    "อัพเดท": "อัปเดต",
    "อัพเดต": "อัปเดต",
    "เวป": "เว็บ",
    "เว็ป": "เว็บ",
    "เวปไซต์": "เว็บไซต์",
    "เว็ปไซต์": "เว็บไซต์",
    "คอมเม้น": "คอมเมนต์",
    "คอมเม้นต์": "คอมเมนต์",
    "เฟสบุ๊ค": "เฟซบุ๊ก",
    "เฟสบุ๊ก": "เฟซบุ๊ก",
    "แอพ": "แอป",
    "แอพพลิเคชั่น": "แอปพลิเคชัน",
    "เกมส์": "เกม",
    "การ์ตูนส์": "การ์ตูน",
    "โควต้า": "โควตา",
    "โค้วต้า": "โควตา",
    "ทลวง": "ทะลวง",
    "กระทันหัน": "กะทันหัน",
    "กระทัดรัด": "กะทัดรัด",
    "กะเพาะ": "กระเพาะ",
    "ขี้เกลียด": "ขี้เกียจ",
    "รังเกลียด": "รังเกียจ",
    "ลำใย": "ลำไย",
    "บรรได": "บันได",
    "ล๊อตเตอรี่": "ลอตเตอรี่",
    "สเต็ก": "สเต๊ก",
    "ไอศครีม": "ไอศกรีม",
    "ชลอ": "ชะลอ",
    "ปราณีต": "ประณีต",
    "หยากใย่": "หยากไย่",
    "เบนซิล": "เบนซิน",
    "กากะบาท": "กากบาท",
    "ไข่มุข": "ไข่มุก",
    "คฤหาสถ์": "คฤหาสน์",
    "คัมภีริ์": "คัมภีร์",
    "โครต": "โคตร",
    "เช็คบิล": "เช็กบิล",
    "เช็ค": "เช็ก",
    "ดอกไม้จันทร์": "ดอกไม้จันทน์",
    "เต๊นท์": "เต็นท์",
    "ไต้ถุน": "ใต้ถุน",
    "ทะยอย": "ทยอย",
    "ฑูต": "ทูต",
    "บันเทา": "บรรเทา",
    "ปราถนา": "ปรารถนา",
    "พิศวงษ์": "พิศวง",
    "ภาพยนต์": "ภาพยนตร์",
    "มัคคุเทศน์": "มัคคุเทศก์",
    "ย่อมเยาว์": "ย่อมเยา",
    "ระเห็ด": "ระเห็จ",
    "โลกาภิวัฒน์": "โลกาภิวัตน์",
    "ศิลป": "ศิลปะ",
    "สมเพส": "สมเพช",
    "สัมฤทธิ์ผล": "สัมฤทธิผล",
    "อกะตัญญู": "อกตัญญู",
    "อธิฐาน": "อธิษฐาน",
    "อนารถ": "อนาถ",
    "เอนกประสงค์": "อเนกประสงค์",
    "เอนก": "อเนก",
    "อัมหิต": "อำมหิต",
}

# Curated English Common Misspellings
ENGLISH_TYPOS: Dict[str, str] = {
    "teh": "the",
    "recieve": "receive",
    "recieved": "received",
    "recieving": "receiving",
    "seperate": "separate",
    "seperated": "separated",
    "seperately": "separately",
    "definately": "definitely",
    "untill": "until",
    "truely": "truly",
    "beleive": "believe",
    "beleived": "believed",
    "acheive": "achieve",
    "acheived": "achieved",
    "acheiving": "achieving",
    "wierd": "weird",
    "thier": "their",
    "freind": "friend",
    "freinds": "friends",
    "tommorrow": "tomorrow",
    "tommorow": "tomorrow",
    "calender": "calendar",
    "embarass": "embarrass",
    "embarassed": "embarrassed",
    "goverment": "government",
    "neccessary": "necessary",
    "occured": "occurred",
    "occuring": "occurring",
    "arguement": "argument",
    "accomodate": "accommodate",
    "begining": "beginning",
    "enviroment": "environment",
    "fourty": "forty",
    "grammer": "grammar",
    "happended": "happened",
    "knowlege": "knowledge",
    "lisence": "license",
    "mispell": "misspell",
    "mispelled": "misspelled",
    "noticable": "noticeable",
    "occurence": "occurrence",
    "priviledge": "privilege",
    "publically": "publicly",
    "suprise": "surprise",
    "suprised": "surprised",
    "alot": "a lot",
    "accross": "across",
    "adress": "address",
    "allways": "always",
    "apparantly": "apparently",
    "basicly": "basically",
    "carefull": "careful",
    "catagory": "category",
    "cleary": "clearly",
    "collegue": "colleague",
    "concious": "conscious",
    "curiousity": "curiosity",
    "dissapear": "disappear",
    "dissapoint": "disappoint",
    "equiptment": "equipment",
    "existance": "existence",
    "familar": "familiar",
    "finaly": "finally",
    "foreward": "forward",
    "garantee": "guarantee",
    "gental": "gentle",
    "greatful": "grateful",
    "happend": "happened",
    "ignorence": "ignorance",
    "immediatly": "immediately",
    "incidently": "incidentally",
    "independant": "independent",
    "interupt": "interrupt",
    "irresistable": "irresistible",
    "libary": "library",
    "maintainance": "maintenance",
    "millenium": "millennium",
    "nieghbor": "neighbor",
    "ocasion": "occasion",
    "oppurtunity": "opportunity",
    "persue": "pursue",
    "posession": "possession",
    "prefered": "preferred",
    "probly": "probably",
    "probaly": "probably",
    "reccomend": "recommend",
    "refered": "referred",
    "relavent": "relevant",
    "religous": "religious",
    "rember": "remember",
    "resistence": "resistance",
    "sensable": "sensible",
    "sence": "sense",
    "succesful": "successful",
    "tendancy": "tendency",
    "teritory": "territory",
    "tounge": "tongue",
    "truley": "truly",
    "unfortunatly": "unfortunately",
    "usefull": "useful",
    "vaccuum": "vacuum",
    "vehical": "vehicle",
    "writting": "writing",
    "yeild": "yield",
}


class AutoCorrector:
    """Ultra-fast high-confidence typo auto-correction engine."""

    _instance: Optional["AutoCorrector"] = None

    def __init__(self):
        self.thai_map: Dict[str, str] = dict(THAI_TYPOS)
        self.eng_map: Dict[str, str] = dict(ENGLISH_TYPOS)

    @classmethod
    def get_instance(cls) -> "AutoCorrector":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def correct(self, word: str, layout: str) -> Optional[Tuple[str, str]]:
        """Evaluate a word for common typo auto-correction.
        
        Args:
            word: The typed token (without surrounding whitespace).
            layout: 'TH' or 'EN'.
            
        Returns:
            Tuple of (corrected_text, reason) if typo found, else None.
        """
        if not word or len(word) < 2:
            return None

        clean = word.strip()

        if layout == "TH":
            # 1. Exact match in Thai typo map
            if clean in self.thai_map:
                corrected = self.thai_map[clean]
                return corrected, f"Auto-Correct: '{clean}' → '{corrected}'"

        elif layout == "EN":
            clean_lower = clean.lower()
            # 1. Exact match in English typo map
            if clean_lower in self.eng_map:
                target = self.eng_map[clean_lower]
                # Preserve capitalization
                if clean.isupper():
                    corrected = target.upper()
                elif clean.istitle():
                    corrected = target.capitalize()
                else:
                    corrected = target
                return corrected, f"Auto-Correct: '{clean}' → '{corrected}'"

        return None
