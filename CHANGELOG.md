# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-14

### Added
- **Cascaded Hybrid Architecture (CHA)**: Multi-tiered evaluation engine combining Syntax Guard, Deterministic Rules, Dual-Lexicon Dictionary Trie (511,076 words), and Bigram Transition Probabilities.
- **Ultra-Fast 0ms Auto-Switch**: Instant bilingual Thai-English keyboard conversion upon space delimiter.
- **Bilingual Auto-Correct**: Built-in instant correction for 150+ common Thai typos and 100+ English typos with case-preservation.
- **Developer Tool Immunity**: Code Guard ignores commands in developer environments (VS Code, terminals, cmd, PowerShell).
- **Instant Undo**: Single backspace keystroke immediately restores the original untranslated input.
- **System Tray Application**: Silent background execution with neon emerald (active) and amber (paused) status icons.
- **Run on Windows Startup**: One-click registration in Windows Registry for auto-boot.
- **CI/CD Workflows**: Automated test matrix across Python 3.11, 3.12, and 3.13 on `windows-latest`.
- **Modern Showcase Website**: Interactive React + Vite + Tailwind + Framer Motion web app with 3D mechanical keyboard playground and productivity savings calculator.
