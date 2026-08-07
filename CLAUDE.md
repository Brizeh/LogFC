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

Hors-ligne, sans dependance externe, ~2s : le pipeline est rejoue sur les
fixtures de `tests/fixtures/` (appels wingman neutralises, `CUSTOM_NAMES`
vide pour que la sortie ne depende pas du fichier local). Voir
`tests/fixtures/README.md` pour ce que couvre chaque fixture.

**A lancer avant et apres tout refactor.** Deux tests de non-regression
comparent les messages produits a `tests/expected/` : un run complet de
trois logs, puis chaque boss rejoue seul pour qu'un echec designe
directement la classe fautive. Si le message change volontairement,
regenerer les references avec `--update` apres avoir verifie le diff.

⚠️ Le filet ne couvre que les boss presents en fixture. Un refactor
transverse peut casser un boss non couvert sans qu'aucun test bronche :
c'est arrive lors du passage au registre, ou la confusion entre `boss_id`
et triggerID n'a ete rattrapee que par une comparaison manuelle avec
l'ancienne table. Pour ce genre de changement, verifier aussi par
equivalence avec l'etat precedent.

Pour ajouter un boss au jeu de tests :
`python -m tests.capture_fixture <url>` puis `--update`.

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

Une classe dans `sub_models/<categorie>_bosses.py`, plus les cles de
message dans `languages_dict/french.py` **et** `english.py`. Il n'y a
aucune table de correspondance a mettre a jour : la classe s'enregistre
seule dans `Boss.registry` via `__init_subclass__`.

```python
class MONBOSS(Boss):

    name       = "MONBOSS"
    boss_id    = 12345      # identifiant de l'API wingman
    url_suffix = "monboss"  # suffixe des URLs dps.report
    wing       = 8
```

⚠️ **`boss_id` n'est pas le triggerID du log.** C'est l'identifiant de
l'API wingman, et les deux different pour DARKAI, HT, KO et OLC. Par
defaut le boss est enregistre sous `boss_id` ; des qu'ils divergent, ou
qu'un boss a plusieurs triggerID, il faut declarer `trigger_ids` :

```python
    boss_id     = 24375     # wingman
    trigger_ids = (43488,)  # triggerID reel du log
```

`url_suffix = None` retire le boss de la detection d'URL dans une liste
collee : c'est le cas du golem, pour que les logs de practice ne
polluent pas un run.

Seul mode d'echec restant : une cle de langue oubliee, qui plante au
moment de generer le message et non au parsing. Le test
`languages_have_the_same_keys` l'attrape.

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
