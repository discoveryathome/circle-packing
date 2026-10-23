// Geometry oracle for well-formed integer-string certificates, not a JSON schema verifier.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const minimum = (a, b) => a < b ? a : b;
const absolute = x => x < 0n ? -x : x;

function signature(c, expectedN) {
  if (c.n !== expectedN || c.centers.length !== expectedN) return '0\n';
  const q = BigInt(c.denominator), r = BigInt(c.radius_numerator);
  if (q <= 0n || r <= 0n || 2n * r > q) return '0\n';
  const points = c.centers.map(p => p.map(BigInt));
  // A disk's center must lie in the concentric square of side Q-2R.
  const bound = q - 2n * r;
  let wall = q;
  for (const [x, y] of points) {
    const gap = minimum(bound - absolute(2n * x - q), bound - absolute(2n * y - q));
    if (gap < 0n) return '0\n';
    wall = minimum(wall, gap / 2n);
  }
  let pair = null;
  for (let i = 0; i < points.length; i++) {
    for (let j = i + 1; j < points.length; j++) {
      const dx = points[i][0] - points[j][0], dy = points[i][1] - points[j][1];
      const gap = dx * dx + dy * dy - (2n * r) ** 2n;
      if (gap < 0n) return '0\n';
      pair = pair === null ? gap : minimum(pair, gap);
    }
  }
  return `1|${c.n}|${r}|${q}|${wall}|${pair ?? '-'}|${c.n * (c.n - 1) / 2}\n`;
}

function certificate(q, r, points) {
  return { n: points.length, denominator: String(q), radius_numerator: String(r),
    centers: points.map(p => p.map(String)) };
}

function* multisets(points, n, start = 0, chosen = []) {
  if (chosen.length === n) {
    yield chosen;
    return;
  }
  for (let i = start; i < points.length; i++) {
    yield* multisets(points, n, i, [...chosen, points[i]]);
  }
}

function grids() {
  const rows = [];
  for (const [n, limit] of [[1, 12], [2, 12], [3, 5]]) {
    for (let q = 1; q <= limit; q++) {
      const points = [];
      for (let x = 0; x <= q; x++) for (let y = 0; y <= q; y++) points.push([x, y]);
      const digest = createHash('sha256');
      let accepted = 0, rejected = 0;
      for (let r = 1; r <= Math.floor(q / 2) + 1; r++) {
        for (const centers of multisets(points, n)) {
          const result = signature(certificate(q, r, centers), n);
          digest.update(result);
          if (result.startsWith('1|')) accepted++; else rejected++;
        }
      }
      rows.push({ n, q, accepted, rejected, signature_sha256: digest.digest('hex') });
    }
  }
  return rows;
}

function working(c) {
  const q = BigInt(c.denominator), r = BigInt(c.radius_numerator);
  const points = c.centers.map(p => p.map(BigInt));
  const results = [{ label: 'original', signature: signature(c, c.n) }];
  for (let bits = 0; bits < 8; bits++) {
    const transformed = [...points].reverse().map(([x, y]) => {
      if (bits & 4) [x, y] = [y, x];
      return [bits & 2 ? q - x : x, bits & 1 ? q - y : y];
    });
    results.push({ label: `symmetry-${bits}`, signature: signature(certificate(q, r, transformed), c.n) });
  }
  results.push({ label: 'scale-97', signature: signature(certificate(q * 97n, r * 97n,
    points.map(p => p.map(v => v * 97n))), c.n) });
  for (const n of [c.n - 1, c.n + 1]) {
    results.push({ label: `requested-${n}`, signature: signature(c, n) });
  }
  return { n: c.n, results };
}

const input = JSON.parse(readFileSync(0, 'utf8'));
console.log(JSON.stringify({ node: process.version, grids: grids(),
  controls: input.controls.map(x => ({ label: x.label, signature: signature(x.certificate, x.expected_n) })),
  working: input.working.map(working) }));
