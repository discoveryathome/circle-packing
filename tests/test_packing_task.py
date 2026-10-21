"""Adversarial checks for exact progress and serial evidence accounting."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import packing_task as task


def cert(r):
    return {'schema':'equal-circle-square/v1','n':4,'denominator':'1000000000000',
            'radius_numerator':str(r),'centers':[['250000000000','250000000000'],
            ['250000000000','750000000000'],['750000000000','250000000000'],['750000000000','750000000000']]}


class ProgressTests(unittest.TestCase):
    def test_exact_gate_and_repeat(self):
        c=cert(200000000000)
        self.assertFalse(task.comparison(cert(200000000001),c,4)['meaningful'])
        self.assertTrue(task.comparison(cert(220000000000),c,4)['meaningful'])
        self.assertFalse(task.comparison(cert(220000000000),cert(220000000000),4)['meaningful'])

    def test_invalid_geometry_and_wrong_count(self):
        bad=cert(250000000001)
        with self.assertRaises(ValueError): task.comparison(bad,cert(200000000000),4)
        with self.assertRaises(ValueError): task.comparison(cert(200000000000),cert(200000000000),5)

    def fixture(self,directory):
        (directory/'inputs').mkdir(); (directory/'certificates').mkdir()
        task.write(directory/'inputs/n4.json',cert(200000000000))
        task.write(directory/'session.json',{'counts':[4],'arms':['polish','original','targeted'],
                   'inputs':{'4':{'path':'inputs/n4.json'}},'session_number':1,'smoke':False})
        rows=[]
        for i,(arm,r) in enumerate([('polish',210000000000),('original',220000000000),('original',190000000000),('targeted',200000000001)]):
            p=directory/'certificates'/f'{i}.json'; task.write(p,cert(r))
            rows.append({'n':4,'arm':arm,'certificate':str(p.relative_to(directory)),'sha256':task.sha(p),
                         'input':'inputs/n4.json','input_sha256':task.sha(directory/'inputs/n4.json'),
                         'radius_exact':str(task.radius(cert(r))),'error':None})
        (directory/'attempts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        blocks=[{'n':4,'arm':arm,'attempts':sum(r['arm']==arm for r in rows)} for arm in ['polish','original','targeted']]
        (directory/'blocks.jsonl').write_text(''.join(json.dumps(b)+'\n' for b in blocks))
        return rows

    def test_all_attempt_maximum_not_last_and_polish_control(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); self.fixture(p); r=task.summarize(p)['rows'][0]
            self.assertEqual(Fraction(r['radius_exact']),Fraction(22,100))
            self.assertTrue(r['beyond_polish_gate'])

    def test_partial_and_duplicate_blocks_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); self.fixture(p)
            lines=(p/'blocks.jsonl').read_text().splitlines()
            for invalid in [lines[:2],lines+[lines[0]]]:
                (p/'blocks.jsonl').write_text('\n'.join(invalid)+'\n')
                with self.assertRaises(ValueError): task.summarize(p)

    def test_false_score_tampered_geometry_and_duplicate_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); rows=self.fixture(p)
            bad=copy.deepcopy(rows);bad[1]['radius_exact']='1/4'
            (p/'attempts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in bad))
            with self.assertRaises(ValueError): task.summarize(p)
            (p/'attempts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows+[rows[0]]))
            with self.assertRaises(ValueError): task.summarize(p)
            (p/'attempts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
            (p/'certificates/1.json').write_text(json.dumps(cert(250000000001)))
            with self.assertRaises(ValueError): task.summarize(p)

    def test_small_gain_still_inherited(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); rows=self.fixture(p)
            for i,row in enumerate(rows):
                c=cert(200000000001 if i==1 else 200000000000)
                file=p/row['certificate'];file.write_text(json.dumps(c))
                row.update(sha256=task.sha(file),radius_exact=str(task.radius(c)))
            (p/'attempts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
            r=task.summarize(p)['rows'][0]
            self.assertFalse(r['meaningful']);self.assertEqual(r['best_source'],'certificates/1.json')

    def test_paths_cannot_escape(self):
        with self.assertRaises(ValueError): task.bound_path(Path('/tmp/session'),'../elsewhere')

    def test_smoke_cannot_count_as_study(self):
        with patch.object(task,'check_session',return_value={'smoke':True,'session_number':3}):
            with self.assertRaises(ValueError):task.study('/tmp/fake-smoke')


class PreparedSessionTests(unittest.TestCase):
    def test_bindings_and_stale_inputs(self):
        (task.ROOT/'tmp').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=task.ROOT/'tmp') as d:
            p=Path(d)/'session'; task.prepare(p,smoke=True); task.check_session(p)
            original=task.read(p/'session.json')
            bad=copy.deepcopy(original);bad['code_and_protocol_hashes'].pop('src/verify.py')
            (p/'session.json').write_text(json.dumps(bad))
            with self.assertRaises(ValueError):task.check_session(p)
            (p/'session.json').write_text(json.dumps(original))
            older=task.ROOT/'certificates/frontier/n500.json'
            (p/'inputs/n500.json').write_bytes(older.read_bytes())
            original['inputs']['500']['sha256']=task.sha(p/'inputs/n500.json')
            (p/'session.json').write_text(json.dumps(original))
            with self.assertRaises(ValueError):task.check_session(p)
            with self.assertRaises(FileExistsError):task.prepare(p,smoke=True)


class SerialChainTests(unittest.TestCase):
    def test_full_chain_inherits_best_and_does_not_pass_on_one_count(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve(); initial=root/'initial.json'; task.write(initial,cert(200000000000))
            index=root/'index.json'; protocol=root/'protocol.json'
            task.write(index,{'rows':[{'n':4,'certificate':'initial.json','sha256':task.sha(initial),
                'radius_exact':str(task.radius(cert(200000000000))),'previous_certificate':'initial.json','previous_sha256':task.sha(initial)}]})
            task.write(protocol,{'counts':[4],'arms':['polish','original','targeted'],'sessions':3,'search_seconds_per_count_arm':60})
            with patch.object(task,'ROOT',root), patch.object(task,'INDEX',index), patch.object(task,'PROTOCOL',protocol), patch.object(task,'required_sources',return_value=[Path('index.json'),Path('protocol.json')]):
                previous=None
                for number in [1,2,3]:
                    current=root/f'session-{number}';task.prepare(current,previous=previous)
                    task.write(current/'execution.json',{'session_sha256':task.sha(current/'session.json')})
                    (current/'certificates').mkdir();(current/'best').mkdir()
                    start=task.read(current/'inputs/n4.json');self.assertEqual(int(start['radius_numerator']),190000000000+number*10000000000)
                    attempts=[]
                    for arm in ['polish','original','targeted']:
                        c=cert(int(start['radius_numerator'])+(10000000000 if arm=='original' else 0))
                        cp=current/'certificates'/f'{arm}.json';task.write(cp,c)
                        attempts.append({'n':4,'arm':arm,'certificate':str(cp.relative_to(current)),'sha256':task.sha(cp),
                            'input':'inputs/n4.json','input_sha256':task.sha(current/'inputs/n4.json'),'radius_exact':str(task.radius(c)),'error':None})
                    (current/'attempts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in attempts))
                    (current/'blocks.jsonl').write_text(''.join(json.dumps({'n':4,'arm':a,'attempts':1})+'\n' for a in ['polish','original','targeted']))
                    summary=task.summarize(current);task.write(current/'summary.json',summary)
                    (current/'best/n4.json').write_bytes((current/summary['rows'][0]['best_source']).read_bytes())
                    task.check_session(current,closed=True);previous=current
                result=task.study(previous)
                self.assertEqual(result['sessions_with_gain'],3)
                self.assertTrue(result['later_nonpolish_gain'])
                self.assertFalse(result['product_gate_passed'])
                # Even rewriting a valid input and its declared hash cannot reset a predecessor.
                metadata=task.read(previous/'session.json')
                (previous/'inputs/n4.json').write_bytes(initial.read_bytes())
                metadata['inputs']['4']['sha256']=task.sha(initial)
                (previous/'session.json').write_text(json.dumps(metadata))
                (previous/'execution.json').write_text(json.dumps({'session_sha256':task.sha(previous/'session.json')}))
                with self.assertRaises(ValueError):task.check_session(previous)


if __name__=='__main__':unittest.main()
