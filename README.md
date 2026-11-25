# Automated NIST NICE Framework Mapping Engine

> **Client-Side & CLI Competency Alignment against NIST SP 800-181 Rev 1 (v2.2.0)**

Live Web Application: **[teddymwai.github.io/nice-framework-mapper](https://teddymwai.github.io/nice-framework-mapper/)**

---

## Overview

Cybersecurity drills, scenario assessments, and workforce readiness evaluations require measurable alignment with industry standards. Manually categorizing hundreds of hands-on simulation questions and telemetry artifacts against the NIST NICE Task, Knowledge, and Skill (TKS) taxonomy is slow and produces inconsistent mappings across authors.

This repository provides both:
1. **Zero-Backend GitHub Pages Web App (`index.html`)**: Runs 100% in the browser over 2,211 embedded NIST NICE TKS statements, supporting drag-and-drop `.csv` / `.xlsx` upload, configurable competences per question (2–5), statement reuse caps, and instant CSV/XLSX export.
2. **Deterministic Python CLI (`nice_mapper.py`)**: Maps scenario telemetry JSON artifacts or assessment question CSVs using TF-IDF cosine similarity against the normalized `data/nice_tks_v2_2_0.json` dictionary.

---

## NIST NICE v2.2.0 Reference Sources

`data/nice_tks_v2_2_0.json` normalizes 2,211 Task, Knowledge, and Skill statements from the official NIST NICE Framework v2.2.0 (`v2-2-0_nf_components.json`):

- **NICE Framework Current Versions**: https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions
- **Components JSON (v2.2.0)**: https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/v2-2-0_nf_components.json
- **Components XLSX (v2.2.0)**: https://www.nist.gov/document/nice-framework-components-v220
- **NICCS Online Framework**: https://niccs.cisa.gov/tools/nice-framework
- **NIST SP 800-181 Rev 1 Publication**: https://csrc.nist.gov/pubs/sp/800/181/r1/final
- **NIST CPRT Catalog (NICE v2.2.0)**: https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/NICE_2_2_0/home

---

## Architecture

```text
  [ Scenario Telemetry (.json) / Assessment Questions (.csv, .xlsx) ]
                                 │
                                 ▼
                  [ Tokenizer & Stopword Filter ]
                                 │
                                 ▼
        [ TF-IDF Index over 2,211 NIST NICE TKS Statements ]
                                 │
                                 ▼
         [ Cosine Similarity + Per-Statement Reuse Cap (2/2) ]
                                 │
                                 ▼
            [ Deterministic JSON / CSV / XLSX Output ]
```

---

## Quick Start (Python CLI)

Requires Python 3.10+ (standard library only).

```bash
# Map a scenario telemetry JSON artifact
python3 nice_mapper.py --input samples/soc_triage_04.json --per-item 3

# Map an assessment question CSV and export results
python3 nice_mapper.py --input samples/sample_questions.csv --per-item 3 --output mapped_results.csv

# Run offline self-test and unit tests
python3 nice_mapper.py --selftest
python3 -m unittest discover -s tests -v
```

---

## Engineering Harness & Security Verification

This repository is aligned with the **Antigravity Core Template**:
- **Agent Rules & Skills**: `.agents/rules/` and `.agents/skills/`
- **Project Constitutions**: [AGENTS.md](AGENTS.md), [GEMINI.md](GEMINI.md), [HARNESS.md](HARNESS.md)
- **Release Governance**: [CHANGELOG.md](CHANGELOG.md), [docs/RELEASE_REGISTER.md](docs/RELEASE_REGISTER.md), [docs/UPCOMING_FEATURES.md](docs/UPCOMING_FEATURES.md)
- **Git Hooks**: `tools/git_hooks/pre-commit` and `tools/git_hooks/pre-push` (linked into `.git/hooks/`)

```bash
# Pre-commit syntax & TedRedCraft Tier 1 SAST
python3 -m compileall -q .
PYTHONPATH=/Users/ted/Development/TedRedCraft python3 -m redcraft audit --mode pre-commit --target .
```

---

## Web Application (GitHub Pages)

Open the live tool at **[https://teddymwai.github.io/nice-framework-mapper/](https://teddymwai.github.io/nice-framework-mapper/)** or open `index.html` locally in any modern browser:

1. Upload a `.csv` or `.xlsx` file (first column = question text, up to 45 rows) or download the built-in CSV template.
2. Adjust competences per question (`2` to `5`).
3. Run mapping to inspect confidence tiers (`strong`, `moderate`, `weak`), category coverage (`Task`, `Skill`, `Knowledge`), and export to CSV or XLSX.

---

## Repository Structure

```text
nice-framework-mapper/
├── index.html                  # Zero-backend browser TKS Mapper (GitHub Pages entry)
├── nice_mapper.py              # Standalone Python CLI mapper
├── data/
│   └── nice_tks_v2_2_0.json    # 2,211 normalized NIST SP 800-181 Rev 1 TKS statements
├── samples/
│   ├── soc_triage_04.json      # Synthetic scenario telemetry artifact
│   └── sample_questions.csv    # Sample assessment questions
├── LICENSE                     # MIT License
└── README.md
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
