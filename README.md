# interviewprep — job hunt tracks

Independent preparation tracks, one per role pursued. Each has its own README with a reading order; **start there, not here**.

Each track is written in the language of its interview. The humanitarian tracks are in French, the commercial ones in English. This README and the agent instructions are in English.

---

## The tracks

| Track | Role | Language | Status |
|---|---|---|---|
| [`crs_spo_meal/`](crs_spo_meal/README.md) | Senior Project Officer MEAL — CRS Haïti, projet RAPID (urgence, Département d'État) | Français (+ pitch anglais) | **Entretien en ligne annoncé le 11 oct. 2026 — date à confirmer** |
| [`panos_mel_acq/`](panos_mel_acq/README.md) | Responsable MEL/ACQ — Institut Panos, programme AFGHS-PANOS (VIH, paiement sur jalons) | Français (+ pitch anglais) | Entretien Zoom du mar. 29 sept. 2026 (reporté du 25) |
| [`metaspace/`](metaspace/output/README.md) | Blockchain Engineer — Metaspace (UAE game studio, Polygon) | English | Interview 30 Sept 2026, 16:00 Haiti time |
| [`cmmb_meal_officer/`](cmmb_meal_officer/README.md) | M&E Officer — CMMB Haïti (VIH, santé publique) | Français (+ annexe anglaise) | **Entretien à venir — pas d'examen** |
| [`remote_leverage_data_analyst/`](remote_leverage_data_analyst/README.md) | Data Analyst — Remote Leverage (VA placement agency, Florida) | English | **Interview Mon 3 Aug 2026** |
| [`acted_bdd/`](acted_bdd/README.md) | Assistant(e) Base de Données — ACTED Haïti, réf. ASSISTBDD_2607 | Français | Dossier déposé, examen à venir |
| [`assitant_pmel/`](assitant_pmel/README.md) | Assistant PMEL — Parole et Action | Français | Entretien et examen passés |
| [`python_bairesdev/`](python_bairesdev/README.md) | Fullstack Python — BairesDev | English | Recruiter screen 22 Jul 2026 |

---

## How the tracks relate

They are not independent bodies of knowledge. Three of them describe the **same competence** — turning messy operational data into numbers someone can act on — dressed for three different audiences.

`assitant_pmel/` establishes the method: the results chain, indicator design, triangulation, weighted versus unweighted averages, XLSForm logic. Everything else refers back to it rather than repeating it.

`acted_bdd/` extends that method into database work: modelling, administration, backup and restore, beneficiary data protection, advanced Kobo, and a reconciled import pipeline.

`remote_leverage_data_analyst/` translates the same method into commercial vocabulary — funnel conversion, time to fill, CAC, cohort censoring — because the analysis is identical and only the words change.

`cmmb_meal_officer/` carries the method into public health, and is the only track whose employer's domain (HIV) has its own measurement apparatus. It deliberately does **not** restate the MEAL theory, statistics or indicator design already written in `assitant_pmel/`; it links back to those modules and adds what health puts on top — the cascade of care and the 95-95-95 arithmetic, PEPFAR MER indicators, cohort retention and the discipline of the denominator, Haiti's health information systems (SISNU, iSanté, MESI, SALVH, DATIM), results-based financing, and the health-facility reporting chain from paper register to donor.

`panos_mel_acq/` builds on `cmmb_meal_officer/` rather than repeating it — the same HIV and MER material, re-read from the mandate of a community sub-partner (treatment interruption, return to care, adherence) — and adds what that post turns on: a funding mechanism whose payments depend on verified milestones (very likely the State Department's America First Global Health Strategy), independent verification, and reconciliation with Haiti's national systems. It ships a small fictional tracing dataset in `exercices/` so the module's SQL figures are real query outputs.

`crs_spo_meal/` is the first emergency-response track. It reuses `panos_mel_acq/` for milestone payments, verification and the pressure stories, and `cmmb_meal_officer/` for HR and salary, then adds CRS's own MEAL method (SMILER+), the humanitarian toolkit (food-security indices, distribution and post-distribution monitoring, MUAC, the feedback and complaints mechanism, the CHS), and twelve management scenarios. Its module 00 also records the donor shift visible on the ground: the State Department replacing USAID, shown by Acted's Artibonite consortium moving from BHA to ECHO plus State funding.

`python_bairesdev/` is the engineering track, and it supplies two anecdotes the others reuse: the N+1 optimisation (36 seconds to under 0.5) and the composite-index deadlock fix.

**Keep shared stories worded consistently across tracks.** The same anecdote told two different ways is worse than either version alone.

---

## Practice datasets

The three tracks below ship data you can actually query, and every figure quoted in their modules was produced by running the query shown. `cmmb_meal_officer/` is the exception: its interview has no written exam, so it ships no dataset — every figure in it comes from a public source cited in its own `sources.md`. `python_bairesdev/` ships runnable apps rather than a dataset.

| Dataset | Track | Contents |
|---|---|---|
| `assitant_pmel/sql_exercices/meal_haiti.db` | PMEL, ACTED | 30 schools, 3 148 pupils, 360 weekly reports, 356 dirty staging rows |
| `acted_bdd/exercices/acted_bdd.db` | ACTED | 1 218 households, 1 428 assistances, 567 PDM surveys, 240 complaints |
| `remote_leverage_data_analyst/practice/agency.duckdb` | Remote Leverage | 302 clients, 635 vacancies, 3 396 submittals, 314 placements, 3 432 pipeline runs |

Each is regenerated by a deterministic script in the same folder, and each carries deliberately injected data-quality defects so that validation and reconciliation can be *demonstrated* rather than described.

Do not open a SQLite or DuckDB file directly from a synced folder — copy it locally first, since some network mounts break file locking.

---

## Related folders outside this one

`../curiculum-vitae-and-letter/` holds the CV sources. `alexandrodislaResume.tex` is the **source of truth in English** for every factual claim made in any track; `alexandro.disla_cv.tex` is its French twin. Per-application tailored versions live under `specific_situation/`, one folder per employer, each with Markdown, DOCX and PDF outputs.

---

## Conventions

Study material follows the "From Zero" writing contract in [`AGENTS.md`](AGENTS.md): open with the problem before naming the tool, build one real thing incrementally with complete runnable code, show the classic failure before explaining the fix, trace what the machine does in plain words, and close with interview-ready answers written as they would be spoken. Complete sentences throughout — no fragment bullets, no arrow chains.

Numbers in the modules are real outputs, not illustrations. When quoting them aloud in an interview, say "in the dataset I've been practising on" — they are realistic, not the employer's actual data.
