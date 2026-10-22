"""Independently audit exported CSV arithmetic and optional rerun identity."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def audit(folder, repeat=None):
    folder = Path(folder)
    checks = []
    manifest = json.loads((folder / 'manifest.json').read_text())
    for name, digest in manifest['files_sha256'].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, name
        if repeat:
            assert (folder / name).read_bytes() == (Path(repeat) / name).read_bytes(), name
    checks.append('All saved hashes match; every evidence file matches the independent rerun.'
                  if repeat else 'All saved evidence hashes match.')

    def rows(name):
        with (folder / name).open(newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def key(r):
        return r['scenario'], r['seed'], r['condition']

    def close(x, y):
        assert math.isclose(float(x), float(y), rel_tol=1e-10, abs_tol=1e-12), (x, y)

    runs = {key(r): r for r in rows('runs.csv')}
    assert len(runs) == manifest['n_runs'] == 300
    cfgs = {s['id']: s['parameters'] for s in json.loads(
        (folder / 'resolved_config.json').read_text())['scenarios']}
    groups = defaultdict(list)
    for row in rows('students.csv'):
        groups[key(row)].append(row)
    for k, run in runs.items():
        students = groups[k]
        n = int(run['n_students'])
        assert len(students) == len({s['student'] for s in students}) == n
        counts = Counter(s['allocated_course'] for s in students if s['allocated_course'])
        for course, count in counts.items():
            assert count <= cfgs[k[0]]['capacities'][int(course)]
        placed = sum(counts.values())
        assert placed == int(run['placed'])
        assert n-placed == int(run['unplaced'])
        close(run['placement_rate'], placed/n)
        close(run['mean_utility'], sum(float(s['preference_utility']) for s in students)/n)
        close(run['mean_net_utility'], sum(float(s['net_utility']) for s in students)/n)
        assert int(run['switches']) == sum(int(s['switches']) for s in students)
        for s in students:
            raw = json.loads(s['values'])[int(s['allocated_course'])] if s['allocated_course'] else 0
            close(raw, s['preference_utility'])
            close(s['net_utility'], raw-cfgs[k[0]]['switching_cost']*int(s['switches']))
    checks.append('All 300 run summaries agree with unique student records, capacities, allocation values and costs.')

    for scenario, seed, arm in runs:
        if arm != 'visible':
            continue
        v, h = (scenario, seed, 'visible'), (scenario, seed, 'hidden')
        assert runs[v]['population_hash'] == runs[h]['population_hash']
        assert [(s['student'], s['initial_course'], s['values']) for s in groups[v]] == [
            (s['student'], s['initial_course'], s['values']) for s in groups[h]]
    checks.append('All 150 visible/hidden pairs contain identical student preferences and initial courses.')

    decisions = rows('decisions.csv')
    assert all(not r['observed_rank'] and not r['rank_age'] for r in decisions if r['condition'] == 'hidden')
    checks.append('No hidden-condition decision record contains a disclosed rank or rank age.')
    arrivals, departures, switches, approved = Counter(), Counter(), Counter(), set()
    for e in rows('events.csv'):
        k = key(e)
        if e['action'] == 'switch':
            assert int(e['new_timestamp']) > int(e['old_timestamp'])
            switches[k] += 1
            arrivals[k, e['round'], e['to_course']] += 1
            departures[k, e['round'], e['from_course']] += 1
        elif e['action'] == 'approve':
            identity = k, e['student']
            assert identity not in approved
            approved.add(identity)
    for k, r in runs.items():
        assert switches[k] == int(r['switches'])
        assert int(r['simulated_operations']) == int(r['scheduled_status_checks'])+2*switches[k]
    for f in rows('flows.csv'):
        k = key(f), f['round'], f['course']
        assert int(f['arrivals']) == arrivals[k]
        assert int(f['departures']) == departures[k]
    for r in rows('rounds.csv'):
        capacity = cfgs[r['scenario']]['capacities'][int(r['course'])]
        assert 0 <= int(r['approved']) <= capacity
        assert int(r['vacancies']) == capacity-int(r['approved'])
    checks.append('Events conserve switching flows, renew timestamps, approve students once and respect capacities at every saved phase.')
    expected = {(1, 'visible'): 10, (1, 'hidden'): 10,
                (2, 'visible'): 4, (2, 'hidden'): 0}
    for r in rows('worked_example.csv'):
        close(r['net_utility'], expected[int(r['focal_rank']), r['condition']])
    checks.append('The four worked-example outcomes equal the hand calculations: 10, 10, 4 and 0.')
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='progress/results')
    parser.add_argument('--repeat', help='Optional second complete output folder to compare byte for byte')
    args = parser.parse_args()
    for item in audit(args.results, args.repeat):
        print('PASS:', item)
