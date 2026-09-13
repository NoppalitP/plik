"""Unit tests for SyntaxGuard immunity engine."""

import pytest
from plik.engine.syntax_guard import SyntaxGuard


def test_urls_protected():
    urls = [
        "https://github.com/project",
        "http://localhost:8000",
        "www.google.co.th",
        "example.com",
        "api.binance.com",
    ]
    for url in urls:
        protected, reason = SyntaxGuard.is_protected_syntax(url)
        assert protected, f"Expected '{url}' to be protected. Reason: {reason}"


def test_file_paths_protected():
    paths = [
        "C:\\Users\\admin\\file.txt",
        "/etc/nginx/nginx.conf",
        "./src/engine/core.py",
        "../models/weights.json",
        "docker-compose.yml",
        "data.csv",
    ]
    for path in paths:
        protected, reason = SyntaxGuard.is_protected_syntax(path)
        assert protected, f"Expected '{path}' to be protected. Reason: {reason}"


def test_code_identifiers_protected():
    identifiers = [
        "calculate_total_amount",
        "user_id",
        "getUserProfileById",
        "UserProfileComponent",
        "api-gateway-service",
    ]
    for ident in identifiers:
        protected, reason = SyntaxGuard.is_protected_syntax(ident)
        assert protected, f"Expected '{ident}' to be protected. Reason: {reason}"


def test_programming_operators_protected():
    ops = ["===", "!==", "=>", "->", "&&", "||", "++", "--", "+="]
    for op in ops:
        protected, reason = SyntaxGuard.is_protected_syntax(op)
        assert protected, f"Expected '{op}' to be protected. Reason: {reason}"


def test_thai_words_not_accidentally_protected():
    # 'g-hk' is 'เข้า' in Kedmanee; it should NOT be protected as a kebab-case identifier
    protected, _ = SyntaxGuard.is_protected_syntax("g-hk")
    assert not protected, "Thai typo 'g-hk' should not be protected by SyntaxGuard"
