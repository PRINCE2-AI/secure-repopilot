# Buggy Python Repo

Small deterministic demo repository for Secure RepoPilot.

Known issue:

`divide(a, b)` raises `ZeroDivisionError` when `b == 0`. The desired behavior is to return `None`.

Run tests:

```bash
python -m unittest discover -s tests
```
