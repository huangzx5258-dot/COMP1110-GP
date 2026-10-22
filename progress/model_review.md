# Model review

Verdict: core simulation matches the supplied design on inspection; no critical queue, information-leak, or RNG-pairing defect found. Reviewed only `study/model.py` and `study/tests/test_model.py`; did not edit either file or rerun the already passing suite.

## Findings

1. **Metric interpretation: `information_checks` counts hidden-arm scheduled checks too.** Each decision logs `information_check = int(fresh)` regardless of condition, and the summary adds these to `simulated_operations`. Hidden agents never receive a rank, so these totals cannot be described as actual rank queries or measured system load. They are a modeled scheduled checking proxy (plus two operations per switch). If reporting rank-query counts, count only actual visible refreshes; if reporting common public-status polling, explicitly document that assumption. The model does not measure server work or latency.

2. **Coverage gap for the most delicate information rule.** Existing tests verify hidden observations avoid `rank`, and exercise interval 3, but do not assert course-specific stale-rank invalidation or the exact refresh cadence. The implementation appears correct (`cache.pop` on switching, course match in `observe`), yet a regression could pass all current tests. Add a targeted deterministic case where a visible agent switches between refreshes and must receive no old-course rank until the next refresh.

3. **Coverage gap for synchronous execution and shared commit ordering.** Source inspection confirms planning precedes all commits, commits precede approval, and full-population commit permutations depend only on seed and tick. The pairing test checks population hash and reproducibility, but does not verify these timing guarantees. A small crafted case with simultaneous departures/arrivals and approval would protect the main experimental mechanism.

## Confirmed design constraints

- True current rank is requested only for visible pending agents on refresh ticks; hidden policy receives no true queue sizes or alternative ranks.
- Both conditions use the same seeded population, arrival order, and full-population commit permutations.
- Switching applies only to pending applications, resets timestamps, and cannot remove approved placements.
- Vacancy means capacity minus approvals; pending queues may exceed capacity, as required.
- Forecasts use public approval counts and subjective priors, not future simulated outcomes. The departure parameter affects beliefs only.
- Deadline purge is explicitly logged; the reported HHI is pending-queue concentration, not enrolment concentration. `peak_pending_hhi` excludes the initial snapshot and includes only post-decision states, so label it accordingly.

## Focused follow-up review

Verdict: the original focused findings are resolved. Separate `scheduled_status_checks` and `rank_refreshes` now distinguish the common polling proxy from actual rank disclosure; `simulated_operations` explicitly combines scheduled checks with two operations per switch. New deterministic tests assert the exact course/rank/age sequence after a switch between refreshes and assert decisions precede commits and approvals. No further important model issue found on inspection.

Also reviewed `study/run_study.py`. Per-seed visible-minus-hidden differences are computed before aggregation, summaries use sample standard deviations across seeds/pairs, population hashes are checked, and exports preserve scenario/seed/condition identifiers. Resolved parameters and file hashes are exported. No important aggregation, pairing, or export defect found for the current pilot. This was a source review; I did not rerun the reported 15 passing tests or the 300 runs.

The interpretation constraints remain: operation counts are a stipulated proxy, probability forecasts are subjective, and peak HHI refers to pending queues after decisions. Those are reporting limitations rather than unresolved implementation defects.
