# Lint and Type Cleanup TODO

- [ ] Update `spotlawful_ai/auth.py`
  - [ ] Fix Pylint line-too-long issues
  - [ ] Add/adjust type annotations for middleware methods to reduce mypy annotation-unchecked noise
  - [ ] Rename demo constant to UPPER_CASE (`DEMO_TOKEN`)
- [ ] Update `spotlawful_ai/database.py`
  - [ ] Fix Pylint line-too-long issues
  - [ ] Add missing function docstrings
  - [ ] Rename demo constant to UPPER_CASE (`DEMO_KEY`)
- [ ] Update `spotlawful_ai/test_api_server.py`
  - [ ] Add module/class/function docstrings
  - [ ] Fix Pylint line-too-long issues
- [ ] Run verification checks
