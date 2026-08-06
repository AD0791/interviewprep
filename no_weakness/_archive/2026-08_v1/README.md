# Archive — no_weakness v1 (August 2026)

This material is **superseded**. It must never be linked from a live module, and nothing in it should be copied into new writing — not the prose, not the structure, and not the voice.

It exists for exactly one reason: it is the provenance record for [`MEASUREMENTS.md`](../../MEASUREMENTS.md). Six modules were written here, and every number in them came out of a real terminal. Those figures are the asset. Mining them out of git history would have been possible but genuinely painful — you cannot grep across a set of blobs, and no agent opening this folder would think to look.

**This directory is deleted at the Phase 3 gate**, on one condition: every figure in it has been transferred into `MEASUREMENTS.md` with an ID, its original environment string, and either a re-run result or a `measured-stale-env` tag.

## What is here

| Path | What it was |
|---|---|
| `v1_plan_README.md` | The v1 plan document — the depth ladder, the module anatomy, the build order. Renamed on archiving so it would not collide with this notice |
| `00_self_assessment.md` | 62 diagnostic questions in six sections. **Never filled in**, which is why v1 built blind |
| `RECALL.md` | Hand-maintained cold-recall list; had already drifted from the modules it summarised |
| `01_python/` | Two modules: async execution model, concurrency threads and processes |
| `02_sql/` | One module: indexes and the query planner |
| `03_js_ts/` | Two modules: event loop and microtasks, the type system |
| `04_mongodb/` | One module: document modelling and indexes. The one weak module, and it says so in its own header — no local `mongod` was available, so its plans and timings were stated from documentation rather than measured |
| `video_syllabi.md` | Transcription of the four `assets/` screenshots, which have been deleted |

## Why it was replaced rather than extended

The writing was good. Six modules at three to four thousand words each, structurally identical, with negative results reported honestly and vendor caveats placed where a stale claim would embarrass. That is above the bar for what most senior candidates ever write for themselves.

What failed was the ratio. Thirty-five modules were listed and six were written. The diagnostic that was supposed to direct the work sat blank for the folder's entire life. Three of seven promised directories were never created, including the cross-cutting capstone that the v1 README itself called the biggest available differentiator. And the style contract that would have stopped the next agent from producing beginner material was argued for at length in its §4 and then never written down.

The rebuild starts from a written contract ([`AGENTS.md`](../../AGENTS.md)), a seven-topic structure, and a scope that was cut deliberately at the start rather than by attrition at month four.

## The environment caveat that matters most

Every measurement in this archive was produced on **CPython 3.10.12, four cores**, and Node **v22.22.3**. The current machine is CPython **3.14.6, eight cores**, Node **v20.20.2**. These are not interchangeable. The process-pool scaling story in particular changes shape between four and eight cores, and CPython's specialising adaptive interpreter landed in 3.11, which moves bytecode-level timings materially.

Figures carried forward without a re-run are tagged `measured-stale-env` and must name the original environment wherever they are quoted.
