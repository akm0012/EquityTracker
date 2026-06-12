# Onboarding Improvements Plan

## Goal

Make first-run setup reliable and understandable for a new EquityTracker user while preserving the current config format and terminal UI behavior.

The target outcome is:

- A fresh clone can save a Finnhub token from the CLI without manual config setup.
- Watch-only stocks require only ticker plus `0` shares.
- Invalid numeric input is rejected before it reaches the config file.
- Users see a clear setup summary before curses takes over the terminal.
- Users can create split same-ticker grant rows during onboarding with the existing optional group label.
- Invalid or partial `config.ini` files recover gracefully instead of failing in surprising places.
- The GitHub README gives first-time visitors enough context to install, configure, run, and safely edit the app.

## Non-Goals

- Do not replace `config.ini` with another storage format.
- Do not change the Finnhub API provider.
- Do not redesign the curses table.
- Do not add a full interactive editor for existing portfolios.
- Do not remove direct hand-editing support for `config.ini`.

## Current First-Run Flow

1. `prod.Main` constructs `ConfigRepository` and `StockRepository`.
2. `process_arguments()` handles `--Token`, `--Reset`, and `--NUKE`.
3. If there are CLI args, the program exits.
4. If `config.ini` does not exist, the app creates an empty config.
5. If the config is valid and has at least one stock grant/watch entry, the app launches curses.
6. Otherwise, the app prompts for a Finnhub token, then prompts for ticker/grant data.
7. The app saves the portfolio and immediately launches curses.

## Problems To Fix

### 1. Fresh-clone `--Token` can fail

`process_arguments()` runs before `config.ini` is created. `ConfigRepository.save_finnhub_api_key()` assumes the config already has an `API_TOKENS` section.

Expected behavior:

- `./venv/bin/python3 -m prod.Main --Token abc123` works even when `config.ini` does not exist.
- Existing stocks are preserved when only the token is changed.
- The command still exits after saving the token.

### 2. Watch-only onboarding asks unnecessary questions

When a user enters `0` shares, the app correctly skips grant price, but still asks for vest count.

Expected behavior:

- Entering `0` shares creates a watch-only row with price `0.0`, vests `0`, and no group label.
- The app does not ask grant price, vest count, or extra grants for that ticker.

### 3. Numeric inputs allow invalid portfolio data

Current prompts accept negative shares, negative vests, and non-positive grant prices.

Expected behavior:

- Shares must be an integer `>= 0`.
- Grant price must be a float `> 0` when shares are greater than zero.
- Vests left must be an integer `>= 0`.
- Input may include a leading `$` for grant price.
- Error messages should say what rule failed, not only that the value is not a number.

### 4. No setup summary before launching curses

After setup, the program immediately switches into curses. New users do not get a clear confirmation of what was saved.

Expected behavior:

- After portfolio creation, print a concise summary with:
  - Config file path.
  - Each ticker.
  - Watch-only rows.
  - Grant count, grant price, vests left, and group label when present.
- Ask whether to start the live tracker now.
- Default should be yes to keep current flow efficient.

### 5. Group labels are not available during onboarding

The code and README support optional group labels for split rows, but first-run prompts never ask for them.

Expected behavior:

- When adding multiple grants for the same ticker, the user can optionally assign a group label.
- Empty group label preserves current combined-row behavior.
- The prompt explains this only when useful, without overwhelming a simple single-grant setup.

### 6. Malformed config recovery is brittle

Invalid config files can lead to later code paths that assume sections exist. The app should explain and repair simple config problems.

Expected behavior:

- Missing config file: create a valid empty config.
- Missing `API_TOKENS`: add it.
- Missing `DATABASE`: add it.
- Missing token value: prompt for token.
- Empty database: run portfolio onboarding.
- Malformed stock rows: skip bad rows with a warning, preserve valid rows, and prompt if no valid rows remain.

### 7. GitHub README can be clearer for new users

The README explains the app, but it should do more work for someone arriving cold from GitHub. It should make the value proposition, prerequisites, setup path, config examples, screenshots, command reference, and troubleshooting easy to scan.

Expected behavior:

- A GitHub visitor can understand what the app does from the first viewport.
- The quick start clearly separates first-time setup from normal usage.
- The Finnhub token requirement is visible before the user runs the app.
- `config.ini` examples cover watch-only stocks, grants, and optional group labels.
- The display explanation links terms like "next vest", "day range", and "gain/loss" back to config fields.
- Troubleshooting covers common first-run failures: invalid token, invalid ticker, no live updates outside market hours, narrow terminal clipping, and auth/config file location.

## Proposed Code Changes

### A. Add config bootstrapping helpers

File: `prod/repository/ConfigRepository.py`

Add:

- `ensure_config_file()`
  - Creates `config.ini` if missing.
  - Ensures `API_TOKENS` and `DATABASE` sections exist.
  - Writes the file only when a repair is needed.

- `get_config_file_location()`
  - Returns the resolved config path for setup summary text.

