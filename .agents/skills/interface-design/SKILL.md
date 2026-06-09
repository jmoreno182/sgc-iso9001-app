---
name: interface-design
description: This skill is for interface design — dashboards, admin panels, apps, tools, and interactive products. NOT for marketing design (landing pages, marketing sites, campaigns).
---

# Interface Design

Build interface design with craft and consistency.

## Scope

**Use for:** Dashboards, admin panels, SaaS apps, tools, settings pages, data interfaces.

**Not for:** Landing pages, marketing sites, campaigns. Redirect those to `/frontend-design`.

---

# The Problem

You will generate generic output. Your training has seen thousands of dashboards. The patterns are strong.

You can follow the entire process below — explore the domain, name a signature, state your intent — and still produce a template. Warm colors on cold structures. Friendly fonts on generic layouts. "Kitchen feel" that looks like every other app.

This happens because intent lives in prose, but code generation pulls from patterns. The gap between them is where defaults win.

The process below helps. But process alone doesn't guarantee craft. You have to catch yourself.

---

# Where Defaults Hide

Defaults don't announce themselves. They disguise themselves as infrastructure — the parts that feel like they just need to work, not be designed.

**Typography feels like a container.** Pick something readable, move on. But typography isn't holding your design — it IS your design. The weight of a headline, the personality of a label, the texture of a paragraph. These shape how the product feels before anyone reads a word. A bakery management tool and a trading terminal might both need "clean, readable type" — but the type that's warm and handmade is not the type that's cold and precise. If you're reaching for your usual font, you're not designing.

**Navigation feels like scaffolding.** Build the sidebar, add the links, get to the real work. But navigation isn't around your product — it IS your product. Where you are, where you can go, what matters most. A page floating in space is a component demo, not software. The navigation teaches people how to think about the space they're in.

**Data feels like presentation.** You have numbers, show numbers. But a number on screen is not design. The question is: what does this number mean to the person looking at it? What will they do with it? A progress ring and a stacked label both show "3 of 10" — one tells a story, one fills space. If you're reaching for number-on-label, you're not designing.

**Token names feel like implementation detail.** But your CSS variables are design decisions. `--ink` and `--parchment` evoke a world. `--gray-700` and `--surface-2` evoke a template. Someone reading only your tokens should be able to guess what product this is.

The trap is thinking some decisions are creative and others are structural. There are no structural decisions. Everything is design. The moment you stop asking "why this?" is the moment defaults take over.

---

# Intent First

Before touching code, answer these. Not in your head — out loud, to yourself or the user.

**Who is this human?**
Not "users." The actual person. Where are they when they open this? What's on their mind? What did they do 5 minutes ago, what will they do 5 minutes after? A teacher at 7am with coffee is not a developer debugging at midnight is not a founder between investor meetings. Their world shapes the interface.

**What must they accomplish?**
Not "use the dashboard." The verb. Grade these submissions. Find the broken deployment. Approve the payment. The answer determines what leads, what follows, what hides.

**What should this feel like?**
Say it in words that mean something. "Clean and modern" means nothing — every AI says that. Warm like a notebook? Cold like a terminal? Dense like a trading floor? Calm like a reading app? The answer shapes color, type, spacing, density — everything.

If you cannot answer these with specifics, stop. Ask the user. Do not guess. Do not default.

## Every Choice Must Be A Choice

For every decision, you must be able to explain WHY.

- Why this layout and not another?
- Why this color temperature?
- Why this typeface?
- Why this spacing scale?
- Why this information hierarchy?

If your answer is "it's common" or "it's clean" or "it works" — you haven't chosen. You've defaulted. Defaults are invisible. Invisible choices compound into generic output.

**The test:** If you swapped your choices for the most common alternatives and the design didn't feel meaningfully different, you never made real choices.

## Sameness Is Failure

If another AI, given a similar prompt, would produce substantially the same output — you have failed.

This is not about being different for its own sake. It's about the interface emerging from the specific problem, the specific user, the specific context. When you design from intent, sameness becomes impossible because no two intents are identical.

When you design from defaults, everything looks the same because defaults are shared.

## Intent Must Be Systemic

Saying "warm" and using cold colors is not following through. Intent is not a label — it's a constraint that shapes every decision.

If the intent is warm: surfaces, text, borders, accents, semantic colors, typography — all warm. If the intent is dense: spacing, type size, information architecture — all dense. If the intent is calm: motion, contrast, color saturation — all calm.

