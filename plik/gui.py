"""Modern Dark-Themed GUI Control Panel for Smart Keyboard.

Features:
- Real-time status display (ACTIVE / PAUSED).
- Live conversion log showing detected switches and instant undos.
- One-click detection and graceful termination of conflicting RightLang instances.
- Background worker thread hosting the Windows WH_KEYBOARD_LL hook.
"""

import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from plik.live_service import LiveKeyboardService


class SmartKeyboardGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Keyboard - CHA Engine (Auto Layout Switcher)")
        self.root.geometry("560x480")
        self.root.minsize(500, 400)
        self.root.configure(bg="#1e1e2e")

        # Style colors (Catppuccin Mocha theme)
        self.BG_DARK = "#1e1e2e"
        self.BG_PANEL = "#181825"
        self.BG_INPUT = "#313244"
        self.FG_TEXT = "#cdd6f4"
        self.FG_MUTED = "#a6adc8"
        self.COLOR_GREEN = "#a6e3a1"
        self.COLOR_YELLOW = "#f9e2af"
        self.COLOR_RED = "#f38ba8"
        self.COLOR_BLUE = "#89b4fa"

        self.service: Optional[LiveKeyboardService] = None
        self.service_thread: Optional[threading.Thread] = None

        self._build_ui()
        self._check_rightlang_conflict()
        self._start_service()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg=self.BG_PANEL, pady=12, padx=16)
        header_frame.pack(fill="x")

        title_lbl = tk.Label(
            header_frame,
            text="⚡ SMART KEYBOARD",
            font=("Segoe UI", 14, "bold"),
            fg=self.COLOR_BLUE,
            bg=self.BG_PANEL,
        )
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(
            header_frame,
            text="Cascaded Hybrid Architecture (CHA)",
            font=("Segoe UI", 9),
            fg=self.FG_MUTED,
            bg=self.BG_PANEL,
        )
        subtitle_lbl.pack(side="left", padx=10, pady=(4, 0))

        # Status Badge
        self.status_badge = tk.Label(
            header_frame,
            text="🟢 ACTIVE",
            font=("Segoe UI", 10, "bold"),
            fg=self.COLOR_GREEN,
            bg="#24273a",
            padx=10,
            pady=4,
            relief="flat",
        )
        self.status_badge.pack(side="right")

        # RightLang Warning Banner (Hidden by default)
        self.warning_frame = tk.Frame(self.root, bg="#451a24", padx=12, pady=8)
        self.warning_lbl = tk.Label(
            self.warning_frame,
            text="⚠️ ตรวจพบ RightLang กำลังรันอยู่ อาจทำให้การดักปุ่มตีกัน",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_RED,
            bg="#451a24",
        )
        self.warning_lbl.pack(side="left")
        self.btn_kill_rl = tk.Button(
            self.warning_frame,
            text="ปิด RightLang ทันที",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_RED,
            fg="#11111b",
            activebackground="#eba0ac",
            relief="flat",
            command=self._kill_rightlang,
            padx=8,
            pady=2,
            cursor="hand2",
        )
        self.btn_kill_rl.pack(side="right")

        # Main Info & Controls Frame
        ctrl_frame = tk.Frame(self.root, bg=self.BG_DARK, padx=16, pady=10)
        ctrl_frame.pack(fill="x")

        # Action Buttons
        self.btn_pause = tk.Button(
            ctrl_frame,
            text="⏸ พักการทำงาน (Pause)",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLOR_YELLOW,
            fg="#11111b",
            activebackground="#f9e2af",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._toggle_pause,
        )
        self.btn_pause.pack(side="left")

        self.btn_clear = tk.Button(
            ctrl_frame,
            text="🧹 ล้างประวัติ (Clear)",
            font=("Segoe UI", 9),
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            activebackground="#45475a",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._clear_log,
        )
        self.btn_clear.pack(side="left", padx=10)

        # Feature badges
        feat_frame = tk.Frame(self.root, bg=self.BG_PANEL, padx=16, pady=8)
        feat_frame.pack(fill="x", padx=16, pady=(0, 10))

        badges = [
            ("🛡️ Asymmetric Dev Protection", self.COLOR_GREEN),
            ("⚡ Instant Undo (Backspace)", self.COLOR_BLUE),
            ("🔒 SyntaxGuard (Code/URL Safe)", self.COLOR_YELLOW),
        ]
        for text, color in badges:
            b_lbl = tk.Label(
                feat_frame,
                text=text,
                font=("Segoe UI", 8, "bold"),
                fg=color,
                bg=self.BG_PANEL,
            )
            b_lbl.pack(side="left", padx=8)

        # Live Log Section
        log_label = tk.Label(
            self.root,
            text="ประวัติการสลับภาษาแบบเรียลไทม์ (Live Conversion History):",
            font=("Segoe UI", 9, "bold"),
            fg=self.FG_MUTED,
            bg=self.BG_DARK,
        )
        log_label.pack(anchor="w", padx=16)

        list_container = tk.Frame(self.root, bg=self.BG_DARK, padx=16, pady=4)
        list_container.pack(fill="both", expand=True)

        self.log_listbox = tk.Listbox(
            list_container,
            bg=self.BG_PANEL,
            fg=self.FG_TEXT,
            selectbackground="#45475a",
            selectforeground="#ffffff",
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#313244",
        )
        self.scrollbar = tk.Scrollbar(
            list_container, orient="vertical", command=self.log_listbox.yview, bg=self.BG_DARK
        )
        self.log_listbox.config(yscrollcommand=self.scrollbar.set)

        self.log_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bottom Bar
        bottom_frame = tk.Frame(self.root, bg=self.BG_PANEL, pady=6, padx=16)
        bottom_frame.pack(fill="x", side="bottom")

        hint_lbl = tk.Label(
            bottom_frame,
            text="Tip: กดปุ่ม 'Pause/Break' บนคีย์บอร์ดเพื่อ Pause/Resume ได้ตลอดเวลา",
            font=("Segoe UI", 8),
            fg=self.FG_MUTED,
            bg=self.BG_PANEL,
        )
        hint_lbl.pack(side="left")

    def _check_rightlang_conflict(self):
        """Checks if rightlang.exe is running and displays a warning banner."""
        try:
            output = subprocess.check_output(
                'tasklist /FI "IMAGENAME eq rightlang.exe" /NH', shell=True, text=True
            )
            if "rightlang.exe" in output.lower():
                self.warning_frame.pack(fill="x", pady=(0, 4))
            else:
                self.warning_frame.pack_forget()
        except Exception:
            pass

    def _kill_rightlang(self):
        """Gracefully or forcefully closes rightlang.exe."""
        try:
            subprocess.run("taskkill /IM rightlang.exe /F", shell=True, check=True)
            self.warning_frame.pack_forget()
            self._log_entry("[SYSTEM] ปิด RightLang สำเร็จเรียบร้อยแล้ว")
            messagebox.showinfo("สำเร็จ", "ปิด RightLang เรียบร้อยแล้ว ตอนนี้ Smart Keyboard ทำงานได้เต็ม 100%")
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถปิด RightLang ได้: {e}")

    def _start_service(self):
        """Starts LiveKeyboardService in a background thread."""
        self.service = LiveKeyboardService(
            on_switch_callback=self._on_switch_event,
            on_status_callback=self._on_status_event,
        )

        def run_thread():
            self.service.start()

        self.service_thread = threading.Thread(target=run_thread, daemon=True)
        self.service_thread.start()

        def verify_startup():
            time.sleep(0.3)
            if self.service and self.service._hook:
                self.root.after(0, lambda: self._log_entry(f"[SYSTEM] ติดตั้ง Keyboard Hook สำเร็จ (ID: {self.service._hook}) พร้อมพิมพ์ได้ทันที!"))
            else:
                self.root.after(0, lambda: self._log_entry("[WARNING] กำลังรอการเชื่อมต่อ Hook..."))

        threading.Thread(target=verify_startup, daemon=True).start()

    def _on_switch_event(self, act_type: str, orig: str, repl: str, target_layout: str, proc: str):
        """Thread-safe callback from the keyboard hook."""
        now_str = time.strftime("%H:%M:%S")
        if act_type == "AUTO_SWITCH":
            entry = f"[{now_str}] 🔄 AUTO-SWITCH: '{orig}' ➜ '{repl}' ({target_layout}) | {proc}"
        elif act_type == "INSTANT_UNDO":
            entry = f"[{now_str}] ⏪ INSTANT-UNDO: คืนค่าเดิม '{repl}' ({target_layout}) | {proc}"
        else:
            entry = f"[{now_str}] {act_type}: {orig} ➜ {repl}"

        self.root.after(0, lambda: self._log_entry(entry))

    def _on_status_event(self, is_paused: bool):
        """Thread-safe status update callback."""
        self.root.after(0, lambda: self._update_status_ui(is_paused))

    def _update_status_ui(self, is_paused: bool):
        if is_paused:
            self.status_badge.config(text="🟡 PAUSED", fg=self.COLOR_YELLOW)
            self.btn_pause.config(text="▶ ทำงานต่อ (Resume)", bg=self.COLOR_GREEN)
            self._log_entry("[STATUS] พักการทำงาน (PAUSED)")
        else:
            self.status_badge.config(text="🟢 ACTIVE", fg=self.COLOR_GREEN)
            self.btn_pause.config(text="⏸ พักการทำงาน (Pause)", bg=self.COLOR_YELLOW)
            self._log_entry("[STATUS] กลับมาทำงาน (ACTIVE)")

    def _toggle_pause(self):
        if self.service:
            is_paused = self.service.toggle_pause()
            self._update_status_ui(is_paused)

    def _clear_log(self):
        self.log_listbox.delete(0, tk.END)

    def _log_entry(self, text: str):
        self.log_listbox.insert(tk.END, f" {text}")
        self.log_listbox.see(tk.END)

    def on_close(self):
        if self.service:
            self.service.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SmartKeyboardGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
