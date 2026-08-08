# Paper Notes

## SWE-Cycle

Used for the full lifecycle structure: environment detection, reproduction, patching, verification, and reporting.

## Phoenix

Used for the multi-agent breakdown: planner, reproducer, coder, tester, and PR/report agent.

## AgentVisor

Used as inspiration for tool privilege boundaries. In v1, this is implemented as command allow-listing, blocked risky command tokens, prompt-injection checks, and secret scanning.

## AgentLeak

Used as inspiration for trace leakage auditing. In v1, the auditor scans logs and trace events for emails, private local paths, and secret-like values.

## What This Project Does Not Claim

- It does not claim SWE-bench benchmark results.
- It does not execute untrusted repositories with production-grade isolation.
- It does not guarantee that every generated patch is semantically correct.
