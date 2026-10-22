"""Reproduce the pilot: python3 -m study.run_study --output progress/results."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

from .model import AgentSpec, Config, simulate

METRICS = ('mean_utility', 'mean_net_utility', 'placement_rate', 'unplaced',
           'switches', 'switches_per_student', 'scheduled_status_checks', 'rank_refreshes',
           'simulated_operations', 'peak_pending_hhi')


def load_suite(path):
    suite = json.loads(Path(path).read_text())
    if not suite['seeds'] or len(set(suite['seeds'])) != len(suite['seeds']):
        raise ValueError('Seeds must be nonempty and unique')
    ids = [s['id'] for s in suite['scenarios']]
    if not ids or len(set(ids)) != len(ids): raise ValueError('Scenario IDs must be unique')
    return suite


def config_for(overrides):
    overrides = dict(overrides)
    for name in ['capacities', 'favourite_shares', 'alternative_values', 'approval_rounds']:
        if name in overrides: overrides[name] = tuple(overrides[name])
    return Config(**overrides)


def write_csv(path, rows):
    if not rows: raise ValueError(f'No evidence rows for {path}')
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def worked_example():
    config = Config(n_students=2, capacities=(1, 1), favourite_shares=(1, 0),
                    switching_cost=1, expected_departure=0, n_rounds=1, approval_rounds=(1,))
    agents = [AgentSpec((10, 5), 0), AgentSpec((10, 0), 0, False)]
    rows = []
    for order, rank in [((0, 1), 1), ((1, 0), 2)]:
        for condition in ['visible', 'hidden']:
            r = simulate(config, 7, condition, agents, order)
            s, d = r.students[0], r.decisions[0]
            rows.append({'focal_rank': rank, 'condition': condition,
                         'observed_rank': d['observed_rank'], 'stay_probability': d['stay_probability'],
                         'stay_benefit': d['stay_benefit'], 'switch_net_benefit': 4,
                         'decision': 'stay' if d['destination'] == 0 else 'switch_to_B',
                         'allocated_course': s['allocated_course'], 'net_utility': s['net_utility']})
    return rows


def run_suite(suite, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    tables = {name: [] for name in ['runs', 'rounds', 'decisions', 'events', 'students']}
    groups, pairs = defaultdict(list), []
    resolved, flow_rows = [], []
    for scenario in suite['scenarios']:
        cfg = config_for(scenario['overrides'])
        resolved.append({'id': scenario['id'], 'parameters': asdict(cfg)})
        for seed in suite['seeds']:
            pair = {}
            for condition in ['visible', 'hidden']:
                r = simulate(cfg, seed, condition)
                tags = {'scenario': scenario['id'], 'seed': seed, 'condition': condition}
                tables['runs'].append({'scenario': scenario['id'], **r.summary})
                for name in ['rounds', 'decisions', 'events', 'students']:
                    tables[name].extend({**tags, **row} for row in getattr(r, name))
                arrivals = Counter((e['round'], e['to_course']) for e in r.events if e['action'] == 'switch')
                departures = Counter((e['round'], e['from_course']) for e in r.events if e['action'] == 'switch')
                for t in range(1, cfg.n_rounds+1):
                    for j in range(len(cfg.capacities)):
                        flow_rows.append({**tags, 'round': t, 'course': j,
                                          'arrivals': arrivals[t,j], 'departures': departures[t,j]})
                pair[condition] = r.summary
                groups[(scenario['id'], condition)].append(r.summary)
            assert pair['visible']['population_hash'] == pair['hidden']['population_hash']
            for metric in METRICS:
                pairs.append({'scenario': scenario['id'], 'seed': seed, 'metric': metric,
                              'visible': pair['visible'][metric], 'hidden': pair['hidden'][metric],
                              'visible_minus_hidden': pair['visible'][metric]-pair['hidden'][metric]})
    for name, rows in tables.items(): write_csv(out/f'{name}.csv', rows)
    write_csv(out/'flows.csv', flow_rows)
    summary = []
    for (scenario, condition), rows in groups.items():
        for metric in METRICS:
            values = [r[metric] for r in rows]
            summary.append({'scenario': scenario, 'condition': condition, 'metric': metric,
                            'n_seeds': len(values), 'mean': statistics.mean(values),
                            'sd_across_seeds': statistics.stdev(values) if len(values)>1 else 0})
    write_csv(out/'summary.csv', summary)
    write_csv(out/'paired_differences.csv', pairs)
    pg = defaultdict(list)
    for row in pairs: pg[(row['scenario'], row['metric'])].append(row['visible_minus_hidden'])
    write_csv(out/'paired_summary.csv', [{'scenario': s, 'metric': m, 'n_pairs': len(v),
              'mean_difference': statistics.mean(v),
              'sd_across_pairs': statistics.stdev(v) if len(v)>1 else 0,
              'positive_pairs': sum(x>1e-12 for x in v), 'negative_pairs': sum(x < -1e-12 for x in v),
              'zero_pairs': sum(abs(x)<=1e-12 for x in v)} for (s,m),v in pg.items()])
    write_csv(out/'worked_example.csv', worked_example())
    (out/'resolved_config.json').write_text(json.dumps({'study_date': suite['study_date'], 'seeds': suite['seeds'], 'scenarios': resolved}, indent=2)+'\n')
    manifest = {'study_date': suite['study_date'], 'n_runs': len(tables['runs']),
                'n_pairs': len(tables['runs'])//2, 'conditions': ['visible', 'hidden'],
                'data_origin': 'synthetic', 'pairing': 'identical agents, initial order and keyed per-round commit order',
                'files_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*')) if p.name != 'manifest.json' and p.is_file()}}
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).parent/'configs'/'pilot.json')
    parser.add_argument('--output', type=Path, default=Path('progress/results'))
    args = parser.parse_args()
    m = run_suite(load_suite(args.config), args.output)
    print(f"Saved {m['n_runs']} runs ({m['n_pairs']} matched pairs) to {args.output}")


if __name__ == '__main__': main()
