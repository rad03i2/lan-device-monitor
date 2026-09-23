# Contributing

Contributions are welcome when they keep the project small, local-first, cross-platform, and safe.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and avoid unnecessary runtime dependencies.
3. Install development requirements with `python -m pip install -e . pytest`.
4. Run `python -m compileall -q src` and `python -m pytest -q`.
5. Add tests for behavioral changes and update both README language sections when user-facing behavior changes.
6. Open a concise pull request describing the problem, approach, and validation.

Do not submit credentials, private network inventories, generated build artifacts, invasive scanning features, or code that weakens validation by default.
