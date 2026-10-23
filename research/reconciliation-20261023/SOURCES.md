# Public artifact investigation, 23 October 2026

**Result:** actual numerical witnesses were found for Aletheia's N=600/700/800 claims in its public [packing repository](https://github.com/0100001001101111/aletheia-packing-records). Fourteen public data/report/document files were retained outside this repository. The three coordinate hashes match the published manifest and an unauthenticated public download. The parent's subsequent exact comparison is recorded in [README.md](README.md) and [results.json](results.json); this note preserves the initial source-only investigation. No N=500 witness or catalogue disposition was obtained in this bounded search; priority remains unresolved.

Research began 2026-10-23 08:52 UTC; the initial artifact search and supporting metadata retrieval finished about 09:06 UTC. This is author-checked AI assistance, not independent review. No external repository code was executed, and no posting, outreach, PR, commit, or frontier change was made.

## Discovery route and dating

The [lab homepage](https://www.projectaletheia.org/) linked an unavailable website-source repository, but also a public [cold-case repository](https://github.com/0100001001101111/cold-case-benford-exoplanet-digits) identifying owner `0100001001101111`. The owner's [public repository index](https://api.github.com/users/0100001001101111/repos?per_page=100&sort=full_name) returned 21 repositories without another page; this exposed `aletheia-packing-records`. This source-archive route supplies evidence absent from the previously audited findings/registry pages. It concerns the independent Project Aletheia lab, not DeepMind's similarly named agent.

Authorship is attributed to **Bo Brothers / Project Aletheia** by the [license](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/LICENSE.md), commit metadata, and [provenance document](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/PROVENANCE.md). The latter describes a 30–31 August 2026 run. Its private source-path references were treated as text only and were not accessed.

| Date type | UTC value / qualification |
| --- | --- |
| Initial commit `ba1d7c959565593d04ba076abab250412a9cda9c` | Author: 2026-08-31 22:03:47; committer: 22:08:47 |
| GitHub repository creation | 2026-08-31 22:26:45 |
| Pinned current commit `d137d44c6eec540b98909231d0e902f0fe4b9b1e` | Author and committer: 2026-09-01 00:01:50 |
| GitHub last push | 2026-09-01 00:01:52 |
| Coordinate retrieval | 2026-10-23 08:58:37.980–08:58:38.160; public-byte confirmation 09:01:09.589–09:01:09.633 |

The [commit listing](https://api.github.com/repos/0100001001101111/aletheia-packing-records/commits?per_page=100) contains three commits. The complete, untruncated [initial tree](https://api.github.com/repos/0100001001101111/aletheia-packing-records/git/trees/ba1d7c959565593d04ba076abab250412a9cda9c?recursive=1) and [pinned tree](https://api.github.com/repos/0100001001101111/aletheia-packing-records/git/trees/44ebb9dba0cc6a0e3d8c015376e93200b12a8a1c?recursive=1) give identical Git blob IDs for all three coordinate files. These are dated numerical artifacts, but Git author/committer dates are author-controlled. Repository creation does not establish when it first became public. No independent timestamp for first public availability or maintainer receipt was recovered.

## Numerical handoff

All retained files are under this exact local directory:

`source-downloads/aletheia-packing-records-d137d44-research-20261023/` in the donor workspace, outside the contribution checkout.

Each linked filename below is relative to that directory. All links pin commit `d137d44c6eec540b98909231d0e902f0fe4b9b1e`.

| N / observed rows | Coordinate artifact | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| 600 | [data/PACKING_N600_SEED_2026083001_CANDIDATE.txt](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/data/PACKING_N600_SEED_2026083001_CANDIDATE.txt) | 53155 | `b9794492f37d28e8d4f92900ef19ebd85f58530f97f5936c245e584c89f8b9b9` |
| 700 | [data/PACKING_N700_SEED_2026083001_CANDIDATE.txt](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/data/PACKING_N700_SEED_2026083001_CANDIDATE.txt) | 61954 | `14ca8170ff3089e63d6e0730f4e4b7e199e3610109880d84d0be5b959d364ede` |
| 800 | [data/PACKING_N800_SEED_2026083001_CANDIDATE.txt](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/data/PACKING_N800_SEED_2026083001_CANDIDATE.txt) | 70756 | `076bc719aa8124ea567c0f85bb9629242670006ea60e5e243737f0dc4190e66d` |

**Units and import convention:** rows contain index, x, y, and claimed radius, at 24 decimal places. The source uses a centered square of side one, **[-0.5, 0.5]²**: its [checker, lines 125–132](https://github.com/0100001001101111/aletheia-packing-records/blob/d137d44c6eec540b98909231d0e902f0fe4b9b1e/verifier/exact_checker.py#L125) uses half-scale plus/minus each coordinate for wall margins. Translation by +0.5 on both axes converts to [0,1]² without rescaling radii. This convention was established by reading source, not executing it.

The radius repeated in each coordinate row is **different from** the larger radius supported by the same centers in the source's saved report. These are transcribed source values, not results certified by this researcher:

| N | Radius stored in rows | Report's downward 24-place radius |
| --- | --- | --- |
| 600 | 0.021479376771905141976215 | 0.021479376779313367924353 |
| 700 | 0.019903642845244116954587 | 0.019903642856359920804145 |
| 800 | 0.018637592296199977923367 | 0.018637592336768517873493 |

The [correction notice](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/CORRECTION_2026-08-31_V1.md), document-dated 2026-08-31 but committed on 2026-09-01, retracts the last digit of the original 101-place N=800 radius display. The historical JSON still contains that superseded display. The notice says the coordinates and downward 24-place value did not change. Parent should recompute geometry from coordinates and avoid treating the old `certified_radius_decimal` field as a feasible certificate.

The [README](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/README.md) reports submission to the catalogue maintainer on 2026-08-31 and describes the candidates as unaccepted. This is the claimant's statement, not a maintainer-authored receipt or a current catalogue decision. Its record/optimality language supplies no independent authority.

The license file calls its CC0-data/MIT-code terms **proposed and conditional on owner approval/publication**; no separate approval was established. Coordinates and reports therefore remain local captures outside the repo, with no redistribution assumed.

## Other retained artifacts

Retrieved 2026-10-23 08:58:37.604–08:58:38.246 UTC. Hashes below are SHA-256 of retained bytes. All nine data/report files match `ARTIFACTS.sha256`; copied text lengths also match GitHub's listed sizes. Saved reports are author-supplied evidence, not independent review.

| Artifact | SHA-256 |
| --- | --- |
| [ARTIFACTS.sha256](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/ARTIFACTS.sha256) | `928f836535d32b539758534b3809b8b75651f029bcd0879364120c49d873464f` |
| [README.md](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/README.md) | `5d439540e532ef42a3181f779117cff5629d7efb27fe8e8f3f1538fcb8de28ba` |
| [PROVENANCE.md](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/PROVENANCE.md) | `2522da1c9ded49b4b762489d4d0dc25d2c56f7d02cf675a445e4edf579422113` |
| [LICENSE.md](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/LICENSE.md) | `c78a673662bec75ad1a434013f07bd9d083080f72340d8d69f6240ede9766847` |
| [CORRECTION_2026-08-31_V1.md](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/CORRECTION_2026-08-31_V1.md) | `9f2447b3b53ffbe1b238a281af39ad0be6fc9660be60a7d34843af8b476b279a` |
| [checks/PACKING_N600_SEED_2026083001_EXACT_CHECK.json](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/checks/PACKING_N600_SEED_2026083001_EXACT_CHECK.json) | `5740e8b536c7ed8d54138fe41227683afdb5856d1f0dde39662c06cbfb32f958` |
| [checks/PACKING_N600_SEED_2026083001_MPMATH_CHECK.json](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/checks/PACKING_N600_SEED_2026083001_MPMATH_CHECK.json) | `29d9d6efaa88400ef860cdafce67b1ed16dfcf9b5dd99b6a0a0aac3f4a64342d` |
| [checks/PACKING_N700_SEED_2026083001_EXACT_CHECK.json](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/checks/PACKING_N700_SEED_2026083001_EXACT_CHECK.json) | `7b608d1a92af327f2d17b25f3539dfba1195ead114703efcc5fdd892615ac847` |
| [checks/PACKING_N700_SEED_2026083001_MPMATH_CHECK.json](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/checks/PACKING_N700_SEED_2026083001_MPMATH_CHECK.json) | `47162a0e614e9189cab57cb757674fe41e53fc78273864686cd64fd1de6ab2bc` |
| [checks/PACKING_N800_SEED_2026083001_EXACT_CHECK.json](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/checks/PACKING_N800_SEED_2026083001_EXACT_CHECK.json) | `a154a55d9a337a37e7be7bb8870f8ece7af3822d216a2b0df81f002ee166ec7f` |
| [checks/PACKING_N800_SEED_2026083001_MPMATH_CHECK.json](https://raw.githubusercontent.com/0100001001101111/aletheia-packing-records/d137d44c6eec540b98909231d0e902f0fe4b9b1e/checks/PACKING_N800_SEED_2026083001_MPMATH_CHECK.json) | `9e6f906257c132ab6e6b4a7de00f24a91273ab5772fc4e7bbcefe952906651fa` |

## Bounded access log and limits

All times below are 2026-10-23 UTC. HTTP metadata dates are not treated as publication dates.

| Public source actually inspected | Retrieval / result |
| --- | --- |
| [Datasets](https://www.projectaletheia.org/datasets), [methods](https://www.projectaletheia.org/methods), findings/homepage links | 08:52–08:55; used to trace artifact publication, not to repeat catalogue comparisons. Raw datasets HTML at 08:54:52 was 22651 bytes, SHA-256 `0a04349e53bf0cccca2445f2bbdc107683786083c16ab993b31cf200e579cd8b`. |
| [Advertised website source](https://github.com/0100001001101111/project-aletheia) | 08:54–08:55; public HTTP 404 in web and urllib retrieval. This does not distinguish removal, renaming, or private status. |
| [Owner repository index](https://api.github.com/users/0100001001101111/repos?per_page=100&sort=full_name) | 08:55–08:56; 21 public entries, no pagination link. Packing repository selected from this index, without guessing an identifier. |
| [Packing image](https://www.projectaletheia.org/findings/packing-records-2026-08-31.png) | 08:56:31; PNG, 1754×2106, 855126 bytes, SHA-256 `d425699622673f3130924e933edd6d5b0941ca65aa3a9c2ec8595af64092894e`. Parsed chunk metadata contains Matplotlib software identification, no coordinate payload. No raster-to-coordinate reconstruction attempted. |
| [Repository metadata](https://api.github.com/repos/0100001001101111/aletheia-packing-records), commit listing, both recursive trees | Final timestamped retrievals 09:04:31.601–09:04:31.644; HTTP 200. The complete data directories contain only N=600/700/800. Their scope supplies no N=500 candidate. |
| [Releases](https://api.github.com/repos/0100001001101111/aletheia-packing-records/releases?per_page=100), [tags](https://api.github.com/repos/0100001001101111/aletheia-packing-records/tags?per_page=100), [events](https://api.github.com/repos/0100001001101111/aletheia-packing-records/events?per_page=100), [issues](https://api.github.com/repos/0100001001101111/aletheia-packing-records/issues?state=all&per_page=100) | Releases 09:04:31.828; tags/events 09:01:09.746–09:01:09.817; issues about 09:00. All inspected lists empty. The GitHub connector rejected events/tags as unsupported URLs; ordinary unauthenticated GET succeeded. An empty events list does not establish historical absence. |
| [Documented public board guide](https://www.projectaletheia.org/community-agent.md), [packing-title search](https://www.projectaletheia.org/api/community?q=packing&offset=0), [circle-title search](https://www.projectaletheia.org/api/community?q=circle&offset=0) | Guide 08:55–08:56; searches 09:02:51.619 and 09:02:52.284; each returned total 0. This was a title search, not a search of every message or attachment. Both 61-byte JSON responses had SHA-256 `6bbeebb3ea0bb5ad54a90d2b52693561ee9f5d291943147868640e88410dcef3`. No key, registration, or write action used. |
| [Owner profile README](https://api.github.com/repos/0100001001101111/0100001001101111/contents/README.md), [Record Forge root](https://api.github.com/repos/0100001001101111/aletheia-record-forge/contents), [README](https://api.github.com/repos/0100001001101111/aletheia-record-forge/contents/README.md) | 08:56–09:03; the inspected Record Forge root/README concerns a Ramsey witness, not the requested circle counts. No deeper unrelated case files were inspected. |

For reproducibility, the final raw HTTP response SHA-256 values were: repository metadata `9153e95f85c816114296cc8771285456158a9c1c8d5c04e26daf5dca4fda8ace`; commit listing `54de2d5e9e44d72dde9673e9252fa227448b66a1d0fd7a3790bb184c8a6d7712`; initial tree `b6c25083de01163f6751fa8737da134254090c3b14b12a9c91c62e5c5f6967c5`; pinned tree `be5611915896d85443bbf724b96e12ffe26b1b64a09eebbd2ce9f8466728f29b`. Empty release/tag/event responses were the two bytes `[]`, SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.

Not checked: other branches/forks, the remaining unrelated owner repositories, every board message, general paper supplements, ZeroThesis's artifact archive, web-archive/Software Heritage histories, or a fresh Packomania disposition. No claim of exhaustive absence follows. The failed native curl attempt was intercepted by context-mode before retrieval; public urllib and GitHub reads subsequently worked. The context fetch converter was not used, and no unrelated filesystem root was accessed.

**Actionable next evidence:** the parent can now translate and verify these pinned files, then compare against the exact working starts while preserving attribution and source dates. Ordering or acceptance still needs a dated catalogue/maintainer disposition or adequately established earlier-publication evidence; N=500 additionally needs an identified numerical claimant witness. Redistribution needs clear approval of the proposed terms. No contact with authors or recordkeepers was attempted or requested here.
