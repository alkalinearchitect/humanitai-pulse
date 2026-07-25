# HumanitAI Pulse — System Architecture

**Status:** Planning / scaffolding (2026-07-25)
**Owner:** HumanitAI CIC (founded by Tyson Architect, Companies House No. 16891121)
**Cost model:** 100% free — self-hosted open-source intelligence + free LLM (Nous Portal `tencent/hy3:free`), no per-query API bills.

---

## 0. The WHY (Sinek frame)

Crisis has a *shape* before it has a *date*. Communities that are about to break are
**visible** long before they break — if anyone is paying attention. Pulse exists to pay
attention, at population scale, for free, and to turn that attention into action.

The enemy is the weakness inside (inertia, silence, blame). The system recommends;
people decide. No false precision. No individual profiling.

---

## 1. The loop (enforced order)

```
OBSERVE → UNDERSTAND → CONNECT → INTERVENE → MEASURE
   ^                                           |
   +----------------- feedback -----------------+
```

Every module maps to a stage. The dataflow is one pipeline, not 15 apps.

---

## 2. Module → component map

| Module | Stage | Repo component | Free-model role |
|---|---|---|---|
| Community Pulse | Observe | `pulse-core` (scores API) | composite scoring, no LLM needed |
| Help Now | Connect | `helpnow` (directory API) | none — verified data |
| Friction Monitor | Understand | `friction` (ingest + score) | classify service-access blockers |
| Prevention Radar | Understand | `radar` (decline detector) | trend → risk narrative (free LLM) |
| Intervention Lab | Intervene | `lab` (simulator) | cost/outcome estimate (free LLM) |
| Impact Tracker | Measure | `impact` (eval) | before/after summary (free LLM) |

---

## 3. OSINT Intelligence layer (the engine room)

Source of truth for the forecast. All inputs are **public UK open data** + **live signals**
gathered without paid APIs.

### 3.1 Collectors (`osint/` — reuses existing `wordhumanitai/osint_scout`)
- **ONS**wellbeing CSV (primary domain: mental health, live LA-level).
- **MHCLG** / gov.uk statutory homelessness stats (open release).
- **NHS England** waiting-list + A&E pressures (open CSV / finder).
- **Companies House** — charity insolvencies, local service closures (free API).
- **Council registers** — FOI-ish open datasets per borough (benefit, eviction, TA).
- **Live signals** — BBC/Reuters UK RSS (crisis keywords: "major incident", "eviction",
  "rough sleeping", "fuel poverty") via RSS, no paid search.

### 3.2 Normalisation
Each record → `{place, region, lat, lng, pressure, severity, detail, src, ts}`.
`pressure ∈ {poverty, homelessness, nhs, mental, isolation, ageing}`.
Tag every record with evidence type: **measured | reported | estimated**.

### 3.3 Scoring (`pulse-core`)
- `composite()` — weighted severity (mental + ageing weighted 1.4).
- `spatial()` — Getis-Ord Gi* hotspot detection (libpysal/esda, free).
- `trend_projection()` — news drift on dominant pressure.
- Output: ranked towns + tier (Critical/Priority/Watch) + confidence.

### 3.4 Where the FREE model is used
The forecast *numbers* are deterministic (pandas/numpy). The **free LLM** (`hy3:free`)
is used only for: narrative synthesis, "what changed this week", intervention recommendations,
and impact summaries — the language layer, never the arithmetic. This keeps it cheap and
auditable. If the model is unavailable, the system degrades to numbers + a "synthesis pending" note.

---

## 4. Stack (all free / self-hosted)

- **Runtime:** Python 3.11 (VPS, already running Hostinger).
- **LLM:** Nous Portal `tencent/hy3:free` (verified free, reliable).
- **Scheduling:** Hermes `cronjob` (hourly OSINT collect, daily forecast, weekly report).
- **Data:** local SQLite / Parquet; no cloud DB bill.
- **Site:** GitHub Pages (already live: `alkalinearchitect.github.io/wordhumanitai`).
- **Repos:** one `humanitai-pulse` monorepo (or multi-repo by module — see §6).

---

## 5. Data flow (concrete)

```
cron(hourly) → osint/scout.py → raw/*.json
                        ↓
cron(daily)  → pulse-core/run.py → prediction/out.json (ranks, tiers, confidence)
                        ↓
             radar + friction + lab + impact (read out.json)
                        ↓
             site/pull from API  (or static JSON committed to Pages)
```

The **5th Space barge** mooring is chosen by `out.json` top-of-list + canal reachability.

---

## 6. Repo layout decision

**Chosen: ONE monorepo `humanitai-pulse`** (not 15 repos, not one per module).
Mirrors the "one platform, not fifteen sites" principle. Modules are folders:

```
humanitai-pulse/
  osint/          # collectors (OSINT intelligence)
  pulse-core/     # scoring engine (Observe)
  friction/       # Friction Monitor (Understand)
  radar/          # Prevention Radar (Understand)
  lab/            # Intervention Lab (Intervene)
  impact/         # Impact Tracker (Measure)
  helpnow/        # Help Now directory (Connect)
  site/           # front-end (GitHub Pages, or links wordhumanitai)
  ARCHITECTURE.md
  README.md
```

`wordhumanitai` stays the public site repo; `humanitai-pulse` is the engine. The site can
consume `humanitai-pulse` output via released JSON or a small API.

---

## 7. Guardrails (from humanitai-pulse skill)
- Never claim exactness from incomplete evidence → label estimated.
- Separate measured / reported / estimated / predicted / simulated.
- No individual-level inference. Population + voluntary only.
- AI = decision support, never allocation authority.
- Show confidence + limitations on every output.
- Design for action on every view.

---

## 8. Build sequence (next steps)
1. Scaffold `humanitai-pulse` repo + this ARCHITECTURE (this commit).
2. Port `osint_scout` + `prevention_system_v3.py` into `osint/` + `pulse-core/`.
3. Add `radar/`, `friction/`, `lab/`, `impact/` as thin modules reading `out.json`.
4. Wire Hermes cron: hourly collect, daily forecast, weekly narrative (free LLM).
5. Expose `out.json` to the site; add Pulse live modules behind the existing section.
6. MVP geography: Bristol (postcode Pressure Score).
