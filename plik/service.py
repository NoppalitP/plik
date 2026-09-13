"""CLI service and test harness for Smart Keyboard."""

import argparse
import sys
import time
from typing import List, Tuple

from plik.config import SwitcherConfig
from plik.engine.core import CoreEngine, SwitchAction
from plik.engine.app_context import AppCategory


def run_benchmark() -> bool:
    """Run evaluation benchmark across typical mixed-typing scenarios."""
    print("=" * 65)
    print(" Smart Keyboard Engine - Accuracy & Performance Benchmark")
    print("=" * 65)

    test_cases = [
        # (typed_text, initial_layout, active_process, expected_action, expected_target_layout, description)
        ("d;y ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "Thai 'วัน' on QWERTY"),
        ("c[[ ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "Thai 'แบบ' on QWERTY"),
        ("l;ylfu ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "Thai 'สวัสดี' on QWERTY"),
        ("4kKk ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "Thai 'ภาษา' on QWERTY"),
        ("gmLk ", "EN", "chrome.exe", "AUTO_SWITCH", "TH", "Thai 'เทศา' on QWERTY"),
        ("ฟยยสำ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "English 'apple' on Thai Kedmanee"),
        ("ะำหะ ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "English 'test' on Thai Kedmanee"),
        ("ิพำฟk ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "English 'break' on Thai Kedmanee"),
        ("ัำห ", "TH", "chrome.exe", "AUTO_SWITCH", "EN", "English 'yes' on Thai Kedmanee"),
        # Developer protection test cases: Must NOT switch in VS Code or Terminal!
        ("git status ", "EN", "code.exe", "NONE", "", "Git command in VS Code (Protected)"),
        ("docker ps ", "EN", "windowsterminal.exe", "NONE", "", "Docker command in Terminal (Protected)"),
        ("npm run dev ", "EN", "powershell.exe", "NONE", "", "NPM command in PowerShell (Protected)"),
        ("def main(): ", "EN", "code.exe", "NONE", "", "Python function in VS Code (Protected)"),
        # Protected slang/acronyms in normal apps
        ("555 ", "EN", "line.exe", "NONE", "", "Thai slang '555' preserved"),
        ("krub ", "EN", "line.exe", "NONE", "", "Thai romanized 'krub' preserved"),
        ("api ", "EN", "chrome.exe", "NONE", "", "Tech acronym 'api' preserved"),
    ]

    engine = CoreEngine()
    passed = 0
    total = len(test_cases)
    total_time_us = 0.0

    print(f"{'Input':<15} {'Layout':<6} {'App':<18} {'Expected':<12} {'Result':<12} {'Status':<6}")
    print("-" * 75)

    for text, layout, proc, exp_action, exp_target, desc in test_cases:
        engine.set_layout(layout)
        # Clear buffer
        engine._current_token = ""

        start = time.perf_counter()
        action = SwitchAction(action_type="NONE")
        for ch in text:
            act = engine.process_key(ch, is_backspace=False, active_process=proc)
            if act.action_type != "NONE":
                action = act
        elapsed_us = (time.perf_counter() - start) * 1_000_000
        total_time_us += elapsed_us

        # Verification
        ok = False
        if exp_action == "NONE" and action.action_type == "NONE":
            ok = True
        elif action.action_type == exp_action and (not exp_target or action.target_layout == exp_target):
            ok = True

        status_str = "PASS" if ok else "FAIL"
        if ok:
            passed += 1

        print(
            f"{text.strip():<15} {layout:<6} {proc:<18} {exp_action:<12} {action.action_type:<12} {status_str:<6}"
        )

    print("-" * 75)
    accuracy = (passed / total) * 100.0
    avg_latency_us = total_time_us / total

    print(f"Passed: {passed}/{total} ({accuracy:.1f}%)")
    print(f"Average Evaluation Latency: {avg_latency_us:.1f} microseconds per word")

    # Test Instant Undo
    print("\nVerifying Instant Undo State Machine...")
    engine.set_layout("EN")
    # Type 'c[[' which converts to 'แบบ' (TH)
    engine.process_key("c", active_process="chrome.exe")
    engine.process_key("[", active_process="chrome.exe")
    act1 = engine.process_key("[", active_process="chrome.exe")
    print(f"  Step 1: Typed 'c[[' -> Auto-switch to: {act1.replacement_text} ({act1.target_layout})")

    # Now simulate pressing Backspace immediately
    undo_act = engine.process_key("", is_backspace=True, active_process="chrome.exe")
    print(f"  Step 2: Pressed Backspace -> Action: {undo_act.action_type}, Restored: '{undo_act.replacement_text}' ({undo_act.target_layout})")

    undo_ok = (
        undo_act.action_type == "INSTANT_UNDO"
        and undo_act.replacement_text == "c[["
        and undo_act.target_layout == "EN"
    )
    print(f"  Instant Undo Status: {'PASS' if undo_ok else 'FAIL'}")

    return passed == total and undo_ok


def run_interactive() -> None:
    """Interactive typing simulator in console."""
    print("=" * 65)
    print(" Smart Keyboard - Interactive Typing Simulation")
    print(" Type characters and observe real-time switching decisions.")
    print(" Type ':q' to exit, ':bs' to simulate Backspace, ':m' to manual convert.")
    print("=" * 65)

    engine = CoreEngine()
    current_app = "chrome.exe"
    print(f"Current App Profile: {current_app} (Type ':app <name>' to change)")
    print(f"Current Layout: {engine.current_layout}\n")

    while True:
        try:
            line = input(f"[{engine.current_layout} | buffer='{engine.current_token}']> ")
        except (KeyboardInterrupt, EOFError):
            break

        if line == ":q":
            break
        elif line == ":bs":
            act = engine.process_key("", is_backspace=True, active_process=current_app)
            if act.action_type != "NONE":
                print(f"  >> [{act.action_type}] Restored: '{act.replacement_text}' (Layout: {act.target_layout}) Reason: {act.reason}")
            continue
        elif line == ":m":
            act = engine.manual_convert()
            print(f"  >> [{act.action_type}] Converted: '{act.original_text}' -> '{act.replacement_text}' (Layout: {act.target_layout})")
            continue
        elif line.startswith(":app "):
            current_app = line.split(" ", 1)[1].strip()
            print(f"  >> Active app changed to: {current_app}")
            continue

        for ch in line:
            act = engine.process_key(ch, is_backspace=False, active_process=current_app)
            if act.action_type != "NONE":
                print(f"  >> [{act.action_type}] '{act.original_text}' -> '{act.replacement_text}' (New Layout: {act.target_layout})")
                print(f"     Confidence: {act.confidence:.2f} | Reason: {act.reason}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Keyboard Switcher Service")
    parser.add_argument("--benchmark", action="store_true", help="Run accuracy & performance benchmark")
    parser.add_argument("--interactive", action="store_true", help="Interactive typing simulator")
    args = parser.parse_args()

    if args.benchmark:
        success = run_benchmark()
        sys.exit(0 if success else 1)
    elif args.interactive:
        run_interactive()
    else:
        # Default to benchmark if no args specified
        run_benchmark()


if __name__ == "__main__":
    main()
