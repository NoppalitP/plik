"""Adversarial & Ambiguity Stress Benchmark (The 'Brutal' Real-World Test).

Evaluates edge cases where real-world systems fail:
1. Ultra-short ambiguous tokens (1-3 characters) with cross-lingual orthographic collisions
2. Typo-on-Typo: Keystroke errors committed while simultaneously on the wrong layout
3. Informal slang, internet karaoke, laughing markers (55555), and gaming jargon
4. Code, SQL, and CLI typed in general applications (Notepad, Slack) where Dev-Tool immunity is OFF
"""

import statistics
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from scipy import stats

from plik.engine.core import CoreEngine
from plik.evaluation.baselines import (
    HeuristicLexiconBaseline,
    PureCharNGramBaseline,
    PureFSABaseline,
)
from plik.layouts.kedmanee import to_english, to_thai


@dataclass
class StressSample:
    id: str
    category: str
    description: str
    initial_layout: str
    keystrokes: str
    expected_switch: bool
    expected_target: Optional[str]
    active_process: str = "notepad.exe"  # Non-dev app to disable dev-tool immunity


def generate_stress_samples() -> List[StressSample]:
    """Generates 150 adversarial and edge-case stress samples."""
    samples = []
    idx = 1

    # =========================================================================
    # 1. Ultra-Short Ambiguous Words (1-3 chars) [40 samples]
    # =========================================================================
    # Case A: English words that are valid Thai words/phonotactics on Kedmanee
    # Typist is typing English in Notepad. Should NOT switch!
    en_ambiguous = [
        ("me", "Valid English 'me' -> Kedmanee maps to 'ทำ'"),
        ("go", "Valid English 'go' -> Kedmanee maps to 'เ-ข'"),
        ("if", "Valid English 'if' -> Kedmanee maps to 'ร-ด'"),
        ("my", "Valid English 'my' -> Kedmanee maps to 'ท-ั'"),
        ("in", "Valid English 'in' -> Kedmanee maps to 'ร-ณ'"),
        ("is", "Valid English 'is' -> Kedmanee maps to 'ร-ห'"),
        ("it", "Valid English 'it' -> Kedmanee maps to 'ร-ะ'"),
        ("no", "Valid English 'no' -> Kedmanee maps to 'น-น'"),
        ("or", "Valid English 'or' -> Kedmanee maps to 'น-พ'"),
        ("an", "Valid English 'an' -> Kedmanee maps to 'ฟ-น'"),
        ("so", "Valid English 'so' -> Kedmanee maps to 'ห-ข'"),
        ("we", "Valid English 'we' -> Kedmanee maps to 'ไ-ำ'"),
        ("am", "Valid English 'am' -> Kedmanee maps to 'ฟ-ท'"),
        ("do", "Valid English 'do' -> Kedmanee maps to 'ก-ห'"),
        ("at", "Valid English 'at' -> Kedmanee maps to 'ฟ-ะ'"),
        ("to", "Valid English 'to' -> Kedmanee maps to 'ะ-น'"),
        ("he", "Valid English 'he' -> Kedmanee maps to 'โ-้'"),
        ("by", "Valid English 'by' -> Kedmanee maps to 'ิ-ั'"),
        ("on", "Valid English 'on' -> Kedmanee maps to 'น-น'"),
        ("as", "Valid English 'as' -> Kedmanee maps to 'ฟ-ห'"),
    ]
    for word, desc in en_ambiguous:
        samples.append(
            StressSample(
                id=f"STRESS-AMB-EN-{idx:03d}",
                category="Ultra-Short Ambiguity (Clean EN)",
                description=desc,
                initial_layout="EN",
                keystrokes=f"{word} ",
                expected_switch=False,
                expected_target=None,
            )
        )
        idx += 1

    # Case B: Mistyped short Thai words on English layout
    # User wanted to type Thai on QWERTY: "ทำ" -> "me ", "ไป" -> "gp ", etc.
    th_mistakes_short = [
        ("me", "TH", "ทำ", "User wanted 'ทำ', typed 'me' on EN"),
        ("gp", "TH", "ไป", "User wanted 'ไป', typed 'gp' on EN"),
        ("dk", "TH", "มา", "User wanted 'มา', typed 'dk' on EN"),
        ("du", "TH", "มี", "User wanted 'มี', typed 'du' on EN"),
        ("fu", "TH", "ดี", "User wanted 'ดี', typed 'fu' on EN"),
        ("7o", "TH", "คน", "User wanted 'คน', typed '7o' on EN"),
        ("dyo", "TH", "วัน", "User wanted 'วัน', typed 'dyo' on EN"),
        ("dbo", "TH", "กิน", "User wanted 'กิน', typed 'dbo' on EN"),
        ("g9k", "TH", "เปา", "User wanted 'เปา', typed 'g9k' on EN"),
        ("d;", "TH", "มัว", "User wanted 'มัว', typed 'd;' on EN"),
        ("l;y", "TH", "สวั", "User wanted 'สวั', typed 'l;y' on EN"),
        ("c[[", "TH", "แบบ", "User wanted 'แบบ', typed 'c[[' on EN"),
        ("0y;", "TH", "นัว", "User wanted 'นัว', typed '0y;' on EN"),
        ("9k", "TH", "ตา", "User wanted 'ตา', typed '9k' on EN"),
        ("8k", "TH", "ขา", "User wanted 'ขา', typed '8k' on EN"),
        ("0hk", "TH", "หน้า", "User wanted 'หน้า', typed '0hk' on EN"),
        ("ihk", "TH", "ร้า", "User wanted 'ร้า', typed 'ihk' on EN"),
        ("xkd", "TH", "ปาม", "User wanted 'ปาม', typed 'xkd' on EN"),
        ("rkd", "TH", "งาม", "User wanted 'งาม', typed 'rkd' on EN"),
        ("t;", "TH", "อะ", "User wanted 'อะ', typed 't;' on EN"),
    ]
    for typed, target, orig, desc in th_mistakes_short:
        samples.append(
            StressSample(
                id=f"STRESS-AMB-TH-{idx:03d}",
                category="Ultra-Short Ambiguity (Mistyped TH on EN)",
                description=desc,
                initial_layout="EN",
                keystrokes=f"{typed} ",
                expected_switch=True,
                expected_target=target,
            )
        )
        idx += 1

    # =========================================================================
    # 2. Typo-on-Typo: Spelled wrong while on wrong layout [30 samples]
    # =========================================================================
    typo_on_typos = [
        # Thai mistyped on EN with typo:
        ("l;yflg", "TH", "สวัสดี with typo 'f' inserted"),
        ("d;yflfg", "TH", "วันสวัสดี with typo"),
        ("c[[x", "TH", "แบบ with accidental 'x'"),
        ("rkomd", "TH", "งาน with accidental 'o'"),
        ("xkd-kd", "TH", "ปาก with extra dash"),
        ("g9b-d", "TH", "เปิด with typo"),
        ("g9yod", "TH", "เตือน with typo"),
        ("d;yl;y", "TH", "วันสวั typo"),
        ("c[[-c[[", "TH", "แบบ-แบบ with typo"),
        ("0hk-ihk", "TH", "หน้า-ร้า typo"),
        ("g9hk0hk", "TH", "เท่าหน้า typo"),
        ("0hk0hk0", "TH", "นานา typo"),
        ("l;y-fg", "TH", "สวั-ดี typo"),
        ("gpk-gpk", "TH", "เอา-เอา typo"),
        ("d;yd;y", "TH", "วันวัน typo"),
        # English code/commands mistyped on Kedmanee with typo:
        ("ดืมแะรนื", "EN", "function mistyped on Kedmanee"),
        ("แนหะรนื", "EN", "const mistyped on Kedmanee"),
        ("พำะีพน", "EN", "return mistyped on Kedmanee"),
        ("ะำหะรืเ", "EN", "testing typo on Kedmanee"),
        ("กพินหะ", "EN", "docker typo on Kedmanee"),
        ("แระ แนททระ", "EN", "git commit typo on Kedmanee"),
        ("หียน แำะ", "EN", "sudo get typo on Kedmanee"),
        ("ฟหัืแ ะำหะ", "EN", "async test on Kedmanee"),
        ("สฟพ ฟหหั", "EN", "var array on Kedmanee"),
        ("สำะแ้", "EN", "fetch on Kedmanee"),
        ("ะำหะ_กฟะฟ", "EN", "test_data on Kedmanee"),
        ("ฟหร_ีกั", "EN", "api_url on Kedmanee"),
        ("ืฟทำหะฟแำ", "EN", "namespace on Kedmanee"),
        ("ยีนพแำ", "EN", "source on Kedmanee"),
        ("ำปยนา", "EN", "export on Kedmanee"),
    ]
    for typed, target, desc in typo_on_typos:
        samples.append(
            StressSample(
                id=f"STRESS-TYPO-{idx:03d}",
                category="Typo-on-Typo (Corrupted Keystrokes)",
                description=desc,
                initial_layout="EN" if target == "TH" else "TH",
                keystrokes=f"{typed} ",
                expected_switch=True,
                expected_target=target,
            )
        )
        idx += 1

    # =========================================================================
    # 3. Slang, Karaoke, Internet Laughs, Gaming [40 samples]
    # =========================================================================
    slang_karaoke = [
        # Karaoke / Internet slang in EN layout (Should STAY in EN)
        ("55555555", False, None, "EN", "Thai laughter 55555 in EN mode"),
        ("555+", False, None, "EN", "Thai laughter 555+"),
        ("mak mak", False, None, "EN", "Karaoke 'mak mak' (very much)"),
        ("jing ror", False, None, "EN", "Karaoke 'jing ror' (really?)"),
        ("eiei", False, None, "EN", "Cute laughter 'eiei'"),
        ("kub", False, None, "EN", "Karaoke polite particle 'kub'"),
        ("krub", False, None, "EN", "Karaoke polite particle 'krub'"),
        ("naja", False, None, "EN", "Karaoke particle 'naja'"),
        ("ggwp", False, None, "EN", "Gaming slang 'ggwp'"),
        ("afk", False, None, "EN", "Gaming slang 'afk'"),
        ("brb", False, None, "EN", "Gaming slang 'brb'"),
        ("rofl", False, None, "EN", "Internet slang 'rofl'"),
        ("lmao", False, None, "EN", "Internet slang 'lmao'"),
        ("btw", False, None, "EN", "Chat acronym 'btw'"),
        ("idk", False, None, "EN", "Chat acronym 'idk'"),
        ("omg", False, None, "EN", "Chat acronym 'omg'"),
        ("thx", False, None, "EN", "Chat acronym 'thx'"),
        ("pls", False, None, "EN", "Chat acronym 'pls'"),
        ("fyi", False, None, "EN", "Chat acronym 'fyi'"),
        ("asap", False, None, "EN", "Chat acronym 'asap'"),
        # Thai informal slang in TH layout (Should STAY in TH)
        ("จึ้งมากแม่", False, None, "TH", "Modern Thai slang 'จึ้งมากแม่'"),
        ("ปังปุริเย่", False, None, "TH", "Modern Thai slang 'ปังปุริเย่'"),
        ("นอยด์อ่า", False, None, "TH", "Modern Thai slang 'นอยด์อ่า'"),
        ("ฟินเวอร์", False, None, "TH", "Thai slang 'ฟินเวอร์'"),
        ("ต๊าชชช", False, None, "TH", "Thai elongated slang 'ต๊าชชช'"),
        ("บูดดด", False, None, "TH", "Thai slang 'บูดดด'"),
        ("เกินปุยมุ้ย", False, None, "TH", "Thai cute slang 'เกินปุยมุ้ย'"),
        ("ตัวแม่จะแคร์เพื่อ", False, None, "TH", "Thai slang phrase"),
        ("สุดปัง", False, None, "TH", "Thai slang 'สุดปัง'"),
        ("เตงงง", False, None, "TH", "Thai informal 'เตงงง'"),
        # Thai slang mistyped in EN layout (Should SWITCH to TH)
        ("0yog", True, "TH", "EN", "'นอย' typed on EN"),
        ("xy'x5ibg9่", True, "TH", "EN", "'ปังปุริเย่' typed on EN"),
        ("fpb'gik", True, "TH", "EN", "'จึ้งมาก' typed on EN"),
        ("xkd0hk", True, "TH", "EN", "'ปากหมา' typed on EN"),
        ("d;yoqyd", True, "TH", "EN", "'กวนตีน' typed on EN"),
        ("c-j0hk", True, "TH", "EN", "'แม่งเอ๊ย' typed on EN"),
        ("r5d0hk", True, "TH", "EN", "'งงมาก' typed on EN"),
        ("ikyg9j", True, "TH", "EN", "'รวยเละ' typed on EN"),
        ("g9y''", True, "TH", "EN", "'เตงง' typed on EN"),
        ("l5fxy'", True, "TH", "EN", "'สุดปัง' typed on EN"),
    ]
    for text, exp_sw, exp_tgt, init_l, desc in slang_karaoke:
        samples.append(
            StressSample(
                id=f"STRESS-SLANG-{idx:03d}",
                category="Slang, Karaoke & Gaming",
                description=desc,
                initial_layout=init_l,
                keystrokes=f"{text} ",
                expected_switch=exp_sw,
                expected_target=exp_tgt,
            )
        )
        idx += 1

    # =========================================================================
    # 4. Code & Technical Syntax in General Apps (Notepad / Slack) [40 samples]
    # Dev-Tool immunity is INACTIVE here to test pure SyntaxGuard & algorithms!
    # =========================================================================
    code_in_general_apps = [
        # Clean Code typed in Notepad: SHOULD NOT SWITCH TO THAI!
        ("const result = await db.query('SELECT * FROM users');", False, None, "EN", "SQL in JS in Notepad"),
        ("if (status === 200 && response.data != null) return;", False, None, "EN", "JS statement in Notepad"),
        ("git checkout -b feature/auth-v2 origin/main", False, None, "EN", "Git command in chat"),
        ("docker run -d -p 8080:80 --name web nginx:alpine", False, None, "EN", "Docker CLI in chat"),
        ("pip install --upgrade numpy pandas scikit-learn", False, None, "EN", "Pip command in chat"),
        ("curl -X POST https://api.stripe.com/v1/charges", False, None, "EN", "Curl with URL in chat"),
        ("npm run build && pm2 restart ecosystem.config.js", False, None, "EN", "Npm build command in chat"),
        ("sudo systemctl restart nginx.service", False, None, "EN", "Sudo CLI in chat"),
        ("let buffer = new Uint8Array(1024);", False, None, "EN", "Typed array in Notepad"),
        ("def calculate_pnl(entry_price, exit_price, qty):", False, None, "EN", "Python def in Notepad"),
        ("users.filter(u => u.age >= 18 && u.isActive);", False, None, "EN", "Arrow func in Notepad"),
        ("chmod -R 755 /var/www/html/storage", False, None, "EN", "Chmod in chat"),
        ("tar -czvf backup-2026-09-13.tar.gz /data/", False, None, "EN", "Tar in chat"),
        ("grep -rn 'TODO' src/components/ | wc -l", False, None, "EN", "Piped grep in chat"),
        ("{\"id\": 101, \"sku\": \"BTC-USDT\", \"is_active\": true}", False, None, "EN", "JSON in Notepad"),
        ("x = (a + b) * (c - d) / 100.0;", False, None, "EN", "Math expr in Notepad"),
        ("cat /etc/nginx/sites-available/default", False, None, "EN", "File path in chat"),
        ("C:\\Windows\\System32\\drivers\\etc\\hosts", False, None, "EN", "Windows path in chat"),
        ("ssh -i ~/.ssh/id_rsa user@192.168.1.50", False, None, "EN", "SSH cmd in chat"),
        ("find . -name '*.pyc' -delete", False, None, "EN", "Find cmd in chat"),
        # Code mistakenly typed in Thai layout in Notepad: SHOULD SWITCH TO EN!
        ("แนหะ พำหีสน = ฟใหระ กิ.ฟีำพั('หำสำแะ * ดพนท ีหำพห');", True, "EN", "TH", "Mistyped SQL query on TH in Notepad"),
        ("รด (หะฟะีห === 200 && พำหยนาหำ.กฟะฟ != นีสส) พำะีพน;", True, "EN", "TH", "Mistyped JS if on TH in Notepad"),
        ("แระ แ้ำแานีะ -ิ ดำฟะีพำ/ฟีะ้-อำ นพรแรน/ทฟรน", True, "EN", "TH", "Mistyped git checkout on TH in Notepad"),
        ("กพินหะ พีผ -ก -ย 8080:80 --ืฟทำ รำิ ทเรืป:ฟสยรืำ", True, "EN", "TH", "Mistyped docker on TH in Notepad"),
        ("ยรย รืหะฟสส --ียแปฟกำ ผีทยั ยฟืกฟห หแราระ-สำฟพน", True, "EN", "TH", "Mistyped pip install on TH in Notepad"),
        ("แีพส -ป ยแหะ ้ะะยห://ฟยร.หะพรยำ.แนท/อำ/แ้ฟพแปห", True, "EN", "TH", "Mistyped curl on TH in Notepad"),
        ("ืยท พีผ ิีรสก && ยท2 พำหะฟพะ ำแนะัหะำท.แนอดรแ.อย", True, "EN", "TH", "Mistyped npm build on TH in Notepad"),
        ("หียน หัหะำทแะส พำหะฟพะ ืเรืป.หำพอรแำ", True, "EN", "TH", "Mistyped sudo on TH in Notepad"),
        ("สำะ ิีดดำพ = นำไ ีรืะ8ฟพพฟั(1024);", True, "EN", "TH", "Mistyped let buffer on TH in Notepad"),
        ("กำด แฟสแีสฟะำ_ยืส(ำืะพั_ยพรแำ, ำประ_ยพรแำ, ษาั):", True, "EN", "TH", "Mistyped def pnl on TH in Notepad"),
        ("ีหำพห.ดรสะำพ(ี => ี.ฟแป >= 18 && ี.รหฟแะรอำ);", True, "EN", "TH", "Mistyped filter arrow on TH in Notepad"),
        ("แ้ทนก -พ 755 /อฟพ/ไไไ/้ะทส/หะนพฟแป", True, "EN", "TH", "Mistyped chmod on TH in Notepad"),
        ("ะฟพ -แนรอำ ิฟแาีย-2026-09-13.ะฟพ.แป /กฟะฟ/", True, "EN", "TH", "Mistyped tar on TH in Notepad"),
        ("แปพย -พื 'ะนกน' หพแ/แนะยนืำืะห/ | ไแ -ส", True, "EN", "TH", "Mistyped grep on TH in Notepad"),
        ("{\"รก\": 101, \"หาน\": \"ิะแ-ีหกะ\", \"รห_ฟแะรอำ\": ะพนี}", True, "EN", "TH", "Mistyped JSON on TH in Notepad"),
        ("ป = (ฟ + ิ) * (แ - ก) / 100.0;", True, "EN", "TH", "Mistyped math expr on TH in Notepad"),
        ("แแฟะ /ำะแ/ืเรืป/หระำห-ฟอฟรสฟิสำ/กำดฟีสะ", True, "EN", "TH", "Mistyped cat /etc/ on TH in Notepad"),
        ("แ:\\ไระกรไห\\หัหะำท32\\กพรอำพห\\ำะแ\\้แหะห", True, "EN", "TH", "Mistyped C:\\Windows on TH in Notepad"),
        ("หห้ -ร ~/.หห้/รก_พหฟ ีหำพ@192.168.1.50", True, "EN", "TH", "Mistyped ssh cmd on TH in Notepad"),
        ("ดรืก . -ืฟทำ '*.ยัแ' -กำสำะำ", True, "EN", "TH", "Mistyped find on TH in Notepad"),
    ]
    for text, exp_sw, exp_tgt, init_l, desc in code_in_general_apps:
        samples.append(
            StressSample(
                id=f"STRESS-CODE-GEN-{idx:03d}",
                category="Code in General Apps (Notepad/Slack)",
                description=desc,
                initial_layout=init_l,
                keystrokes=f"{text} ",
                expected_switch=exp_sw,
                expected_target=exp_tgt,
            )
        )
        idx += 1

    return samples


