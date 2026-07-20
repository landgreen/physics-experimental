# Simplified Motion Two-Train Challenge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Replace the existing train challenge with a simpler two-equation problem that asks only for meeting time and position.

**Architecture:** Replace one existing div.example in the Motion Practice section. The replacement preserves the existing HTML and KaTeX conventions and adds no scripts, styles, or dependencies.

**Tech Stack:** Static HTML and KaTeX already loaded by the page.

## Global Constraints

- Modify only the existing two-train card in notes/motion/motion/index.html.
- Use no unit conversions or negative position markers.
- Do not ask for distance traveled.
- Retain Example, solution details, display math, and no more than one equal sign per display-math line.
- Keep the card immediately before the Reading card at the end of Practice.

---

### Task 1: Simplify the two-train practice card

**Files:**
- Modify: notes/motion/motion/index.html:1088-1116
- Test: inline structural and arithmetic checks from the repository root

**Interfaces:**
- Consumes: the existing Motion Practice section and KaTeX auto-rendering.
- Produces: one replacement div.example before the Reading card.

- [ ] **Step 1: Run the failing check**

~~~bash
node -e 'const fs=require("fs");const h=fs.readFileSync("notes/motion/motion/index.html","utf8");if(h.includes("one train is at the 0 m marker and travels east at a constant 20 m/s")) process.exit(1)'
~~~

Expected: exit status 1.

- [ ] **Step 2: Replace the existing train card**

Replace the entire existing two-train div.example with:

~~~html
		<div class='example'>
			<strong>Example:</strong> Two trains move toward each other on a straight east-west track. Let east be positive. At the same instant, one train is at the 0 m marker and travels east at a constant 20 m/s. The other train is at the 600 m marker and travels west at a constant 10 m/s. When do they meet, and where is the meeting point?
			<details>
				<summary>solution</summary>
				<p>Write one position equation for each train. The westbound train has a negative velocity.</p>
				$$x_1=20\Delta t$$
				$$x_2=600-10\Delta t$$
				<p>At the meeting time, both trains have the same position.</p>
				$$20\Delta t=600-10\Delta t$$
				$$30\Delta t=600$$
				$$\Delta t=20\,\mathrm{s}$$
				<p>Use either equation to find the meeting position, then check it with the other train.</p>
				$$x_1=(20)(20)$$
				$$x_1=400\,\mathrm{m}$$
				$$x_2=600-(10)(20)$$
				$$x_2=400\,\mathrm{m}$$
				<p>The trains meet after 20 s at the 400 m marker.</p>
			</details>
		</div>
~~~

- [ ] **Step 3: Verify structure, arithmetic, and markup**

~~~bash
node -e 'const fs=require("fs");const h=fs.readFileSync("notes/motion/motion/index.html","utf8");const a=h.indexOf("one train is at the 0 m marker and travels east at a constant 20 m/s");const b=h.indexOf("Reading (5 minutes)");if(a<0||a>b||h.includes("234 000 m marker")||h.includes("72 km/h")||!h.includes("$$\\Delta t=20\\,\\mathrm{s}$$")||!h.includes("$$x_2=400\\,\\mathrm{m}$$")) process.exit(1);console.log("simplified train challenge structure: pass")'
node -e 'const t=600/(20+10),x=20*t;if(t!==20||x!==400||600-10*t!==400) process.exit(1);console.log("simplified train challenge arithmetic: pass")'
git diff --check
~~~

Expected output:

~~~text
simplified train challenge structure: pass
simplified train challenge arithmetic: pass
~~~

- [ ] **Step 4: Inspect and commit**

~~~bash
git diff -- notes/motion/motion/index.html
git add notes/motion/motion/index.html docs/superpowers/plans/2026-07-16-motion-two-train-simplification-plan.md
git commit -m "content: simplify motion train challenge"
~~~

Expected: one focused page rewrite and its implementation plan are committed.
