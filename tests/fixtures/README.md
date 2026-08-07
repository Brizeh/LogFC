# Fixtures

Deux charges utiles par log (`jcontent` scrape depuis la page HTML,
`pjcontent` depuis l'API JSON), gzippees et elaguees des cles qu'aucun
fichier de `src/` ne reference.

| Fixture | Ce qu'elle couvre |
|---|---|
| `sh` | cas standard, mecaniques de mur et de chute |
| `dei` | huiles noires, tears, MVP a plusieurs joueurs |
| `adina` | degats de split via `jcontent['phases'][n]['dpsStats']`, indices en dur |
| `gors` | degats de split via `get_phase_id("Split 1")` et `dpsStatsTargets` |
| `dhuum` | `real_phase = "Dhuum Fight"` (seul boss a le surcharger) et mode CM |
| `qadim` | phases multiples, comparaison DPS/support |

## URLs

`sh`, `dei` et `adina` portent leur permalink d'origine.

`gors`, `dhuum` et `qadim` proviennent de dumps JSON locaux qui n'avaient
pas conserve le leur : leur URL est reconstruite a partir du timestamp
reel du log, avec un code a quatre caracteres neutre (`Fix1`, `Fix2`,
`Fix3`). Ces liens ne pointent donc nulle part — ils servent uniquement
de cle dans ARXIV et de cible au regex de detection. C'est sans effet sur
les tests.

## Ajouter une fixture

```bash
python -m tests.capture_fixture <url>
python -m tests.test_pipeline --update
```
