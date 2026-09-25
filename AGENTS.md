# AGENTS.md

## Project Overview

This is a static physics course notes website. Most course content lives in `notes/`, with each notes page usually stored as an `index.html` file inside its topic folder.

## Workflow

- Make edits directly in the existing local `physics-experimental` directory.
- Complete the requested edits and local verification without pausing for intermediate design, specification, plan, or review approval unless a necessary user decision blocks the work.
- Preserve the user's existing work and exclude unrelated or generated files from the requested edits.
- When the work is ready, provide one concise summary of the local changes and verification.

## Git and GitHub

- Do not run any Git commands or perform any Git operations in this repository, including status, diff, log, branch, worktree, staging, committing, pulling, merging, rebasing, tagging, or pushing.
- Do not interact with GitHub for this repository through the website, CLI, apps, APIs, plugins, or other tools. Do not create or modify pull requests, issues, releases, Actions, repository settings, or remote content.
- Limit all work to direct local file edits and non-Git local verification.

## Publishing

- Never upload, deploy, or publish this repository to `https://landgreen.github.io/` or the main Landgreen site.
- This repository is for local work only. Publishing may be appropriate for the user's other repositories when they explicitly request it.

## General Editing Guidance

- Match the existing HTML, CSS classes, page structure, and teacher voice on the page being edited.
- Keep student-facing explanations clear, direct, and useful.
- Make focused changes to the requested page or section. Do not rewrite unrelated content.
- Preserve existing examples, simulations, diagrams, and links unless the user asks to change them.
- Use normal readable text in prompts when possible. Avoid LaTeX in the question text unless the page already uses it cleanly there.
- Use display math with double-dollar delimiters in solutions when math formatting is needed.
- Use scientific notation in prompt text with HTML when appropriate, such as `3.65 × 10<sup>12</sup> N`.

## Practice Problems and Examples

Use `practice-question-quality-steps.txt` as the detailed source of truth when creating or revising practice problems. The following summary should guide every set of example problems added to the notes pages.

### Page Fit

- Read the page like a teacher before writing problems.
- Identify the equations, concepts, assumptions, vocabulary, representations, and math level already taught on the page.
- Only write problems that can be solved from that page or from clearly expected earlier course content.
- Do not require formulas, techniques, or concepts from later course pages.
- Check that each problem can actually be solved with the information given, except for the one deliberate unsolvable problem described below.

### Research and Planning

- Look at reputable physics sources for common problem types, misconceptions, and difficulty progressions. Use them for inspiration, not copied wording.
- Build a problem-type map before writing: list the specific skills the page should train.
- Build a misconception map: include problems that expose common mistakes for the topic.
- Plan the set as a sequence: basic recognition, direct calculation, rearranged calculation, multi-step word problems, representation changes, then interpretation or challenge problems.
- Include about one out of every ten problems that connects to earlier course content while keeping the current page's topic as the main target.

### Difficulty and Variety

- Use intentional difficulty tiers, from direct substitution to rearranging, multi-step setup, sign or direction reasoning, and challenge applications.
- Prefer word problems that require students to identify the model before calculating.
- Avoid making the set feel like repeated plug-and-chug with different numbers.
- Vary the unknown variable, context, equation form, sign convention, units, difficulty, and solution path.
- Mix short direct prompts with longer realistic prompts. Longer prompts may include interesting background details or extra unused numbers when they feel natural and do not make the problem confusing.
- Mix representations when the page supports it: words, equations, tables, graphs, diagrams, before/after descriptions, comparisons, or simple sketches.

### Numbers, Units, and Assumptions

- Choose numbers intentionally. Use clean numbers early and more realistic numbers later.
- Aim for about one out of every four problems to require a natural unit conversion, such as grams to kilograms, kilometers to meters, centimeters to meters, minutes to seconds, km/h to m/s, or kN to N.
- Make unit conversions feel like a natural part of the situation, not extra work pasted onto the end.
- State required assumptions in the prompt or solution, such as ignore air resistance, constant acceleration, level surface, ideal battery, point charges, or uniform field.

### Deliberately Unsolvable Problem

- Include exactly one intentionally unsolvable problem per practice set.
- It should use the `Example:` label because it should initially look like a normal math problem.
- It should include at least two given numbers, but still be missing one required value, assumption, or taught equation.
- Mix it into the practice set instead of placing it last.
- Build it from a real object with a real missing value, not an invented unit or artificial setup.
- Keep the answer constructive: explain what information is missing or what equation has not been taught, so students practice recognizing when a physics problem cannot be solved from the given information.

### Labels and Solution Style

- Give each practice card `data-topic="<page section>"`, and add `data-hard` for trig, 2-D, complex-circuit, or long multi-step problems (see step 26 of the quality steps). Use `class='example printout-ignore'` to leave a card off the printout PDF.

- Use `Example:` for math problems.
- Use `Question:` for non-math conceptual problems.
- Use `<summary>solution</summary>` for math Examples and `<summary>answer</summary>` for conceptual Questions.
- For calculation-heavy pages, include at most one or two conceptual-only questions unless the user asks for more.
- Solutions should show the equation, substitution, algebra if needed, final answer with units, and a short interpretation when useful.
- Keep algebra to one equal sign per line. Do not chain multiple equal signs across one displayed line.
- Match the page's solution method, not just its notation, such as the decimal-moving method for metric prefixes or colored cancelling units in conversion fractions.
- Conversion factors always show their units, even though other intermediate steps omit units.
- For trig, write the degree sign, state what the angle is measured from, and remind students about calculator degree mode in the first trig solution of a set.
- Check formulas, substitutions, arithmetic, units, signs, assumptions, and physical reasonableness for every solution.
- Check that every given value is believable for the object in the prompt, and that multi-part data agree with each other.
- For multi-step or realistic-number problems, verify rounded answers independently.

### Final Quality Check

- Confirm the set practices every major equation, important rearrangement, common mistake, and major representation taught on the page.
- Review for repetition and near-duplicates. Different numbers alone do not make a different problem. Also compare against the worked examples already on the page.
- Rewrite prompts until they sound like the existing notes: plain, direct, readable, and useful rather than generic worksheet filler.
