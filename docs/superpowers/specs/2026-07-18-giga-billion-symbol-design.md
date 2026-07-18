# Giga and Billion Chart Symbol Design

## Goal

Show students that `B` is sometimes used to mean billion while preserving `G` as the metric-prefix symbol for giga.

## Scope

Update the symbol cell in every existing metric-prefix chart row labeled `giga` from `G` to `G,B`.

The six matching rows are in:

- `notes/review/units/index.html` (two charts)
- `notes/electromagnetism/electrostatics/index.html`
- `notes/waves/quantum/index.html` (two charts)
- `notes/waves/waves/index.html`

Do not change other uses of `G`, `B`, `giga`, billion, or powers of ten. Do not refactor the repeated charts.

## Verification

- Every `<td>giga</td>` chart row is immediately followed by a symbol cell containing `G,B`.
- No `<td>giga</td>` chart row remains followed by a symbol cell containing only `G`.
- The four edited HTML files retain valid table structure and contain no unrelated changes from this task.
