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

CHAPTER_EMOJI = {
    "01": "📘", "02": "🛒", "03": "🏭", "04": "📦", "05": "⚖️",
    "06": "🏬", "07": "📊", "08": "🏦", "09": "📉", "10": "🏛️",
}
ACCENTS = [
    "#2563eb", "#059669", "#d97706", "#db2777", "#7c3aed",
    "#0891b2", "#dc2626", "#4f46e5", "#ca8a04", "#0d9488",
]


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


HEAD = """<!doctype html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quiz ΑΟΘ</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%93%98%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet">
<script>
(function () {
  try {
    var t = localStorage.getItem('quiz-theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
  } catch (e) {}
})();
</script>
<style>
  :root {
    --bg: #f2f3f7;
    --card-bg: #ffffff;
    --text: #1a1a1e;
    --muted: #6b7280;
    --border: #e5e7eb;
    --chip-bg: #f1f2f6;
    --chip-text: #33343a;
    --shadow: 0 1px 3px rgba(20,20,30,.07), 0 6px 18px rgba(20,20,30,.05);
    --hero-1: #4f46e5;
    --hero-2: #0891b2;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #131419;
      --card-bg: #1e1f27;
      --text: #f1f1f4;
      --muted: #9b9ca7;
      --border: #2e2f3a;
      --chip-bg: #262733;
      --chip-text: #d7d8e0;
      --shadow: 0 1px 3px rgba(0,0,0,.5), 0 6px 18px rgba(0,0,0,.35);
    }
  }
  :root[data-theme="dark"] {
    --bg: #131419;
    --card-bg: #1e1f27;
    --text: #f1f1f4;
    --muted: #9b9ca7;
    --border: #2e2f3a;
    --chip-bg: #262733;
    --chip-text: #d7d8e0;
    --shadow: 0 1px 3px rgba(0,0,0,.5), 0 6px 18px rgba(0,0,0,.35);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'Rubik', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  .hero {
    position: relative;
    padding: 3rem 1.25rem 5rem;
    background: linear-gradient(135deg, var(--hero-1), var(--hero-2));
    color: #fff;
    text-align: center;
    overflow: hidden;
  }
  .hero h1 {
    margin: 0 0 .5rem;
    font-size: clamp(1.6rem, 4vw, 2.3rem);
    font-weight: 700;
  }
  .hero p { margin: 0; opacity: .92; font-size: 1rem; }
  .hero .stats {
    display: inline-block;
    margin-top: 1rem;
    padding: .35rem .9rem;
    background: rgba(255,255,255,.18);
    border-radius: 999px;
    font-size: .85rem;
    backdrop-filter: blur(4px);
  }
  .hero .credit {
    margin-top: .7rem;
    font-size: .8rem;
    opacity: .85;
  }
  #theme-toggle {
    position: absolute;
    top: 1.1rem;
    right: 1.1rem;
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 50%;
    border: none;
    background: rgba(255,255,255,.2);
    color: #fff;
    font-size: 1.25rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background .15s, transform .15s;
  }
  #theme-toggle:hover { background: rgba(255,255,255,.32); transform: scale(1.06); }
  .wrap { max-width: 820px; margin: -2.75rem auto 0; padding: 0 1.1rem 4rem; position: relative; }
  .search-box {
    display: block;
    width: 100%;
    padding: .85rem 1.1rem;
    border-radius: 14px;
    border: 1px solid var(--border);
    background: var(--card-bg);
    color: var(--text);
    box-shadow: var(--shadow);
    font: inherit;
    font-size: .95rem;
    margin-bottom: 1.4rem;
  }
  .search-box:focus { outline: 2px solid var(--hero-2); outline-offset: 1px; }
  .chapter {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-left: 5px solid var(--accent, var(--hero-1));
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    transition: transform .15s;
  }
  .chapter-head { display: flex; align-items: center; gap: .75rem; margin-bottom: .9rem; }
  .chapter-emoji {
    font-size: 1.6rem;
    width: 2.6rem;
    height: 2.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--chip-bg);
    border-radius: 12px;
    flex-shrink: 0;
  }
  .chapter-num { font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
  .chapter-head h2 { margin: .1rem 0 0; font-size: 1.08rem; font-weight: 600; }
  .chips { display: flex; flex-wrap: wrap; gap: .5rem; }
  .chip {
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    padding: .45rem .85rem;
    border-radius: 999px;
    background: var(--chip-bg);
    color: var(--chip-text);
    text-decoration: none;
    font-size: .85rem;
    font-weight: 500;
    transition: transform .12s, background .12s, color .12s;
    border: 1px solid transparent;
  }
  .chip:hover { background: var(--accent, var(--hero-1)); color: #fff; transform: translateY(-2px); }
  .chip-main {
    background: var(--accent, var(--hero-1));
    color: #fff;
    font-weight: 600;
  }
  .chip-main:hover { filter: brightness(1.1); transform: translateY(-2px); }
  .empty { color: var(--muted); font-size: .88rem; margin: 0; }
  footer { margin-top: 2.5rem; color: var(--muted); font-size: .8rem; text-align: center; }
  .no-results { display: none; text-align: center; color: var(--muted); padding: 2rem 0; }
</style>
</head>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters, unmatched = collect()
    total_quizzes = sum(1 + len(c["units"]) for c in chapters.values()) + len(unmatched)

    body = ['<body>']
    body.append('<div class="hero">')
    body.append('<button id="theme-toggle" aria-label="Εναλλαγή θέματος φωτεινό/σκοτεινό">🌙</button>')
    body.append('<h1>📘 Quiz &mdash; Αρχές Οικονομικής Θεωρίας</h1>')
    body.append('<p>Πάτησε ένα quiz για να ανοίξει στο Quizdy και δοκίμασε τις γνώσεις σου!</p>')
    body.append(f'<span class="stats">{total_quizzes} διαθέσιμα quiz &middot; {len(chapters)} κεφάλαια</span>')
    body.append('<div class="credit">👩‍🏫 Μουτουσίδου Βάσω &middot; Σχολικό έτος <span id="school-year">&hellip;</span></div>')
    body.append('</div>')

    body.append('<div class="wrap">')
    body.append('<input class="search-box" id="quiz-search" type="search" placeholder="🔍 Αναζήτηση κεφαλαίου ή ενότητας...">')

    for i, chap_num in enumerate(sorted(chapters.keys(), key=lambda n: int(n))):
        chap = chapters[chap_num]
        title = chap["title"] or f"Κεφάλαιο {chap_num}"
        emoji = CHAPTER_EMOJI.get(chap_num, "📚")
        accent = ACCENTS[i % len(ACCENTS)]
        search_blob = html.escape((title + " " + " ".join(u[1] for u in chap["units"])).casefold())

        body.append(f'<section class="chapter" style="--accent:{accent}" data-search="{search_blob}">')
        body.append('<div class="chapter-head">')
        body.append(f'<span class="chapter-emoji">{emoji}</span>')
        body.append(f'<div><div class="chapter-num">Κεφάλαιο {int(chap_num)}</div><h2>{html.escape(title)}</h2></div>')
        body.append('</div>')

        body.append('<div class="chips">')
        if chap["chapter_file"]:
            href = html.escape(quizdy_url(chap["chapter_file"]))
            body.append(f'<a class="chip chip-main" href="{href}" target="_blank" rel="noopener">🔁 Επαναληπτικό</a>')
        for unit_num, unit_title, filename in chap["units"]:
            href = html.escape(quizdy_url(filename))
            unit_search = html.escape(unit_title.casefold())
            body.append(
                f'<a class="chip unit-chip" data-search="{unit_search}" href="{href}" target="_blank" rel="noopener">'
                f'Ε{unit_num:02d} &middot; {html.escape(unit_title)}</a>'
            )
        body.append('</div>')

        if not chap["chapter_file"] and not chap["units"]:
            body.append('<p class="empty">Δεν έχουν προστεθεί ακόμη quiz.</p>')
        body.append('</section>')

    if unmatched:
        body.append('<section class="chapter" style="--accent:#6b7280" data-search="άλλα">')
        body.append('<div class="chapter-head"><span class="chapter-emoji">📄</span><div><h2>Άλλα quiz</h2></div></div>')
        body.append('<div class="chips">')
        for filename in unmatched:
            href = html.escape(quizdy_url(filename))
            title = filename[:-5]
            body.append(f'<a class="chip" href="{href}" target="_blank" rel="noopener">{html.escape(title)}</a>')
        body.append('</div></section>')

    body.append('<p class="no-results" id="no-results">Δεν βρέθηκε quiz που να ταιριάζει με την αναζήτηση.</p>')
    body.append(f'<footer>Παράγεται αυτόματα από {html.escape(REPO)} &middot; ενημερώνεται σε κάθε push</footer>')
    body.append('</div>')

    body.append("""