- `get_stock_portfolio_with_errors()`
  - Returns `(portfolio, errors)` where `errors` contains bad config row descriptions.
  - Existing `get_stock_portfolio()` can call this and raise or ignore errors based on existing behavior.

Update:

- `save_finnhub_api_key()` should call `ensure_config_file()` first.
- `clear_stocks()` should call `ensure_config_file()` first.
- `save_stock_portfolio()` should call `ensure_config_file()` first.
- `is_config_file_valid()` can remain for compatibility, but startup should move toward repair-oriented logic.

Acceptance criteria:

- Token save works with no config file.
- Token save works with a config file missing `API_TOKENS`.
- Clearing stocks works with a config file missing `DATABASE`.
- Existing valid config output remains unchanged.

### B. Rework startup sequencing

File: `prod/Main.py`

Change startup to:

1. Create repositories.
2. Call `config_repo.ensure_config_file()`.
3. Process CLI args.
4. If CLI args were provided, exit.
5. Load portfolio with parse errors.
6. Print warnings for any skipped malformed rows.
7. If token is empty, prompt for token.
8. If portfolio has no rows, run portfolio onboarding.
9. Print setup summary after new onboarding.
10. Ask whether to start tracker.
11. Launch curses only when user confirms.

Acceptance criteria:

- Fresh config creation happens before all config-writing CLI commands.
- Existing configured users still go straight to tracker after the existing portfolio message.
- Newly onboarded users see the setup summary before tracker launch.

### C. Split input parsing from prompting

File: `prod/Main.py`

Add small pure helpers:

- `parse_non_negative_int(raw_value: str) -> int`
- `parse_positive_float(raw_value: str) -> float`
- `normalize_optional_group(raw_value: str) -> str`

Update prompt helpers:

- `get_grant_count_from_user()` uses non-negative int parsing.
- `get_grant_price(grant_count)` requires positive float when `grant_count > 0`.
- `get_num_of_vests_left_from_user()` uses non-negative int parsing.

Acceptance criteria:

- Negative shares are rejected.
- Negative vest counts are rejected.
- Zero or negative grant prices are rejected when shares are greater than zero.
- `$123.45` is accepted as `123.45`.
- Unit tests can cover parsing without interactive input.

### D. Improve watch-only flow

File: `prod/Main.py`

Update `get_stock_grants_from_user()`:

- Prompt for share count.
- If share count is `0`:
  - Add `StockGrant(stock_ticker, 0, 0.0, 0)`.
  - Print a watch-only confirmation.
  - Return immediately for that ticker.
- Otherwise continue with grant price, vest count, and optional group label.

Acceptance criteria:

- Watch-only setup prompts for ticker and share count only.
- Watch-only row serializes to `TICKER,0,0.00,0`.
- Existing watch-only display behavior remains unchanged.

### E. Add optional group-label onboarding

File: `prod/Main.py`

Add:

- `get_grant_group_from_user(stock_ticker: str, has_existing_grants_for_ticker: bool) -> str`

Prompt behavior:

- For the first grant of a ticker, do not ask by default unless the user is adding another grant later.
- For the second and later grant of the same ticker, ask:
  - "Press Enter to combine this grant with the previous {TICKER} row, or enter a short group label to show it separately."
- Keep the label optional.
- Strip whitespace.
- Reject commas, because commas are field delimiters in `config.ini`.

Implementation option:

- Ask the group-label question immediately after the user says they want to add another grant for the same ticker. That keeps the concept tied to the moment it matters.
- Simpler option: ask for an optional group label for every real grant, but word it as "usually leave blank." This is easier to implement and test, but adds one prompt to simple setups.

Recommended choice:

- Use the simpler "optional group label for every real grant" prompt first. It is predictable, exposes the feature, and avoids a more complex prompt state machine.

Acceptance criteria:

- Empty group label preserves combined-row behavior.
- Non-empty group label serializes as the fifth config field.
- Commas in group labels are rejected.
- Existing tests for grouped config continue to pass.

### F. Add setup summary and start confirmation

Files:

- `prod/Main.py`
- `prod/resources/Strings.py`

Add:

- `render_portfolio_summary(portfolio: StockPortfolio, config_path: str) -> str`
- `print_setup_summary(portfolio: StockPortfolio)`
- `prompt_start_tracker() -> bool`

Summary format:

```text
Saved portfolio to /path/to/config.ini

Portfolio:
- RDDT: 357 shares @ $216.99, 2 vests left, group "a"
- RDDT: 399 shares @ $147.86, 2 vests left, group "b"
- AAPL: watch only

Start live tracker now? (Y/n):
```

Acceptance criteria:

- New setup displays the saved config path.
- Watch-only rows are readable.
- Group labels are visible only when present.
- Pressing Enter or `Y` starts tracker.
- Pressing `n` exits cleanly.

### G. Improve onboarding copy

File: `prod/resources/Strings.py`

Recommended copy changes:

- Replace "grants" with "shares in this grant" where appropriate.
- Explain watch-only mode at the share-count prompt.
- Fix typos:
  - "light weight" -> "lightweight"
  - "preforming" -> "performing"
  - "Finhub" -> "Finnhub"
- Add specific numeric validation messages:
  - "Please enter a whole number greater than or equal to 0."
  - "Please enter a grant price greater than 0."
  - "Group labels cannot contain commas."

Acceptance criteria:

- Prompt wording matches README concepts.
- Error messages tell the user exactly how to recover.

### H. Improve the GitHub README

File: `README.md`

Recommended structure:

1. Short product summary and screenshot.
2. Feature list focused on what the user gets.
3. Requirements:
   - Python 3.
   - Finnhub API token.
   - UTF-8 terminal.
4. Quick start:
   - Clone.
   - Run `make run`.
   - Enter token.
   - Add a watch-only stock or grant.
5. Normal usage:
   - `make run`.
   - `Ctrl + C` to quit.
6. Config guide:
   - Explain every field.
   - Include grant, watch-only, multi-grant, and group-label examples.
7. Reading the terminal display.
8. CLI commands.
9. Troubleshooting.
10. Development and tests.

Acceptance criteria:

- A user can configure a watch-only stock without reading the full FAQ.
- A user can configure two independent same-ticker grants without guessing the group label syntax.
- The token setup path is explicit and avoids suggesting that secrets should be committed.
- Screenshots remain near the top but do not interrupt setup instructions.

## Test Plan

### Unit tests

Update `test/repository/test_ConfigRepository.py`:

- `ensure_config_file` creates a missing config file.
- `ensure_config_file` repairs missing `API_TOKENS`.
- `ensure_config_file` repairs missing `DATABASE`.
- `save_finnhub_api_key` works with no existing config.
- `clear_stocks` works with missing `DATABASE`.
- malformed stock rows are reported by `get_stock_portfolio_with_errors`.

Update or add `test/test_Main_onboarding.py`:

- `parse_non_negative_int("0") == 0`
- `parse_non_negative_int("-1")` raises `ValueError`
- `parse_positive_float("$12.34") == 12.34`
- `parse_positive_float("0")` raises `ValueError`
- `normalize_optional_group(" b ") == "b"`
- `normalize_optional_group("a,b")` raises `ValueError`
- `render_portfolio_summary` includes config path, watch-only rows, grant rows, and groups.

Update `test/objects/test_StockGrant.py` if needed:

- Group labels with whitespace are normalized before `StockGrant` construction or during prompt parsing, not necessarily in the object itself.

README review checklist:

- First viewport states what the project does and shows what it looks like.
- Quick start is runnable from a fresh clone.
- Config examples match parser behavior.
- No real API tokens or personal portfolio values are added.
- Troubleshooting answers the most likely first-run questions.

### Interactive smoke tests

Run from a temporary copy or with a temporary config path in tests if possible:

1. Fresh no-config token save:
   - Remove temp config.
   - Run `python -m prod.Main --Token test-token`.
   - Verify config contains both sections and token.

2. Watch-only onboarding:
   - Start with empty valid config and stubbed API validation if automated.
   - Enter ticker `AAPL`.
   - Enter shares `0`.
   - Verify no grant price or vests prompt appears.

3. Real grant onboarding:
   - Enter ticker.
   - Enter shares, price, vests, blank group.
   - Verify config has four fields.

4. Split-grant onboarding:
   - Enter same ticker twice.
   - Enter group labels.
   - Verify config has fifth field for labeled grants.

5. Start confirmation:
   - Complete setup.
   - Press `n` at "Start live tracker now?"
   - Verify process exits without curses.

### Regression tests

Run:

```bash
./venv/bin/python3 -m unittest discover -s test -t .
```

Expected:

- All tests pass.
- Existing warning about LibreSSL may appear and is not part of this work.

## Implementation Order

1. Add `ConfigRepository.ensure_config_file()` and update config-writing methods.
2. Reorder startup so config bootstrapping happens before CLI arg handling.
3. Add parsing helpers and tests.
4. Fix watch-only flow.
5. Add optional group-label prompt.
6. Add setup summary and start confirmation.
7. Add malformed-row recovery.
8. Polish strings and README snippets if prompt wording changes materially.
9. Add a README improvement pass for GitHub-first visitors.
10. Run the full test suite.

## Risk Notes

- `Main.py` currently relies on module-level `config_repo` and `stock_repo`, which makes interactive flow testing harder. Keep the first pass small, but consider extracting onboarding into a separate module later.
- Curses should remain untouched except for the decision to launch or exit after setup.
- `configparser` lowercases keys by default, but values are what matter for stock rows. Preserve the existing behavior.
- The optional group label uses comma-separated config fields, so commas must be rejected in labels.

## Future Follow-Ups

- Add `--config PATH` for easier testing and safer local experimentation.
- Add a non-interactive `--add-stock` or `--add-grant` command for power users.
- Show a one-time "how to edit config.ini" hint after setup.
- Add a command to print the current portfolio summary without launching curses.
