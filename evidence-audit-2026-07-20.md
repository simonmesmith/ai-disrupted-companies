# Historical evidence audit — 2026-07-20

## Scope and decision rule

Reviewed all 97 rows that were present after the Active/Recovered implementation, without searching for or adding companies. Recovered status was ignored for causal qualification. Each row was classified as direct/strong, mixed, or weak/speculative after checking its stored narrative against current company filings/results, credible independent reporting, ticker continuity, and post-ChatGPT split history.

A row was retained when AI is a credible primary structural pressure on its core workflow or monetization model, even if macro or execution factors also matter. Mixed rows were rewritten when the old text overstated causality or omitted major co-drivers. Rows were removed when current evidence showed AI as a product/demand tailwind, no material operating impact, or a clearly better primary explanation for the decline.

## Outcome

- Reviewed: 97
- Kept unchanged: 46
- Rewritten: 22
- Removed: 29
- Final index: 68 companies — 66 Active and 2 Recovered
- Recovered rows retained on causal merit: `KFRC`, `YEXT`

## Full disposition

- **Kept unchanged (46):** `CHGG`, `DAVA`, `GETY`, `RWS.L`, `FVRR`, `SSTK`, `PERI`, `ASAN`, `EPAM`, `TRIP`, `ZD`, `TASK`, `FRSH`, `UPWK`, `BZFD`, `CNDT`, `CAP.PA`, `LAW`, `ANGI`, `FLN.AX`, `PD`, `YEXT`, `NRDY`, `DOMO`, `RCH.L`, `KNOS.L`, `FUTR.L`, `RGP`, `BL`, `TEP.PA`, `HAS.L`, `SFOR.L`, `PAGE.L`, `GTM`, `WIX`, `STG.AX`, `TMV.DE`, `CINT.ST`, `ACN`, `ALFRE.PA`, `TCS.NS`, `HUBS`, `LBG.L`, `NABL`, `YOU.L`, `GAMB`.
- **Rewritten as mixed (22):** `LPSN`, `TTEC`, `FORR`, `GLOB`, `FIVN`, `WPP.L`, `CNXC`, `CLVT`, `MAN`, `RHI`, `WKL.AS`, `ADBE`, `G`, `IT`, `TEAM`, `DSY.PA`, `INFY`, `NICE`, `KFRC`, `RPD`, `APX.AX`, `4324.T`.
- **Removed as weak/speculative (29):** `EXFY`, `SPT`, `DH`, `ZIP`, `BMBL`, `TBI`, `BILL`, `PAYC`, `ASGN`, `COUR`, `KELYA`, `TEP.L`, `LZ`, `HRB`, `TDC`, `OMC`, `CXM`, `DV`, `U`, `AI`, `SMWB`, `MNDY`, `MTCH`, `FDS`, `GTLB`, `QLYS`, `TENB`, `HCAT`, `VERI`.

## Removal rationale

| Ticker(s) | Finding |
|---|---|
| `EXFY`, `SPT`, `DH`, `BILL`, `CXM`, `DV` | Current results do not establish AI as the primary operating pressure. The companies are embedding AI in their products; BILL core revenue grew 16%, DoubleVerify revenue grew 10%, and Expensify's full-year revenue grew 2%. Pricing/packaging, product transitions, customer budgets, execution, and ordinary competition better explain the weakness. |
| `ZIP`, `TBI`, `KELYA`, `ASGN` | Company filings point to the hiring cycle, customer/contract changes, government exposure, and acquisitions as the principal causes. `ASGN` also ceased trading in April 2026 after becoming Everforth under `EFOR`; the successor's filings still do not supply an AI-primary operating link. |
| `BMBL`, `MTCH` | Paying-user weakness is tied to dating-app fatigue, product quality, monetization, and deliberate product resets. AI is being deployed as a matching, safety, and productivity tool; evidence that AI companions or synthetic profiles primarily caused the decline was not sufficient. |
| `PAYC`, `LZ`, `HRB`, `COUR` | Current operations contradict the casualty thesis: Paycom revenue grew 9% with improved retention; LegalZoom subscription revenue grew 12%; H&R Block raised its outlook as assisted and DIY volumes grew; Coursera's AI-skills demand is a material tailwind. |
| `TEP.L`, `OMC`, `TDC`, `U` | Better company-specific explanations dominate: Telecom Plus's 2026 plunge followed an investment-plan profit reset; Omnicom is dominated by the IPG acquisition/integration; Teradata is in a long-running cloud transition and returned to growth; Unity's decline is chiefly tied to the runtime-fee/ironSource/ads reset while AI products are contributing growth. |
| `AI`, `VERI` | C3.ai attributed its collapse to a sales reorganization and CEO/leadership disruption; Veritone's continuing operations were broadly stable and its changes reflect divestitures, mix, and talent-acquisition consumption. Neither filing supports the stored claim that foundation models destroyed the platform. |
| `SMWB`, `MNDY`, `FDS`, `GTLB` | These were market-fear stories without material operating confirmation. Current results show strong or continued growth, high retention, and AI-driven demand or monetization; management either reported no direct displacement or described AI as a growth driver. |
| `QLYS`, `TENB`, `HCAT` | Mythos increases vulnerability volume and demand for exposure management; Qualys and Tenable grew about 10% and explicitly position AI as a tailwind. Health Catalyst identifies DOS-to-Ignite migration churn—not AI substitution—as the direct cause of retention pressure. |

