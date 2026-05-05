# AI Disruption Index

**One-liner:** Find publicly traded companies whose stock crashed below their pre-ChatGPT price due to AI disruption, and track them in a master list.

## Git Workflow

Always commit and push to the **`main`** branch. Never use `master`.

## What This Project Does

This repo tracks publicly traded companies whose stock price has fallen below its November 29, 2022 close (the day before ChatGPT launched) because AI is disrupting their core business. The master list lives in `companies.csv`. An interactive dashboard is deployed automatically via GitHub Pages.

## When Asked to Find a New Company

### Step 1: Prepare (read memory + CSV)
1. Read `companies.csv` to see what's currently covered.
2. Read auto memory (`MEMORY.md` and any referenced topic files, especially `leads.md`).
3. Note which categories are thin and which are saturated.
4. Check `leads.md` for previously identified promising candidates.

### Step 2: Search (with limits)
1. **Start with leads from memory.** Evaluate any promising candidates from previous sessions first.
2. **Pick a search approach.** Focus on underrepresented categories or new angles from `search-strategies.md`.
3. **Evaluate candidates one at a time.** For each:
   - Web search for AI disruption angle
   - Verify ticker is yfinance-compatible and still active
   - Check pre-ChatGPT price vs. current price
   - Check for reverse stock splits or other distortions
   - If it qualifies, add it. If not, note why for memory.
4. **Respect the limits** defined in the Search Effort Limits section below.
5. **Track everything** as you go: what you tried, what failed, what succeeded.

### Step 3: Add qualifying companies
- **Before adding any company, check for duplicate tickers.** Read `companies.csv` and verify the ticker does not already exist (case-insensitive). Also verify the company name is not already listed under a different ticker (e.g., different exchange). Never add a ticker that is already in the CSV.
- Run `uv run ai-index-validate` after editing to confirm no duplicates were introduced.
- Append to `companies.csv` with all fields (see CSV schema below).
- Commit and push. GitHub Actions handles price updates and site deployment automatically.

### Step 4: Update memory
- Update `MEMORY.md` with new company count and category distribution.
- Append failed candidates to `failed-candidates.md` with reasons.
- Update `search-strategies.md` with what worked and didn't.
- Move any unevaluated promising candidates to `leads.md`.
- If you hit a limit and stopped early, note that so the next session knows to continue.

Do not run `ai-index-update-prices` or `ai-index-generate-page` manually unless explicitly asked — the automation handles it.

---

## Environment Setup

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management. To set up:

```bash
uv sync --all-extras    # Creates .venv and installs all deps including dev
```

All Python commands should use `uv run` to ensure the venv is active:

```bash
uv run pytest
uv run ai-index-update-prices
uv run ai-index-generate-page
uv run ai-index-daily-brief
```

## Folder Structure

```
├── companies.csv              # Master list (source of truth)
├── src/ai_disruption_index/   # Python package for data, validation, price updates, and site generation
├── tests/                     # Pytest suite
├── template.html              # HTML/CSS/JS template for the site
├── pyproject.toml             # Python dependencies and CLI scripts
├── uv.lock                    # Locked dependency graph for reproducible runs
├── AGENTS.md                  # Codex instructions
├── README.md                  # Public-facing project description
├── docs/                      # GitHub Pages output (index.html is generated, not committed)
└── .github/workflows/         # GitHub Actions: price updates + site deployment
```

---

## CSV Schema

`companies.csv` columns:

| Column | Description |
|---|---|
| `ticker` | yfinance-compatible ticker symbol (e.g., `CHGG`, `WPP.L`, `WKL.AS`) |
| `name` | Company name |
| `category` | Broad category (see Categories below) |
| `subcategory` | Specific subcategory |
| `description` | What the company does |
| `disruption` | How AI is disrupting them |
| `price_prechatgpt` | Closing price on November 29, 2022 |
| `price_now` | Most recent closing price (updated automatically) |
| `change_percentage` | `(price_now - price_prechatgpt) / price_prechatgpt` (updated automatically) |

---

## Categories

Companies are organized into broad categories with specific subcategories:

| Category | Subcategories |
|---|---|
| Business Services | BPO / Contact Centers, IT Services, IT Staffing & Consulting, Staffing & Recruitment, Translation & Localization, Multi-Utility / Network Marketing |
| Software & SaaS | Contact Center Software, Conversational AI, Customer Support, Expense Management, HCM / Payroll, Project Management, Social Media Management, AP Automation / Fintech |
| Content & Media | Stock Media, Content Moderation / AI Data, Creative Software, Online Dating, Online Reviews / Travel |
| Marketing & Advertising | Ad Services / Agencies, Ad Tech, Digital Media / Affiliate |
| Research & Analytics | Data Warehousing, Healthcare Analytics, Market Research, Professional Information, Research / IP Analytics |
| Education | EdTech |
| Freelance Marketplaces | Freelance Platform |
| Legal & Tax | Legal Tech, Tax Preparation |

### Categorization Guidelines

- **Prefer existing categories and subcategories** when a company fits reasonably well.
- **New categories or subcategories are fine** when a company genuinely doesn't fit existing ones — but minimize fragmentation so we can do meaningful trend analysis.
- Subcategories should be **specific enough to be useful** but **broad enough to accumulate multiple entries** over time.

---

## Finding New Companies

### Stock Price Verification

Use `yfinance` — it's installed, fast, and reliable. Tickers must be **yfinance-compatible** (e.g., `WPP.L` not `LON:WPP`, `WKL.AS` not `AMS:WKL`).

