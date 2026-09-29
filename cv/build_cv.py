#!/usr/bin/env python3
"""Build CV_AMB_full.pdf from the website's data files.

Sources (all in the repo root, the same files the web pages read):
    profile.json                          header, appointments, education, projects, service, affiliations
    research_entries.json                 publications, grants, talks
    public_engagement_entries_clean.json  public engagement
    teaching.json                         courses, theses, advising

Usage (from the repo root or from cv/):
    python cv/build_cv.py            # writes cv/build/CV_AMB_full.tex and ./CV_AMB_full.pdf
    python cv/build_cv.py --tex-only # just the .tex

Requires XeLaTeX (TeX Live or MiKTeX) with fontspec + polyglossia. Fonts are bundled in cv/fonts.
"""
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

CV_DIR = Path(__file__).resolve().parent
ROOT = CV_DIR.parent
BUILD = CV_DIR / "build"
SITE = "https://winjapati.github.io/"
SELF_NAMES = {"A.M. Byrd", "Andrew Byrd", "Andrew M. Byrd"}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- HTML -> LaTeX
TEX_ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
           "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
ARABIC = re.compile(r"[\u0600-\u06FF\u200c][\u0600-\u06FF\u200c\s:،]*[\u0600-\u06FF]")


def _capcirc(m):
    # Libertinus Italic has no anchor for a circumflex over some capitals (e.g. K̂): stack it in TeX.
    import unicodedata
    return m.group(0) if len(unicodedata.normalize("NFC", m.group(0))) == 1 else r"\capcirc{" + m.group(1) + "}"


def esc(s):
    s = "".join(TEX_ESC.get(c, c) for c in str(s))
    s = re.sub("([A-Z])\u0302", _capcirc, s)
    return ARABIC.sub(lambda m: r"\mbox{\textpersian{" + m.group(0) + "}}", s)


def esc_url(u):
    return u.replace("\\", "/").replace("%", r"\%").replace("#", r"\#")


class _H2T(HTMLParser):
    MAP = {"em": (r"\emph{", "}"), "i": (r"\emph{", "}"), "strong": (r"\textbf{", "}"),
           "b": (r"\textbf{", "}"), "sup": (r"\textsuperscript{", "}")}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.out.append(r"\href{" + esc_url(dict(attrs).get("href", "")) + "}{")
            self.stack.append("}")
        elif tag in self.MAP:
            self.out.append(self.MAP[tag][0])
            self.stack.append(self.MAP[tag][1])
        elif tag == "br":
            self.out.append(r"\\ ")

    def handle_endtag(self, tag):
        if tag == "a" or tag in self.MAP:
            self.out.append(self.stack.pop() if self.stack else "")

    def handle_data(self, data):
        self.out.append(esc(data))


def tex(s):
    """Convert the small HTML subset used in the JSON files to LaTeX."""
    if not s:
        return ""
    p = _H2T()
    p.feed(s)
    p.close()
    return "".join(p.out + p.stack[::-1])


def link(url, body):
    return r"\href{" + esc_url(url) + "}{" + body + "}" if url else body


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or ""))


# ---------------------------------------------------------------- dates
def fmt_date(d):
    """'10/24' -> 'Oct 2024'; '1/26–7/26' -> 'Jan–Jul 2026'; '2021–23' unchanged."""
    if not d:
        return ""
    d = str(d).replace("-", "–")

    def one(x):
        m = re.fullmatch(r"(\d{1,2})/(\d{2,4})", x.strip())
        if not m:
            return None
        y = int(m.group(2))
        y = y + 2000 if y < 100 else y
        return MONTHS[int(m.group(1)) - 1], y

    parts = d.split("–")
    if len(parts) == 1:
        o = one(d)
        return f"{o[0]} {o[1]}" if o else d
    a, b = parts[0], parts[1]
    oa, ob = one(a), one(b) if b.strip() else None
    if oa and ob:
        return f"{oa[0]}–{ob[0]} {oa[1]}" if oa[1] == ob[1] else f"{oa[0]} ’{str(oa[1])[2:]}–{ob[0]} ’{str(ob[1])[2:]}"
    if oa and not b.strip():
        return f"{oa[0]} {oa[1]}–"
    return d


