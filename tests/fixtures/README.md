# Fixtures

La reponse de l'API JSON de dps.report pour un log (`<nom>.pjcontent.json.gz`),
gzippee et elaguee des cles qu'aucun fichier de `src/` ne reference.
Certaines ont en plus un `<nom>.crdata.json.gz` : les donnees de replay
HTML, pour les boss avec `Boss.needs_replay_data = True` (uniquement SH
aujourd'hui).

| Fixture | Ce qu'elle couvre |
|---|---|
| `sh` | cas standard ; pas de `crdata`, la detection de mur n'y est pas exercee |
| `sh_wall` | mort reelle au mur, verifiee a la main (voir `test_sh_wall_detection`) ; a son propre `crdata` |
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
python -m tools.update_mechanic_icd <url>
python -m tests.test_pipeline --update
```

La deuxieme commande n'est necessaire que si le boss manque encore a
`src/mechanic_icd.json` ; `test_icd_table_covers_the_fixtures` le
signale. Le `crdata` (pour un boss avec `needs_replay_data = True`) est
capture automatiquement par la premiere commande.

`--name <fixture>` force le nom de fichier au lieu du suffixe d'URL du
boss : necessaire pour capturer un second log d'un boss deja couvert
par une fixture existante (cas de `sh_wall`, meme boss que `sh`).
