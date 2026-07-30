# Remote Leverage — Data Analyst

**Interview: Monday 3 August 2026 · Language: English · Compensation band: $1,920–2,080/month**

Remote Leverage is a Florida-based virtual-assistant placement agency recruiting English-speaking VAs from Latin America and the Philippines, on a **one-time flat fee** model with the VA paid directly by the client. This role is **in-house** — you would be measuring their own funnel: client acquisition, open requisitions, candidate pipeline, ad spend.

---

## Read in this order

| # | File | Read when | Why |
|---|---|---|---|
| 00 | [Plan and cheat sheet](00_prep_plan_and_cheatsheet.md) | **Start here** | Company brief, gap analysis, the five-day plan, key numbers |
| 01 | [Recruiting, sales & marketing metrics](01_recruiting_sales_marketing_metrics.md) | Wed evening | The vocabulary you don't have yet — funnel, time-to-fill, CAC, censoring |
| 02 | [BigQuery for analysts](02_bigquery_for_analysts.md) | Thursday | Cost control, partitioning, `COUNTIF`/`QUALIFY`/`MERGE`, dialect table |
| 03 | [Tableau in five days](03_tableau_in_five_days.md) | Friday | LOD, order of operations, extract vs live, Power BI → Tableau map |
| 04 | [Positioning and mock interview](04_positioning_and_mock_interview.md) | Saturday | 90-second pitch, CV coherence, honest answers, full mock |
| 05 | [SQL drills with answers](05_sql_drills_with_answers.md) | Sunday | Twelve drills, verified outputs — self-check |
| 06 | [Sales lens and objection handling](06_sales_lens_and_objections.md) | Saturday | Rep-level sales metrics, and the "you've never worked in sales" objection |
| 99 | [During-call one pager](99_during_call_one_pager.md) | **Monday only** | One screen to keep open while you talk |

The cheat sheet (00) is for Sunday revision. The one-pager (99) is for the call itself. Do not confuse them.

---

## The practice dataset

`practice/` holds 18 months of a simulated VA-placement agency — the business Remote Leverage actually runs.

```bash
pip install duckdb
python3 -c "import duckdb; con=duckdb.connect('practice/agency.duckdb'); print(con.sql('SHOW TABLES'))"
python3 practice/build_dataset.py     # regenerate from scratch (deterministic)
```

| Table | Rows | Grain |
|---|---|---|
| `marketing_spend` | 1 716 | day × paid channel |
| `leads` | 3 933 | inbound enquiry, with owner and deal stage |
| `sales_reps` | 5 | closer, with monthly quota |
| `sales_activities` | 26 564 | call, email or demo logged by a rep |
| `clients` | 327 | converted client |
| `vacancies` | 709 | requisition |
| `candidates` | 4 240 | registered candidate |
| `submittals` | 3 918 | candidate presented to a vacancy |
| `interviews` | 1 835 | interview scheduled |
| `placements` | 347 | successful hire |
| `pipeline_runs` | 3 432 | ETL job execution |

`practice/csv/` holds the same tables as CSV — **Tableau Public opens these directly**, which is what the Friday and Saturday build uses.

Seven data-quality defects are injected deliberately (orphan placements, impossible dates, duplicates, missing campaign attribution) so the "validation and reconciliation" responsibility can be *demonstrated* rather than described. They are documented in [module 01](01_recruiting_sales_marketing_metrics.md) §9 and drilled in [module 05](05_sql_drills_with_answers.md) D6.

---

## Your three gaps, and where each is addressed

| Gap | Severity | Where |
|---|---|---|
| **Tableau** — not on your CV, first responsibility in the posting | Decisive | [03](03_tableau_in_five_days.md) — honest script + weekend build |
| **Domain vocabulary** — your language is MEAL, theirs is sales/recruiting | Decisive | [01](01_recruiting_sales_marketing_metrics.md) · [06](06_sales_lens_and_objections.md) |
| **No commercial-sector experience** — the objection you'll actually get | Decisive | [06](06_sales_lens_and_objections.md) |
| **Positioning** — titles read "engineer" and "M&E", not "Data Analyst" | Decisive | [04](04_positioning_and_mock_interview.md) |
| BigQuery as analyst rather than pipeline engineer | Likely probed | [02](02_bigquery_for_analysts.md) |
| n8n — none | Minor, preferred only | [04](04_positioning_and_mock_interview.md) §6 |
| Spoken English unrehearsed | Real risk | [04](04_positioning_and_mock_interview.md) §8 |

Data quality, pipeline monitoring, Git and secure AI use are **existing strengths** — they need repackaging in commercial language, not learning.

---

## Related files outside this folder

Tailored CV for this application, in Markdown, DOCX and PDF:
`../../curiculum-vitae-and-letter/specific_situation/remoteleverage_data_analyst/outputs/`

Source of truth for every factual claim: `../../curiculum-vitae-and-letter/alexandrodislaResume.tex`.

---

## Conventions

Every number quoted in these modules was produced by executing the query shown against `practice/agency.duckdb`; 14 headline figures are re-verified after any dataset rebuild. Prefix them in conversation with *"in the dataset I've been practising on…"* — they are realistic, not real.
