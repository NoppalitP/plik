"""Bidirectional mapping between US QWERTY and Thai Kedmanee layouts."""

# Mapping from US QWERTY characters to Thai Kedmanee characters
QWERTY_TO_THAI = {
    # Number row unshifted
    "1": "ๅ",
    "2": "/",
    "3": "-",
    "4": "ภ",
    "5": "ถ",
    "6": "ุ",
    "7": "ึ",
    "8": "ค",
    "9": "ต",
    "0": "จ",
    "-": "ข",
    "=": "ช",
    # Number row shifted
    "!": "+",
    "@": "๑",
    "#": "๒",
    "$": "๓",
    "%": "๔",
    "^": "ู",
    "&": "฿",
    "*": "๕",
    "(": "๖",
    ")": "๗",
    "_": "๘",
    "+": "๙",
    # Top row unshifted
    "q": "ๆ",
    "w": "ไ",
    "e": "ำ",
    "r": "พ",
    "t": "ะ",
    "y": "ั",
    "u": "ี",
    "i": "ร",
    "o": "น",
    "p": "ย",
    "[": "บ",
    "]": "ล",
    "\\": "ฃ",
    # Top row shifted
    "Q": "๐",
    "W": '"',
    "E": "ฎ",
    "R": "ฑ",
    "T": "ธ",
    "Y": "ํ",
    "U": "๊",
    "I": "ณ",
    "O": "ฯ",
    "P": "ญ",
    "{": "ฐ",
    "}": ",",
    "|": "ฅ",
    # Home row unshifted
    "a": "ฟ",
    "s": "ห",
    "d": "ก",
    "f": "ด",
    "g": "เ",
    "h": "้",
    "j": "่",
    "k": "า",
    "l": "ส",
    ";": "ว",
    "'": "ง",
    # Home row shifted
    "A": "ฤ",
    "S": "ฆ",
    "D": "ฏ",
    "F": "โ",
    "G": "ฌ",
    "H": "็",
    "J": "๋",
    "K": "ษ",
    "L": "ศ",
    ":": "ซ",
    '"': ".",
    # Bottom row unshifted
    "z": "ผ",
    "x": "ป",
    "c": "แ",
    "v": "อ",
    "b": "ิ",
    "n": "ื",
    "m": "ท",
    ",": "ม",
    ".": "ใ",
    "/": "ฝ",
    # Bottom row shifted
    "Z": "(",
    "X": ")",
    "C": "ฉ",
    "V": "ฮ",
    "B": "ฺ",
    "N": "์",
    "M": "?",
    "<": "ฒ",
    ">": "ฬ",
    "?": "ฦ",
    # Space & whitespace
    " ": " ",
    "\t": "\t",
    "\n": "\n",
}

# Reverse mapping: Thai Kedmanee characters to US QWERTY
THAI_TO_QWERTY = {}
for q, t in QWERTY_TO_THAI.items():
    if t not in THAI_TO_QWERTY:
        THAI_TO_QWERTY[t] = q
# Notice: some punctuation like / and - appears on multiple keys or mappings.
# Ensure consistent primary reverse mapping:
THAI_TO_QWERTY["/"] = "2"
THAI_TO_QWERTY["-"] = "3"
THAI_TO_QWERTY[","] = "}"
THAI_TO_QWERTY["."] = '"'
THAI_TO_QWERTY["("] = "Z"
THAI_TO_QWERTY[")"] = "X"
THAI_TO_QWERTY["?"] = "M"


def to_thai(text: str) -> str:
    """Translate English QWERTY string to Thai Kedmanee string."""
    return "".join(QWERTY_TO_THAI.get(ch, ch) for ch in text)


def to_english(text: str) -> str:
    """Translate Thai Kedmanee string to English QWERTY string."""
    return "".join(THAI_TO_QWERTY.get(ch, ch) for ch in text)
