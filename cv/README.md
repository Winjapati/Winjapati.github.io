# CV build

`CV_AMB_full.pdf` (repo root) is generated from the same data files the website reads:

| File | Feeds |
|---|---|
| `profile.json` | header, appointments, education, current projects, service, affiliations, reviewing |
| `research_entries.json` | publications, grants & awards, invited talks, conference talks |
| `public_engagement_entries_clean.json` | public engagement (grouped by `cv_section`) |
| `teaching.json` | courses, theses supervised, other advising |

To update the CV, edit the JSON, then run from the repo root:

    python cv/build_cv.py

This writes `cv/build/CV_AMB_full.tex` and copies the PDF to `CV_AMB_full.pdf`.
Needs XeLaTeX (TeX Live or MiKTeX) with fontspec, polyglossia, titlesec, enumitem, fancyhdr, lastpage.
Fonts are bundled in `cv/fonts` (Libertinus and Amiri, both SIL Open Font License 1.1).

Design lives in `cv/template.tex` (colors, fonts, spacing); the text formatting of each entry type is in `build_cv.py`.

## Field notes
- Publications: `authors` (list; "A.M. Byrd" is bolded), `title`, `venue` (an edited volume as "Editors (eds.), Book Title"),
  `volume`, `pages`, optional `cv_year` (e.g. "2011 [2012]"), `type: "book"`, `editors: true`, `url`, `pdf`.
- Talks: `title` (ending in "(with …)" for co-presenters), `venue`, `date` as M/YY.
- Grants: `text` as shown on the site; a trailing "(2005-2006)" becomes the date.
- Public engagement: `pre` + linked `title` + `rest`; `date`; `cv_section`; `cv_details` (sub-bullets);
  `id` / `cv_under` to nest an item under another.
- Small HTML is allowed in text fields: `<em>`, `<a href>`, `<sup>`, `<strong>`.
