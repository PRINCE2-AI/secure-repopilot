# Architecture

Secure RepoPilot implements a full-cycle coding-agent loop:

```text
Issue -> Repo Analyzer -> Planner -> Reproducer -> Patcher -> Tester -> Safety Guard -> Privacy Auditor -> Judge -> PR Report
```

The central design decision is baseline-aware verification. A patch is not considered good just because code changed. The agent compares baseline and patched test results, then produces a judge verdict.

## Components

| Component | Role |
| --- | --- |
| `repo_analyzer.py` | Detects language, dependencies, test commands, and important files |
| `issue_intake.py` | Parses local issue text or GitHub issue URLs |
| `planner.py` | Creates suspected-file and verification plan |
| `reproducer.py` | Runs baseline commands to reproduce failure |
| `patcher.py` | Applies deterministic patch rules and produces diffs |
| `tester.py` | Runs commands with timeout and captures output |
| `security_guard.py` | Blocks risky commands and scans for secrets/prompt injection |
| `privacy_auditor.py` | Detects leakage in traces |
| `judge.py` | Produces final verdict and confidence |
| `report_writer.py` | Generates PR-ready markdown |

## Production Gaps

V1 uses lightweight local execution. A production system should run every repository in a container, apply network controls, isolate secrets, record full provenance, and require explicit approval before writing to remote GitHub.
