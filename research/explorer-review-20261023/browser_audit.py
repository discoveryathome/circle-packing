"""Rendered explorer checks using actual browser controls and pointer coordinates."""
import argparse
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(page, name):
    return [float(x) for x in page.locator('#'+name).get_attribute('viewBox').split()]


def capture_click(page, name, fx, fy):
    page.locator('#'+name).scroll_into_view_if_needed()
    position = page.evaluate('''({name,fx,fy}) => {
        const svg=document.getElementById(name),v=svg.viewBox.baseVal;
        svg.addEventListener('click',e=>{
            const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(svg.getScreenCTM().inverse());
            window.__auditClick={x:p.x,y:p.y,clientX:e.clientX,clientY:e.clientY};
        },{capture:true,once:true});
        const p=new DOMPoint(v.x+fx*v.width,v.y+fy*v.height).matrixTransform(svg.getScreenCTM());
        return {x:p.x,y:p.y};
    }''', {'name': name, 'fx': fx, 'fy': fy})
    page.mouse.click(position['x'], position['y'])
    expected = page.evaluate('window.__auditClick')
    actual = box(page, 'before')
    span = actual[2]
    wanted = [max(span/2, min(1-span/2, expected[k])) for k in ('x', 'y')]
    center = [actual[0]+span/2, actual[1]+span/2]
    return {'pane': name, 'relative_click': [fx, fy], 'event': expected,
            'expected_center': wanted, 'actual_center': center,
            'maximum_coordinate_error': max(abs(x-y) for x, y in zip(wanted, center)),
            'views_linked': actual == box(page, 'after')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page', type=Path, default=ROOT/'gallery/index.html')
    parser.add_argument('--browser', choices=('chromium', 'firefox'), default='chromium')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    target = args.page.resolve()
    rows = json.loads((ROOT/'discover/working-starts.json').read_text())['rows']
    policy = json.loads((ROOT/'PARTICIPATION.json').read_text())
    failures, views, console_errors = [], [], []
    with sync_playwright() as p:
        browser = getattr(p, args.browser).launch(headless=True)
        version = browser.version
        for label, width, height in [('desktop', 1440, 900), ('narrow', 390, 844)]:
            context = browser.new_context(viewport={'width': width, 'height': height})
            page = context.new_page()
            page.set_default_timeout(10000)
            page.on('pageerror', lambda error: console_errors.append(str(error)))
            page.goto(target.as_uri(), wait_until='load')
            page.locator('details summary').click()
            status = page.locator('.status').inner_text()
            if status != 'Pre-release research preview · Contributor intake '+policy['intake']:
                failures.append(label+': participation status mismatch')
            options = page.locator('#count option').evaluate_all('(els)=>els.map(e=>Number(e.value))')
            if options != [row['n'] for row in rows]:
                failures.append(label+': target list mismatch')
            checks = []
            for row in rows:
                n = row['n']
                page.select_option('#count', str(n))
                data = []
                radii = []
                for name, certificate, digest, radius_id, link_id in [
                        ('before', row['previous_certificate'], row['previous_sha256'], 'oldRadius', 'oldLink'),
                        ('after', row['certificate'], row['sha256'], 'newRadius', 'newLink')]:
                    c = json.loads((ROOT/certificate).read_text())
                    q = int(c['denominator'])
                    r = Fraction(int(c['radius_numerator']), q)
                    radii.append(r)
                    circles = page.locator('#'+name+' circle').evaluate_all(
                        '(els)=>els.map(e=>[Number(e.getAttribute("cx")),Number(e.getAttribute("cy")),Number(e.getAttribute("r"))])')
                    expected = [[int(x)/q, 1-int(y)/q, float(r)] for x, y in c['centers']]
                    coordinate_error = max((abs(a-b) for actual, want in zip(circles, expected)
                                            for a, b in zip(actual, want)), default=0)
                    href = page.locator('#'+link_id).get_attribute('href')
                    resolved = urljoin(target.as_uri(), href)
                    linked_path = Path(unquote(urlparse(resolved).path))
                    linked = href == '../'+certificate and linked_path.is_file() and sha(linked_path) == digest
                    text = page.locator('#'+radius_id).inner_text()
                    good = len(circles) == n and coordinate_error < 1e-14 and linked and text == f'Radius {float(r):.15f}'
                    if not good:
                        failures.append(f'{label}: N={n} {name} coordinate/label/link mismatch')
                    data.append({'pane': name, 'circles': len(circles), 'maximum_coordinate_error': coordinate_error,
                                 'radius_label': text, 'certificate_hash_matches': linked})
                gain = (radii[1]-radii[0])/radii[0]*1_000_000
                gain_text = page.locator('#gain').inner_text()
                match = re.fullmatch(r'\+([0-9.]+) ppm', gain_text)
                gain_ok = gain_text == 'No additional gain' if gain == 0 else (
                    match is not None and abs(float(match.group(1))-float(gain)) <= 0.0005001)
                exact = page.locator('#exact').inner_text()
                exact_ok = all(str(value) in exact for value in (radii[0], radii[1], radii[1]-radii[0]))
                credit_ok = row['construction_credit'] in page.locator('#credit').inner_text()
                hash_ok = row['sha256'] in page.locator('#hash').inner_text()
                dimensions = page.locator('.panel svg').evaluate_all('''(els)=>els.map(e=>{
                    const r=e.getBoundingClientRect(),m=e.getScreenCTM();
                    return {width:r.width,height:r.height,scaleX:Math.hypot(m.a,m.b),scaleY:Math.hypot(m.c,m.d)};
                })''')
                scales = [d[key] for d in dimensions for key in ('scaleX', 'scaleY')]
                equal_scale = max(scales)-min(scales) < 1e-6
                linked = box(page, 'before') == box(page, 'after') == [0, 0, 1, 1]
                if not all((gain_ok, exact_ok, credit_ok, hash_ok, equal_scale, linked)):
                    failures.append(f'{label}: N={n} metadata/scale mismatch')
                checks.append({'n': n, 'panes': data, 'gain_label': gain_text, 'gain_matches': bool(gain_ok),
                               'exact_text_matches': exact_ok, 'credit_matches': credit_ok,
                               'hash_text_matches': hash_ok, 'equal_scale': equal_scale, 'reset_views_linked': linked})
            page.select_option('#count', '700')
            clicks = []
            for name, fx, fy in [('before', .25, .75), ('after', .75, .25), ('before', .02, .98)]:
                page.get_by_role('button', name='Reset view').click()
                click = capture_click(page, name, fx, fy)
                clicks.append(click)
                if click['maximum_coordinate_error'] > 1e-7 or not click['views_linked']:
                    failures.append(f'{label}: {name} click mapping error {click["maximum_coordinate_error"]}')
            page.get_by_role('button', name='Reset view').click()
            slider = page.locator('#zoom')
            slider.scroll_into_view_if_needed()
            bounds = slider.bounding_box()
            page.mouse.click(bounds['x']+bounds['width']*.75, bounds['y']+bounds['height']/2)
            zoom = float(slider.input_value())
            linked = box(page, 'before') == box(page, 'after')
            zoom_ok = zoom > 1 and linked and math.isclose(box(page, 'before')[2], 1/zoom, abs_tol=1e-7)
            if not zoom_ok:
                failures.append(label+': real-pointer zoom slider failed')
            zoomed_click = capture_click(page, 'after', .4, .6)
            clicks.append(zoomed_click)
            if (zoomed_click['maximum_coordinate_error'] > 1e-7 or not zoomed_click['views_linked']
                    or float(slider.input_value()) != zoom):
                failures.append(label+': click while zoomed failed')
            page.get_by_role('button', name='Reset view').click()
            reset = slider.input_value() == '1' and box(page, 'before') == box(page, 'after') == [0, 0, 1, 1]
            if not reset:
                failures.append(label+': reset failed')
            overflow = page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth')
            if overflow:
                failures.append(label+': horizontal overflow')
            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshots/(label+'.png')), full_page=True)
            views.append({'label': label, 'viewport': [width, height], 'status': status, 'targets': checks,
                          'clicks': clicks, 'slider_zoom': zoom, 'slider_linked': bool(zoom_ok),
                          'reset_passed': reset, 'horizontal_overflow': overflow})
            context.close()
        browser.close()
    failures += ['page error: '+error for error in console_errors]
    result = {'status': 'author-checked; no independent review or acceptance', 'engine': args.browser, 'browser': version,
              'page_sha256': sha(target), 'audit_sha256': sha(Path(__file__)),
              'policy_sha256': sha(ROOT/'PARTICIPATION.json'), 'index_sha256': sha(ROOT/'discover/working-starts.json'),
              'views': views, 'page_errors': console_errors, 'failures': failures,
              'not_checked': ['HTTP delivery, physical touch devices, other engines in this invocation',
                              'Wheel zoom or drag panning, which are not advertised or implemented',
                              'External novelty, global optimality or scientific acceptance']}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'engine': args.browser, 'browser': version, 'target_selections': len(rows)*len(views), 'failures': failures}))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
