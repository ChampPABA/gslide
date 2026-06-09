## 1. Phase 1 — Persistent profile migration

- [ ] 1.1 `src/gslide/browser.py`: refactor `BrowserSession.__init__(user_data_dir, headed=False)`; use `launch_persistent_context(user_data_dir, headless=not headed, args=["--disable-blink-features=AutomationControlled"])`
- [ ] 1.2 `src/gslide/browser.py`: `__exit__` closes context only (no `.browser.close()`); read `GSLIDE_HEADED=1` to force headed
- [ ] 1.3 `src/gslide/browser.py`: delete `save_session()`; add clear error on profile-lock (ProcessSingleton) contention
- [ ] 1.4 `src/gslide/auth.py`: `get_storage_path()` → `get_profile_dir()` (`~/.gslide/profile`); update `is_logged_in`, `require_login`, `delete_storage_state` → `delete_profile`
- [ ] 1.5 `src/gslide/auth.py`: `login()` uses persistent profile, no `save_session`, prints migration notice if legacy `storage_state.json` found; `status()` and `logout()` updated
- [ ] 1.6 `src/gslide/gen.py`: `gen_single`/`gen_batch` pass `user_data_dir` to `BrowserSession` (remove `storage_state=`)

## 2. Phase 2 — Mid-batch resilience

- [ ] 2.1 `src/gslide/gen.py`: add `_assert_session(page)` and call at start of each batch loop iteration (slides + images)
- [ ] 2.2 `src/gslide/gen.py`: add `start_from: int = 1` to `gen_batch`, skip slides with index < start_from
- [ ] 2.3 `src/gslide/gen.py`: per-slide error screenshots `/tmp/gslide_error_slide_{i}.png`; print resume hint on abort/failure
- [ ] 2.4 `src/gslide/cli.py`: add `--start-from` option to `batch` command, pass to `gen_batch`

## 3. Tests

- [ ] 3.1 `tests/test_auth.py`: rewrite for profile-dir semantics (`get_profile_dir`, `is_logged_in`, `delete_profile`, `require_login`)
- [ ] 3.2 `tests/test_browser.py`: `BrowserSession(user_data_dir=tmp)` launches persistent context headless
- [ ] 3.3 `tests/test_gen.py`: patch `require_login` → profile dir; test `_assert_session` and `start_from` skip
- [ ] 3.4 `tests/test_cli.py`: logout patches `get_profile_dir`; test `--start-from` parsing

## 4. Docs

- [ ] 4.1 `README.md`: clarify session saved as Chromium profile
- [ ] 4.2 `docs/project_brief.md`: update path to `~/.gslide/profile`

## 5. Verification

- [ ] 5.1 `pytest` all green
- [ ] 5.2 E2E: `auth login` → `auth status` valid → batch (2-3 slides) succeeds
- [ ] 5.3 E2E: cold-restart (new shell) batch again without re-login
- [ ] 5.4 E2E: `--start-from 2` skips slide 1; profile-lock error clear; `GSLIDE_HEADED=1` shows window
- [ ] 5.5 Archive change (sync delta into `openspec/specs/`)
