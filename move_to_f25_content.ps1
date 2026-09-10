# Run this from inside: C:\Users\andre\Documents\git_repos\current_teaching\winjapati.github.io
# It archives last semester's (Fall 2025) course/301 content into courses\301\f25_content
# using `git mv` so history/blame is preserved.

Set-Location "$PSScriptRoot"
Set-Location "courses\301"

$paths = @()

# Old numbered decks (1.html..36.html + matching N_files folders)
for ($i = 1; $i -le 36; $i++) {
    $paths += "$i.html"
    $paths += "${i}_files"
}

# Old homework
$hw = @(
    "hw1_latex", "hw2_website", "hw3_terminal_python", "hw4_loops_conditionals",
    "hw5_pandas", "hw6_spacy", "hw7_groupwork", "project_component_3"
)
foreach ($h in $hw) {
    $paths += "$h.html"
    $paths += "${h}_files"
}

# Old standalone demo files
$paths += @("7_mock_site.html", "8_stinkys.html", "9_stinkys_beautified.html", "9_stinky_style.css")

# Old-only images/assets (confirmed unused by current-semester .qmd files)
$paths += @(
    "1_comp_ling_battle.png", "1_HW_Leipzig.png", "12_bash_settings.png", "12_powershell.png",
    "2_latex_glove.jpeg", "2_syllable_tree.jpg", "2_syntax_tree.png",
    "3_mathmode.jpg", "3_tabular_1.jpg",
    "4_OT_ex.png", "4_phon_rules.png",
    "5_gb4e_activity.png", "5_IE_tree.png", "5_leipzig.png",
    "activity_2_syntax_tree.svg", "duckuments.sty", "for_loop.gif", "syntax_tree.svg"
)

# Only attempt to move things that actually exist (skip anything already gone)
$existing = $paths | Where-Object { Test-Path $_ }
$missing  = $paths | Where-Object { -not (Test-Path $_) }

if ($missing.Count -gt 0) {
    Write-Host "Skipping (not found):" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  $_" }
}

Write-Host "`nMoving $($existing.Count) items into f25_content\ ..." -ForegroundColor Cyan
git mv $existing f25_content/

Write-Host "`nDone. Review with 'git status', then commit:" -ForegroundColor Green
Write-Host '  git commit -m "Archive Fall 2025 course/301 content to f25_content"'
Write-Host "  git push"
