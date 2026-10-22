# Final verification record

Completed 20 October 2026. All evidence is synthetic.

## Automated tests

```text
test_analytic_rank_cases (test_model.ProbabilityTests.test_analytic_rank_cases) ... ok
test_tail_uses_common_prior (test_model.ProbabilityTests.test_tail_uses_common_prior) ... ok
test_ties_stay (test_model.ProbabilityTests.test_ties_stay) ... ok
test_capacity_and_closed_course (test_model.QueueTests.test_capacity_and_closed_course) ... ok
test_hidden_observation_does_not_request_rank (test_model.QueueTests.test_hidden_observation_does_not_request_rank) ... ok
test_rejoining_loses_timestamp (test_model.QueueTests.test_rejoining_loses_timestamp) ... ok
test_all_decisions_precede_commits_and_approvals (test_model.SimulationTests.test_all_decisions_precede_commits_and_approvals) ... ok
test_capacity_across_conditions_and_slow_queries (test_model.SimulationTests.test_capacity_across_conditions_and_slow_queries) ... ok
test_check_metric_distinguishes_rank_disclosure (test_model.SimulationTests.test_check_metric_distinguishes_rank_disclosure) ... ok
test_pairing_and_reproducibility (test_model.SimulationTests.test_pairing_and_reproducibility) ... ok
test_switch_invalidates_rank_until_next_scheduled_refresh (test_model.SimulationTests.test_switch_invalidates_rank_until_next_scheduled_refresh) ... ok
test_two_student_worked_example (test_model.SimulationTests.test_two_student_worked_example) ... ok
test_unsupported_configuration_rejected (test_model.SimulationTests.test_unsupported_configuration_rejected) ... ok
test_pilot_has_300_runs (test_runner.RunnerTests.test_pilot_has_300_runs) ... ok
test_small_suite_exports_matched_evidence (test_runner.RunnerTests.test_small_suite_exports_matched_evidence) ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.030s

OK
```

## Export audit and complete rerun

```text
PASS: All saved hashes match; every evidence file matches the independent rerun.
PASS: All 300 run summaries agree with unique student records, capacities, allocation values and costs.
PASS: All 150 visible/hidden pairs contain identical student preferences and initial courses.
PASS: No hidden-condition decision record contains a disclosed rank or rank age.
PASS: Events conserve switching flows, renew timestamps, approve students once and respect capacities at every saved phase.
PASS: The four worked-example outcomes equal the hand calculations: 10, 10, 4 and 0.
```

The rerun is a reproducibility check and is not counted as another 300 experimental samples. The optional full comparison command was `python3 -m study.verify_evidence --repeat tmp/repro_results`; the temporary rerun is not packaged. Use `python3 -m study.verify_evidence` to recheck packaged evidence.

## Documents and citations

- All eight report pages and four briefing pages visually inspected after final rendering: no clipping, unintended blank pages, missing Chinese glyphs or broken table rows found.
- Report PDF has 8 pages; briefing PDF has 4 pages. Chinese text is extractable from the exported briefing PDF.
- Report and briefing numbers checked against saved summary/paired summary/worked example CSVs; see materials_review.md.
- Eight sources audited against primary publisher, institutional or author records. Access limits and unknown HKU details are recorded in source_audit.md.
- Original proposal files retained. Actual TA feedback and individual contributions remain to be filled after confirmation.

## Final document SHA256

- `progress/progress_report.docx`: `cf6245a042ac85117f4a7ef3c82e44477f92d32df65e056d6ae43f31ffce9aa7`
- `progress/progress_report.pdf`: `ce48ff0b8af41566ae862cc83f14165389f7983e132d45150ad61ec8f76edcce`
- `progress/tutorial_briefing.docx`: `2be642bdbb4fa56a9dc05840abf7ff345d832927cfb52411e364610100328cf8`
- `progress/tutorial_briefing.pdf`: `5a47882bce1fdefa147e8cfa0c81facae291b8d162713b76b7f6e025760def52`
