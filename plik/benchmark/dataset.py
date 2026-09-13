"""Comprehensive Benchmark Dataset (100+ Test Cases).

Categories:
1. THAI_TYPED_ON_QWERTY: Expected AUTO_SWITCH to TH
2. ENGLISH_TYPED_ON_KEDMANEE: Expected AUTO_SWITCH to EN
3. DEV_TOOLS_CODE: Expected NONE (zero false positives in VS Code, Terminal, etc.)
4. URLS_AND_FILE_PATHS: Expected NONE (zero false positives on paths, URLs, and code identifiers)
5. MIXED_SENTENCES: Natural mixed Thai-English writing
6. SLANG_AND_CHAT: Expected NONE (preserve 555, krub, eiei, lol)
7. SHORT_AMBIGUOUS_WORDS: Careful resolution of 2-letter tokens
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TestCase:
    id: int
    category: str
    input_text: str
    initial_layout: str
    active_process: str
    expected_action: str  # 'AUTO_SWITCH' or 'NONE'
    expected_target_layout: str  # 'TH', 'EN', or ''
    description: str


BENCHMARK_DATASET: List[TestCase] = [
    # ==========================================
    # 1. THAI TYPED ON QWERTY (20 cases)
    # ==========================================
    TestCase(1, "THAI_ON_QWERTY", "d;y ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "วัน (d;y)"),
    TestCase(2, "THAI_ON_QWERTY", "c[[ ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "แบบ (c[[)"),
    TestCase(3, "THAI_ON_QWERTY", "l;ylfu ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "สวัสดี (l;ylfu)"),
    TestCase(4, "THAI_ON_QWERTY", "4kKk ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "ภาษา (4kKk)"),
    TestCase(5, "THAI_ON_QWERTY", "gmLk ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "เทศา (gmLk)"),
    TestCase(6, "THAI_ON_QWERTY", ";yo ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "วอน (;yo)"),
    TestCase(7, "THAI_ON_QWERTY", "dkfo ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "การ์น (dkfo)"),
    TestCase(8, "THAI_ON_QWERTY", "8y[ ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "ครับ (8y[)"),
    TestCase(9, "THAI_ON_QWERTY", "g]y ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "เลย (g]y)"),
    TestCase(10, "THAI_ON_QWERTY", "]yf; ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "ลัดว (]yf;)"),
    TestCase(11, "THAI_ON_QWERTY", "8yf; ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "คัดว (8yf;)"),
    TestCase(12, "THAI_ON_QWERTY", "[=k ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "บชา ([=k)"),
    TestCase(13, "THAI_ON_QWERTY", "czj ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "แผ่ (czj)"),
    TestCase(14, "THAI_ON_QWERTY", "8k, ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "คาม (8k,)"),
    TestCase(15, "THAI_ON_QWERTY", "xki ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "ปาร (xki)"),
    TestCase(16, "THAI_ON_QWERTY", "l;y ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "สวั (l;y)"),
    TestCase(17, "THAI_ON_QWERTY", "g-hk ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "เข้า (g-hk)"),
    TestCase(18, "THAI_ON_QWERTY", "mewfh ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "ทำได้ (mewfh)"),
    TestCase(19, "THAI_ON_QWERTY", "g]j; ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "แล้ว (g]j;)"),
    TestCase(20, "THAI_ON_QWERTY", "w,j ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "ไม่ (w,j)"),

    # ==========================================
    # 2. ENGLISH TYPED ON KEDMANEE (20 cases)
    # ==========================================
    TestCase(21, "ENGLISH_ON_KEDMANEE", "ฟยยสำ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "apple (ฟยยสำ)"),
    TestCase(22, "ENGLISH_ON_KEDMANEE", "ะำหะ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "test (ะำหะ)"),
    TestCase(23, "ENGLISH_ON_KEDMANEE", "ิพำฟา ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "break (ิพำฟา)"),
    TestCase(24, "ENGLISH_ON_KEDMANEE", "ัำห ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "yes (ัำห)"),
    TestCase(25, "ENGLISH_ON_KEDMANEE", "้ำสสน ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "hello (้ำสสน)"),
    TestCase(26, "ENGLISH_ON_KEDMANEE", "แนกำ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "code (แนกำ)"),
    TestCase(27, "ENGLISH_ON_KEDMANEE", "พีื ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "run (พีื)"),
    TestCase(28, "ENGLISH_ON_KEDMANEE", "ยีห้ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "push (ยีห้)"),
    TestCase(29, "ENGLISH_ON_KEDMANEE", "ยีสส ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "pull (ยีสส)"),
    TestCase(30, "ENGLISH_ON_KEDMANEE", "แนททระ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "commit (แนททระ)"),
    TestCase(31, "ENGLISH_ON_KEDMANEE", "ดำฟะีพำ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "feature (ดำฟะีพำ)"),
    TestCase(32, "ENGLISH_ON_KEDMANEE", "หำพอำพ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "server (หำพอำพ)"),
    TestCase(33, "ENGLISH_ON_KEDMANEE", "แสรำืะ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "client (แสรำืะ)"),
    TestCase(34, "ENGLISH_ON_KEDMANEE", "กฟะฟ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "data (กฟะฟ)"),
    TestCase(35, "ENGLISH_ON_KEDMANEE", "ำพพนพ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "error (ำพพนพ)"),
    TestCase(36, "ENGLISH_ON_KEDMANEE", "ะฟหาห ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "tasks (ะฟหาห)"),
    TestCase(37, "ENGLISH_ON_KEDMANEE", "ีหำพ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "user (ีหำพ)"),
    TestCase(38, "ENGLISH_ON_KEDMANEE", "สราำ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "like (สราำ)"),
    TestCase(39, "ENGLISH_ON_KEDMANEE", "ะรทำ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "time (ะรทำ)"),
    TestCase(40, "ENGLISH_ON_KEDMANEE", "้ร ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "hi (้ร)"),

    # ==========================================
    # 3. DEV TOOLS & CODE (20 cases)
    # Expected: NONE (Protected from auto-switching in IDEs and terminals)
    # ==========================================
    TestCase(41, "DEV_TOOLS_CODE", "git status ", "EN", "code.exe", "NONE", "", "git status in VS Code"),
    TestCase(42, "DEV_TOOLS_CODE", "git commit -m \"fix\" ", "EN", "code.exe", "NONE", "", "git commit in VS Code"),
    TestCase(43, "DEV_TOOLS_CODE", "docker ps -a ", "EN", "windowsterminal.exe", "NONE", "", "docker ps in Terminal"),
    TestCase(44, "DEV_TOOLS_CODE", "npm install --save ", "EN", "powershell.exe", "NONE", "", "npm install in PowerShell"),
    TestCase(45, "DEV_TOOLS_CODE", "kubectl get pods ", "EN", "cmd.exe", "NONE", "", "kubectl in CMD"),
    TestCase(46, "DEV_TOOLS_CODE", "def calculate_pnl(): ", "EN", "code.exe", "NONE", "", "Python def in VS Code"),
    TestCase(47, "DEV_TOOLS_CODE", "import pandas as pd ", "EN", "code.exe", "NONE", "", "Python import in VS Code"),
    TestCase(48, "DEV_TOOLS_CODE", "const [state, setState] = useState() ", "EN", "code.exe", "NONE", "", "React hook in VS Code"),
    TestCase(49, "DEV_TOOLS_CODE", "SELECT * FROM users; ", "EN", "devenv.exe", "NONE", "", "SQL query in Visual Studio"),
    TestCase(50, "DEV_TOOLS_CODE", "cargo build --release ", "EN", "windowsterminal.exe", "NONE", "", "Cargo in Terminal"),
    TestCase(51, "DEV_TOOLS_CODE", "python -m pytest ", "EN", "powershell.exe", "NONE", "", "pytest command in PowerShell"),
    TestCase(52, "DEV_TOOLS_CODE", "curl -X POST http://localhost:8000 ", "EN", "windowsterminal.exe", "NONE", "", "curl in Terminal"),
    TestCase(53, "DEV_TOOLS_CODE", "sudo systemctl restart nginx ", "EN", "bash.exe", "NONE", "", "systemctl in Bash"),
    TestCase(54, "DEV_TOOLS_CODE", "npm run dev ", "EN", "windowsterminal.exe", "NONE", "", "npm run dev in Terminal"),
    TestCase(55, "DEV_TOOLS_CODE", "grep -rn \"pattern\" . ", "EN", "bash.exe", "NONE", "", "grep in Bash"),
    TestCase(56, "DEV_TOOLS_CODE", "echo $PATH ", "EN", "bash.exe", "NONE", "", "echo in Bash"),
    TestCase(57, "DEV_TOOLS_CODE", "go run main.go ", "EN", "code.exe", "NONE", "", "go run in VS Code"),
    TestCase(58, "DEV_TOOLS_CODE", "export ENV=production ", "EN", "windowsterminal.exe", "NONE", "", "export in Terminal"),
    TestCase(59, "DEV_TOOLS_CODE", "kill -9 1234 ", "EN", "bash.exe", "NONE", "", "kill in Bash"),
    TestCase(60, "DEV_TOOLS_CODE", "git checkout -b feature/login ", "EN", "code.exe", "NONE", "", "git checkout in VS Code"),

    # ==========================================
    # 4. URLS, FILE PATHS & IDENTIFIERS (15 cases)
    # Expected: NONE (Protected by SyntaxGuard even in normal apps like Chrome/Slack)
    # ==========================================
    TestCase(61, "URLS_AND_FILE_PATHS", "https://github.com/project ", "EN", "chrome.exe", "NONE", "", "GitHub HTTPS URL"),
    TestCase(62, "URLS_AND_FILE_PATHS", "www.google.co.th ", "EN", "chrome.exe", "NONE", "", "Google URL"),
    TestCase(63, "URLS_AND_FILE_PATHS", "C:\\Users\\admin\\Desktop\\data.json ", "EN", "slack.exe", "NONE", "", "Windows File Path"),
    TestCase(64, "URLS_AND_FILE_PATHS", "./src/engine/core.py ", "EN", "chrome.exe", "NONE", "", "Python file path"),
    TestCase(65, "URLS_AND_FILE_PATHS", "getUserProfileById ", "EN", "slack.exe", "NONE", "", "camelCase function name"),
    TestCase(66, "URLS_AND_FILE_PATHS", "UserProfileComponent ", "EN", "chrome.exe", "NONE", "", "PascalCase component name"),
    TestCase(67, "URLS_AND_FILE_PATHS", "calculate_total_amount ", "EN", "discord.exe", "NONE", "", "snake_case variable name"),
    TestCase(68, "URLS_AND_FILE_PATHS", "MAX_RETRY_COUNT ", "EN", "slack.exe", "NONE", "", "UPPER_SNAKE_CASE constant"),
    TestCase(69, "URLS_AND_FILE_PATHS", "api-gateway-service ", "EN", "chrome.exe", "NONE", "", "kebab-case service name"),
    TestCase(70, "URLS_AND_FILE_PATHS", "user@example.com ", "EN", "outlook.exe", "NONE", "", "Email address"),
    TestCase(71, "URLS_AND_FILE_PATHS", "=== ", "EN", "chrome.exe", "NONE", "", "Strict equality operator"),
    TestCase(72, "URLS_AND_FILE_PATHS", "=> ", "EN", "chrome.exe", "NONE", "", "Arrow function operator"),
    TestCase(73, "URLS_AND_FILE_PATHS", "docker-compose.yml ", "EN", "slack.exe", "NONE", "", "YAML filename"),
    TestCase(74, "URLS_AND_FILE_PATHS", "--no-verify ", "EN", "chrome.exe", "NONE", "", "CLI flag parameter"),
    TestCase(75, "URLS_AND_FILE_PATHS", "$PORT ", "EN", "slack.exe", "NONE", "", "Shell variable"),

    # ==========================================
    # 5. MIXED THAI-ENGLISH WRITING (10 cases)
    # Expected: NONE for English tech terms embedded in Thai
    # ==========================================
    TestCase(76, "MIXED_SENTENCES", "PR ", "EN", "chrome.exe", "NONE", "", "Tech term 'PR'"),
    TestCase(77, "MIXED_SENTENCES", "repo ", "EN", "chrome.exe", "NONE", "", "Tech term 'repo'"),
    TestCase(78, "MIXED_SENTENCES", "server ", "EN", "chrome.exe", "NONE", "", "Tech term 'server'"),
    TestCase(79, "MIXED_SENTENCES", "sprint ", "EN", "chrome.exe", "NONE", "", "Tech term 'sprint'"),
    TestCase(80, "MIXED_SENTENCES", "meeting ", "EN", "slack.exe", "NONE", "", "Meeting word in Slack"),
    TestCase(81, "MIXED_SENTENCES", "deploy ", "EN", "chrome.exe", "NONE", "", "Deploy word in Chrome"),
    TestCase(82, "MIXED_SENTENCES", "token ", "EN", "slack.exe", "NONE", "", "Auth token word"),
    TestCase(83, "MIXED_SENTENCES", "issue ", "EN", "chrome.exe", "NONE", "", "Issue tracker word"),
    TestCase(84, "MIXED_SENTENCES", "config ", "EN", "chrome.exe", "NONE", "", "Config word"),
    TestCase(85, "MIXED_SENTENCES", "login ", "EN", "chrome.exe", "NONE", "", "Login word"),

    # ==========================================
    # 6. SLANG & CHAT EXPRESSIONS (10 cases)
    # Expected: NONE (Preserve Thai laughter & slang)
    # ==========================================
    TestCase(86, "SLANG_AND_CHAT", "555 ", "EN", "line.exe", "NONE", "", "Thai laughter 555"),
    TestCase(87, "SLANG_AND_CHAT", "5555 ", "EN", "line.exe", "NONE", "", "Thai laughter 5555"),
    TestCase(88, "SLANG_AND_CHAT", "55555 ", "EN", "line.exe", "NONE", "", "Thai laughter 55555"),
    TestCase(89, "SLANG_AND_CHAT", "krub ", "EN", "line.exe", "NONE", "", "Polite particle krub"),
    TestCase(90, "SLANG_AND_CHAT", "kub ", "EN", "line.exe", "NONE", "", "Polite particle kub"),
    TestCase(91, "SLANG_AND_CHAT", "eiei ", "EN", "line.exe", "NONE", "", "Playful eiei"),
    TestCase(92, "SLANG_AND_CHAT", "lol ", "EN", "discord.exe", "NONE", "", "English slang lol"),
    TestCase(93, "SLANG_AND_CHAT", "btw ", "EN", "slack.exe", "NONE", "", "English acronym btw"),
    TestCase(94, "SLANG_AND_CHAT", "thx ", "EN", "line.exe", "NONE", "", "Thanks slang thx"),
    TestCase(95, "SLANG_AND_CHAT", "pls ", "EN", "slack.exe", "NONE", "", "Please slang pls"),

    # ==========================================
    # 7. SHORT AMBIGUOUS WORDS (10 cases)
    # Expected: Keep original layout unless unmistakable
    # ==========================================
    TestCase(96, "SHORT_AMBIGUOUS_WORDS", "to ", "EN", "chrome.exe", "NONE", "", "English 'to' preserved"),
    TestCase(97, "SHORT_AMBIGUOUS_WORDS", "in ", "EN", "chrome.exe", "NONE", "", "English 'in' preserved"),
    TestCase(98, "SHORT_AMBIGUOUS_WORDS", "is ", "EN", "chrome.exe", "NONE", "", "English 'is' preserved"),
    TestCase(99, "SHORT_AMBIGUOUS_WORDS", "go ", "EN", "chrome.exe", "NONE", "", "English 'go' preserved"),
    TestCase(100, "SHORT_AMBIGUOUS_WORDS", "me ", "EN", "chrome.exe", "NONE", "", "English 'me' preserved"),
    TestCase(101, "SHORT_AMBIGUOUS_WORDS", "we ", "EN", "chrome.exe", "NONE", "", "English 'we' preserved"),
    TestCase(102, "SHORT_AMBIGUOUS_WORDS", "do ", "EN", "chrome.exe", "NONE", "", "English 'do' preserved"),
    TestCase(103, "SHORT_AMBIGUOUS_WORDS", "on ", "EN", "chrome.exe", "NONE", "", "English 'on' preserved"),
    TestCase(104, "SHORT_AMBIGUOUS_WORDS", "at ", "EN", "chrome.exe", "NONE", "", "English 'at' preserved"),
    TestCase(105, "SHORT_AMBIGUOUS_WORDS", "up ", "EN", "chrome.exe", "NONE", "", "English 'up' preserved"),
]