def expected(d):
    """Prefix 'Exp.' to an M/YY date that lies in the future."""
    m = re.fullmatch(r"(\d{1,2})/(\d{2})", str(d))
    if m and (2000 + int(m.group(2)), int(m.group(1))) > (dt.date.today().year, dt.date.today().month):
        return "Exp. " + fmt_date(d)
    return fmt_date(d)


# ---------------------------------------------------------------- pieces
def authors_tex(auths, editors=False):
    names = [r"\textbf{" + esc(a) + "}" if a in SELF_NAMES else esc(a) for a in auths]
    if len(names) == 1:
        s = names[0]
    elif len(names) == 2:
        s = f"{names[0]} and {names[1]}"
    else:
        s = ", ".join(names[:-1]) + ", and " + names[-1]
    return s + (" (eds.)" if editors else "")


def pdf_link(e):
    return r" \pdflink{" + esc_url(SITE + e["pdf"]) + "}" if e.get("pdf") else ""


def pub_article(e):
    title = link(e.get("url"), tex(e["title"]))
    venue = e["venue"]
    m = re.match(r"(.+?) \(eds?\.\), (.+)", venue)
    if m:
        venue_t = "In " + tex(m.group(1)) + r" (eds.), \emph{" + tex(m.group(2)) + "}"
    else:
        venue_t = r"\emph{" + tex(venue) + "}"
    vol = ""
    if e.get("volume"):
        vol = (", " if e["volume"].startswith("vol.") else " ") + tex(e["volume"])
    pub = ". " + tex(e["publisher"]) if e.get("publisher") else ""
    pages = ", " + tex(e["pages"]) if e.get("pages") else ""
    return f"{authors_tex(e['authors'])}. ``{title}.'' {venue_t}{vol}{pages}{pub}.{pdf_link(e)}"


def pub_book(e):
    title = link(e.get("url"), r"\emph{" + tex(e["title"]) + "}")
    return f"{authors_tex(e['authors'], e.get('editors'))}. {title}. {tex(e['venue'])}.{pdf_link(e)}"


def pub_digital(e):
    role = f" ({esc(e['role'])})" if e.get("role") else ""
    url = e.get("url", "")
    return (f"{authors_tex(e['authors'])}{role}. " + link(url, r"\emph{" + tex(e["title"]) + "}")
            + f". {tex(e['venue'])}. " + link(url, esc(re.sub(r"^https?://", "", url))) + "."
            + (f" {tex(e['note'])}" if e.get("note") else ""))


def pub_contracted(e):
    venue = f" ({tex(e['venue'])})" if e.get("venue") else ""
    note = f" {tex(e['note'])}" if e.get("note") else ""
    return f"{authors_tex(e['authors'])}. {tex(e['title'])}{venue}. Under contract.{note}"


def grant(e):
    t = re.sub(r"^(Award|Grant): ", "", e["text"]).replace(" — (", " (").replace(" — ", ", ")
    date = str(e["year"])
    m = re.search(r"\s*\((\d{4})[-–](\d{4})\)\s*$", t)
    if m:
        date, t = f"{m.group(1)}–{m.group(2)[2:]}", t[: m.start()]
    t = t.rstrip(".") + "."
    # link the grant name (text up to the first comma or parenthesis)
    m = re.match(r"([^,(]+)(.*)", t, re.S)
    name, rest = (m.group(1).rstrip(), m.group(2)) if m else (t, "")
    sep = " " if rest.startswith("(") else ""
    return date, link(e.get("url"), tex(name)) + sep + tex(rest.lstrip() if sep else rest)


def talk(e):
    title = tex(e["title"])
    m = re.match(r"(.*?)\s*(\(with [^)]*\))\s*$", title)
    if m:
        title = f"``{m.group(1)}'' {m.group(2)},"
    else:
        title = f"``{title}''" if re.search(r"[?!]$", plain(e["title"])) else f"``{title},''"
    return fmt_date(e.get("date") or e["year"]), f"{link(e.get('url'), title)} \\venue{{{tex(e['venue'])}}}."


