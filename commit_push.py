#!/usr/bin/env python3
"""Committe et push les changements de LogFC.

Affiche le statut git courant, demande confirmation puis un titre de
commit, committe (git add -A) et push sur origin/main. Une reponse
negative ou un titre vide annule l'operation.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def main():
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout

    if not status.strip():
        print("Rien a committer.")
        return

    print("=== Changements detectes ===")
    print(status)

    confirm = input("Continuer avec ces changements ? (o/n) : ").strip().lower()
    if confirm not in ("o", "oui", "y", "yes"):
        print("Annule.")
        return

    title = input("Titre du commit : ").strip()
    if not title:
        print("Titre vide, annule.")
        return

    run("git", "add", "-A")
    run("git", "commit", "-m", title)
    run("git", "push", "origin", "main")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAnnule.")