<script>
(function () {
  function systemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') || systemTheme();
  }
  function updateIcon() {
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = currentTheme() === 'dark' ? '☀️' : '🌙';
  }
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('quiz-theme', next); } catch (e) {}
      updateIcon();
    });
  }
  updateIcon();

  var yearEl = document.getElementById('school-year');
  if (yearEl) {
    var now = new Date();
    var y = now.getFullYear();
    var startY = (now.getMonth() + 1) >= 9 ? y : y - 1; // σχολικό έτος ξεκινά τον Σεπτέμβριο
    yearEl.textContent = startY + '-' + (startY + 1);
  }

  var search = document.getElementById('quiz-search');
  var noResults = document.getElementById('no-results');
  if (search) {
    search.addEventListener('input', function () {
      var q = this.value.trim().toLowerCase();
      var visibleChapters = 0;
      document.querySelectorAll('.chapter').forEach(function (chapter) {
        var chapterMatch = (chapter.getAttribute('data-search') || '').indexOf(q) !== -1;
        var anyUnitMatch = false;
        chapter.querySelectorAll('.unit-chip').forEach(function (chip) {
          var match = (chip.getAttribute('data-search') || '').indexOf(q) !== -1;
          chip.style.display = (q === '' || match || chapterMatch) ? '' : 'none';
          if (match) anyUnitMatch = true;
        });
        var show = (q === '' || chapterMatch || anyUnitMatch);
        chapter.style.display = show ? '' : 'none';
        if (show) visibleChapters++;
      });
      if (noResults) noResults.style.display = visibleChapters === 0 ? 'block' : 'none';
    });
  }
})();
</script>
</body>
</html>""")

    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(HEAD + "".join(body))

    print(f"Δημιουργήθηκε {OUT_DIR}/index.html με {total_quizzes} quiz σε {len(chapters)} κεφάλαια.")


if __name__ == "__main__":
    main()
