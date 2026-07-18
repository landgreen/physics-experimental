# Giga and Billion Chart Symbol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `B` as an alternate billion abbreviation in every existing metric-prefix chart's giga symbol cell.

**Architecture:** Make one focused HTML text change in each duplicated chart row: replace the symbol cell `G` with `G,B` immediately after `<td>giga</td>`. Preserve the existing page structures and all unrelated content.

**Tech Stack:** Static HTML, ripgrep, Perl, Git

## Global Constraints

- Use the exact symbol text `G,B` with no space.
- Update all six existing `<td>giga</td>` chart rows across the four identified notes pages.
- Do not change other uses of `G`, `B`, `giga`, billion, or powers of ten.
- Do not refactor the repeated charts.
- Include the user's pre-existing content changes in `notes/review/units/index.html` in the completed upload.
- Exclude the unrelated untracked motion plan and generated `tools/__pycache__/` files.

---

### Task 1: Update every duplicated giga chart row

**Files:**
- Modify: `notes/review/units/index.html:225` and `notes/review/units/index.html:276`
- Modify: `notes/electromagnetism/electrostatics/index.html:101`
- Modify: `notes/waves/quantum/index.html:421` and `notes/waves/quantum/index.html:840`
- Modify: `notes/waves/waves/index.html:715`

**Interfaces:**
- Consumes: Existing static metric-prefix table rows whose name cell is `<td>giga</td>` and symbol cell is `<td>G</td>`.
- Produces: Six rows whose symbol cell is exactly `<td>G,B</td>`.

- [ ] **Step 1: Run the new-state check and verify it fails before editing**

Run:

```bash
perl -0ne '$count += () = /<td>giga<\/td>\s*<td>G,B<\/td>/g; END { print "matching updated rows: $count\n"; exit($count == 6 ? 0 : 1) }' notes/review/units/index.html notes/electromagnetism/electrostatics/index.html notes/waves/quantum/index.html notes/waves/waves/index.html
```

Expected: exit 1 with `matching updated rows: 0`.

- [ ] **Step 2: Apply the minimal HTML edits**

At each of the six identified rows, preserve the existing indentation and change only this pair:

```html
<td>giga</td>
<td>G</td>
```

to:

```html
<td>giga</td>
<td>G,B</td>
```

- [ ] **Step 3: Verify all six updated rows and no old rows remain**

Run:

```bash
perl -0ne '$new += () = /<td>giga<\/td>\s*<td>G,B<\/td>/g; $old += () = /<td>giga<\/td>\s*<td>G<\/td>/g; END { print "updated rows: $new\nold rows: $old\n"; exit($new == 6 && $old == 0 ? 0 : 1) }' notes/review/units/index.html notes/electromagnetism/electrostatics/index.html notes/waves/quantum/index.html notes/waves/waves/index.html
```

Expected: exit 0 with:

```text
updated rows: 6
old rows: 0
```

- [ ] **Step 4: Inspect the focused diffs and whitespace**

Run:

```bash
git diff --check
git diff -- notes/review/units/index.html notes/electromagnetism/electrostatics/index.html notes/waves/quantum/index.html notes/waves/waves/index.html
```

Expected: `git diff --check` exits 0. The four-file diff shows the six requested `G` to `G,B` edits and the units page's pre-existing content work that the user requested be included.

- [ ] **Step 5: Stage the chart edits and current units-page work, then commit**

Stage the four intended HTML pages and this implementation plan directly:

```bash
git add notes/review/units/index.html notes/electromagnetism/electrostatics/index.html notes/waves/quantum/index.html notes/waves/waves/index.html docs/superpowers/plans/2026-07-18-giga-billion-symbol.md
```

Confirm the staged diff contains the six symbol-cell edits, the current units-page content changes, and the implementation plan, then commit:

```bash
git diff --cached --check
git diff --cached
git commit -m "docs: add billion symbol to giga charts"
```

Expected: the staged whitespace check exits 0, the staged diff contains the agreed changes, and the commit succeeds without the unrelated motion plan or generated cache files.

- [ ] **Step 6: Upload the completed branch**

Run:

```bash
git push -u origin codex/giga-billion-symbol
```

Expected: the push succeeds and the remote branch tracks `origin/codex/giga-billion-symbol`.
