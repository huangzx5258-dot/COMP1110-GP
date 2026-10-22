# Factual review of progress materials

Reviewed 20 October 2026: `progress_report.md` and `tutorial_briefing.md` against `source_audit.md`, `study/model_spec.md`, `results/summary.csv`, `results/paired_summary.csv`, and the result manifest.

**Verdict: no material numerical inconsistency, source misrepresentation, or unsupported real-world causal claim found.** The materials appropriately distinguish synthetic results, documented HKU rules, and modelling assumptions.

## Numerical checks

- The manifest confirms 300 runs and 150 pairs. Five scenarios × two conditions × 30 seeds agrees with the stated 180 main and 120 sensitivity runs.
- Baseline placement, changes, and net-utility table values for N=30/60/90 match the CSV means at the displayed precision. The N=30 values are equal only after rounding; the prose correctly says “almost identical.”
- N=60 raw utility 0.7018 versus 0.6986, net utility 0.6661 versus 0.6784, paired raw difference 0.0032, paired SD 0.0224, and 11/30 positive raw differences all match the saved summaries.
- Higher-cost changes 39.1/17.7 and net utility 0.6037/0.6698 match. Slower-refresh changes 21.4/24.2 and net utility 0.6837/0.6784 match. The slower-refresh mean net reversal and 13/30 positive paired net differences are reported accurately.
- The controlled example agrees with the model specification: visible expectation 7, hidden expectation 5. It is clearly labelled as distinct from the pilot.

## Sources, interpretation, and history

HKU FCFS, CCTM exception, personal rank and vacancy display, periodic approvals, closure to new applications, surrendered position, and separate auto-ballot are represented consistently with the audit. Frozen approved allocations, one-course demand, synthetic values, uncalibrated beliefs, no later arrivals, and omitted low-enrolment cancellation are explicit simplifications.

The report incorporates the important literature qualifications: Diebold includes a field experiment; Romero-Medina/Triossi's adjustments differ from HKU drop/rejoin; New Haven uses truncated DA; related information studies cannot predict HKU outcomes. The research-gap wording remains cautious and does not claim exhaustive coverage or first discovery.

The materials do not equate HHI with harmful herding or operation counts with SIS load. They report mean changes with variation and explicitly restrict conclusions to the chosen model. Follow-up scenarios are labelled planned rather than completed.

No invented member names, actual contributions, meeting attendance, TA feedback, or prior meeting outcomes appear. Collective first-person tutorial answers are reusable scripts for the group to adopt after reviewing the generated artefacts, as the opening instruction says; the contribution and feedback records remain blank for confirmation. The completed artefacts substantiate the technical progress described, but do not establish who personally performed it.

No correction required from this factual review. Figure rendering, document pagination, and independent test execution were outside this review.
