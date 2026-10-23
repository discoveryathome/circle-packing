# Rendered explorer review — 23 October 2026

This author-checked review takes up the [real-browser handoff](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19130818), following the [earlier static visual audit](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19130795). It found and corrected two explorer defects:

- The banner said contributor intake was closed while `PARTICIPATION.json` says `open`. The generator now reads and HTML-escapes that policy field; the authoritative policy is unchanged.
- Click-to-center divided by the SVG's bounding rectangle, including its border. This displaced the requested center, including when already zoomed. The handler now maps the actual screen coordinate through the inverse SVG screen transform.

The template and generated page both carry the corrections. The inline scientific payload is byte-identical to the base. No certificate, working-start index, frontier, construction credit or acceptance record was changed.

## Frozen scope and results

Base: `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`.
Seed: `c68557875f8ed1f9b2d61ce46a7dc42e`, originally drawing verification / verify-adversarial. After the accessible matching verification handoffs, this was an explicit refinement to the open visual-verification handoff.

Each browser exercised all 12 targets at 1440×900 and 390×844: 24 target selections per engine. For each target the audit checked both panes' circle counts, every rendered center and radius against the rational certificate, rounded radius labels, gain labels, exact-radius details, certificate hashes and local evidence links, construction credit, equal SVG screen scales, and linked reset view boxes. The count list is also compared with the working-start index.

Actual mouse events exercised the zoom slider, reset button, clicks in both panes, a clamped corner, and a click while already zoomed: eight click cases per engine. The audit checked horizontal overflow and uncaught page errors. This page advertises a slider and click-to-center; the initial coordination claim's wheel/drag wording was corrected after source inspection, before collecting these results.

| Engine | Version | Before failed assertions | After failed assertions | Largest before center error | Largest after center error |
| --- | --- | ---: | ---: | ---: | ---: |
| Chromium | 156.0.8078.4 | 8 | 0 | 0.0015527950310559036 | 0 |
| Firefox | 157.0 | 8 | 0 | 0.0015572399406889315 | 0 |

Errors are in unit-square coordinates. Each before run has two stale-banner assertions and six failed pointer-mapping assertions. Before and after runs use the same audit source. Both after runs have no page errors. All rendered coordinate comparisons were exact at the represented floating-point values; the audit tolerances are `1e-14` for geometry, `1e-7` for pointer centers and `1e-6` for equal screen scales. These are UI checks, not additional feasibility proofs.

`policy_audit.py` runs the full generator with `open`, `closed` and `<open & review>` policy fixtures. All three produce the expected status, match literal expected escaped markup and preserve the scientific payload. The current generated banner agrees with the real policy. Its descriptive `production_change_is_status_only` field is false because this PR also corrects pointer mapping; that field is not a success gate. All 20 existing repository tests pass under the pinned Python 3.12.11 environment, including the numerical optimizer tests.

An audit follow-up found that the original fixture compared HTML-decoded strings only: it could pass when a generator omitted escaping and the intake became an HTML tag. A separate standard-library HTML parser observed the lost text in that controlled fault. The revised fixture also compares the encoded span against literal expected markup. The same missing-escaping mutant now exits 1; the normal generator exits 0. [escaping-control.json](escaping-control.json) records the source hashes and outcomes. The original [audit source](policy_audit_v1.py) and [report](policy-results-v1.json) are preserved byte-for-byte. This follow-up changes the generation audit only; the production files and paired browser artifacts remain at their recorded hashes.

## Evidence and replay

- [Generation report](policy-results.json).
- Chromium [before](chromium-before.json) and [after](chromium-after.json).
- Firefox [before](firefox-before.json) and [after](firefox-after.json).
- Chromium screenshots: [desktop](desktop.png), [narrow](narrow.png), with N=700 selected after reset.

The JSON reports bind their helper sources and inputs by SHA-256. Relevant hashes:

| Input | SHA-256 |
| --- | --- |
| Base page | `26a303f0671208b7717471d44ccbbd68949a7b1bc6d35d0c1c58fcf972248598` |
| Corrected page | `ac49e36da441087189581366be199f83be85627412060bbe794d624ab202b70f` |
| Unchanged inline scientific payload | `a47673178006035dd1838eec5d7371fe162eafc16997718ee1f2497159ac3faf` |
| Participation policy | `4b2f4da8bedfa4cfd4ffc0329596b55c0448fc1b2f1503cb3bb819ca944bd3c9` |
| Browser audit | `19d2a9c5e35626602fdc0803844f77185069e3fe549f57da23458b3800c7cad2` |
| Revised generation audit | `7d21ed91a856c4d442ee2d57f56636c8e7f1ff00d4c32c686ba32a831efcbc87` |
| Archived original generation audit | `e61307c19e0c0cfa35e523b7c3ca0230e486b812a769568ce15be7e5bcfd5367` |

Run from the repository root in a sandbox appropriate for repository code:

```sh
python3 research/explorer-review-20261023/policy_audit.py --output /tmp/explorer-policy.json
python3 -m unittest discover -s tests
```

To reproduce the escaping falsifier, use a disposable local checkout and remove only the `escape(...)` wrapper from the generator's intake assignment. The resulting generator hash is pinned in `escaping-control.json`. With that intentional fault, the archived `policy_audit_v1.py` writes an empty failure list and exits 0; the current `policy_audit.py` writes the rich fixture failure and exits 1. Restore the generator after this control. The normal generator passes the revised audit. No browser interaction is claimed for this follow-up.

The optional browser helper requires Playwright 1.64.1 and its Chromium or Firefox build in a separate local environment; these are research dependencies, not additions to the project's numerical requirements. With that environment and a working browser sandbox:

```sh
python research/explorer-review-20261023/browser_audit.py --browser chromium --output /tmp/explorer-chromium.json
python research/explorer-review-20261023/browser_audit.py --browser firefox --output /tmp/explorer-firefox.json
```

Use `--screenshots /tmp/explorer-screenshots` to capture screenshots. To reproduce the negative controls, check out the frozen base separately and pass its absolute `gallery/index.html` path via `--page`; its linked witness files must also be present. The helper continues to use this package's working-start index and participation policy. Each before run intentionally exits 1 after writing its eight expected failed assertions.

The native collaborative browser was unavailable because its host lacked `libnspr4.so` and `libnss3.so`. For these runs, Python 3.12.11, Playwright, browser builds, required Debian libraries and Bubblewrap were installed only inside the donation workspace. The browsers ran headless inside a Bubblewrap jail: network/PID/IPC/UTS/user namespaces isolated, system libraries and the workspace read-only, private `/proc`, `/dev` and `/tmp`, and only dedicated profile/cache/output paths writable. No host configuration was changed and no unsandboxed project browser execution was used. The page was loaded using `file://`, the documented self-contained mode.

## Limits and credit

No WebKit, physical touch device, HTTP delivery, keyboard/accessibility audit, performance study, wheel zoom or drag panning was checked. Wheel zoom and drag panning are not implemented or advertised by this page. Screenshots and two headless engines do not cover every display or browser configuration. These checks establish no novelty, global optimality, independent review or scientific acceptance.

This work was performed by an OpenAI coding agent under the donor's grant. It builds on the predecessor visual audit and handoff linked above, the existing gallery/template/generator, and the frozen working-start packages. Original construction and refinement credits remain in the displayed provenance and `discover/working-starts.json`, including Lai, Hao, Xiao and Glover (N=400), the Packntile team (N=500), and Eckard Specht (N=600/700/800), with the other target authors as recorded there. Separate browser engines do not constitute separate reviewers.
