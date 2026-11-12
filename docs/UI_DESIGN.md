# SupeRR Selector UI

This is an independent student selection-analysis project, visually inspired by the Rajasthan Royals website. It is not an official RR product.

## Direction

Reference: https://www.rajasthanroyals.com/ and the two screenshots supplied on 11 November 2026. The official site's Montserrat typography, bold pink highlights, royal-blue backgrounds, pale pink statistic panels and diagonal treatments informed this interface. The layout is adapted for reading rankings and evaluating evidence rather than fan news.

- Light: off-white workspace, white panels, navy text, deep pink accents.
- Dark: layered navy panels, brighter pink highlights and readable lavender secondary text.
- A persistent navigation rail, selection-room banner, metric cards and player dossier establish the page hierarchy.
- Controls, charts, tables, reports, loading and error states share the same palette.
- Layouts adapt to desktop, tablet and phone widths; wide evidence tables scroll within their panels.

## Files

- `web/royals.css`: visual system and responsive overrides over the existing base stylesheet.
- `web/theme.js`: immediate theme initialization, system preference, local persistence and cross-tab synchronization.
- `web/index.html`: branded application shell, accessible navigation and theme switch.
- `web/app.js`: view markup and theme-aware chart colors. Ranking and analysis calculations are unchanged.
- `web/report.html`: matching typography and theme, with a light print treatment.
- `web/assets/fonts/`: self-hosted Montserrat variable font and its SIL Open Font License, obtained from the Google Fonts repository. No font CDN is required.

The user-supplied PNG has an opaque checkerboard. An SVG color-matrix display filter removes neutral pixels and shows its pink artwork as a white crest. The original image file is unmodified. A genuinely transparent PNG can replace it later if desired.

## Interaction

The Dark mode switch retains the chosen appearance on reload. Switching themes does not recreate views or reset active filters. Palette transitions last 240ms; reduced-motion preferences disable transitions and animations. Keyboard focus is visible and the switch exposes its checked state to assistive technology.

## Verification

Checked in a Chromium-based browser at 1440px, 768px and 390px. Confirmed theme persistence, ranking category/scope/search controls, player selection and evidence, match innings controls, methodology and report rendering. All five views fit the 390px page width; wide tables remain locally scrollable. No browser errors appeared during the check. JavaScript syntax checks passed.

Start normally from the project directory with `py app.py`, then refresh the dashboard with Ctrl+F5 if an older stylesheet is cached.
