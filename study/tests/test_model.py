import unittest
from dataclasses import replace

from study.model import (AgentSpec, Config, Observation, QueueState, choose, observe,
                         probability_at_rank, probability_at_tail, simulate)


class ProbabilityTests(unittest.TestCase):
    def test_analytic_rank_cases(self):
        self.assertEqual(probability_at_rank(1, 1, 0), 1)
        self.assertEqual(probability_at_rank(2, 1, 0), 0)
        self.assertAlmostEqual(probability_at_rank(2, 1, .1), .1)
        self.assertAlmostEqual(probability_at_rank(3, 1, .1), .01)
        self.assertEqual(probability_at_rank(1, 0, .1), 0)

    def test_tail_uses_common_prior(self):
        self.assertEqual(probability_at_tail(0, 1, 0), 1)
        self.assertAlmostEqual(probability_at_tail(1, 1, 0), 0.36787944117144233)
        self.assertEqual(probability_at_tail(0, 0, .1), 0)

    def test_ties_stay(self):
        o = Observation(0, (1, 1), (0, 0), (2, 0), None, None)
        d = choose(AgentSpec((10, 6), 0), o, 1, 0)
        self.assertEqual(d.destination, 0)


class QueueTests(unittest.TestCase):
    def test_rejoining_loses_timestamp(self):
        q = QueueState((1, 1))
        q.add(0, 0); q.add(1, 0)
        first = q.pending[0][1]
        q.move(0, 1); q.move(0, 0)
        self.assertGreater(q.pending[0][1], first)
        self.assertEqual(q.rank(0), 2)
        q.approve()
        self.assertEqual(q.enrolled, {1: 0})

    def test_capacity_and_closed_course(self):
        q = QueueState((1, 1))
        q.add(0, 0); q.add(1, 0); q.approve()
        with self.assertRaises(ValueError): q.add(2, 0)
        self.assertEqual(q.vacancies(), (0, 1))
        self.assertEqual(len(q.enrolled), 1)
        q.check()

    def test_hidden_observation_does_not_request_rank(self):
        q = QueueState((1, 1)); q.add(0, 0)
        q.rank = lambda _: (_ for _ in ()).throw(AssertionError('rank read'))
        o = observe(q, 0, (2, 0), 'hidden', None)
        self.assertIsNone(o.observed_rank)
        self.assertEqual(o.prior_pending, (2, 0))


class SimulationTests(unittest.TestCase):
    def test_two_student_worked_example(self):
        c = Config(n_students=2, capacities=(1, 1), favourite_shares=(1, 0),
                   n_rounds=1, approval_rounds=(1,), switching_cost=1,
                   expected_departure=0)
        agents = [AgentSpec((10, 5), 0), AgentSpec((10, 0), 0, False)]
        nets = {'visible': [], 'hidden': []}
        for order in [(0, 1), (1, 0)]:
            for condition in nets:
                result = simulate(c, 7, condition, agents, order)
                focal = result.students[0]
                nets[condition].append(focal['net_utility'])
                expected = (0 if order == (0, 1) else
                            (1 if condition == 'visible' else None))
                self.assertEqual(focal['allocated_course'], expected)
        self.assertEqual(nets['visible'], [10, 4])
        self.assertEqual(nets['hidden'], [10, 0])

    def test_pairing_and_reproducibility(self):
        c = Config(n_students=30)
        a = simulate(c, 4, 'visible')
        b = simulate(c, 4, 'hidden')
        self.assertEqual(a.summary['population_hash'], b.summary['population_hash'])
        self.assertEqual(a.summary, simulate(c, 4, 'visible').summary)
        self.assertEqual(a.events, simulate(c, 4, 'visible').events)
        self.assertTrue(all(d['observed_rank'] is None for d in b.decisions))

    def test_capacity_across_conditions_and_slow_queries(self):
        for interval in [1, 3]:
            c = Config(n_students=60, rank_update_interval=interval)
            for condition in ['visible', 'hidden']:
                r = simulate(c, 2, condition)
                allocations = [s['allocated_course'] for s in r.students]
                self.assertLessEqual(sum(a is not None for a in allocations), 45)
                for j in range(3): self.assertLessEqual(allocations.count(j), 15)
                self.assertEqual(r.summary['placed'] + r.summary['unplaced'], 60)
                self.assertTrue(all(e['new_timestamp'] > e['old_timestamp'] for e in r.events if e['action'] == 'switch'))

    def test_switch_invalidates_rank_until_next_scheduled_refresh(self):
        c = Config(n_students=3, capacities=(1, 1, 1), favourite_shares=(1, 0, 0),
                   n_rounds=4, approval_rounds=(4,), rank_update_interval=3,
                   expected_departure=0)
        agents = [AgentSpec((10, 9, 0), 0), AgentSpec((10, 0, 0), 0, False),
                  AgentSpec((0, 10, 0), 1, False)]
        r = simulate(c, 1, 'visible', agents, [1, 0, 2])
        d = [row for row in r.decisions if row['student'] == 0]
        self.assertEqual([x['observed_rank'] for x in d], [2, None, None, 2])
        self.assertEqual([x['current_course'] for x in d], [0, 1, 1, 1])
        self.assertEqual([x['rank_age'] for x in d], [0, None, None, 0])

    def test_all_decisions_precede_commits_and_approvals(self):
        c = Config(n_students=3, capacities=(1, 1, 1), favourite_shares=(1, 0, 0),
                   n_rounds=1, approval_rounds=(1,), expected_departure=0)
        agents = [AgentSpec((10, 0, 0), 0, False), AgentSpec((10, 9, 0), 0),
                  AgentSpec((10, 9, 0), 0)]
        r = simulate(c, 2, 'visible', agents, [0, 1, 2])
        self.assertEqual([x['observed_rank'] for x in r.decisions], [2, 3])
        self.assertEqual([e['action'] for e in r.events],
                         ['switch', 'switch', 'approve', 'approve', 'expire'])
        b = [x for x in r.rounds if x['course'] == 1 and x['phase'] == 'after_decisions'][0]
        self.assertEqual((b['pending'], b['vacancies']), (2, 1))

    def test_check_metric_distinguishes_rank_disclosure(self):
        c = Config(n_students=30)
        v, h = simulate(c, 0, 'visible'), simulate(c, 0, 'hidden')
        self.assertEqual(h.summary['rank_refreshes'], 0)
        self.assertGreater(v.summary['rank_refreshes'], 0)
        for r in [v, h]:
            self.assertEqual(r.summary['simulated_operations'],
                             r.summary['scheduled_status_checks'] + 2*r.summary['switches'])

    def test_unsupported_configuration_rejected(self):
        with self.assertRaises(ValueError): Config(n_students=0)
        with self.assertRaises(ValueError): Config(expected_departure=2)
        with self.assertRaises(ValueError): Config(approval_rounds=(2,))


if __name__ == '__main__': unittest.main()
