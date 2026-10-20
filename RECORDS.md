# Source-backed record table

All radii refer to equal circles inside a unit square. Published values are rounded source numbers; local values are exact feasible decimal rationals. No row claims external acceptance or optimality. Source snapshots: 20 October 2026.

| N | Published radius | Certified local radius | Δ vs published | Disposition | Witness / SVG |
|---:|---:|---:|---:|---|---|
|100|[0.051401071774](https://packomania.com/csq/csq100.html)|0.051401071774379|+3.790E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n100.json) · [SVG](images/frontier/n100.svg)|
|106|[0.050015200426](https://packomania.com/csq/csq106.html)|0.050015200426096|+9.600E-14|numerical tie; baseline reproduced|[JSON](certificates/frontier/n106.json) · [SVG](images/frontier/n106.svg)|
|134|[0.044564244207](https://packomania.com/csq/csq134.html)|0.044564244207095|+9.500E-14|numerical tie; baseline reproduced|[JSON](certificates/frontier/n134.json) · [SVG](images/frontier/n134.svg)|
|150|[0.042145465901](https://packomania.com/csq/csq150.html)|0.042145465901232|+2.320E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n150.json) · [SVG](images/frontier/n150.svg)|
|200|[0.036612798904](https://packomania.com/csq/csq200.html)|0.03661279890382|-1.800E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n200.json) · [SVG](images/frontier/n200.svg)|
|250|[0.032879800210](https://packomania.com/csq/csq250.html)|0.032879800209483|-5.170E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n250.json) · [SVG](images/frontier/n250.svg)|
|300|[0.030219555704](https://packomania.com/csq/csq300.html)|0.030219555704457|+4.570E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n300.json) · [SVG](images/frontier/n300.svg)|
|400|[0.026202507077](https://packomania.com/csq/csq400.html)|0.026202507076218|-7.820E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n400.json) · [SVG](images/frontier/n400.svg)|
|500|[0.023455498994](https://packomania.com/csq/csq500.html)|0.0234554989935|-5.000E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n500.json) · [SVG](images/frontier/n500.svg)|
|600|[0.021479376754](https://packomania.com/csq/csq600.html)|0.021479896578172|+5.198E-7|published-baseline improvement; novelty unresolved|[JSON](certificates/frontier/n600.json) · [SVG](images/frontier/n600.svg)|
|700|[0.019903642828](https://packomania.com/csq/csq700.html)|0.019903696933565|+5.411E-8|published-baseline improvement; novelty unresolved|[JSON](certificates/frontier/n700.json) · [SVG](images/frontier/n700.svg)|
|800|[0.018637592286](https://packomania.com/csq/csq800.html)|0.01863759228589|-1.100E-13|numerical tie; baseline reproduced|[JSON](certificates/frontier/n800.json) · [SVG](images/frontier/n800.svg)|

N=500–800 overlap the range of 557 pending `csq` submissions. N=600,700,800 also have Aletheia pending claims without accessible numerical witnesses in this audit. Other rows have no matching range in the frozen pending list, which does not establish novelty. Full attribution, source dates and uncertainty are in `data/frontier.json`.

## Comparison with pre-2023 history

Lai et al. Tables 4/6 report earlier best container side lengths for unit-radius circles. Inverting their conservatively guarded printed values gives the radius comparison below. Gains already present in the published source are rediscoveries, not new records.

| N | Historical L | Guarded historical r upper | Local r minus upper | Interpretation |
|---:|---:|---:|---:|---|
|100|19.454847253|0.051401071776454|-2.075E-12|Tie/precision-scale difference; no novelty inference|
|106|19.993921681|0.050015200419651|+6.445E-12|Tie/precision-scale difference; no novelty inference|
|200|27.312853154|0.036612798904539|-7.193E-13|Tie/precision-scale difference; no novelty inference|
|250|30.417031057|0.032876318472994|+3.482E-6|Known historical advance already in Packomania|
|300|33.091154939|0.030219555705252|-7.945E-13|Tie/precision-scale difference; no novelty inference|
|400|38.164523000|0.026202345042442|+1.620E-7|Known historical advance already in Packomania|

Source: [Lai et al., author manuscript](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalJOC2023.pdf), Tables 4 and 6; historical centers were not imported. [Audit and guards](AUDIT.md).
