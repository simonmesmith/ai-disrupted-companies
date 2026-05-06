# AI Disruption Index - Memory

## Current State
- **Company count:** 80 (as of 2026-05-06)
- **Last updated:** 2026-05-06

## Category Distribution
| Category | Count |
|---|---|
| Software & SaaS | 22 |
| Business Services | 21 |
| Content & Media | 13 |
| Research & Analytics | 9 |
| Marketing & Advertising | 6 |
| Education | 3 |
| Freelance Marketplaces | 3 |
| Legal & Tax | 3 |

## Thin Categories (good targets for next session)
- Legal & Tax (3): HRB, LZ, LAW
- Freelance Marketplaces (3): FVRR, UPWK, FLN.AX
- Education (3): CHGG, COUR, NRDY

## Topic Files
- `leads.md` — current watchlist and next-session candidates.
- `failed-candidates.md` — rejected candidates and reasons; check before re-evaluating.
- `search-strategies.md` — what approaches worked, failed, or remain unexplored.

## Session Log: 2026-05-06
- **Added:** TEP.PA (Teleperformance SE) — Business Services / BPO / Contact Centers. Pre-ChatGPT EUR 214.00, current EUR 61.94 (-71.1%). French global customer experience/BPO leader with ~490,000 employees. Reuters/CNBC tied the 2024 share plunge directly to AI call-center automation fears after Klarna said its OpenAI-powered assistant handled two-thirds of service chats, equivalent to 700 full-time agents. Company previously said 20-30% of activities could be automated and is now pivoting to TP.ai FAB, 500+ AI projects, an AI-native CEO, and a Chief AI Officer.
- **Rejected from leads:** TRI (-21.6%, too modest), DOCU (+4.7%, above pre-ChatGPT), NCNO (-29.9% but AI beneficiary with ACV +17% and 112% net retention), SFIX (-4.1%, too modest), CRTO (-36.2% but decline tied to retail-media client scope/ad spend and AI partnerships, not primary AI disruption), DUOL (+57.4%, far above pre-ChatGPT).
- **Search approaches used:** 2 of 5 (lead re-checks; international peers of proven BPO/contact-center disruption cluster).
- **Validation:** Ran `uv run ai-index-update-prices` (79/80 tickers refreshed; ASGN had no current data and retained old value), `uv run ai-index-validate`, and `uv run pytest` (49 passed).
- **Observation:** International peers of already validated clusters can still work even when broad searches are exhausted. BPO/contact centers are now saturated; next sessions should prioritize thin categories or monitor borderline leads rather than force adds.

## Session Log: 2026-05-05 (Codex workflow refactor)
- **Added:** No companies. Refactored the repo for daily Codex operation.
- **Code changes:** Added shared CSV/data helpers, stronger CSV validation, and `daily_research.py` to generate a deterministic Codex research brief from current CSV coverage plus leads.
- **Automation:** GitHub Actions now runs on a weekday post-market schedule in addition to push/manual triggers, so price refresh + deploy can happen daily without an LLM session.

## Session Log: 2026-05-05 (Codex-only repo cleanup)
- **Added:** No companies. Reorganized Python implementation into `src/ai_disruption_index/`, moved tests into `tests/`, and added `ai-index-*` CLI scripts.
- **Deleted:** Legacy Claude support files and tracked assistant hook configs. `.claude/` and `.codex/` are now ignored local-only folders.
- **Automation:** GitHub Actions now calls package scripts and watches `src/**`, `tests/**`, `pyproject.toml`, and `uv.lock`. The lockfile is tracked for reproducible installs.

## Session Log: 2026-04-26 (zero-find session)
- **Added:** None. At ~80 companies, qualifying candidates are very scarce.
- **Evaluated:** PUBM, CCSI, PLTK, BLKB, CINT, DHX plus broad batch screens across SaaS, real estate, gaming, fintech, ad tech, healthcare staffing, European IT, education, and insurance.
- **Observation:** Most remaining large stock declines are NOT primarily AI-driven. The gap between "stock is down" and "stock is down because of AI" is the binding constraint.

## Session Log: 2026-04-25
- **Added:** VERI (Veritone Inc) — Software & SaaS / Enterprise AI Platform. AI platform commoditized by foundation models; revenue collapse, going-concern warning, and heavy debt made it a clean "AI company disrupted by better AI" case.

## Session Log: 2026-04-24
- **Added:** APX.AX (Appen Limited) — Content & Media / AI Data Labeling. AI training data company disrupted by synthetic data and customers bringing labeling in-house; Google contract termination was decisive.
- **Observation:** Re-evaluating borderline failed candidates can work as prices move, but most SaaS decliners remain sentiment or macro stories rather than AI disruption.
