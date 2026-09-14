# Contributing to Plik (คู่มือการมีส่วนร่วมพัฒนา)

ขอบคุณที่สนใจร่วมพัฒนา **Plik (พลิก)**! เรายินดีต้อนรับการมีส่วนร่วมจากทุกคน ไม่ว่าจะเป็นการรายงานบั๊ก เสนอแนะคำศัพท์ใหม่ หรือการส่ง Pull Request

---

## 🛠️ การติดตั้งสภาพแวดล้อมเพื่อพัฒนา (Development Setup)

### สิ่งที่ต้องเตรียม:
* **Windows 10 / 11** (เนื่องจากระบบใช้ Windows Low-Level Hook API)
* **Python 3.10+** (แนะนำ 3.11 หรือ 3.13)
* **Git**

### ขั้นตอน:
1. Fork repository นี้ไปยังบัญชี GitHub ของคุณ
2. Clone repository:
   ```powershell
   git clone https://github.com/<your-username>/plik.git
   cd plik
   ```
3. สร้าง Virtual Environment และติดตั้ง dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

---

## 🧪 การรันชุดทดสอบ (Testing)

ก่อนส่ง Pull Request ทุกครั้ง ชุดทดสอบต้องผ่านทั้งหมด 100%:

```powershell
pytest tests -v --durations=10
```

> [!IMPORTANT]
> **Privacy Invariant**: โปรแกรม Plik ต้องทำงานแบบ **100% Offline** เสมอ ห้ามเพิ่มไลบรารีหรือฟังก์ชันที่มีการส่งข้อมูลผ่านเครือข่ายอินเทอร์เน็ตโดยเด็ดขาด

---

## 💡 แนวทางการเพิ่มคำศัพท์ / คำผิด (Vocabulary Contributions)

* หากต้องการเพิ่มคำภาษาไทย: แก้ไขที่ `plik/data/thai.txt` (เรียงตามตัวอักษร)
* หากต้องการเพิ่มคำภาษาอังกฤษ: แก้ไขที่ `plik/data/eng.txt`
* หากต้องการเพิ่มคู่คำแก้คำผิดยอดฮิต: แก้ไขที่ `plik/engine/rules.py` ในส่วน `THAI_TYPO_PAIRS` หรือ `ENGLISH_TYPO_PAIRS` พร้อมเพิ่ม unit test ใน `tests/test_autocorrect.py`

---

## 🚀 การส่ง Pull Request (PR)

1. สร้าง branch ใหม่จาก `main`:
   ```powershell
   git checkout -b feature/your-feature-name
   ```
2. Commit การเปลี่ยนแปลงด้วยข้อความที่ชัดเจน (แนะนำ Conventional Commits เช่น `feat: ...`, `fix: ...`, `docs: ...`)
3. Push ไปยัง Fork ของคุณ และเปิด Pull Request บน GitHub