## Important narrative corrections

- `LPSN`, `TTEC`, `CNXC`, `CLVT`: retained the AI thesis but added debt, portfolio, integration, execution, and demand-cycle co-drivers.
- `MAN`, `RHI`, `KFRC`: made the current hiring cycle explicit; AI is the structural risk to the recovery, not a blanket explanation for every revenue decline.
- `WKL.AS`, `ADBE`, `IT`, `TEAM`, `DSY.PA`, `NICE`: distinguished direct AI-driven market repricing from still-resilient current revenue and product adoption.
- `APX.AX`: removed the unsupported assertion that Google replaced Appen with its own AI and added customer concentration, contract loss, restructuring, and new GenAI-evaluation demand.
- `RPD`: acknowledged that autonomous vulnerability discovery can commoditize scanning while simultaneously increasing demand for exposure management.

## Continuity and distortion checks

- All 97 historical rows were checked with current yfinance history. `ASGN` was the only inactive ticker; the official successor is `EFOR` after the April 24, 2026 Everforth rebrand.
- Post-ChatGPT splits were found for `LPSN` (1:15 reverse split), `BZFD` (1:4 reverse split), and `ANGI` (1:10 reverse split). Their stored baselines are split-adjusted; `LPSN`'s rewritten narrative now states this explicitly, while `BZFD` and `ANGI` already disclosed their adjustments.

## Evidence anchors

The audit relied primarily on current filings and results, including [Telecom Plus FY2026 results](https://www.telecomplus.co.uk/~/media/Files/T/Telecomplus/documents/full-year-results-fy26.pdf), [TrueBlue's 2025 10-K](https://investor.trueblue.com/sec-filings/all-sec-filings/content/0000768899-26-000009/tbi-20251228.htm), [ZipRecruiter's 2025 shareholder letter](https://www.sec.gov/Archives/edgar/data/1617553/000161755326000015/ex992-q42025shareholderl.htm), [Paycom FY2025 results](https://investors.paycom.com/news/news-details/2026/Paycom-Software-Inc--Reports-Fourth-Quarter-and-Year-End-2025-Results/default.aspx), [FactSet Q3 FY2026 results](https://investor.factset.com/static-files/a86df6bd-9866-41a9-bb4c-75afcf4744d0), [GitLab FY2026 results](https://ir.gitlab.com/news/news-details/2026/GitLab-Reports-Fourth-Quarter-and-Full-Year-Fiscal-Year-2026-Financial-Results-Board-of-Directors-Authorizes-400-million-for-Share-Repurchase-Program/default.aspx), [Adobe Q2 FY2026 filing](https://www.sec.gov/Archives/edgar/data/796343/000079634326000112/adbe-20260529.htm), [Qualys Q1 2026 results](https://www.qualys.com/company/newsroom/news-releases/usa/2026-05-05-qualys-announces-first-quarter-2026-financial-results), [Tenable Q1 2026 results](https://investors.tenable.com/news-releases/news-release-details/tenable-announces-first-quarter-2026-financial-results), [Health Catalyst Q1 2026 results](https://ir.healthcatalyst.com/news-releases/news-release-details/health-catalyst-reports-first-quarter-2026-results/), [C3.ai's FY2026 update](https://c3.ai/c3-ai-announces-preliminary-fourth-quarter-and-full-fiscal-year-2026-results-thomas-m-siebel-resumes-role-of-chief-executive-officer/), [Veritone's 2025 10-K](https://investors.veritone.com/sec-filings/all-sec-filings/content/0001628280-26-025214/veri-20251231.htm), and [Everforth's ticker-change announcement](https://investors.everforth.com/news/news-details/2026/Everforth-Launches-New-Era-as-Rebrand-Elevates-Technology-and-Digital-Engineering-Capabilities-at-Scale/default.aspx).
