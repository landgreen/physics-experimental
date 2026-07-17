# AGENTS.md

## Project Overview

This is a static physics course notes website. Most course content lives in `notes/`, with each notes page usually stored as an `index.html` file inside its topic folder.

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
- Keep the answer constructive: explain what information is missing or what equation has not been taught, so students practice recognizing when a physics problem cannot be solved from the given information.

### Labels and Solution Style

- Use `Example:` for math problems.
- Use `Question:` for non-math conceptual problems.
- Use `<summary>solution</summary>` for math Examples and `<summary>answer</summary>` for conceptual Questions.
- For calculation-heavy pages, include at most one or two conceptual-only questions unless the user asks for more.
- Solutions should show the equation, substitution, algebra if needed, final answer with units, and a short interpretation when useful.
- Keep algebra to one equal sign per line. Do not chain multiple equal signs across one displayed line.
- Check formulas, substitutions, arithmetic, units, signs, assumptions, and physical reasonableness for every solution.
- For multi-step or realistic-number problems, verify rounded answers independently.

### Final Quality Check

- Confirm the set practices every major equation, important rearrangement, common mistake, and major representation taught on the page.
- Review for repetition and near-duplicates. Different numbers alone do not make a different problem.
- Rewrite prompts until they sound like the existing notes: plain, direct, readable, and useful rather than generic worksheet filler.
