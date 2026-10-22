"""Timestamp queues and information-limited decisions, not an HKU SIS replica.

All probability estimates forecast the next approval under a subjective model.
They are not the simulator's true final-placement probabilities.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Config:
    n_students: int = 60
    capacities: tuple[int, ...] = (15, 15, 15)
    favourite_shares: tuple[float, ...] = (.6, .25, .15)
    alternative_values: tuple[float, float] = (.3, .8)
    switching_cost: float = .05
    expected_departure: float = .1
    rank_update_interval: int = 1
    prior_multiplier: float = 1
    n_rounds: int = 12
    approval_rounds: tuple[int, ...] = (3, 6, 9, 12)

    def __post_init__(self):
        if self.n_students < 1 or len(self.capacities) < 2 or any(c < 1 for c in self.capacities):
            raise ValueError('Need students and at least two positive course capacities')
        if len(self.favourite_shares) != len(self.capacities) or any(x < 0 for x in self.favourite_shares) or not math.isclose(sum(self.favourite_shares), 1):
            raise ValueError('Favourite shares must match courses and sum to one')
        if not 0 <= self.expected_departure <= 1 or self.switching_cost < 0 or self.prior_multiplier <= 0:
            raise ValueError('Invalid behaviour parameters')
        if self.rank_update_interval < 1 or self.n_rounds < 1:
            raise ValueError('Round counts must be positive')
        if tuple(sorted(set(self.approval_rounds))) != self.approval_rounds or not self.approval_rounds or self.approval_rounds[-1] != self.n_rounds or self.approval_rounds[0] < 1:
            raise ValueError('Approval rounds must be increasing and include the final round')
        if not 0 <= self.alternative_values[0] <= self.alternative_values[1] <= 1:
            raise ValueError('Alternative values must be within zero and one')


@dataclass(frozen=True)
class AgentSpec:
    values: tuple[float, ...]
    initial_course: int
    can_switch: bool = True


@dataclass(frozen=True)
class Observation:
    current_course: int
    vacancies: tuple[int, ...]
    approved_counts: tuple[int, ...]
    prior_pending: tuple[float, ...]
    observed_rank: int | None
    rank_age: int | None


@dataclass(frozen=True)
class Decision:
    destination: int
    stay_probability: float
    stay_benefit: float
    alternative_probabilities: tuple[float, ...]
    destination_probability: float
    destination_net_benefit: float


@lru_cache(maxsize=100000)
def probability_at_rank(rank: int, vacancies: int, departure: float) -> float:
    """P(Binomial(rank-1, 1-departure) < vacancies)."""
    if rank < 1: raise ValueError('Rank starts at one')
    if vacancies <= 0: return 0.0
    if vacancies >= rank: return 1.0
    n = rank - 1
    return min(1.0, max(0.0, sum(
        math.comb(n, k) * (1-departure)**k * departure**(n-k)
        for k in range(min(n, vacancies-1)+1))))


@lru_cache(maxsize=100000)
def probability_at_tail(prior_pending: float, vacancies: int, departure: float) -> float:
    """Poisson prior for unobserved people ahead; independent departure thinning."""
    if vacancies <= 0: return 0.0
    mean = max(0.0, prior_pending) * (1-departure)
    term = math.exp(-mean)
    total = term
    for k in range(1, vacancies):
        term *= mean/k
        total += term
    return min(1.0, total)


def choose(agent: AgentSpec, obs: Observation, cost: float, departure: float) -> Decision:
    """Only this immutable observation reaches the policy. No simulator state."""
    j = obs.current_course
    if obs.observed_rank is not None:
        p = probability_at_rank(obs.observed_rank, obs.vacancies[j], departure)
    else:
        m = max(1, math.ceil(obs.prior_pending[j]))
        p = sum(probability_at_rank(r, obs.vacancies[j], departure) for r in range(1, m+1))/m
    stay = p * agent.values[j]
    alternatives = tuple(probability_at_tail(lam, v, departure)
                         for lam, v in zip(obs.prior_pending, obs.vacancies))
    destination, best, destination_p = j, stay, p
    if agent.can_switch:
        for k, (value, chance) in enumerate(zip(agent.values, alternatives)):
            if k == j or obs.vacancies[k] == 0 or value <= 0: continue
            benefit = value * chance - cost
            if benefit > best + 1e-12:
                destination, best, destination_p = k, benefit, chance
    return Decision(destination, p, stay, alternatives, destination_p, best)


class QueueState:
    def __init__(self, capacities):
        self.capacities = tuple(capacities)
        self.pending: dict[int, tuple[int, int]] = {}
        self.enrolled: dict[int, int] = {}
        self.clock = 0

    def vacancies(self):
        return tuple(cap-self.approved_count(j) for j, cap in enumerate(self.capacities))

    def approved_count(self, course):
        return sum(j == course for j in self.enrolled.values())

    def ordered(self, course):
        return sorted((a for a, (j, _) in self.pending.items() if j == course),
                      key=lambda a: self.pending[a][1])

    def rank(self, agent):
        return self.ordered(self.pending[agent][0]).index(agent)+1

    def add(self, agent, course):
        if agent in self.pending or agent in self.enrolled: raise ValueError('Duplicate active application')
        if not 0 <= course < len(self.capacities) or self.vacancies()[course] <= 0:
            raise ValueError('Course is closed')
        self.clock += 1
        self.pending[agent] = (course, self.clock)

    def move(self, agent, course):
        if self.vacancies()[course] <= 0: raise ValueError('Course is closed')
        self.pending.pop(agent)
        self.add(agent, course)

    def approve(self):
        admitted = []
        for j, vacancy in enumerate(self.vacancies()):
            for a in self.ordered(j)[:vacancy]:
                timestamp = self.pending.pop(a)[1]
                self.enrolled[a] = j
                admitted.append((a, j, timestamp))
        self.check()
        return admitted

    def check(self):
        assert not (self.pending.keys() & self.enrolled.keys())
        assert all(v >= 0 for v in self.vacancies())
        assert len({timestamp for _, timestamp in self.pending.values()}) == len(self.pending)


def observe(state, agent, prior_pending, condition, rank_cache):
    """Hidden calls never request a true rank. Cached rank belongs to one course."""
    j = state.pending[agent][0]
    rank, age = None, None
    if condition == 'visible' and rank_cache is not None and rank_cache[0] == j:
        rank, age = rank_cache[1:]
    return Observation(j, state.vacancies(), tuple(state.approved_count(k) for k in range(len(state.capacities))),
                       tuple(prior_pending), rank, age)


@dataclass
class Result:
    summary: dict
    rounds: list[dict]
    decisions: list[dict]
    events: list[dict]
    students: list[dict]


def population(config, seed):
    rng = random.Random(f'{seed}:population')
    agents = []
    for _ in range(config.n_students):
        fav = rng.choices(range(len(config.capacities)), weights=config.favourite_shares)[0]
        values = tuple(1.0 if j == fav else rng.uniform(*config.alternative_values) for j in range(len(config.capacities)))
        agents.append(AgentSpec(values, fav))
    order = list(range(config.n_students))
    random.Random(f'{seed}:initial_order').shuffle(order)
    return agents, order


def simulate(config: Config, seed: int, condition: str, agents=None, initial_order=None) -> Result:
    if condition not in ('visible', 'hidden'): raise ValueError('Unknown information condition')
    generated_agents, generated_order = population(config, seed)
    agents = list(agents) if agents is not None else generated_agents
    order = list(initial_order) if initial_order is not None else generated_order
    if len(agents) != config.n_students or sorted(order) != list(range(len(agents))):
        raise ValueError('Population and arrival order do not match student count')
    if any(len(a.values) != len(config.capacities) or any(v < 0 for v in a.values) or not 0 <= a.initial_course < len(config.capacities) for a in agents):
        raise ValueError('Invalid agent specification')
    fingerprint = hashlib.sha256(json.dumps({'agents': [asdict(a) for a in agents], 'order': order}, sort_keys=True).encode()).hexdigest()
    state = QueueState(config.capacities)
    for a in order: state.add(a, agents[a].initial_course)
    decisions, events, rounds = [], [], []
    switches = [0]*len(agents)
    cache = {}
    snapshot_id = 0

    def snapshot(t, phase):
        nonlocal snapshot_id
        snapshot_id += 1
        counts = [len(state.ordered(j)) for j in range(len(config.capacities))]
        total = sum(counts)
        hhi = sum((q/total)**2 for q in counts) if total else 0.0
        for j, count in enumerate(counts):
            rounds.append({'round': t, 'phase': phase, 'snapshot': snapshot_id,
                           'course': j, 'pending': count, 'approved': state.approved_count(j),
                           'vacancies': state.vacancies()[j], 'pending_per_capacity': count/config.capacities[j],
                           'pending_total': total, 'pending_hhi': hhi})

    snapshot(0, 'initial')
    for t in range(1, config.n_rounds+1):
        # All policies see the same tick-start state; no true rank for alternatives.
        fresh = (t-1) % config.rank_update_interval == 0
        vacancies = state.vacancies()
        approved = tuple(state.approved_count(j) for j in range(len(config.capacities)))
        prior = tuple(max(0.0, config.prior_multiplier*config.n_students*s-approved[j])
                      for j, s in enumerate(config.favourite_shares))
        planned = {}
        for a in sorted(state.pending):
            course = state.pending[a][0]
            if not agents[a].can_switch: continue
            if condition == 'visible' and fresh:
                cache[a] = (course, state.rank(a), t)
            saved = cache.get(a)
            rank_cache = (saved[0], saved[1], t-saved[2]) if saved else None
            obs = observe(state, a, prior, condition, rank_cache)
            decision = choose(agents[a], obs, config.switching_cost, config.expected_departure)
            planned[a] = decision
            decisions.append({'round': t, 'student': a, 'current_course': course,
                              'observed_rank': obs.observed_rank, 'rank_age': obs.rank_age,
                              'vacancies': json.dumps(vacancies), 'prior_pending': json.dumps(prior),
                              'stay_probability': decision.stay_probability, 'stay_benefit': decision.stay_benefit,
                              'alternative_probabilities': json.dumps(decision.alternative_probabilities),
                              'destination': decision.destination,
                              'destination_probability': decision.destination_probability,
                              'destination_net_benefit': decision.destination_net_benefit,
                              'scheduled_status_check': int(fresh),
                              'rank_refresh': int(condition == 'visible' and fresh)})
        commit_order = list(range(len(agents)))
        random.Random(f'{seed}:commit:{t}').shuffle(commit_order)
        for a in commit_order:
            if a not in planned or planned[a].destination == state.pending[a][0]: continue
            old_course, old_stamp = state.pending[a]
            target = planned[a].destination
            state.move(a, target)
            switches[a] += 1
            cache.pop(a, None)  # Old course's rank cannot follow the student.
            events.append({'round': t, 'action': 'switch', 'student': a,
                           'from_course': old_course, 'to_course': target,
                           'old_timestamp': old_stamp, 'new_timestamp': state.pending[a][1]})
        snapshot(t, 'after_decisions')
        if t in config.approval_rounds:
            for a, course, timestamp in state.approve():
                events.append({'round': t, 'action': 'approve', 'student': a,
                               'from_course': course, 'to_course': course,
                               'old_timestamp': timestamp, 'new_timestamp': timestamp})
        snapshot(t, 'after_approval')
        state.check()
    for a, (course, timestamp) in list(state.pending.items()):
        events.append({'round': config.n_rounds, 'action': 'expire', 'student': a,
                       'from_course': course, 'to_course': None,
                       'old_timestamp': timestamp, 'new_timestamp': None})
    state.pending.clear()
    snapshot(config.n_rounds, 'deadline_purge')
    students = []
    for a, spec in enumerate(agents):
        j = state.enrolled.get(a)
        utility = spec.values[j] if j is not None else 0.0
        students.append({'student': a, 'initial_course': spec.initial_course,
                         'values': json.dumps(spec.values), 'allocated_course': j,
                         'switches': switches[a], 'preference_utility': utility,
                         'net_utility': utility-config.switching_cost*switches[a]})
    checks = sum(d['scheduled_status_check'] for d in decisions)
    summary = {'seed': seed, 'condition': condition, 'n_students': len(agents),
               'population_hash': fingerprint, 'placed': len(state.enrolled),
               'unplaced': len(agents)-len(state.enrolled), 'placement_rate': len(state.enrolled)/len(agents),
               'mean_utility': sum(s['preference_utility'] for s in students)/len(agents),
               'mean_net_utility': sum(s['net_utility'] for s in students)/len(agents),
               'switches': sum(switches), 'switches_per_student': sum(switches)/len(agents),
               'scheduled_status_checks': checks,
               'rank_refreshes': sum(d['rank_refresh'] for d in decisions),
               'simulated_operations': checks+2*sum(switches),
               'decision_evaluations': len(decisions),
               'peak_pending_hhi': max(r['pending_hhi'] for r in rounds if r['phase'] == 'after_decisions')}
    return Result(summary, rounds, decisions, events, students)