def run_stress_benchmark() -> Dict[str, Any]:
    """Executes the stress benchmark across all 4 paradigms."""
    samples = generate_stress_samples()
    print("=" * 96)
    print(" BRUTAL ADVERSARIAL STRESS BENCHMARK (REAL-WORLD EDGE CASES)")
    print(f" Total Hard / Adversarial Samples: N={len(samples)}")
    print(" Categories: Ultra-Short Ambiguity, Typo-on-Typo, Slang/Karaoke, Code in General Apps")
    print(" (Notice: Active window is set to 'notepad.exe' - Dev Tool immunity is OFF!)")
    print("=" * 96)

    fsa = PureFSABaseline()
    ngram = PureCharNGramBaseline()
    lex = HeuristicLexiconBaseline(use_installed_dict=True)
    cha = CoreEngine()

    models = [
        ("1. Pure Phonotactic FSA (Aroonmanakun 2002)", fsa),
        ("2. Pure Char N-Gram (Cavnar & Trenkle 1994)", ngram),
        ("3. Real RightLang (Installed 38,871 words)", lex),
        ("4. Proposed CHA (Our Architecture)", cha),
    ]

    results = []

    for name, sys_engine in models:
        is_cha = isinstance(sys_engine, CoreEngine)
        tp = fp = tn = fn = 0
        cat_metrics: Dict[str, Dict[str, int]] = {}

        for s in samples:
            cat = s.category
            if cat not in cat_metrics:
                cat_metrics[cat] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "total": 0}
            cat_metrics[cat]["total"] += 1

            sys_engine.set_layout(s.initial_layout)
            switched = False

            for ch in s.keystrokes:
                if is_cha:
                    act = sys_engine.process_key(ch, False, s.active_process)
                    if act.action_type == "AUTO_SWITCH":
                        switched = True
                        break
                else:
                    act_str = sys_engine.process_key(ch, False, s.active_process)
                    if act_str == "AUTO_SWITCH":
                        switched = True
                        break

            if s.expected_switch:
                if switched:
                    tp += 1
                    cat_metrics[cat]["tp"] += 1
                else:
                    fn += 1
                    cat_metrics[cat]["fn"] += 1
            else:
                if not switched:
                    tn += 1
                    cat_metrics[cat]["tn"] += 1
                else:
                    fp += 1
                    cat_metrics[cat]["fp"] += 1

        total = len(samples)
        acc = (tp + tn) / total * 100.0
        prec = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
        rec = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        fpr = (fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0

        results.append({
            "name": name,
            "total": total,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "fpr": fpr,
            "cat_metrics": cat_metrics,
        })

    # Print main table
    print(f"{'Methodology / Paradigm':<46} {'Accuracy':<9} {'Precision':<10} {'Recall':<9} {'F1-Score':<9} {'FPR':<7}")
    print("-" * 96)
    for r in results:
        print(
            f"{r['name']:<46} {r['accuracy']:5.1f}%   {r['precision']:5.1f}%    {r['recall']:5.1f}%   {r['f1']:5.1f}%   {r['fpr']:4.1f}%"
        )

    print("=" * 96)
    print(" BREAKDOWN BY ADVERSARIAL CATEGORY (Proposed CHA vs. Real RightLang)")
    print("=" * 96)
    cha_res = results[3]
    rl_res = results[2]

    categories = list(cha_res["cat_metrics"].keys())
    print(f"{'Adversarial Category':<40} {'CHA Acc / Rec':<18} {'RightLang Acc / Rec':<20}")
    print("-" * 96)
    for cat in categories:
        cm = cha_res["cat_metrics"][cat]
        rm = rl_res["cat_metrics"][cat]

        cha_acc = (cm["tp"] + cm["tn"]) / cm["total"] * 100.0
        rl_acc = (rm["tp"] + rm["tn"]) / rm["total"] * 100.0

        print(f"{cat:<40} {cha_acc:5.1f}% (TP={cm['tp']},FP={cm['fp']})   {rl_acc:5.1f}% (TP={rm['tp']},FP={rm['fp']})")

    print("=" * 96)
    return results


if __name__ == "__main__":
    run_stress_benchmark()
