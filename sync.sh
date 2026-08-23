#!/usr/bin/env bash
# Συγχρονίζει όλα τα .quiz αρχεία από το vault (10.Quiz/) σε αυτό το repo και
# κάνει push στο GitHub. Το GitHub Actions workflow αναλαμβάνει να ανανεώσει
# αυτόματα το index.html στο Pages μετά το push.
#
# Χρήση:
#   ~/quiz-repo/sync.sh
set -euo pipefail

VAULT_QUIZ_DIR="/home/vasiliki/Έγγραφα/ΑΟΘ/10.Quiz"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="$REPO_DIR/quizzes"

if [ ! -d "$VAULT_QUIZ_DIR" ]; then
  echo "Δεν βρέθηκε ο φάκελος του vault: $VAULT_QUIZ_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# Αντιγραφή/ενημέρωση όλων των τρεχόντων .quiz
shopt -s nullglob
for f in "$VAULT_QUIZ_DIR"/*.quiz; do
  cp "$f" "$DEST_DIR/"
done

# Αφαίρεση .quiz που υπάρχουν στο repo αλλά όχι πια στο vault
for f in "$DEST_DIR"/*.quiz; do
  base="$(basename "$f")"
  if [ ! -f "$VAULT_QUIZ_DIR/$base" ]; then
    rm -f "$f"
  fi
done
shopt -u nullglob

cd "$REPO_DIR"
git add -A quizzes/

if git diff --cached --quiet; then
  echo "Δεν υπάρχουν αλλαγές — τα quiz είναι ήδη συγχρονισμένα."
  exit 0
fi

echo "Αλλαγές προς commit:"
git diff --cached --stat -- quizzes/

git commit -q -m "Sync quizzes: $(date '+%Y-%m-%d %H:%M')"
git push -q

echo "Έγινε push — το site θα ανανεωθεί σε ~30-60 δευτ."
