# Seeing the Queue: A Simulation of Course-Selection Decisions in HKU Common Core

**COMP1110: Computing and Data Science in Everyday Life**  
**Project Plan, 2026/27 Semester 1**  
**Team:** [Member 1], [Member 2], [Member 3], [Member 4], [Member 5]

## 1. Problem statement and research question

Choosing a Common Core course is a familiar decision for HKU students, but the outcome may remain uncertain after a request is submitted. During the August course-selection period, HKU timestamps Common Core requests and normally approves them on a first-come-first-served basis. Pending students can check their own queue position and the number of vacancies. They may also revise their selections before the period closes, while approval is processed several times a day (HKU Common Core, n.d.-a; n.d.-b). A student who drops a course cannot regain the former queue position (HKU Common Core, n.d.-b). These rules create a practical choice: remain in a preferred queue with an uncertain outcome, or give up that position to pursue an alternative.

**Primary research question:** *How does visibility of an individual's queue position affect course-selection strategies and the distribution of applications during HKU Common Core's first-come-first-served selection period?*

We will ask when position information helps students obtain an acceptable course or a more preferred one, and when several students responding to similar information move toward the same alternatives. The effect is not predetermined. A switch after learning that admission is unlikely may be sensible, while staying in a strong queue may also be sensible. We will compare the outcomes of these decisions, not label them “irrational” simply because they involve revision.

The study concerns the regular first-come-first-served selection period and an ordinary student's decision about one target Common Core course. HKU's designated priority periods for eligible Common Core Transdisciplinary Minor students are outside our baseline model. The later add/drop period is also outside scope because HKU uses auto-ballot there and clears the earlier waiting lists (HKU Common Core, n.d.-a). We will not design a replacement SIS, infer the behaviour of real students from simulated agents, or measure actual SIS performance.

## 2. Computing and data science connection

**Main project type: simulation/modelling.** Our technical contribution will be a small, reproducible model of how an information display changes decisions within a capacity-constrained, timestamp-ordered queue. A simulation is appropriate because we can hold course offerings and student preferences constant while changing only whether an agent sees their position. A real comparison between two otherwise identical HKU selection periods is not available to us.

The model will contain a fixed number of synthetic students, initially about 40–150, and two to five courses. Each course has a capacity. Each student has a ranked set of acceptable courses, a value for each course, a current request and its timestamp, and a small cost for making a change. To keep the decision clear, each simulated student seeks one course place. This is a modelling choice: actual HKU students may select multiple Common Core courses within curriculum limits (HKU Common Core, n.d.-b). Students may move only to an eligible course that is open to new requests under the model's current state.

At each simulated decision point, requests are ordered by timestamp. Some requests are approved, vacancies and ranks are updated, and pending students decide whether to stay or move. We will model the published feature that approval occurs in batches, without assuming an undocumented exact schedule. Dropping a request removes it from its queue; a later request receives a new timestamp. This makes the loss of an earlier position an explicit consequence of switching, separate from the small effort cost.

We will compare two **counterfactual information conditions**. In the *visible* condition, an agent sees their position and vacancies. In the *hidden* condition, the agent sees vacancies and their approval status but not their exact position. Both conditions use the same course capacities, student preferences, initial arrival times, decision opportunities, and random events. This isolates the effect of position visibility rather than changing every part of the interface at once. HKU currently provides position information; the hidden condition is a research comparison, not a description of current SIS.

Each agent estimates a chance of admission from the information available to them. This estimate is a belief within the model, **not** a probability issued by HKU or a guarantee implied by rank. For a pending student considering course *j*, estimated benefit is the student's value for *j* multiplied by the estimated admission chance. The student switches only when the highest estimated benefit at an eligible alternative, minus the effort cost of changing, exceeds the estimated benefit of staying. Receiving no course has value zero. We will show the rule in plain language and a small worked example in the Final Report. We do not need to solve a full game-theoretic equilibrium.

For each run, the model records three primary outcomes: **mean realised preference value**, **number of course changes**, and **concentration of active requests** across courses. Concentration will be reported alongside demand per available seat so that a large course is not treated like a small one. Secondary outcomes are the share of students receiving an acceptable course, the share receiving none, and the number of scheduled information checks and request changes in the model. The last measure is only a proxy for potential interaction volume; it is not a measure of server congestion.

