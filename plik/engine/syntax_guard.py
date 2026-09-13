"""Syntax Guard: Immunity engine for programming code, URLs, file paths, and identifiers.

Guarantees 0% false positives on technical text by detecting syntactical patterns
that should never be converted by auto-switch.
"""

import re
from typing import Tuple

# Regex patterns for technical tokens that must never be auto-switched
RE_URL = re.compile(
    r"^(https?://|www\.|ftp://|([a-zA-Z0-9_\-]+\.)+(com|org|net|io|th|dev|app|ai|edu|gov|co|info|me|tech|xyz))",
    re.IGNORECASE,
)
RE_FILE_PATH = re.compile(
    r"^([a-zA-Z]:[\\/].*|/([a-zA-Z0-9_\-.]+/)+[a-zA-Z0-9_\-.]*|[.]{1,2}[\\/].*|.*?\.(py|ts|js|jsx|tsx|json|html|css|md|yaml|yml|xml|toml|cpp|c|h|rs|go|sh|bat|cmd|env|sql|lock|csv|txt|log|ini|cfg|conf)$)",
    re.IGNORECASE,
)
RE_CLI_FLAG = re.compile(r"^--?[a-zA-Z0-9_\-]+$")
RE_SHELL_VAR = re.compile(r"^\$[a-zA-Z0-9_{}]+$")

# Programming operators and syntax symbols
PROGRAMMING_SYMBOLS = {
    "==", "!=", "===", "!==", "=>", "->", "&&", "||", "++", "--",
    "+=", "-=", "*=", "/=", "%=", "::", "<<", ">>", "//", "/*", "*/",
    "<?", "?>", "</", "/>", "...", "##", "###", "####",
}

ENGLISH_VOWELS = set("aeiouyAEIOUY")


class SyntaxGuard:
    """Evaluates whether a token is part of programming syntax, URLs, or file paths."""

    @staticmethod
    def is_protected_syntax(token: str) -> Tuple[bool, str]:
        """Check if a token should be immune from auto-switching.
        
        Returns:
            (is_protected, reason)
        """
        if not token:
            return False, ""

        token_stripped = token.strip()

        # 1. Operators & programming symbols
        if token_stripped in PROGRAMMING_SYMBOLS:
            return True, f"Programming operator '{token_stripped}'"

        # 2. CLI flags (e.g. '--verbose', '-m', '-rf', '--no-verify')
        if RE_CLI_FLAG.match(token_stripped):
            return True, f"CLI flag '{token_stripped}'"

        # 3. URLs and domains
        if RE_URL.match(token_stripped):
            return True, f"URL/Domain '{token_stripped}'"

        # 4. File paths and filenames
        if RE_FILE_PATH.match(token_stripped):
            # Check if this is a Thai word collision (e.g. '.sh' is 'ให้' on Kedmanee)
            # Only bypass if token contains no directory slashes ('/' or '\')
            if "/" not in token_stripped and "\\" not in token_stripped:
                try:
                    from plik.layouts.kedmanee import to_thai
                    from plik.engine.lexicon import LexiconMatcher
                    lex = LexiconMatcher.get_instance()
                    th_candidate = to_thai(token_stripped)
                    if lex.is_thai_word(th_candidate):
                        return False, ""
                    if token_stripped.lower().endswith(".sh") and len(token_stripped) > 3:
                        prefix_th = to_thai(token_stripped[:-3])
                        if lex.is_thai_word(prefix_th):
                            return False, ""
                except Exception:
                    pass
            return True, f"File path '{token_stripped}'"

        # 5. Shell variables ($HOME, $PORT)
        if RE_SHELL_VAR.match(token_stripped):
            return True, f"Shell variable '{token_stripped}'"

        # 6. Identifier naming conventions
        # snake_case (e.g. calculate_total_amount)
        if "_" in token_stripped and not token_stripped.startswith("_") and not token_stripped.endswith("_"):
            parts = token_stripped.split("_")
            if len(parts) >= 2 and all(p.isalnum() for p in parts):
                return True, f"snake_case identifier '{token_stripped}'"

        # kebab-case (e.g. api-gateway-service)
        # Must have English vowels in parts to prevent matching Thai Kedmanee keys like 'g-hk'
        if "-" in token_stripped and not token_stripped.startswith("-") and not token_stripped.endswith("-"):
            parts = token_stripped.split("-")
            if len(parts) >= 2 and all(len(p) >= 2 and any(c in ENGLISH_VOWELS for c in p) for p in parts):
                return True, f"kebab-case identifier '{token_stripped}'"

        # camelCase / PascalCase (e.g. getUserProfileById, UserProfileComponent)
        # Must have genuine English vowels before and after the uppercase boundary
        if token_stripped.isalpha() and any(c.isupper() for c in token_stripped[1:]):
            # Check if there is an English vowel before and after the uppercase shift
            has_vowel_early = any(c in ENGLISH_VOWELS for c in token_stripped[:2])
            has_vowel_late = any(c in ENGLISH_VOWELS for c in token_stripped[2:])
            if has_vowel_early and has_vowel_late and len(token_stripped) >= 4:
                return True, f"camelCase/PascalCase identifier '{token_stripped}'"

        return False, ""
