"""Cross-record consistency of successful attempts and logged solver fallbacks."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import packing_task as task


def certificate(radius):
    return {'schema': 'equal-circle-square/v1', 'n': 4, 'denominator': '100',
            'radius_numerator': str(radius), 'centers': [['25', '25'], ['25', '75'],
                                                       ['75', '25'], ['75', '75']]}


class SessionBindingTests(unittest.TestCase):
    def fixture(self, directory):
        for name in ('inputs', 'attempt-inputs', 'certificates'):
            (directory/name).mkdir()
        start = certificate(20)
        start['provenance'] = {'source': 'inherited from an earlier session'}
        task.write(directory/'inputs/n4.json', start)
        session = {'counts': [4], 'arms': ['polish', 'original', 'targeted'],
                   'inputs': {'4': {'path': 'inputs/n4.json'}}, 'session_number': 1,
                   'smoke': False, 'seed': '1234567890abcdef1234567890abcdef'}
        task.write(directory/'session.json', session)
        rows = []
        for arm in session['arms']:
            rows.append(self.attempt(directory, session, arm, 0, certificate(21)))
        return session, rows, start

    def attempt(self, directory, session, arm, index, cert, error=None):
        name = f'{arm}-{index}'
        ip = directory/'attempt-inputs'/f'{name}.json'
        task.write(ip, {'points': [[.25, .25], [.25, .75], [.75, .25], [.75, .75]],
                        'attempt': index})
        cert = copy.deepcopy(cert)
        if error is None:
            cert['provenance'] = {'session_seed': session['seed'], 'arm': arm,
                                  'input_sha256': task.sha(ip),
                                  'base_input_sha256': task.sha(directory/'inputs/n4.json')}
        cp = directory/'certificates'/f'{name}.json'
        task.write(cp, cert)
        return {'n': 4, 'arm': arm, 'attempt': index, 'certificate': str(cp.relative_to(directory)),
                'sha256': task.sha(cp), 'input': str(ip.relative_to(directory)),
                'input_sha256': task.sha(ip), 'radius_exact': str(task.radius(cert)), 'error': error}

    def save(self, directory, rows):
        (directory/'attempts.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in rows))
        blocks = [{'n': 4, 'arm': arm, 'attempts': sum(t['arm'] == arm for t in rows)}
                  for arm in ('polish', 'original', 'targeted')]
        (directory/'blocks.jsonl').write_text(''.join(json.dumps(b)+'\n' for b in blocks))

    def replace(self, directory, row, cert):
        cp = directory/row['certificate']
        cp.write_text(json.dumps(cert)+'\n')
        row.update(sha256=task.sha(cp), radius_exact=str(task.radius(cert)))

    def test_success_binds_each_provenance_field(self):
        for field in ('session_seed', 'arm', 'input_sha256', 'base_input_sha256'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                p = Path(d); _, rows, _ = self.fixture(p)
                c = task.read(p/rows[0]['certificate']); c['provenance'][field] = 'wrong'
                self.replace(p, rows[0], c); self.save(p, rows)
                with self.assertRaises(ValueError): task.summarize(p)

    def test_success_requires_each_provenance_field(self):
        for field in ('session_seed', 'arm', 'input_sha256', 'base_input_sha256'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                p = Path(d); _, rows, _ = self.fixture(p)
                c = task.read(p/rows[0]['certificate']); del c['provenance'][field]
                self.replace(p, rows[0], c); self.save(p, rows)
                with self.assertRaises(ValueError): task.summarize(p)

    def test_success_requires_provenance_object(self):
        for value in (None, [], 'metadata', 1):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as d:
                p = Path(d); _, rows, _ = self.fixture(p)
                c = task.read(p/rows[0]['certificate']); c['provenance'] = value
                self.replace(p, rows[0], c); self.save(p, rows)
                with self.assertRaises(ValueError): task.summarize(p)

    def test_extra_provenance_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); _, rows, _ = self.fixture(p)
            c = task.read(p/rows[0]['certificate']); c['provenance']['note'] = 'extra context'
            self.replace(p, rows[0], c); self.save(p, rows)
            self.assertEqual(task.summarize(p)['attempts'], 3)

    def test_first_failure_retains_inherited_certificate(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); _, rows, start = self.fixture(p)
            self.replace(p, rows[0], start); rows[0]['error'] = 'RuntimeError: solver failed'
            self.save(p, rows)
            self.assertEqual(task.summarize(p)['solver_or_certificate_errors'], 1)

    def test_failure_after_improvement_retains_same_arm_best(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); s, rows, _ = self.fixture(p)
            best = task.read(p/rows[1]['certificate'])
            rows.append(self.attempt(p, s, 'original', 1, best, error='RuntimeError: failed'))
            self.save(p, rows)
            self.assertEqual(task.summarize(p)['solver_or_certificate_errors'], 1)

    def test_equal_radius_success_does_not_replace_fallback_best(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); s, rows, _ = self.fixture(p)
            first = task.read(p/rows[1]['certificate'])
            rows.append(self.attempt(p, s, 'original', 1, certificate(21)))
            rows.append(self.attempt(p, s, 'original', 2, first, error='RuntimeError: failed'))
            self.save(p, rows)
            self.assertEqual(task.summarize(p)['solver_or_certificate_errors'], 1)

    def test_success_tied_with_inherited_start_keeps_inherited_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); s, rows, start = self.fixture(p)
            c = task.read(p/rows[1]['certificate']); c['radius_numerator'] = '20'
            self.replace(p, rows[1], c)
            rows.append(self.attempt(p, s, 'original', 1, start, error='RuntimeError: failed'))
            self.save(p, rows)
            self.assertEqual(task.summarize(p)['solver_or_certificate_errors'], 1)

    def test_failed_attempt_cannot_change_fallback_geometry(self):
        for radius in (19, 22):
            with self.subTest(radius=radius), tempfile.TemporaryDirectory() as d:
                p = Path(d); s, rows, _ = self.fixture(p)
                rows.append(self.attempt(p, s, 'original', 1, certificate(radius), error='RuntimeError: failed'))
                self.save(p, rows)
                with self.assertRaises(ValueError): task.summarize(p)

    def test_failed_attempt_cannot_borrow_another_arms_best(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); _, rows, _ = self.fixture(p)
            other = task.read(p/rows[1]['certificate'])
            self.replace(p, rows[0], other); rows[0]['error'] = 'RuntimeError: failed'
            self.save(p, rows)
            with self.assertRaises(ValueError): task.summarize(p)

    def test_failed_attempt_cannot_change_fallback_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); s, rows, _ = self.fixture(p)
            best = task.read(p/rows[1]['certificate']); best['provenance']['note'] = 'changed'
            rows.append(self.attempt(p, s, 'original', 1, best, error='RuntimeError: failed'))
            self.save(p, rows)
            with self.assertRaises(ValueError): task.summarize(p)

    def test_error_requires_nonempty_text(self):
        for error in ('', False, 0, [], {}):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as d:
                p = Path(d); _, rows, start = self.fixture(p)
                self.replace(p, rows[0], start); rows[0]['error'] = error
                self.save(p, rows)
                with self.assertRaises(ValueError): task.summarize(p)


if __name__ == '__main__':
    unittest.main()
