"""Test for Gentle Cycle and cotoe.sh -> แนะนำให้ conversion."""

import pytest
from plik.engine.core import CoreEngine
from plik.layouts.kedmanee import to_thai, to_english


def test_cotoe_sh_converts_to_thai():
    """Verify 'cotoe.sh' converts directly to 'แนะนำให้' without syntax guard blocking."""
    engine = CoreEngine()
    engine.set_layout('EN')

    # In-flight typing:
    for ch in 'cotoe':
        act = engine.process_key(ch, is_backspace=False, active_process='notepad.exe')
    assert act.action_type == 'AUTO_SWITCH'
    assert act.replacement_text == 'แนะนำ'
    assert act.target_layout == 'TH'

    # Single token evaluation:
    engine.set_layout('EN')
    act_single = engine._evaluate_token('cotoe.sh', is_delimiter=True)
    assert act_single.action_type == 'AUTO_SWITCH'
    assert act_single.replacement_text == 'แนะนำให้'
    assert act_single.target_layout == 'TH'


def test_gentle_cycle_colon_converts_to_english():
    """Verify '(Gentle' and 'Cycle):' conversion."""
    engine = CoreEngine()
    engine.set_layout('TH')

    # (Gentle in Thai Kedmanee keys
    act1 = engine._evaluate_token('๖ฌำืะสำ', is_delimiter=True)
    assert act1.action_type == 'AUTO_SWITCH'
    assert act1.replacement_text == '(Gentle'
    assert act1.target_layout == 'EN'

    # Cycle): in Thai Kedmanee keys
    engine.set_layout('TH')
    act2 = engine._evaluate_token('ฉัแสำ๗ซ', is_delimiter=True)
    assert act2.action_type == 'AUTO_SWITCH'
    assert act2.replacement_text == 'Cycle):'
    assert act2.target_layout == 'EN'


def test_thai_words_ending_in_hai_not_blocked_by_syntax_guard():
    """Ensure Thai words ending in .sh (ให้) are never blocked as shell script file paths."""
    from plik.engine.syntax_guard import SyntaxGuard
    sg = SyntaxGuard()

    # Real shell scripts must still be protected
    assert sg.is_protected_syntax('deploy.sh')[0] is True
    assert sg.is_protected_syntax('./run.sh')[0] is True
    assert sg.is_protected_syntax('scripts/build.sh')[0] is True

    # Thai words ending in .sh must NOT be protected
    assert sg.is_protected_syntax('cotoe.sh')[0] is False  # แนะนำให้
    assert sg.is_protected_syntax('g-hk.sh')[0] is False   # เข้าให้
    assert sg.is_protected_syntax('.sh')[0] is False       # ให้