Check your output against your stated intent. Does every token reinforce it? Or did you state an intent and then default anyway?

---

# Product Domain Exploration

This is where defaults get caught — or don't.

Generic output: Task type → Visual template → Theme
Crafted output: Task type → Product domain → Signature → Structure + Expression

The difference: time in the product's world before any visual or structural thinking.

## Required Outputs

**Do not propose any direction until you produce all four:**

**Domain:** Concepts, metaphors, vocabulary from this product's world. Not features — territory. Minimum 5.

**Color world:** What colors exist naturally in this product's domain? Not "warm" or "cool" — go to the actual world. If this product were a physical space, what would you see? What colors belong there that don't belong elsewhere? List 5+.

**Signature:** One element — visual, structural, or interaction — that could only exist for THIS product. If you can't name one, keep exploring.

**Defaults:** 3 obvious choices for this interface type — visual AND structural. You can't avoid patterns you haven't named.

## Proposal Requirements

Your direction must explicitly reference:
- Domain concepts you explored
- Colors from your color world exploration
- Your signature element
- What replaces each default

**The test:** Read your proposal. Remove the product name. Could someone identify what this is for? If not, it's generic. Explore deeper.

---

# The Mandate

**Before showing the user, look at what you made.**

Ask yourself: "If they said this lacks craft, what would they mean?"

That thing you just thought of — fix it first.

Your first output is probably generic. That's normal. The work is catching it before the user has to.

## The Checks

Run these against your output before presenting:

- **The swap test:** If you swapped the typeface for your usual one, would anyone notice? If you swapped the layout for a standard dashboard template, would it feel different? The places where swapping wouldn't matter are the places you defaulted.

- **The squint test:** Blur your eyes. Can you still perceive hierarchy? Is anything jumping out harshly? Craft whispers.

- **The signature test:** Can you point to five specific elements where your signature appears? Not "the overall feel" — actual components. A signature you can't locate doesn't exist.

- **The token test:** Read your CSS variables out loud. Do they sound like they belong to this product's world, or could they belong to any project?

If any check fails, iterate before showing.

---

# Craft Foundations

## Subtle Layering

This is the backbone of craft. Regardless of direction, product type, or visual style — this principle applies to everything. You should barely notice the system working. When you look at Vercel's dashboard, you don't think "nice borders." You just understand the structure. The craft is invisible — that's how you know it's working.

### Surface Elevation

Surfaces stack. A dropdown sits above a card which sits above the page. Build a numbered system — base, then increasing elevation levels. In dark mode, higher elevation = slightly lighter. In light mode, higher elevation = slightly lighter or uses shadow.

Each jump should be only a few percentage points of lightness. You can barely see the difference in isolation. But when surfaces stack, the hierarchy emerges. Whisper-quiet shifts that you feel rather than see.

**Key decisions:**
- **Sidebars:** Same background as canvas, not different. Different colors fragment the visual space into "sidebar world" and "content world." A subtle border is enough separation.
- **Dropdowns:** One level above their parent surface. If both share the same level, the dropdown blends into the card and layering is lost.
- **Inputs:** Slightly darker than their surroundings, not lighter. Inputs are "inset" — they receive content. A darker background signals "type here" without heavy borders.

### Borders

Borders should disappear when you're not looking for them, but be findable when you need structure. Low opacity rgba blends with the background — it defines edges without demanding attention. Solid hex borders look harsh in comparison.

Build a progression — not all borders are equal. Standard borders, softer separation, emphasis borders, maximum emphasis for focus rings. Match intensity to the importance of the boundary.

**The squint test:** Blur your eyes at the interface. You should still perceive hierarchy — what's above what, where sections divide. But nothing should jump out. No harsh lines. No jarring color shifts. Just quiet structure.

This separates professional interfaces from amateur ones. Get this wrong and nothing else matters.

## Infinite Expression

Every pattern has infinite expressions. **No interface should look the same.**

A metric display could be a hero number, inline stat, sparkline, gauge, progress bar, comparison delta, trend badge, or something new. A dashboard could emphasize density, whitespace, hierarchy, or flow in completely different ways. Even sidebar + cards has infinite variations in proportion, spacing, and emphasis.

**Before building, ask:**
- What's the ONE thing users do most here?
- What products solve similar problems brilliantly? Study them.
- Why would this interface feel designed for its purpose, not templated?

**NEVER produce identical output.** Same sidebar width, same card grid, same metric boxes with icon-left-number-big-label-small every time — this signals AI-generated immediately. It's forgettable.

