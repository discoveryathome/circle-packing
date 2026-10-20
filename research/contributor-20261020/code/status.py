"""Lightweight progress view; no numerical work while comparisons run."""
import json
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for path in sorted((ROOT/'logs').glob('*/blocks.jsonl'),key=lambda p:p.stat().st_mtime):
    for line in path.read_text().splitlines():
        r=json.loads(line);gain=D(r['best_radius'])-D(r['start_radius']);gate=max(D('1e-10'),D(r['start_radius'])*D('1e-8'))
        print(f"{path.parent.name:38s} N={r['n']:3d}  r={r['best_radius']}  gain={gain:+.3E}  {'GAIN' if gain>gate else 'tie':4s}  CPU={r['cpu_seconds']:5.1f}s wall={r['wall_seconds']:5.1f}s attempts={r['attempts']}")
