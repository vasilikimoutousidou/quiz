#!/usr/bin/env python3
"""
Σαρώνει τα .quiz αρχεία στο quizzes/ και παράγει _site/index.html με links
της μορφής https://vicajilau.github.io/quizdy/?data=<raw.githubusercontent URL>

Τρέχει αυτόματα σε κάθε push μέσω .github/workflows/deploy.yml — δεν χρειάζεται
να τρέχει χειροκίνητα.
"""
import os
import re
import html
from urllib.parse import quote

QUIZ_DIR = "quizzes"
OUT_DIR = "_site"
QUIZDY_BASE = "https://vicajilau.github.io/quizdy/"

REPO = os.environ.get("REPO", "vasilikimoutousidou/quiz")
BRANCH = os.environ.get("BRANCH", "main")

# Κ01 - Τίτλος.quiz            -> κεφάλαιο 01, επαναληπτικό
# Κ01.Ε02 - Τίτλος.quiz        -> κεφάλαιο 01, ενότητα 02
FNAME_RE = re.compile(r"^Κ(\d+)(?:\.Ε(\d+))? - (.+)\.quiz$")


def raw_url(filename: str) -> str:
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{QUIZ_DIR}/{quote(filename)}"


def quizdy_url(filename: str) -> str:
    return f"{QUIZDY_BASE}?data={quote(raw_url(filename), safe='')}"


def collect():
    chapters = {}  # num -> {"title": str|None, "chapter_file": str|None, "units": [(unit_num, title, filename)]}
    unmatched = []

    if not os.path.isdir(QUIZ_DIR):
        return chapters, unmatched

    for filename in sorted(os.listdir(QUIZ_DIR)):
        if not filename.endswith(".quiz"):
            continue
        m = FNAME_RE.match(filename)
        if not m:
            unmatched.append(filename)
            continue
        chap_num, unit_num, title = m.groups()
        chap = chapters.setdefault(chap_num, {"title": None, "chapter_file": None, "units": []})
        if unit_num is None:
            chap["title"] = title
            chap["chapter_file"] = filename
        else:
            chap["units"].append((int(unit_num), title, filename))

    for chap in chapters.values():
        chap["units"].sort(key=lambda u: u[0])

    return chapters, unmatched


def render(chapters, unmatched) -> str:
    parts = []
    parts.append("""<!doctype html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quiz ΑΟΘ</title>
<style>
  :root {
    color-scheme: light dark;
    --bg: #f7f7f8;
    --card-bg: #ffffff;
    --text: #1a1a1a;
    --muted: #666;
    --accent: #2563eb;
    --border: #e2e2e6;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #16171a;
      --card-bg: #212226;
      --text: #f0f0f0;
      --muted: #9a9a9f;
      --accent: #6ea8fe;
      --border: #33343a;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 2.5rem 1.25rem 4rem;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  .wrap { max-width: 780px; margin: 0 auto; }
  h1 { font-size: 1.6rem; margin-bottom: .25rem; }
  .subtitle { color: var(--muted); margin-bottom: 2rem; font-size: .95rem; }
  .chapter {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
  }
  .chapter h2 { font-size: 1.1rem; margin: 0 0 .6rem; }
  .chapter h2 a { color: var(--text); text-decoration: none; }
  .chapter h2 a:hover { color: var(--accent); }
  ul.units { list-style: none; margin: 0; padding: 0; }
  ul.units li { margin: .35rem 0; padding-left: .9rem; border-left: 2px solid var(--border); }
  ul.units li a { color: var(--accent); text-decoration: none; font-size: .95rem; }
  ul.units li a:hover { text-decoration: underline; }
  .badge {
    display: inline-block;
    font-size: .7rem;
    color: var(--muted);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: .05rem .5rem;
    margin-left: .4rem;
  }
  .empty { color: var(--muted); font-size: .9rem; }
  footer { margin-top: 2.5rem; color: var(--muted); font-size: .8rem; text-align: center; }
</style>
</head>
<body>
<div class="wrap">
<h1>Quiz &mdash; Αρχές Οικονομικής Θεωρίας</h1>
<p class="subtitle">Πάτησε ένα quiz για να ανοίξει στο Quizdy.</p>
""")

    for chap_num in sorted(chapters.keys(), key=lambda n: int(n)):
        chap = chapters[chap_num]
        title = chap["title"] or f"Κεφάλαιο {chap_num}"
        parts.append('<section class="chapter">')
        if chap["chapter_file"]:
            href = html.escape(quizdy_url(chap["chapter_file"]))
            parts.append(
                f'<h2><a href="{href}" target="_blank" rel="noopener">'
                f'Κ{chap_num} &mdash; {html.escape(title)}</a>'
                f'<span class="badge">Επαναληπτικό</span></h2>'
            )
        else:
            parts.append(f'<h2>Κ{chap_num} &mdash; {html.escape(title)}</h2>')

        if chap["units"]:
            parts.append('<ul class="units">')
            for unit_num, unit_title, filename in chap["units"]:
                href = html.escape(quizdy_url(filename))
                parts.append(
                    f'<li><a href="{href}" target="_blank" rel="noopener">'
                    f'Ε{unit_num:02d} &mdash; {html.escape(unit_title)}</a></li>'
                )
            parts.append("</ul>")
        else:
            parts.append('<p class="empty">Δεν έχουν προστεθεί ακόμη quiz ενοτήτων.</p>')
        parts.append("</section>")

    if unmatched:
        parts.append('<section class="chapter"><h2>Άλλα quiz</h2><ul class="units">')
        for filename in unmatched:
            href = html.escape(quizdy_url(filename))
            title = filename[:-5]
            parts.append(f'<li><a href="{href}" target="_blank" rel="noopener">{html.escape(title)}</a></li>')
        parts.append("</ul></section>")

    parts.append(f"""
<footer>Παράγεται αυτόματα από {html.escape(REPO)} &middot; ενημερώνεται σε κάθε push</footer>
</div>
</body>
</html>""")
    return "".join(parts)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters, unmatched = collect()
    out = render(chapters, unmatched)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    total = sum(1 + len(c["units"]) for c in chapters.values()) + len(unmatched)
    print(f"Δημιουργήθηκε {OUT_DIR}/index.html με {total} quiz σε {len(chapters)} κεφάλαια.")


if __name__ == "__main__":
    main()