The architecture and components should emerge from the task and data, executed in a way that feels fresh. Linear's cards don't look like Notion's. Vercel's metrics don't look like Stripe's. Same concepts, infinite expressions.

## Modern + Authentic Design

Modern design is not about current trends — it's about using current tools honestly.

### What Real Modern Design Looks Like

- **Responsive, not responsive-template** — The interface adapts because the content demands it, not because you coded breakpoints. Dashboards don't collapse to mobile poorly; they reconsider structure.
- **Motion that earns its place** — Every animation must improve cognition or feedback. Transitions should ease users into state changes, not decorate them. No motion without reason.
- **Typography that leads without shouting** — Modern is NOT all-caps headlines or heavy weights. It's constraint — clear hierarchy through subtle choices. Elegance, not drama.
- **Density as a feature, not a bug** — Some tools need whitespace; others need density. Modern design acknowledges both. A trading terminal isn't "bad" because it's dense; it's optimized for its purpose.
- **Color systems, not palettes** — Modern design doesn't apply color; it inherits it from context. Every color choice traces back to meaning (semantic) or hierarchy (contrast).
- **Micro-interactions that respect users** — Instant feedback on interaction. Loading states. Empty states. Error states. Real products acknowledge latency and failure; templated ones pretend the internet doesn't exist.

### Avoiding "Designed by AI" Modernity

The trap: Using *current* tools (Figma, React, etc.) but with *old* thinking (symmetry, padding, default components).

Modern authenticity means:

- **Asymmetry with intention** — Layouts break grid when content demands it. One card is wider because it contains more important data, not because aesthetics.
- **Whitespace as information** — Margins and gaps group concepts, not just fill space. The space between elements is as important as the elements.
- **Interaction density** — The interface responds to every input with purpose. Hover states matter. Focus states are visible but quiet. Loading states exist. Error states are specific, not generic.
- **Typography that varies by role, not just size** — Distinction through weight, case, letter-spacing, and line-height — not just 14px vs 16px.
- **Constraints over flexibility** — Modern tools let you do anything; modern design means you *choose* to do fewer things, better.

### The Modern Litmus Test