def end(s):
    """Add a final period unless the text already ends in punctuation (possibly inside quotes/braces)."""
    if re.search(r"[.!?][}'’”]*\s*$", s):
        return s
    m = re.search(r"”(}*)\s*$", s)
    return s[: m.start()] + ".”" + m.group(1) if m else s + "."


def quote_comma(s):
    """Move a comma that follows a closing quote (possibly after a link's closing brace) inside it."""
    return re.sub(r"”(}*),", r",”\1", s)


def pe_body(e):
    t = tex(e.get("title", ""))
    return quote_comma(tex(e.get("pre", "")) + link(e.get("url"), t) + tex(e.get("rest", "")))


# ---------------------------------------------------------------- document
def section(title):
    return f"\n\\cvsection{{{title}}}\n"


def subsection(title):
    return f"\\cvsubsection{{{title}}}\n"


def entries(items):
    """items: iterable of (date, body[, sub-bodies])"""
    out = ["\\begin{entries}"]
    for it in items:
        date, body = it[0], it[1]
        out.append(f"\\item[\\datebox{{{date}}}] {body}")
        subs = it[2] if len(it) > 2 else []
        if subs:
            out.append("\\begin{subentries}")
            out += [f"\\item {s}" for s in subs]
            out.append("\\end{subentries}")
    out.append("\\end{entries}")
    return "\n".join(out) + "\n"


