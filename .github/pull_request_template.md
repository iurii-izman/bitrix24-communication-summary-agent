## Summary

- explain the change clearly
- state whether this is feature, fix, docs, or maintenance work

## Validation

- [ ] `pytest -q`
- [ ] `ruff check .`
- [ ] relevant docs updated if behavior or scope changed

## Risk Check

- [ ] no secrets added
- [ ] no real PII added
- [ ] no unreviewed write-enabled Bitrix behavior introduced

## Notes

- related issue:
- rollout or cleanup considerations:
