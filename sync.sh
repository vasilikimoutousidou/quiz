#!/usr/bin/env bash
# Συγχρονίζει όλα τα .quiz αρχεία από το vault (10.Κουίζ/) σε αυτό το repo και
# κάνει push στο GitHub. Το GitHub Actions workflow αναλαμβάνει να ανανεώσει
# αυτόματα το index.html στο Pages μετά το push.
#
# Χρήση:
#   ~/quiz-repo/sync.sh
set -euo pipefail

VAULT_QUIZ_DIR="/home/vasiliki/Έγγραφα/OBSIDIAN/ΑΟΘ/Εκπαιδευτικό υλικό/10.Κουίζ"
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

# Προειδοποίηση για quiz με τίτλο εκτός μορφής (θα πέσουν στα «unmatched» του index).
# Μορφή: "Κεφάλαιο 1: Τίτλος" ή "Κεφάλαιο 1, Ενότητα 2: Τίτλος" στο metadata.title.
if command -v jq >/dev/null; then
  for f in "$DEST_DIR"/*.quiz; do
    t="$(jq -r '.metadata.title // ""' "$f")"
    if ! [[ "$t" =~ ^Κεφάλαιο\ [0-9]+(,\ Ενότητα\ [0-9]+)?:\  ]]; then
      echo "Προσοχή: $(basename "$f") έχει τίτλο εκτός μορφής: «$t»" >&2
    fi
  done
fi

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
