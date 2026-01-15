# Prescrypt TODO

**Current Status:** Stage 6.1 Complete | **Tests:** 2087 passing | **Coverage:** 83%

See `notes/history.md` for completed work (Stages 0-5).

---

## Stage 6: Developer Experience

**Goal:** Make the transpiler pleasant to use.

See `local-notes/plan-stage6.md` for detailed design.

**Implementation order:**
- [x] 6.1 Error messages with source locations
- [ ] 6.2 Export generation for ES6 modules
- [ ] 6.3 Import code generation (ES6 imports)
- [ ] 6.4 JS FFI (`import js` for JS globals)
- [ ] 6.5 Module resolution (file lookup)
- [ ] 6.6 Multi-file CLI (`--output-dir`, `--module-path`)
- [ ] 6.7 Source map generation
- [ ] 6.8 Watch mode
- [ ] 6.9 Documentation

---

## Interlude: Cleanup

- [ ] Move all tests to `tests/`.

---


## Stage 7: Async Support

**Goal:** Basic async/await transpilation.

- [ ] `gen_await` expression handler
- [ ] `gen_async_for` statement handler
- [ ] `gen_async_with` statement handler
- [ ] Test with common patterns:
  - `await fetch(...)`
  - `async for x in stream:`
  - `async with lock:`

**Note:** `gen_asyncfunctiondef` already exists with basic implementation.

---

## Stage 8: Generators

**Goal:** Support `yield` and generator functions.

- [ ] `gen_yield` expression handler
- [ ] `gen_yield_from` for delegation
- [ ] Generator expressions (currently converted to arrays)

**Complexity:** High - generators have complex state machine semantics.

---

## Future Enhancements

- [ ] Dataclasses and/or attrs support
- [ ] `__slots__` support
- [ ] Unify `stdlib_js` and `stdlib_py` directories (low priority)

---

## Milestones

| Milestone | Stage | Status |
|-----------|-------|--------|
| MVP | Stage 4 | **Complete** |
| Beta | Stage 6 | Next |
| Production | Stage 8 | Future |

---

## Quick Reference

```bash
make test                    # Run all tests
pytest -k "test_name" -v     # Run specific test
pytest --cov=prescrypt       # Run with coverage
```