We will run matched visible and hidden simulations across several random seeds. The main scenarios vary the student-to-seat ratio, how attractive the alternatives are, and the effort cost of changing. Further checks vary how often agents receive updated information and whether their admission estimates are optimistic, pessimistic, or approximately calibrated. Comparing distributions of outcomes, rather than one example run, will show whether a pattern is stable. A short trace of one student and one queue will make the mechanics understandable to readers without simulation experience.

## 3. Literature and background review

**The local mechanism.** HKU's published guidance establishes the features that the model must respect: time-stamped first-come-first-served requests in the ordinary selection period, visible queue position and vacancies, periodic approval, and a separate auto-ballot rule in add/drop (HKU Common Core, n.d.-a). Its FAQ clarifies that a dropped course does not retain its queue place and that being on a waiting list does not guarantee approval (HKU Common Core, n.d.-b). These documents describe procedure, not how many students change selections or how the interface affects outcomes.

**Course allocation and strategy.** Budish and Cantillon (2012) use theory and field evidence from Harvard Business School to show that a course-allocation mechanism can induce strategic reports with welfare costs. Their setting is a draft rather than a visible, timestamped queue. Diebold et al. (2014) review course allocation through matching and discuss the incentive problems of first-come-first-served approaches. Their comparison concerns allocation mechanisms, not the information shown to students during repeated revisions. More recently, Romero-Medina and Triossi (2024) examine strategic course allocation and a post-allocation adjustment mechanism. Their mechanism uses priorities and conditional acceptance, so its results cannot be imported as predictions about HKU's selection queue. Together, these studies make students' responses to allocation rules a serious research issue, while leaving our proposed information comparison open.

**Information and application patterns.** Arteaga et al. (2022) study school-choice platforms that provide personalised feedback about placement risk. They find that such feedback can improve search and placement in the systems they study. This is a reason to test beneficial effects of visibility rather than assume harm. Their platforms do not display a position in a university course queue. Sato and Shirakawa (2025) model how information about admissions priorities changes applications across colleges. Their theoretical result links disclosure to application distribution, but their students do not repeatedly leave and rejoin a timestamped course queue. In another setting, Zou et al. (2026) use simulation to find that the quality and update frequency of announced hospital waiting-time information affect whether demand is redistributed helpfully or crowding worsens. Hospital queues differ from course requests; this study motivates our sensitivity tests, not a forecast for HKU.

This review finds substantial work on course allocation, strategic behaviour, and admissions information. It finds less work directly addressing **the combination** of personal queue-position visibility, timestamped first-come-first-served ordering, loss of a surrendered position, and repeated course-choice revision. Our project contributes a bounded comparison of that combination. We do not claim to be the first to study information in allocation systems, and our simulation will support conditional statements about its assumptions rather than causal statements about real HKU students.

## 4. Feasibility, limitations, and ethics

The model needs published rules, synthetic preference lists, capacities, request arrival times, and assumptions about future withdrawals and decision costs. HKU's official guidance supplies the rule description. Synthetic values will supply the rest. No queue logs, individual enrolment records, or SIS access are required. The implementation can be a short event-based simulation in Python or another familiar language; the substantive work is specifying the rules, checking that they are applied consistently, comparing matched conditions, and interpreting outcomes. A hand-calculated small case will be used to check queue order, seat limits, and the effect of dropping a request before larger runs.

The largest limitation is behavioural validity. We do not know students' true course values, their beliefs about admission, their willingness to switch, or how often they check SIS. A simple one-course decision also omits timetable clashes, multiple-course planning, special priority rules, and possible cancellation of low-enrolment courses. We will state these omissions explicitly and vary uncertain parameters. If the direction of an effect changes across plausible settings, that change is a result, not a failed project. Simulated operations cannot establish technical load, response time, or outages on the real SIS; actual server congestion would require performance or access logs that we do not possess.