def build():
    P = load("profile.json")
    R = load("research_entries.json")
    E = load("public_engagement_entries_clean.json")
    T = load("teaching.json")
    by = lambda cat: [e for e in R if e["category"] == cat]
    desc = lambda xs: sorted(xs, key=lambda e: -int(e["year"]))  # stable: keeps file order within a year

    body = []
    # --- header
    body.append(r"""\begin{cvheader}
{\namefont %s}\par\vspace{5pt}
{\color{muted}\sffamily\small %s \textperiodcentered\ \href{%s}{%s} \textperiodcentered\ \href{%s}{%s}}\par\vspace{2pt}
{\color{muted}\sffamily\small \href{mailto:%s}{%s} \textperiodcentered\ \href{%s}{%s}}
\end{cvheader}
""" % (esc(P["name"]), esc(P["position"]), P["department"]["url"], esc(P["department"]["name"]),
        P["university"]["url"], esc(P["university"]["name"]), P["email"], esc(P["email"]),
        P["website"], esc(P["website"].replace("https://", ""))))
    body.append("\\noindent{\\small " + " ".join(tex(s) for s in P["statement"]) +
                " Areas of specialization: " + tex(P["specializations"]) + ".}\n")

    body.append(section("Appointments"))
    body.append(entries((esc(a["dates"]), f"\\textbf{{{esc(a['title'])}}}, {esc(a['org'])}") for a in P["appointments"]))

    body.append(section("Education"))
    body.append(entries((esc(ed["dates"]), f"\\textbf{{{tex(ed['degree'])}}}, \\emph{{{tex(ed['school'])}}}"
                         + "".join(f"\\\\\n{{\\small {tex(d)}}}" for d in ed["details"])) for ed in P["education"]))

    body.append(section("Current Projects"))
    body.append(entries(("", f"\\textbf{{{tex(p['name'])}}}. {tex(p['description'])}") for p in P["projects"]))

    pubs = by("Publication")
    body.append(section("Publications"))
    contracted = [p for p in pubs if p.get("status")]
    if contracted:
        body.append(subsection("Books under Contract"))
        body.append(entries((f"Exp. {e['year']}", pub_contracted(e), [tex(v) for v in e.get("volumes", [])])
                            for e in desc(contracted)))
    body.append(subsection("Books"))
    body.append(entries((esc(e.get("cv_year", e["year"])), pub_book(e))
                        for e in desc(p for p in pubs if p.get("type") == "book" and not p.get("status"))))
    body.append(subsection("Articles and Chapters"))
    body.append(entries((esc(e.get("cv_year", e["year"])), pub_article(e)) for e in desc(p for p in pubs if p.get("type") != "book" and not p.get("status"))))

    digital = by("Digital Publication")
    if digital:
        body.append(subsection("Digital Publications"))
        body.append(entries((f"{e['year']}–" if e.get("ongoing") else esc(e["year"]), pub_digital(e)) for e in desc(digital)))

    body.append(section("Grants and Awards"))
    body.append(subsection("External"))
    body.append(entries(grant(e) for e in desc(by("Grant (External)"))))
    body.append(subsection("Internal"))
    body.append(entries(grant(e) for e in desc(by("Grant/Award (Internal)"))))

    body.append(section("Invited Talks"))
    body.append(entries(talk(e) for e in desc(by("Talk"))))
    body.append(section("Conference and Symposium Presentations"))
    body.append(entries(talk(e) for e in desc(by("Conference Talk"))))

    body.append(section("Teaching"))
    body.append(subsection("Courses Taught"))
    courses = [c["name"] for c in T["courses_regular"] + T["courses_other"]]
    body.append("\\begin{courselist}\n" + "\n".join(f"\\item {esc(c)}" for c in courses) + "\n\\end{courselist}\n")
    body.append(subsection("Theses Supervised"))
    body.append(entries((expected(t["date"]), f"{esc(t['name'])}, {esc(t['degree'])}, University of Kentucky. "
                         + link(t.get("url"), f"``{tex(t['title'])}.''")) for t in T["theses"]))
    body.append(subsection("Other Advising"))
    body.append(entries((fmt_date(a["date"]), esc(a["name"]) + (f", {esc(a['program'])}" if a.get("program") else "")
                         + ". " + link(a.get("url"), f"``{tex(a['title'])}.''")) for a in T["advising"]))

    body.append(section("Public Engagement"))
    order = []
    for e in E:
        if e["cv_section"] not in order:
            order.append(e["cv_section"])
    pref = ["Language Creation", "Translation of PIE and Ancient Languages", "Interviews and Media Coverage",
            "Outreach, Service, and Consulting", "Other Contributions"]
    order = [s for s in pref if s in order] + [s for s in order if s not in pref]
    for sec in order:
        items = [e for e in desc(E) if e["cv_section"] == sec and not e.get("cv_under")]
        rows = []
        for e in items:
            subs = [tex(d) for d in e.get("cv_details", [])]
            if e.get("id"):
                subs += [pe_body(c) + f" ({fmt_date(c['date'])})" for c in E if c.get("cv_under") == e["id"]]
            rows.append((fmt_date(e["date"]), end(pe_body(e)), subs))
        body.append(subsection(sec))
        body.append(entries(rows))

    body.append(section("Service"))
    for g in P["service"]:
        body.append(subsection(esc(g["group"])))
        body.append(entries(("Current" if i["dates"] == "current" else esc(i["dates"]), esc(i["role"])) for i in g["items"]))

    body.append(section("Professional Activities"))
    body.append(subsection("Affiliations"))
    body.append("\\noindent " + "; ".join(tex(a) for a in P["affiliations"]) + ".\n")
    body.append(subsection("Reviewer for"))
    body.append("\\noindent " + "; ".join(tex(a) for a in P["reviewing"]) + ".\n")

    updated = dt.date.today().strftime("%B %Y")
    tpl = (CV_DIR / "template.tex").read_text(encoding="utf-8")
    return tpl.replace("%%NAME%%", esc(P["name"])).replace("%%UPDATED%%", updated).replace("%%BODY%%", "\n".join(body))


def main():
    BUILD.mkdir(exist_ok=True)
    texfile = BUILD / "CV_AMB_full.tex"
    texfile.write_text(build(), encoding="utf-8")
    print("wrote", texfile)
    if "--tex-only" in sys.argv:
        return
    for _ in range(2):  # second pass resolves page x of y
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", texfile.name],
                           cwd=BUILD, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            print(r.stdout[-3000:])
            sys.exit("xelatex failed; see cv/build/CV_AMB_full.log")
    shutil.copy(BUILD / "CV_AMB_full.pdf", ROOT / "CV_AMB_full.pdf")
    print("wrote", ROOT / "CV_AMB_full.pdf")


if __name__ == "__main__":
    main()