```python
import yfinance as yf
stock = yf.Ticker('TICKER')
hist = stock.history(start='2022-11-28', end='2022-11-30')
nov_price = hist['Close'].iloc[-1]
current_price = stock.history(period='1d')['Close'].iloc[-1]
```

### Gotchas

- **DUPLICATE TICKERS** — Before adding ANY company, search `companies.csv` for the ticker (case-insensitive) AND the company name. A company may already be listed under a different ticker variant (e.g., different exchange suffix). If it's already there, skip it. Run `uv run ai-index-validate` after every edit to catch duplicates. CI will block pushes with duplicate tickers.
- **Reverse stock splits** distort yfinance's adjusted data (e.g., LivePerson had a 1:15 split). Always check.
- **Delisted/acquired tickers** — verify the ticker is still active (e.g., ZoomInfo went private, Perficient was acquired).
- **CSV format** — standard comma-delimited with double-quoted fields containing commas. Use the Edit tool to append rows.
- **Trailing newline** — before appending a row, verify the file ends with a newline (`\n`). If it doesn't, the new row will be concatenated onto the last existing row. Never use `cat >>` or shell heredocs to append; always use the Edit tool or a Python script that explicitly checks for/adds a trailing newline first.

---

## Search Effort Limits

Finding new companies gets harder as the list grows. To avoid burning excessive tokens on fruitless searches, follow these limits:

### Definitions

- **Candidate evaluation** = researching a specific company name/ticker to determine if it qualifies (web search for AI disruption angle + yfinance price check). Each company you investigate counts as one evaluation, whether it succeeds or fails.
- **Search approach** = a distinct strategy for generating candidates (e.g., "search for AI-disrupted accounting firms", "look at competitors of companies already on the list", "explore Asian markets"). Brainstorming a list of names from a single approach counts as one approach, not one per name.

### Limits

- **Maximum 15 candidate evaluations per session.** Each yfinance price check or web search about a specific company counts as one. Stop after 15 regardless of success.
- **Maximum 5 search approaches per session.** If your first 5 strategies all come up empty, stop. Don't keep trying new angles.
- **Stop after 3 consecutive failures.** If you evaluate 3 candidates in a row and none qualify (wrong price direction, already delisted, not really AI-disrupted, etc.), pause and reassess your approach before continuing. If your next approach also yields 3 consecutive failures, stop for this session.

### When You Hit a Limit

1. **Stop searching** — do NOT push past the limits.
2. **Report to the user** what you found (or didn't find) and why you're stopping.
3. **Update auto memory** with what you tried (see Auto Memory section below).
4. **Zero finds is fine.** The list doesn't need to grow every session. Say so honestly.

---

## Auto Memory

This project uses repo-local memory files to track search history across sessions. Codex should read and update these files directly.

### When to Read Memory

At the **start** of every company search session, before brainstorming candidates:

1. Read `MEMORY.md` (loaded automatically, first 200 lines).
2. If `MEMORY.md` references topic files, read the relevant ones (especially `failed-candidates.md` and `search-strategies.md`).

### When to Write Memory

At the **end** of every company search session (whether successful or not), update memory with:

- Any new companies you added (ticker, category, brief note on how you found it)
- Failed candidates and why they failed (price went up, delisted, not AI-related, already on list, etc.)
- Which search strategies worked or didn't
- Promising leads you didn't have time to fully evaluate
- Observations about category saturation or gaps

### Memory File Structure

| File | Purpose | Size Limit |
|------|---------|------------|
| `MEMORY.md` | Index and summary: company count, category distribution, top leads for next session, pointers to topic files | < 150 lines |
| `failed-candidates.md` | Table of rejected companies with ticker, name, reason, and date | < 200 lines; prune entries older than 6 months |
| `search-strategies.md` | What search approaches worked, didn't work, and remain unexplored | < 200 lines |
| `leads.md` | Promising candidates to evaluate next session | < 50 lines; entries get consumed or moved to failed-candidates |

### Memory Guidelines

- **Memory is advisory, not constraining.** A candidate that failed 3 months ago might qualify now if its stock dropped further. Strategies that didn't work before might work with a different angle. Don't skip something just because it's in the failed list — use judgment.
- **Keep it concise.** Respect the size limits above. Prune old entries that are no longer useful.
- **Create files organically.** Don't create all files on day one. Create each file the first time you have content for it.
- **Failed candidates are the most valuable memory.** They prevent wasting evaluations re-checking the same company every session.

---

## Automation

### GitHub Actions (`.github/workflows/update-and-generate.yml`)

Triggered on push to `main` when `companies.csv`, `src/**`, `tests/**`, `template.html`, `pyproject.toml`, or `uv.lock` change.

Also triggered on a weekday schedule after US market close so the published index can refresh daily even when no new company is added.

1. **update-prices job** — refreshes all prices via yfinance, commits updated CSV
2. **deploy-page job** — generates `docs/index.html` and deploys directly to GitHub Pages via `actions/deploy-pages`

The generated `docs/index.html` is **not committed** — it's built and deployed on the fly. Can also be triggered manually via `workflow_dispatch`.

### GitHub Pages

The site is deployed using the GitHub Pages action (not served from a committed file). Configure in repo Settings > Pages > Source: "GitHub Actions".

### Running Locally

```bash
uv run ai-index-update-prices      # Refresh prices
uv run ai-index-generate-page      # Generate docs/index.html locally
uv run ai-index-daily-brief        # Prepare deterministic Codex research brief
uv run pytest                       # Run all tests
```
