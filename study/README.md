# HKU Common Core queue visibility pilot

Completed 20 October 2026. This is a small synthetic simulation for COMP1110, not an implementation of SIS. No real student or server records are used. The original proposal is retained in the workspace root.

## Run the study

From the workspace root, using Python 3.10 or newer:

```bash
python3 -m unittest discover -s study/tests -v
python3 -m study.run_study --config study/configs/pilot.json --output progress/results
python3 -m study.verify_evidence
```

The simulator and tests need only Python's standard library. The default pilot has 300 runs (150 matched pairs): three student counts and two additional sensitivities, each with 30 seeds in both information conditions. CSVs can be opened in a spreadsheet or text editor. Opening a CSV in Excel is optional.

To change assumptions, copy the JSON configuration and change scenario overrides. Supported parameters are documented in `model_spec.md`. Keep the same seeds in both arms. Never replace synthetic parameters with claims about actual HKU behaviour.

## Files to read first

- `progress/tutorial_briefing.docx` / `.pdf`: English answers, Chinese explanation, likely follow-up questions and a blank TA feedback page.
- `progress/progress_report.docx` / `.pdf`: complete English methods and results report.
- `progress/source_audit.md`: primary-source checks and documented/simplified/unknown rule matrix.
- `study/model_spec.md`: exact algorithm, forecasts, measurement and limitations.
- `progress/results/summary.csv`: mean and SD for each condition and scenario.
- `progress/results/paired_summary.csv`: differences within the 30 matched pairs.

## Evidence outputs

| File | Unit of observation and purpose |
|---|---|
| `runs.csv` | One complete run; seed, arm, population hash and final outcomes |
| `students.csv` | One student in one run; values, allocation, switches, raw and net utility |
| `decisions.csv` | One pending revising student at one tick; only the information supplied to the policy, forecasts and decision |
| `events.csv` | Actual switch, approval or expiry; old/new timestamps permit tracing loss of position |
| `rounds.csv` | One course at a recorded phase; queue length, approvals, vacancies and concentration |
| `flows.csv` | One course per tick per run; arrivals and departures due to switching, including zeros |
| `summary.csv` | Mean and sample SD across seeds; synthetic variation, not uncertainty about real students |
| `paired_differences.csv` | Visible minus hidden for each metric and shared seed |
| `paired_summary.csv` | Mean/SD and positive/negative/zero counts among paired differences |
| `worked_example.csv` | Four hand-checkable cases for the two-person example |
| `resolved_config.json` | Every effective parameter, including defaults |
| `manifest.json` | Run counts and SHA256 hashes of result files |

Courses are numbered 0=A, 1=B, 2=C. A blank allocation means no course; a blank observed rank means no rank was disclosed or available from a valid cache. `rounds.csv` records initial state at round 0, then `after_decisions` (after all switches, before that round's approval) and `after_approval`. `deadline_purge` clears pending requests after the final approval. Counts must only be compared at the same phase.

`scheduled_status_checks` counts exogenously scheduled status-page checks in both arms; `rank_refreshes` counts actual fresh disclosures only in the visible arm. The operation index is scheduled checks + 2 x switches (drop and add). Public vacancy/status updates used by the policy every round are treated as supplied metadata; initial submissions, background system jobs, network requests, and latency are not modeled. The index is an incomplete constructed proxy, not measured load. When refresh frequency is changed, part of its reduction follows mechanically from the imposed checking schedule.

The plotting/document builder requires `python-docx`, `reportlab`, Pillow, and Poppler. These are only needed to rebuild the supplied report, not to run the simulation. Build with the bundled Codex Python runtime when working in Codex; see the printed workspace dependency paths. `python3 -m study.build_materials` regenerates Markdown, charts and Word sources from the saved CSVs. PDF export is produced from those Word documents using the document renderer to preserve the same pagination.

## Responsible interpretation

The 15-seat courses are scaled examples. HKU's real low-enrolment cancellation rule is excluded; the capacities are not empirical HKU course quotas. Approved students do not drop in this baseline, although HKU permits approved-course drop/add. The hidden-rank case is counterfactual. Forecasts are heuristic and myopic, and the next-batch departure rate is a belief, not an externally imposed withdrawal process. Do not present results as a causal estimate for HKU students, a universal benefit/harm of visibility, or evidence of actual SIS congestion.
