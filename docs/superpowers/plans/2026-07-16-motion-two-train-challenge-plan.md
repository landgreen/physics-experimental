# Motion Two-Train Challenge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one rigorous, fully solved two-train meeting problem near the end of the Motion page's Practice section.

**Architecture:** This is a single, self-contained HTML practice card. It relies on the existing KaTeX auto-renderer and the page's `div.example` plus `details` pattern; it adds no scripts, styles, or dependencies.

**Tech Stack:** Static HTML and KaTeX delimiters already loaded by the site.

## Global Constraints

- Modify only the Motion page's Practice section.
- Use only position, displacement, elapsed time, average velocity, signed direction, and unit conversion already taught on that page.
- Use `Example:` with `<summary>solution</summary>`, display math, and at most one equal sign per display-math line.
- Keep exactly the existing deliberately unsolvable example; this new problem is solvable.
- Preserve the page's direct, student-facing teacher voice.

---

### Task 1: Add and verify the two-train challenge

**Files:**
- Modify: `notes/motion/motion/index.html:1087-1104`
- Test: inline structural and arithmetic checks run from the repository root

**Interfaces:**
- Consumes: the existing Practice article and KaTeX rendering at `notes/motion/motion/index.html`.
- Produces: one new `div.example` placed immediately before the existing Reading card.

- [ ] **Step 1: Write the failing structural check**

Run this command before editing. It must fail because the unique challenge phrase is not on the page yet.

```bash
node -e "const fs=require('fs');const h=fs.readFileSync('notes/motion/motion/index.html','utf8');if(!h.includes('Two trains move toward each other on a straight east-west track')) process.exit(1)"
```

Expected: exit status `1`.

- [ ] **Step 2: Insert the practice card before the Reading card**

Add this block immediately before the `<div class='example'>` containing `Reading (5 minutes)`:

```html
		<div class='example'>
			<strong>Example:</strong> Two trains move toward each other on a straight east-west track. Let east be positive. At the same instant, a commuter train is at the -18.0 km marker and travels east at a constant 72 km/h. A freight train is at the 234 000 m marker and travels west at a constant 15 m/s. How long after that instant do they meet, where do they meet, and how far does each train travel?
			<details>
				<summary>solution</summary>
				<p>Use meters and seconds for both trains. East is positive, so the freight train has a negative velocity.</p>
				$$-18.0\,\mathrm{km}=-18000\,\mathrm{m}$$
				$$72\,\mathrm{km/h}=20\,\mathrm{m/s}$$
				$$v_{\mathrm{commuter}}=20\,\mathrm{m/s}$$
				$$v_{\mathrm{freight}}=-15\,\mathrm{m/s}$$
				<p>At the meeting time, both trains have the same position.</p>
				$$x_{\mathrm{commuter}}=-18000+20\Delta t$$
				$$x_{\mathrm{freight}}=234000-15\Delta t$$
				$$-18000+20\Delta t=234000-15\Delta t$$
				$$35\Delta t=252000$$
				$$\Delta t=7200\,\mathrm{s}$$
				$$\Delta t=2.00\,\mathrm{h}$$
				<p>Now use either train to find the meeting position.</p>
				$$x_{\mathrm{commuter}}=-18000+(20)(7200)$$
				$$x_{\mathrm{commuter}}=126000\,\mathrm{m}$$
				$$x_{\mathrm{freight}}=234000-(15)(7200)$$
				$$x_{\mathrm{freight}}=126000\,\mathrm{m}$$
				<p>Both calculations agree: they meet at the 126 km marker.</p>
				$$d_{\mathrm{commuter}}=126000-(-18000)$$
				$$d_{\mathrm{commuter}}=144000\,\mathrm{m}$$
				$$d_{\mathrm{freight}}=234000-126000$$
				$$d_{\mathrm{freight}}=108000\,\mathrm{m}$$
				<p>The commuter train travels farther because it has the greater speed during the same 2.00 h interval.</p>
			</details>
		</div>
```

- [ ] **Step 3: Run structural and arithmetic verification**

Run these commands:

```bash
node -e "const fs=require('fs');const h=fs.readFileSync('notes/motion/motion/index.html','utf8');const a=h.indexOf('Two trains move toward each other on a straight east-west track');const b=h.indexOf('Reading (5 minutes)');if(a<0||a>b||!h.includes('<summary>solution</summary>')||!h.includes('$$\\Delta t=7200\\,\\mathrm{s}$$')||!h.includes('$$x_{\\mathrm{commuter}}=126000\\,\\mathrm{m}$$')) process.exit(1);console.log('motion train challenge structure: pass')"
node -e "const t=252000/(20+15),x=-18000+20*t,dc=x-(-18000),df=234000-x;if(t!==7200||x!==126000||dc!==144000||df!==108000) process.exit(1);console.log('motion train challenge arithmetic: pass')"
```

Expected:

```text
motion train challenge structure: pass
motion train challenge arithmetic: pass
```

- [ ] **Step 4: Inspect the diff and commit**

Run:

```bash
git diff --check
git diff -- notes/motion/motion/index.html
git add notes/motion/motion/index.html docs/superpowers/plans/2026-07-16-motion-two-train-challenge-plan.md
git commit -m "content: add motion train challenge"
```

Expected: `git diff --check` produces no output, and the commit contains only the Motion practice card and this plan.
