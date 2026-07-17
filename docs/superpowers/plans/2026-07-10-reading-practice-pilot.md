# Reading Practice Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one article-based reading problem to the end of the Interference page's practice section.

**Architecture:** Extend the existing static HTML practice list with one `.example` block. The block links to the selected Science Journal for Kids PDF, presents four numbered reading questions, and keeps model answers inside the page's established `<details>` solution pattern.

**Tech Stack:** Static HTML5 and the site's existing CSS classes.

## Global Constraints

- Use the label `Reading:` for the new problem type.
- Place the block last in the More Practice section.
- Keep the questions answerable from the linked article and the Interference notes page.
- Use original wording and concise model answers.
- Do not alter any existing practice questions.

---

### Task 1: Add the pilot reading problem

**Files:**
- Modify: `notes/waves/waveproperties/index.html`

**Interfaces:**
- Consumes: the existing `.example`, `<details>`, and `<summary>solution</summary>` practice-problem structure.
- Produces: one final `Reading:` practice block linking to the duckling wave-interference article.

- [x] **Step 1: Verify the reading problem is absent**

Run: `rg -n "<strong>Reading:</strong>" notes/waves/waveproperties/index.html`

Expected: no matches.

- [x] **Step 2: Add the reading block**

Insert one `.example` block immediately after the standing-wave question and before the practice `<article>` closes. Include the article title as a link, four numbered questions, and four corresponding model answers inside `<details>`.

- [x] **Step 3: Verify the new structure and placement**

Run a Node assertion that checks for exactly one `Reading:` label, the exact article URL, four prompt list items, four answer list items, and placement before the practice article closes.

Expected: `reading problem checks passed`.

- [x] **Step 4: Review the focused diff**

Run: `git diff -- notes/waves/waveproperties/index.html`

Expected: only the new final reading block appears in the page diff from this task.
