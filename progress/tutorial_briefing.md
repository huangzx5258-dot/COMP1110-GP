# Tutorial Progress Briefing

**English answers and Chinese explanation | 20 October 2026**

Use the statements below after reviewing the model and saved results as a group. They describe completed artefacts and do not assign unverified past work to particular members.

## 1 What was the last thing your team accomplished

Our most recent completed task was a matched pilot of the simulation in our proposal. We specified the queue rules, added visible and hidden rank conditions, and checked the program against a hand-calculated example. We then completed 300 runs. In the 60-student baseline, the visible condition produced 42.8 course changes per run, compared with 24.2 under hidden ranks. Placement was slightly higher, but net utility after change costs was lower. This is a preliminary finding within our synthetic model, rather than evidence about actual HKU student behaviour.

## 2 What is the next task your team plans to undertake

Our next task is to test whether these patterns survive changes to the belief assumptions. We will vary how students estimate course demand and the likelihood that people ahead leave. We will also compare simultaneous decisions with students acting one at a time. Each comparison will use the same synthetic students in both information conditions. This should help us distinguish a result that depends on one forecasting rule from a pattern that persists across several reasonable settings.

## 3 Are there any obstacles your team has encountered

The main obstacle is that we do not have real HKU queue logs or measured student beliefs, so we cannot calibrate the probability estimates directly. We have made those estimates explicit and started sensitivity checks. We also simplify the system to one requested course per student and stop strategic changes after approval. These assumptions keep the model manageable, but limit its realism. We can compare outcomes inside the model; we cannot infer actual SIS congestion from the number of simulated operations.

Approximate answer lengths: 87, 77, 81 words. Rehearse each for about 30-45 seconds and keep the units clear: changes per complete run, not changes per student.


<!-- page break -->

## 中文讲解与数字口径

### 第一题的回答逻辑

先说最近完成了什么：把 proposal 里的想法做成了可运行的模型，再完成了配对试验。接着给一个实际结果，并立即说明结果只属于合成模型。不要声称已经观察或证明了真实 HKU 学生的行为。

| 数字 | 准确含义 |
| --- | --- |
| 300 次运行 | 5 个情景 × 2 种信息条件 × 30 个种子；不是 300 名真实学生。 |
| 42.8 与 24.2 | 60 人基准情景中，每次完整运行的平均改选总次数。 |
| 75.0% 与 73.9% | 可见组与隐藏组的平均获批比例；总名额为 45。 |
| 0.6661 与 0.6784 | 扣除每次 0.05 改选成本后的平均净收益，包含最终没选到课的人。 |
| 13 / 30 | 慢更新情景中，可见组净收益高于隐藏组的配对数；平均差变正不代表每次都更好。 |

### 第二题的回答逻辑

我们已完成成本提高和排名慢更新两个初步检查。下一步改的是学生怎样猜测录取机会，以及学生是否同时行动。每次只改变一个条件，保持两组的学生和偏好一致，才能解释变化来自哪里。

### 第三题的回答逻辑

障碍是没有真实队列记录和学生信念数据，所以模型不能直接校准。我们采取的处理是公开假设并检查不同假设下的结果。10% 是学生预测“前面的人可能离开”的信念参数；程序没有强迫 10% 的学生随机退课。

在模型中，同一轮先算完所有学生的决定，再按共享随机顺序提交改选，最后才审批。已获批者停止改选；真实 HKU 允许获批后 drop/add，所以这是需要明确讲出的简化。

最容易混淆的三件事：排位不是录取概率；模型偏好分不是现实满意度调查；模拟操作数不是 SIS 服务器负载。


<!-- page break -->

## Likely follow up questions

**What exactly differs between the conditions?**

Only access to the latest own queue rank. Public vacancies, course values, decision rules, initial students and random commit order are matched. Neither arm receives the true queue for another course.

**How do hidden students make a decision?**

They use the synthetic course-popularity prior to estimate pending demand, treat their possible positions as equally likely, and average the next-batch admission forecasts. This is a documented heuristic, not an empirically measured belief.

**Does seeing rank make students irrational?**

We have not tested that claim. Every modeled switch improves estimated next-batch benefit at the time of choice. Realised benefit can be worse because forecasts omit future responses and many students act together.

**Does visibility help at all?**

Yes in the controlled two-student example. In the 60-person baseline it slightly improves placement on average. However, extra changes can offset value gains when we deduct the assumed effort cost.

**Have you demonstrated herding?**

We have recorded course-level inflows, outflows and queue trajectories that allow us to examine concentration. A long queue or a high HHI by itself is insufficient, especially when very few students remain pending.

**Why not use real data?**

No administrative queue or server logs have been supplied. Synthetic data let us compare exactly matched information conditions. Obtaining real logs or a consented survey would be a separate data-access task.

**Is the 15-seat setup an actual HKU course?**

No. It is a scaled model setting. The real low-enrolment cancellation rule is excluded, as are multiple-course bundles and special priority windows. We study a mechanism, not an exact reproduction of a course.

**Why did slower rank updates reduce changes?**

In this tested setting agents responded less often to a newly disclosed rank. After changing course, an old rank is invalidated until the next query. The mean net comparison reversed, but only 13 of 30 paired comparisons favoured visibility; this is not a universal policy recommendation.

中文提醒：若被问到概率公式，打开研究进度报告的第三页；若被问到比较是否公平，说明两组使用相同学生、初始顺序和按轮次固定的提交顺序。


<!-- page break -->

## TA feedback record

Meeting date and time: ____________________   TA: ____________________

Attendees: _________________________________________________________

| Question for the TA | Actual feedback and agreed action |
| --- | --- |
| Is the one-course and pending-only revision scope suitable? | 

 |
| Is the stated belief rule technically sufficient at COMP1110 level? | 

 |
| Which robustness comparison should be prioritised next? | 

 |
| Any change needed for the Final Report or presentation? | 

 |

| Action after meeting | Owner | Due date | Evidence / status |
| --- | --- | --- | --- |
| ____________________ | ____________ | __________ | ____________ |
| ____________________ | ____________ | __________ | ____________ |
| ____________________ | ____________ | __________ | ____________ |

### Actual contribution record to be confirmed by the group

| Member | Current planned responsibility | Actual work and date |
| --- | --- | --- |
| [Member 1] | HKU rules and limitations | ___________________ |
| [Member 2] | Literature and output definitions | ___________________ |
| [Member 3] | Beliefs and information comparison | ___________________ |
| [Member 4] | Simulation and reproducibility | ___________________ |
| [Member 5] | Figures and tutorial coordination | ___________________ |

Complete this page after the actual meeting. Task ownership and past contributions must be confirmed by members; the prepared artefacts do not establish who personally completed each task.

