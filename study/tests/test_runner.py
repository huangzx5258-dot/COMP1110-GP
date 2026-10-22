import csv
import json
import tempfile
import unittest
from pathlib import Path

from study.run_study import load_suite, run_suite


class RunnerTests(unittest.TestCase):
    def test_pilot_has_300_runs(self):
        suite = load_suite(Path('study/configs/pilot.json'))
        self.assertEqual(len(suite['scenarios'])*len(suite['seeds'])*2, 300)

    def test_small_suite_exports_matched_evidence(self):
        suite = {'study_date': '2026-10-20', 'seeds': [0, 1],
                 'scenarios': [{'id': 'small', 'overrides': {'n_students': 6}}]}
        with tempfile.TemporaryDirectory() as tmp:
            run_suite(suite, Path(tmp))
            with (Path(tmp)/'runs.csv').open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 4)
            for seed in ['0', '1']:
                pair = [r for r in rows if r['seed'] == seed]
                self.assertEqual(pair[0]['population_hash'], pair[1]['population_hash'])
            self.assertEqual(json.loads((Path(tmp)/'manifest.json').read_text())['n_runs'], 4)
            self.assertTrue((Path(tmp)/'decisions.csv').stat().st_size > 0)
            self.assertTrue((Path(tmp)/'paired_differences.csv').stat().st_size > 0)
            with (Path(tmp)/'flows.csv').open() as f:
                flows = list(csv.DictReader(f))
            for row in rows:
                matching = [x for x in flows if x['seed'] == row['seed'] and x['condition'] == row['condition']]
                self.assertEqual(sum(int(x['arrivals']) for x in matching), int(row['switches']))
                self.assertEqual(sum(int(x['departures']) for x in matching), int(row['switches']))


if __name__ == '__main__': unittest.main()
