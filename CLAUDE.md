# LogFC

Analyse des logs GW2 (dps.report) pour produire un message de run Discord
avec titres MVP/LVP. Le dossier `src/` est aussi consomme tel quel par le
bot Discord `clean_bot` (sous le nom `gw2_analyzer`), d'ou les imports
relatifs.

## Lancer le projet

```bash
python -m src.main
```

Depuis la racine, **jamais** `python src/main.py` : `src` est un package a
imports relatifs, l'execution directe leve
`ImportError: attempted relative import with no known parent package`.
Sous VSCode, utiliser F5 avec la config `LogFC: src.main`.

La console Windows est en cp1252 et plante sur les emojis du message :
prefixer par `PYTHONIOENCODING=utf-8` ou rediriger vers un fichier.

## Tests

```bash
python -m tests.test_pipeline
```

Hors-ligne, sans dependance externe, ~1s : le pipeline est rejoue sur les
fixtures de `tests/fixtures/` (appels wingman neutralises, `CUSTOM_NAMES`
vide pour que la sortie ne depende pas du fichier local).

**A lancer avant et apres tout refactor.** Le test principal compare le
message produit a `tests/expected/run_message.txt` : c'est le filet qui
protege les changements de structure. Si le message change volontairement,
regenerer la reference avec `--update` apres avoir verifie le diff.

Pour ajouter un boss au jeu de tests :
`python -m tests.capture_fixture <url>` (les fixtures sont elaguees des
donnees que le code ne lit jamais, ce qui divise leur poids par deux).

## Les deux sources dps.report

Chaque `Log` porte deux charges utiles **distinctes**, recuperees par deux
requetes separees :

| Attribut | Origine | Usage |
|---|---|---|
| `pjcontent` | API JSON officielle (`getJson?permalink=`) | quasi tout |
| `jcontent` | **scraping HTML** de la page (variable JS `_logData`) | voir ci-dessous |

`jcontent` ne sert qu'a quatre choses :
- `triggerID` (identification du boss, dans `boss_facto.py`)
- `mechanicMap` et `phases[].mechanicStats` (compteurs de mecaniques)
- `players[].name`
- `phases[].dpsStatsTargets` / `dpsStats` (degats par phase, splits)

Le scraping teste deux formats en dur (`var _logData =` puis
`const _logData =`) et laisse `jcontent = None` en cas d'echec : si
dps.report change son template, tout casse a `log.jcontent['triggerID']`.

⚠️ Les deux schemas nomment differemment les memes concepts :
`jcontent` utilise `name` / `shortName`, `pjcontent` utilise
`fullName` / `name`. Ne pas les confondre en passant de l'un a l'autre.

## Ajouter un boss

Quatre endroits, a tenir en coherence :

1. `const.py` -> `BOSS_DICT[triggerID] = "suffixe_url"` (le suffixe des URLs
   dps.report, ex. `_sh`, `_dei` ; il sert aussi au regex de `input.py`)
2. `boss_facto.py` -> `_BOSS_FACTORY["suffixe_url"] = MaClasse`
3. `sub_models/<categorie>_bosses.py` -> la classe, heritant de `Boss`
4. `languages_dict/french.py` **et** `english.py` -> les cles de message

Modes d'echec : oubli en 1 -> le boss est ignore sans aucun message ;
oubli en 2 -> `KeyError` ; oubli en 4 -> plantage au moment de generer le
message, pas au parsing.

Un boss peut avoir plusieurs `triggerID` (ex. DECIMA : 26774 et 26867).

## Structure d'ARXIV

```
ARXIV[url_log][account][categorie][stat] = {"value": ..., "description": ...}
```

C'est un **instantane par log** : pas de cumul ni de moyenne a l'ecriture.
Les agregations (somme, `presence`, moyennes) se font en aval, cote bot.

Indexe par `account` (identifiant stable, ex. `Lyco.3528`), jamais par
surnom d'affichage : un surnom qui change scinderait le joueur en deux
entrees.

## Donnees locales

`src/custom_names.json` et `src/input_logs.txt` contiennent des donnees
personnelles (comptes, identifiants Discord) et sont **non suivis par
git**. Templates : les fichiers `.example` correspondants. Ne jamais les
re-tracker : `Commit.bat` fait `git add -A`.

## Conventions

- Alignement des `=` en colonnes dans les blocs d'affectations consecutives
- Bannieres de section : `################################ MVP ################################`
- Messages `print` en anglais dans le code ; le francais vit dans
  `languages_dict/`
- Etat global mutable dans `const.py` (`ALL_BOSSES`, `ALL_PLAYERS`, `ARXIV`,
  `EXTRA_MECHS`, `DUPS_CHECKER`) ; `func.get_message_reward` les vide en fin
  d'appel
