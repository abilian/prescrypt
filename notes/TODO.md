# Prescrypt TODO

**Current Status:** Stage 6 Complete | **Tests:** 2224 passing | **Coverage:** 83%

See `notes/history.md` for completed work (Stages 0-6).

---

## Stage 6: Developer Experience ✓

**Goal:** Make the transpiler pleasant to use.

See `local-notes/plan-stage6.md` for detailed design.

**Implementation order:**
- [x] 6.1 Error messages with source locations
- [x] 6.2 Export generation for ES6 modules
- [x] 6.3 Import code generation (ES6 imports)
- [x] 6.4 JS FFI (`import js` for JS globals)
- [x] 6.5 Module resolution (file lookup)
- [x] 6.6 Multi-file CLI (`--output-dir`, `--module-path`)
- [x] 6.7 Source map generation
- [ ] 6.8 Watch mode (deferred)
- [x] 6.9 Documentation (MkDocs site)
- [x] 6.10 Strict mode compatibility

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

## Short-term Fixes

- [ ] Lambda with default arguments (e.g., `lambda x=1: x`)
- [ ] `__all__` to control module exports
- [ ] Context manager protocol (`__enter__`/`__exit__`)
- [ ] Type-informed operator codegen (emit `a + b` instead of `_pyfunc_op_add(a, b)` when types are known)

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
| Beta | Stage 6 | **Complete** |
| Production | Stage 8 | Next |

---

## Quick Reference

```bash
make test                    # Run all tests
pytest -k "test_name" -v     # Run specific test
pytest --cov=prescrypt       # Run with coverage
```