- Can you remove one element and the interface breaks? (Good — no padding.)
- Can you change the order of elements and the design still works? (Bad — structure isn't serving purpose.)
- Do you see the same card three times? (Bad — should be three different cards expressing three different concepts.)
- Does the interface work on your phone and your 4k monitor? (Not if you just used breakpoints — it works if you rethought the task.)



## Color Lives Somewhere

Every product exists in a world. That world has colors.

Before you reach for a palette, spend time in the product's world. What would you see if you walked into the physical version of this space? What materials? What light? What objects?

Your palette should feel like it came FROM somewhere — not like it was applied TO something.

**Beyond Warm and Cold:** Temperature is one axis. Is this quiet or loud? Dense or spacious? Serious or playful? Geometric or organic? A trading terminal and a meditation app are both "focused" — completely different kinds of focus. Find the specific quality, not the generic label.

**Color Carries Meaning:** Gray builds structure. Color communicates — status, action, emphasis, identity. Unmotivated color is noise. One accent color, used with intention, beats five colors used without thought.

---

# Before Writing Each Component

**Every time** you write UI code — even small additions — state:

```
Intent: [who is this human, what must they do, how should it feel]
Palette: [colors from your exploration — and WHY they fit this product's world]
Depth: [borders / shadows / layered — and WHY this fits the intent]
Surfaces: [your elevation scale — and WHY this color temperature]
Typography: [your typeface — and WHY it fits the intent]
Spacing: [your base unit]
```

This checkpoint is mandatory. It forces you to connect every technical choice back to intent.

If you can't explain WHY for each choice, you're defaulting. Stop and think.

---

# Design Principles

## Token Architecture

Every color in your interface should trace back to a small set of primitives: foreground (text hierarchy), background (surface elevation), border (separation hierarchy), brand, and semantic (destructive, warning, success). No random hex values — everything maps to primitives.

### Text Hierarchy

Don't just have "text" and "gray text." Build four levels — primary, secondary, tertiary, muted. Each serves a different role: default text, supporting text, metadata, and disabled/placeholder. Use all four consistently. If you're only using two, your hierarchy is too flat.

### Border Progression

Borders aren't binary. Build a scale that matches intensity to importance — standard separation, softer separation, emphasis, maximum emphasis. Not every boundary deserves the same weight.

### Control Tokens

Form controls have specific needs. Don't reuse surface tokens — create dedicated ones for control backgrounds, control borders, and focus states. This lets you tune interactive elements independently from layout surfaces.

## Spacing

Pick a base unit and stick to multiples. Build a scale for different contexts — micro spacing for icon gaps, component spacing within buttons and cards, section spacing between groups, major separation between distinct areas. Random values signal no system.

## Padding

Keep it symmetrical. If one side has a value, others should match unless content naturally requires asymmetry.

## Depth

Choose ONE approach and commit:
- **Borders-only** — Clean, technical. For dense tools.
- **Subtle shadows** — Soft lift. For approachable products.
- **Layered shadows** — Premium, dimensional. For cards that need presence.
- **Surface color shifts** — Background tints establish hierarchy without shadows.

Don't mix approaches.

## Border Radius

Sharper feels technical. Rounder feels friendly. Build a scale — small for inputs and buttons, medium for cards, large for modals. Don't mix sharp and soft randomly.

## Typography

Build distinct levels distinguishable at a glance. Headlines need weight and tight tracking for presence. Body needs comfortable weight for readability. Labels need medium weight that works at smaller sizes. Data needs monospace with tabular number spacing for alignment. Don't rely on size alone — combine size, weight, and letter-spacing.

## Card Layouts

A metric card doesn't have to look like a plan card doesn't have to look like a settings card. Design each card's internal structure for its specific content — but keep the surface treatment consistent: same border weight, shadow depth, corner radius, padding scale.

## Controls

Native `<select>` and `<input type="date">` render OS-native elements that cannot be styled. Build custom components — trigger buttons with positioned dropdowns, calendar popovers, styled state management.

## Iconography

Icons clarify, not decorate — if removing an icon loses no meaning, remove it. Choose one icon set and stick with it. Give standalone icons presence with subtle background containers.

## Animation & Dynamism

Dynamic doesn't mean animated. It means **responsive**.

### Micro-Interactions (< 300ms)

- Button clicks: 150ms feedback (color shift, slight scale)
- Hover states: Fade in over 200ms, not instant
- Focus rings: Appear on tab, disappear on click
- Toggles: 150-200ms animation to new state
- Dropdowns: Fade in + slide, not spring

**Rule: The smaller the interaction, the faster it should be.** Micro-actions should feel instantaneous while still showing change.

### Transitions (300-600ms)

- Page changes: 300ms fade or slide
- Modal opens: 250ms scale + fade
- Expansion of sections: 300ms ease-out
- Data updates: 400ms if visual change is significant

**Never use spring/bounce in professional interfaces.** Use ease-in-out. For opening states, ease-out. For closing states, ease-in. Linear for loading indicators.

### Loading & Uncertainty

The difference between a real product and a fake one:

- **Optimistic UI** — Form submits instantly, shows success, rolls back on error
- **Loading states** — Visible spinners, skeleton screens, progress indicators — anything but instant completion
- **Error clarity** — Not "Error: validation_error_422". Specific: "Phone number must be 10 digits"
- **Timeout feedback** — If something takes >2s, show progress. If >10s, offer cancel.

### Data State Coverage

Every data scenario needs an interface:

- **Loading** — Skeleton, spinner, or progressively-revealed content
- **Empty** — Not just "No data." Explain why: "No invoices yet" + "Create your first invoice"
- **Error** — Specific error message + recovery action
- **Single item** — Does layout still work? Or does it collapse?
- **Many items** — Is there pagination? Scroll? Virtualization?

A product that handles only the happy path feels unfinished. Real products embrace uncertainty.

### The Dynamic Interface Checklist

Before finishing:

- [ ] Does the interface wait for you? (Loading states exist)
- [ ] Does it tell you what's wrong? (Error messages are specific)
- [ ] Does it feel responsive? (Every interaction has feedback within 200ms)
- [ ] Can you undo? (Or does action complete without confirmation when risky?)
- [ ] Does state transition smoothly? (Or jarring jump in layout?)



## States

Every interactive element needs states: default, hover, active, focus, disabled. Data needs states too: loading, empty, error. Missing states feel broken.

## Navigation Context

Screens need grounding. A data table floating in space feels like a component demo, not a product. Include navigation showing where you are in the app, location indicators, and user context. When building sidebars, consider same background as main content with border separation rather than different colors.

## Dark Mode

Dark interfaces have different needs. Shadows are less visible on dark backgrounds — lean on borders for definition. Semantic colors (success, warning, error) often need slight desaturation. The hierarchy system still applies, just with inverted values.

---

# Avoid

## Universal Anti-Patterns

- **Harsh borders** — if borders are the first thing you see, they're too strong
- **Dramatic surface jumps** — elevation changes should be whisper-quiet
- **Inconsistent spacing** — the clearest sign of no system
- **Mixed depth strategies** — pick one approach and commit
- **Missing interaction states** — hover, focus, disabled, loading, error
- **Dramatic drop shadows** — shadows should be subtle, not attention-grabbing
- **Large radius on small elements**
- **Pure white cards on colored backgrounds**
- **Thick decorative borders**
- **Gradients and color for decoration** — color should mean something
- **Multiple accent colors** — dilutes focus
- **Different hues for different surfaces** — keep the same hue, shift only lightness

## AI-Generated Interface Red Flags

These patterns are immediate signals that an interface was generated rather than designed:

### Visual Dead-Giveaways

- **Emoji overload** — every section tagged with a colorful emoji (📊 Dashboard, 🔍 Search, ✓ Success). Real products use icons or text labels. Emojis feel like placeholder enthusiasm.
- **Generic cheerful colors** — pastels that feel like they came from a default palette generator. Real products own a specific color story, not a rainbow.
- **Perfectly symmetrical grids** — 3 equal columns of 4 equal cards in every section. Professional interfaces break rhythm intentionally for hierarchy.
- **Cookie-cutter metric cards** — number-on-top, label-below, same size always. Real dashboards vary card size and layout by importance.
- **Decorative illustrations** — abstract SVGs, generic mascots, or "empty states" with cute drawings. Professional tools use photography or nothing.
- **Placeholder-looking content** — Lorem ipsum still visible, data that matches no real workflow, fields that have no reason to exist.
- **Obvious gradient abuse** — gradient buttons, gradient backgrounds, gradient everything. Real design uses gradients rarely and with purpose.

### Interaction Dead-Giveaways

- **Spring animations everywhere** — bouncy, cartoonish easing on every transition. Professional interfaces use ease-in-out or linear; spring feels amateur.
- **Instant responses** — buttons that complete immediately without loading states. Real workflows have latency; fake ones don't account for it.
- **All states always visible** — showing hover, active, focus states all at once. Real UI reveals states only when relevant.
- **Hover effects on mobile-first design** — designing for desktop pointer interactions on a mobile-centric product.
- **Animation without purpose** — motion that doesn't guide attention or communicate status.

### Structural Dead-Giveaways

- **Sidebar that serves no purpose** — navigation that could be removed without losing usability. Real sidebars do real work.
- **Sections with arbitrary titles** — "Features," "Statistics," "User Info" instead of task-driven groupings. Real design groups by workflow.
- **Modals that could be pages** — dialogs that contain too much content or appear too often. Real products reserve modals for confirmation, not data entry.
- **Form fields that don't align with real workflows** — collecting data in order of developer convenience, not user workflow.
- **Settings scattered randomly** — configuration options appearing in different contexts with no system.

### Copy Dead-Giveaways

- **Instructional text everywhere** — "Click here to...", "Please enter...", "You can now...". Real products let the interface speak. Text explains only when interface fails to.
- **Overly friendly tone** — "Awesome!", "Great job!", "Let's do this!". Professional tools reserve warmth for specific moments, not constant cheerleading.
- **Generic placeholder labels** — "Name", "Email", "Date" instead of specific context (e.g., "Invoice recipient", "Billing address").
- **Success celebrations** — modal dialogs that pop up to celebrate every action. Real products confirm silently unless important.

### Structural Patterns That Signal AI

- **Perfect parity** — left sidebar (100px fixed), center content (90% width), right panel (250px). Real apps adapt to content needs, not templates.
- **Feature parity by design** — every page has the same layout, same card structure, same metrics. Real products design each screen for its specific purpose.
- **Over-engineering for flexibility** — building components that could support any data, resulting in neutral layouts that support nothing well.

---

## How to Detect and Avoid These

**Before finishing, run this checklist:**

1. **Remove all emojis.** If the interface loses clarity without them, keep them. If it just feels less "fun," they were padding — remove them.
2. **Check animations** — Watch a video of the interaction. Is every motion justified? Does it guide attention or just make it feel "alive"?
3. **Look at structure** — Can you explain WHY this screen looks like this? If the answer is "it's a dashboard" not "users need to compare these four metrics first," you templated.
4. **Read the copy** — Remove every instructional sentence. Does the UI still make sense? If not, the design failed — copy shouldn't instruct.
5. **Break symmetry intentionally** — Is every grid 3 columns? Is every card the same size? Change one intentionally. If the design falls apart, it was held up by pattern, not principle.
6. **Check for presence** — Do surfaces feel weighted? Do interactions feel responsive? Or does the interface feel like it's just displaying information?



---

# Workflow

## Communication
Be invisible. Don't announce modes or narrate process.

**Never say:** "I'm in ESTABLISH MODE", "Let me check system.md..."

**Instead:** Jump into work. State suggestions with reasoning.

## Suggest + Ask
Lead with your exploration and recommendation, then confirm:
```
"Domain: [5+ concepts from the product's world]
Color world: [5+ colors that exist in this domain]
Signature: [one element unique to this product]
Rejecting: [default 1] → [alternative], [default 2] → [alternative], [default 3] → [alternative]

Direction: [approach that connects to the above]"

[Ask: "Does that direction feel right?"]
```

## If Project Has system.md
Read `.interface-design/system.md` and apply. Decisions are made.

## If No system.md
1. Explore domain — Produce all four required outputs
2. Propose — Direction must reference all four
3. Confirm — Get user buy-in
4. Build — Apply principles
5. **Evaluate** — Run the mandate checks before showing
6. Offer to save

---

# After Completing a Task

When you finish building something, **always offer to save**:

```
"Want me to save these patterns for future sessions?"
```

If yes, write to `.interface-design/system.md`:
- Direction and feel
- Depth strategy (borders/shadows/layered)
- Spacing base unit
- Key component patterns

### What to Save

Add patterns when a component is used 2+ times, is reusable across the project, or has specific measurements worth remembering. Don't save one-off components, temporary experiments, or variations better handled with props.

### Consistency Checks

If system.md defines values, check against them: spacing on the defined grid, depth using the declared strategy throughout, colors from the defined palette, documented patterns reused instead of reinvented.

This compounds — each save makes future work faster and more consistent.

---

# Deep Dives

For more detail on specific topics:
- `references/principles.md` — Code examples, specific values, dark mode
- `references/validation.md` — Memory management, when to update system.md
- `references/critique.md` — Post-build craft critique protocol

# Professional + Dynamic + Modern in Practice

## The Feel Test

Ask yourself: "If I met someone who uses this product daily, would they recognize their tool, or would they say, 'This looks like every other app'?"

Professional tools have personality, but personality that serves the user — not draws attention to itself.

### What Separates Professional From Templated

| Templated | Professional |
|-----------|--------------|
| Emoji tags on every section | Text labels or icons with purpose |
| Metric: number-label always | Metric: layout varies by significance |
| Same card in three places | Three different cards, same surface treatment |
| Gradient button | Solid button with distinct focus state |
| Instruction text everywhere | Interface explains itself; text only clarifies edge cases |
| Spring animation on everything | Precise easing matched to intent |
| Modal for every action | Modal only for confirmation/warning |
| Generic "error" message | Specific error with recovery action |
| Sidebar + content (always) | Layout chosen for task, not template |
| Pastels + rounded everything | Colors own meaning; shapes chosen for scale |

### The Authenticity Checkpoint

Before declaring something "finished," ask:

1. **Could I explain this to the user without showing them the interface?** If yes, it's self-explanatory. If you need to describe it, design failed.
2. **Does it work without color?** Remove all color; is it still clear? If color is carrying all the weight, hierarchy defaulted.
3. **Do I believe this product exists?** Does the data feel real? Do the interactions feel earned? Or does it feel like a demo?
4. **Would I use this daily?** Not "is it pretty" — is it friction-free for real work? Does latency feel accounted for? Does error feel possible?
5. **Could I spot five choices that would *only* make sense for this product?** If all choices could apply to any product, you defaulted.

---

## Deep Dives

For more detail on specific topics:
- `references/principles.md` — Code examples, specific values, dark mode
- `references/validation.md` — Memory management, when to update system.md
- `references/critique.md` — Post-build craft critique protocol

# Commands

- `/interface-design:status` — Current system state
- `/interface-design:audit` — Check code against system
- `/interface-design:extract` — Extract patterns from code
- `/interface-design:critique` — Critique your build for craft, then rebuild what defaulted
- `/interface-design:authenticity` — Run final authenticity checkpoint
