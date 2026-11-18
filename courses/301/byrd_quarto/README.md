# Andrew M. Byrd: Model Website for HW 8 (Quarto version)

A model for LIN 301, HW 8 (Path A: Quarto, with AI help).

## How I Built This Site

- **Path:** A (Quarto, with AI help).
- **AI use:** I gave Claude my HTML version of this site and asked it to turn it into a three-page Quarto website. It wrote the first drafts of `_quarto.yml`, the three `.qmd` files, and `styles.css`. I checked every page against my HTML version.
- **Today's techniques:** a grid of cards (`::: {.cards}`, on the homepage and research page), an embedded video (an `<iframe>`, on the research page), and a media query at the bottom of `styles.css`.
- **One thing I fixed:** My UK blue `header` rule from Wednesday stopped working: Quarto's navigation bar isn't a `<header>`. I used Inspect Element, found `<nav class="navbar">`, and changed my selector to `.navbar`.
- **To publish:** `quarto render`, then commit and push. GitHub Pages shows the `docs/` folder.
