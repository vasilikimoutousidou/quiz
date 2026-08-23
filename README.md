# Quiz — Αρχές Οικονομικής Θεωρίας

Τα `.quiz` αρχεία στο [`quizzes/`](./quizzes) τροφοδοτούν την εφαρμογή
[Quizdy](https://vicajilau.github.io/quizdy/) μέσω raw links.

Η σελίδα με τα links δημοσιεύεται αυτόματα στο GitHub Pages και ανανεώνεται
σε κάθε push (βλ. `.github/workflows/deploy.yml` + `generate_index.py`) —
δεν χρειάζεται καμία χειροκίνητη ενέργεια πέρα από το `git push`.

## Συγχρονισμός νέων/αλλαγμένων quiz από το vault

```bash
~/quiz-repo/sync.sh
```

Αντιγράφει όλα τα `.quiz` από το `10.Quiz/` του vault εδώ, κάνει commit και
push μόνο αν κάτι άλλαξε (νέο, τροποποιημένο ή διαγραμμένο quiz).
