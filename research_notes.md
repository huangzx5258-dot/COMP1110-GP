# Research notes and proposal outline

Research checked on 30 September 2026. These notes distinguish documented HKU rules, findings from other settings, and assumptions proposed for our simulation. They are not evidence of actual HKU student behaviour.

## Verified HKU mechanism and necessary corrections

- HKU's Common Core course-selection period uses time-stamped requests and, apart from designated priority periods for eligible Common Core Transdisciplinary Minor students, first-come-first-served approval. Students can see their own queue position and the number of vacancies, and can change selections while the period is open. Approval runs several times a day. Source: [HKU Common Core Course Selection](https://commoncore.hku.hk/cccourseselection/) and [HKU Common Core FAQs](https://commoncore.hku.hk/faqs/).
- Pending requests that are not approved because of oversubscription form a ranked waiting list. The lists are purged after the course-selection period. A student who drops a course cannot recover the former queue position. The FAQ also says a direct swap is unavailable; changing an approved course requires dropping and adding. Source: [HKU FAQs](https://commoncore.hku.hk/faqs/).
- The later add/drop period uses auto-ballot, not the same FCFS rule. It is excluded from the model. The CCTM priority period is also excluded from the baseline. Source: [HKU Common Core Course Selection](https://commoncore.hku.hk/cccourseselection/).
- A rank is not a guaranteed probability of admission. Future vacancies, approvals, and students' decisions matter. Our probability estimates are model assumptions, not HKU forecasts.
- HKU permits more than one Common Core course subject to curriculum limits. The model's one-target-course student is an abstraction for one course-choice decision, not a claim about SIS restrictions. Source: [HKU FAQs](https://commoncore.hku.hk/faqs/).
- HKU states that courses with fewer than 20 enrollments at the end of the selection period may be cancelled. We exclude this rule from the baseline and identify it as a limitation. Source: [HKU Common Core Course Selection](https://commoncore.hku.hk/cccourseselection/).

## Literature and source annotations

1. **HKU Common Core.** [Common Core Course Selection](https://commoncore.hku.hk/cccourseselection/). Official institutional source; no DOI. **Supports:** queue visibility, vacancies, time-stamped FCFS requests, periodic approval, CCTM exception, waiting-list purge, separate auto-ballot add/drop. **Limit:** describes rules, not measured behavioural effects. **Gap role:** fixes the actual setting and identifies the combination of mechanisms to model.

2. **HKU Common Core.** [Frequently Asked Questions on Common Core](https://commoncore.hku.hk/faqs/). Official institutional source; no DOI. **Supports:** timestamp ordering, advice to check one's position, loss of original place after dropping, inability to swap an approved course directly, approval uncertainty. **Limit:** not an empirical analysis of switching or congestion. **Gap role:** justifies a queue-exit cost and prevents treating rank as a guarantee.

3. **Budish, E., & Cantillon, E. (2012).** [The multi-unit assignment problem: Theory and evidence from course allocation at Harvard](https://doi.org/10.1257/aer.102.5.2237). *American Economic Review, 102*(5), 2237–2271. DOI: 10.1257/aer.102.5.2237. **Question/result:** studies a Harvard Business School draft mechanism with theory and field data; finds strategic manipulation and welfare costs, while noting its welfare can still exceed a strategy-proof alternative. **Relation:** shows that student strategies and allocation quality must be analysed together. **Does not study:** HKU's FCFS queue, personal position display, or repeated switching under that display.

4. **Diebold, F., Bichler, M., Matthes, F., Schneider, A., & Aziz, H. (2014).** [Course allocation via stable matching](https://doi.org/10.1007/s12599-014-0316-6). *Business & Information Systems Engineering, 6*(2), 97–110. DOI: 10.1007/s12599-014-0316-6. **Question/result:** surveys course-allocation mechanisms, including FCFS and matching-based alternatives, with discussion of stability and incentives. **Relation:** provides the mechanism-design background and a warning against treating FCFS as strategically neutral. **Does not study:** rank visibility as an information treatment in a revisable HKU-style queue.

5. **Romero-Medina, A., & Triossi, M. (2024).** [Strategic priority-based course allocation](https://doi.org/10.1016/j.jebo.2024.106701). *Journal of Economic Behavior & Organization, 226*, 106701. DOI: 10.1016/j.jebo.2024.106701. **Question/result:** develops a conditional-acceptance course-allocation mechanism and a repeated adjustment variant under strategic students and priorities. **Relation:** confirms that adjustment behaviour is a substantive feature of course-allocation models. **Does not study:** FCFS timestamp queues or visibility of an individual's live position; its mechanism is different from HKU's.

6. **Arteaga, F., Kapor, A. J., Neilson, C. A., & Zimmerman, S. D. (2022).** [Smart matching platforms and heterogeneous beliefs in centralized school choice](https://doi.org/10.1093/qje/qjac013). *The Quarterly Journal of Economics, 137*(3), 1791–1848. DOI: 10.1093/qje/qjac013. **Question/result:** studies live, personalised feedback about school-placement risk; experimental and quasi-experimental evidence indicates that feedback changes search and can improve placement. **Relation:** directly challenges an assumed harmful effect of greater visibility; supports comparing benefits and costs. **Does not study:** university courses, FCFS queue ranks, or loss of place after leaving a queue.

7. **Sato, H., & Shirakawa, R. (2025).** [Information structures in college admissions](https://doi.org/10.1016/j.jebo.2025.107322). *Journal of Economic Behavior & Organization, 240*, 107322. DOI: 10.1016/j.jebo.2025.107322. **Question/result:** models how information about priority order shapes applications across colleges and equilibrium distributions. **Relation:** supports treating position disclosure as an information condition with distributional effects. **Does not study:** observed HKU enrolment behaviour or students revising timestamped course queues over time.

8. **Zou, C., Zhang, Y., Ouyang, H., & Sun, Z. (2026).** [Impact of announced wait time information on emergency department overcrowding mitigation: A simulation study](https://doi.org/10.1093/jamia/ocag036). *Journal of the American Medical Informatics Association, 33*(6), 1112–1120. DOI: 10.1093/jamia/ocag036. **Question/result:** a simulation in another queueing setting finds that information quality and update frequency affect whether announcements redistribute demand helpfully or worsen crowding. **Relation:** motivates sensitivity tests for update frequency and belief accuracy, and a balanced hypothesis. **Does not study:** educational admissions or SIS/server performance; its numerical results cannot be transferred to HKU.

### Research-gap assessment

Searches covered combinations of “queue position”, “visibility”, “course registration”, “waitlist”, “switching”, “first come first served”, course-allocation mechanisms, information disclosure, and matching markets. This is a targeted search, not a systematic review. The located work strongly covers strategic course allocation, school-choice information, and feedback in other queues. We did not locate a study directly testing the joint effect of individual rank visibility, timestamped FCFS ordering, loss of a surrendered queue place, and repeated revision in HKU Common Core selection. The defensible claim is **limited direct work found on this combination**, not that the topic has never been studied. A directly comparable paper found later would require narrowing or revising the gap.

## Detailed proposal outline and rubric alignment

1. **Title and five members:** concise title names visibility, strategy, application distribution, and HKU Common Core. Placeholders used because names are unavailable. *Clarity; format; roles.*
2. **Problem and one question:** explain HKU's August FCFS period, the visible information, revisions, periodic approvals, and the uncertainty of admission. State one primary question and two measurable aspects (student outcome and demand distribution). Exclude add/drop, CCTM priority window, real SIS performance, and design of a replacement platform. *Clarity 25%; creativity 25%.*
3. **Computing link:** main type is simulation/modelling. Define students, courses, capacities, timestamp queues, information states, decision rule, update/approval events, and synthetic runs. Compare matched visible/hidden runs, with the same student preferences and random events. Give primary metrics: average realised preference utility, switch count, and demand concentration; secondary placement and operation metrics. *Computing 25%.*
4. **Literature review:** group the eight sources into (a) HKU rules, (b) course allocation and strategic revision, (c) information disclosure and feedback. Finish with cautious gap statement. *Creativity 25%; academic format 10%.*
5. **Feasibility, limitations, ethics:** synthetic data and official rules suffice; no administrative logs required. Mark behaviour and probability estimates as assumptions. Sensitivity analysis on scarcity, alternatives, costs, and information timeliness. No real SIS load inference. No personal data by default. *Feasibility 10%.*
6. **Timeline and five named placeholder roles:** Sep 30–Oct 4 planning; Oct–Nov model, implementation, checks, experiments, report, presentation. Allocate each member an identifiable analysis or writing component; spread technical work across Members 2–4. *Roles 5%.*

### Pre-writing rubric check

- Creativity: eight verified sources, including close work with distinct mechanisms; claim only a narrow gap.
- Computing: technical core is a reproducible stochastic simulation, not the name of a programming language.
- Clarity: one question and explicit exclusions; no assumption that visibility harms students.
- Feasibility/ethics: bounded synthetic model, no claimed access to private records.
- Format: six recommended headings, consistent author-year citations and full references.
- Roles: dated milestones and separate deliverables for all five members.
