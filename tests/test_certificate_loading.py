import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verify import load_verify, verify

LIMIT = 10_000_000


class CertificateLoadingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name)/'certificate.json'
        self.c = {'schema': 'equal-circle-square/v1', 'n': 1, 'denominator': '2',
                  'radius_numerator': '1', 'centers': [['1', '1']],
                  'provenance': {'note': 'NaN is an ordinary string', 'score': 0.125}}

    def save(self, raw=None):
        self.path.write_bytes(json.dumps(self.c).encode() if raw is None else raw)
        return self.path

    def test_valid_file_hash_and_finite_provenance(self):
        self.save()
        report = load_verify(self.path, 1)
        self.assertTrue(report['valid'])
        self.assertEqual(report['sha256'], hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_expected_count_is_bound(self):
        with self.assertRaisesRegex(ValueError, 'wrong circle count'):
            load_verify(self.save(), 2)

    def test_top_level_values_are_rejected_by_loader(self):
        for value in (None, True, 1, 1.5, 'text', []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                load_verify(self.save(json.dumps(value).encode()), 1)

    def test_top_level_values_are_rejected_by_verifier(self):
        for value in (None, True, 1, 1.5, 'text', []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verify(value, 1)

    def test_cli_returns_json_for_nonobject(self):
        self.save(b'[]')
        result = subprocess.run([sys.executable, str(ROOT/'src/verify.py'), str(self.path), '--n', '1'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.strip(), result.stderr)
        self.assertIs(json.loads(result.stdout)['valid'], False)

    def test_malformed_json(self):
        for raw in (b'', b'{', b'{} trailing', b'not json', b'{"bad":"\xff"}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                load_verify(self.save(raw), 1)

    def test_decoder_recursion_error_is_rejected_cleanly(self):
        self.save()
        with patch('verify.json.loads', side_effect=RecursionError('decoder depth exceeded')):
            with self.assertRaisesRegex(ValueError, 'nesting'):
                load_verify(self.path, 1)

    def test_duplicate_geometry_keys(self):
        for key in ('schema', 'n', 'denominator', 'radius_numerator', 'centers'):
            raw = ('{'+json.dumps(key)+':'+json.dumps(self.c[key])+','+json.dumps(self.c)[1:]).encode()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                load_verify(self.save(raw), 1)

    def test_escaped_duplicate_key(self):
        raw = b'{"\\u006e":1,'+json.dumps(self.c).encode()[1:]
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            load_verify(self.save(raw), 1)

    def test_duplicate_nested_provenance_key(self):
        c = {key: value for key, value in self.c.items() if key != 'provenance'}
        raw = b'{"provenance":{"source":"A","source":"B"},'+json.dumps(c).encode()[1:]
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            load_verify(self.save(raw), 1)

    def test_nonfinite_constants_in_metadata(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            c = dict(self.c, provenance={'score': value})
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'non-finite JSON constant'):
                load_verify(self.save(json.dumps(c).encode()), 1)

    def test_supported_byte_encodings(self):
        for encoding in ('utf-8', 'utf-8-sig', 'utf-16', 'utf-32'):
            raw = json.dumps(self.c).encode(encoding)
            with self.subTest(encoding=encoding):
                report = load_verify(self.save(raw), 1)
                self.assertEqual(report['sha256'], hashlib.sha256(raw).hexdigest())

    def test_exact_file_limit(self):
        raw = json.dumps(self.c).encode()
        report = load_verify(self.save(raw+b' '*(LIMIT-len(raw))), 1)
        self.assertTrue(report['valid'])

    def test_one_byte_over_file_limit(self):
        raw = json.dumps(self.c).encode()
        with self.assertRaisesRegex(ValueError, 'exceeds 10 MB'):
            load_verify(self.save(raw+b' '*(LIMIT+1-len(raw))), 1)

    def test_read_budget_is_enforced_before_parsing(self):
        class BudgetedFile(io.BytesIO):
            consumed = 0

            def read(self, size=-1):
                if size < 0:
                    raise AssertionError('unbounded certificate read')
                data = super().read(size)
                self.consumed += len(data)
                if self.consumed > LIMIT+1:
                    raise AssertionError('certificate read exceeded limit+1')
                return data

        stream = BudgetedFile(b' '*(LIMIT+2))
        with patch('verify.Path.open', return_value=stream):
            with self.assertRaisesRegex(ValueError, 'exceeds 10 MB'):
                load_verify(self.path, 1)
        self.assertLessEqual(stream.consumed, LIMIT+1)


if __name__ == '__main__':
    unittest.main()