The baseline uses no identifiable student information, so its direct privacy risk is low. We do not plan to scrape personal SIS pages. If the team later seeks surveys or interviews to check behavioural assumptions, participation would require informed consent and appropriate handling of responses; that optional activity is not needed for the core project. The Final Report will not claim that observed HKU students are irrational, that visibility causes real-world switching, or that SIS performance is affected.

## 5. Timeline and team roles

The dates below are working milestones. Course submission dates in the guidelines are tentative and should be checked on Moodle.

| Period | Milestone and responsible members |
|---|---|
| **30 Sep–4 Oct** | **[Member 1]** verifies HKU rules and scope; **[Member 2]** reviews course-allocation papers; **[Member 3]** reviews information-disclosure papers; **[Member 4]** drafts the model outline; **[Member 5]** integrates and edits the 4–6-page Project Plan. All five check references before submission. |
| **5–11 Oct** | **[Member 4]** specifies event order and queue updates with **[Member 1]**; **[Member 3]** specifies belief and switching rules; **[Member 2]** checks whether the literature gap remains accurate; **[Member 5]** prepares a small worked example. |
| **12–18 Oct** | **[Member 4]** builds the basic simulation; **[Member 3]** adds visible/hidden decision conditions; **[Member 1]** checks mechanism fidelity against HKU guidance; **[Member 2]** checks output definitions; **[Member 5]** prepares explanatory diagrams. |
| **19–25 Oct** | **[Member 2]** and **[Member 3]** design matched scenarios and sensitivity tests; **[Member 4]** runs pilot cases; **[Member 1]** records limitations; **[Member 5]** coordinates the interim progress meeting and records feedback. |
| **26 Oct–1 Nov** | **[Member 2]** analyses outcomes; **[Member 3]** checks sensitivity to beliefs and update frequency; **[Member 4]** checks reproducibility; **[Member 1]** drafts the mechanism section; **[Member 5]** drafts figures. |
| **2–8 Nov** | **[Member 1]** writes limitations and ethics; **[Member 2]** and **[Member 3]** interpret scenario comparisons; **[Member 4]** documents the model; **[Member 5]** combines report sections. Each member submits their own progress log by the course deadline. |
| **9–15 Nov** | All five review the Final Report and references. **[Member 5]** completes editing; **[Members 1–4]** verify their respective rules, literature, model, and results sections. |
| **16–26 Nov** | **[Member 5]** structures the 10-minute presentation. **[Members 1–4]** each present their assigned section. All five rehearse and answer questions. |

## References

Arteaga, F., Kapor, A. J., Neilson, C. A., & Zimmerman, S. D. (2022). Smart matching platforms and heterogeneous beliefs in centralized school choice. *The Quarterly Journal of Economics, 137*(3), 1791–1848. https://doi.org/10.1093/qje/qjac013

Budish, E., & Cantillon, E. (2012). The multi-unit assignment problem: Theory and evidence from course allocation at Harvard. *American Economic Review, 102*(5), 2237–2271. https://doi.org/10.1257/aer.102.5.2237

Diebold, F., Bichler, M., Matthes, F., Schneider, A., & Aziz, H. (2014). Course allocation via stable matching. *Business & Information Systems Engineering, 6*(2), 97–110. https://doi.org/10.1007/s12599-014-0316-6

HKU Common Core. (n.d.-a). *Common Core course selection*. https://commoncore.hku.hk/cccourseselection/

HKU Common Core. (n.d.-b). *Frequently asked questions on Common Core*. https://commoncore.hku.hk/faqs/

Romero-Medina, A., & Triossi, M. (2024). Strategic priority-based course allocation. *Journal of Economic Behavior & Organization, 226*, 106701. https://doi.org/10.1016/j.jebo.2024.106701

Sato, H., & Shirakawa, R. (2025). Information structures in college admissions. *Journal of Economic Behavior & Organization, 240*, 107322. https://doi.org/10.1016/j.jebo.2025.107322

Zou, C., Zhang, Y., Ouyang, H., & Sun, Z. (2026). Impact of announced wait time information on emergency department overcrowding mitigation: A simulation study. *Journal of the American Medical Informatics Association, 33*(6), 1112–1120. https://doi.org/10.1093/jamia/ocag036
