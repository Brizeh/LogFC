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

## La source de donnees

Une seule requete par log, vers l'API JSON officielle
(`getJson?permalink=`) : `log.pjcontent`. Le projet ne scrape plus la
page HTML de dps.report.

Une seule chose n'existe pas dans cette API : le temps de grace (`icd`)
de chaque mecanique, necessaire pour reproduire les valeurs agregees
d'Elite Insights. Il est fige dans `src/mechanic_icd.json`, alimente par
`python -m tools.update_mechanic_icd <url>` — le seul endroit du projet
qui lit encore le HTML, et uniquement a la demande.

Quand un boss ou une mecanique manque a cette table, LogFC l'ecrit sur
la sortie standard et suppose un `icd` nul, ce qui **surestime** la
valeur de la mecanique concernee. Le run continue.

### Le calcul des mecaniques

`src/mechanics.py` reproduit le tableau que la page HTML fournissait
tout fait. Trois regles, validees sur 7676 cellules de reference :

- la valeur est une **somme de poids** (`weight`), pas un nombre
  d'evenements : un "Breakbar Damage" pese les degats infliges
- la fenetre d'`icd` demarre a **t=0**, pas au premier evenement
- elle **se rearme a chaque evenement**, meme ignore : une rafale
  rapprochee ne compte donc que pour un

⚠️ Les noms different entre l'API et l'ancien HTML : `pjcontent` expose
`fullName` (nom long, celui qu'utilise `get_mech_value`) et `name` (nom
court, la cle dans ARXIV). L'ancien HTML les appelait respectivement
`name` et `shortName`.

**Ajustements de comptage au cas par cas** : `Boss.mechanic_exclusions(mech_name)`
renvoie une liste de fenetres `(debut_ms, fin_ms)` a exclure des evenements
d'une mecanique avant l'agregation par `icd` — vide par defaut, a surcharger
dans une classe de boss pour un choix de comptage propre a ce boss (pas pour
corriger un bug d'Elite Insights). Exemple : DHUUM ignore les "Ender's Pick
up" survenant a moins de 5s du debut de la phase "Shielded Dhuum".

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

## L'objet Analysis

Tout ce qui varie d'un run a l'autre vit dans une instance d'`Analysis`
(`src/analysis.py`) : `bosses`, `players`, `arxiv`, `extra_mechs`, `dups`.
Elle se cree en debut d'analyse et se passe explicitement :

```python
analysis = Analysis(title="Run", language="FR")
InputParser(texte, analysis)
BossFactory.create_boss(log, analysis)      # pour chaque log
wingman.fetch_percentiles(analysis.bosses)  # une passe parallele
func.get_message_reward(analysis)
```

⚠️ **`fetch_percentiles` est une etape a part entiere.** L'oublier ne
provoque aucune erreur : les notes wingman disparaissent simplement du
message. Elle est separee parce que la creation d'un boss ne fait plus
aucun appel reseau, ce qui rend le pipeline testable hors-ligne, et
parce que ces appels ne valent la peine qu'en lot (un par boss, sinon
sequentiels).

Deux analyses peuvent donc tourner en parallele, y compris dans des
langues differentes. Il n'y a rien a reinitialiser entre deux runs :
l'objet est jete a la fin.

Ne vit **pas** dans `Analysis` : la configuration partagee en lecture
seule (`CUSTOM_NAMES`, `ALL_MECHS`, `LANGUES`, `mechanic_icd.json`).

### Les messages localises

Depuis une methode de `Boss`, toujours passer par le helper, jamais par
`LANGUES` directement :

```python
return self.msg("GORS MVP EGG P", mvp_names=mvp_names)
```

Il resout la cle dans la langue de l'analyse en cours et leve une erreur
explicite si elle manque aux deux dictionnaires. En dehors d'un `Boss`
(`func.py`), utiliser `analysis.language["CLE"]`.

## Structure d'ARXIV

```
analysis.arxiv[url_log][account][categorie][stat] = {"value": ..., "description": ...}
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
- L'etat de run se passe explicitement via `Analysis`, jamais par une
  variable de module
