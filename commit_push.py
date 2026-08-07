#!/usr/bin/env python3
"""Commits and pushes LogFC's changes.

Displays the current git status, asks for confirmation then a commit
title, commits (git add -A) and pushes to origin/main. A negative
answer or an empty title cancels the operation. Also detects local
commits already made but never pushed (e.g. committed via another
tool) and offers to push them even when there's nothing new to commit.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def capture(*args):
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout


def push_pending_commits():
    try:
        run("git", "fetch", "origin", "main")
    except subprocess.CalledProcessError:
        print("Impossible de contacter origin (pas de reseau ?), verification annulee.")
        return

    pending = capture("git", "log", "origin/main..HEAD", "--oneline").strip()
    if not pending:
        print("Rien a committer ni a pousser.")
        return

    print("=== Commits locaux non pousses ===")
    print(pending)
    confirm = input("Pousser ces commits sur origin/main ? (o/n) : ").strip().lower()
    if confirm not in ("o", "oui", "y", "yes"):
        print("Annule.")
        return
    run("git", "push", "origin", "main")


def main():
    status = capture("git", "status", "--short")

    if not status.strip():
        push_pending_commits()
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
