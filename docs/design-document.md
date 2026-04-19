# Teacher Model App — Design Document

---

## 1. Design Philosophy

**Core principle:** The UI should feel like a professional SaaS tool, not a school project.
The teacher fills in a simple form; the AI complexity is visible but not overwhelming.
Three ideas drive every decision:

- **Clarity** — one action per screen zone, no ambiguity about what to do next
- **Trust** — showing the debate process (not hiding it) builds confidence in the output
- **Speed perception** — live progress indicators make waiting feel shorter

---

## 2. Colour Palette

| Token | Hex | Usage |
|---|---|---|
| `bg-base` | `#0a0f1e` | Page background |
| `bg-surface` | `#0f172a` | Cards, panels |
| `bg-raised` | `#1e293b` | Input fields, inner cards |
| `border` | `#334155` | All borders |
| `text-primary` | `#f1f5f9` | Headlines, labels |
| `text-secondary` | `#94a3b8` | Captions, hints |
| `text-muted` | `#64748b` | Placeholder, disabled |
| `accent-blue` | `#3b82f6` | Primary CTA, active tabs, focus rings |
| `accent-blue-dark` | `#1d4ed8` | Button hover |
| `accent-emerald` | `#10b981` | Success states, Round done |
| `accent-amber` | `#f59e0b` | Round 2 critique indicators |
| `accent-orange` | `#f97316` | Claude model badge |
| `accent-purple` | `#a855f7` | Llama model badge |
| `white` | `#ffffff` | Question paper body only |

---

## 3. Typography

| Use | Style |
|---|---|
| Page title | `system-ui`, 18px, semibold, `#f1f5f9` |
| Section headers | 13px, semibold, `#f1f5f9` |
| Body / labels | 12–13px, regular, `#94a3b8` |
| Input text | 13px, regular, `#f1f5f9` |
| Paper body (output) | `Georgia` serif, 13–14px, `#1e293b` |
| Code / debate panel | `monospace`, 11px, `#94a3b8` |
| Caption / footer | 11px, `#64748b` |

---

## 4. Layout

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR  (sticky, 56px)                             │
├─────────────────────────────────────────────────────┤
│  HOW IT WORKS STRIP  (48px)                         │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  INPUT PANEL │  RESULTS AREA                        │
│  (320px)     │  (flex-1)                            │
│              │                                      │
│  + PROGRESS  │                                      │
│  TRACKER     │                                      │
│              │                                      │
├──────────────┴──────────────────────────────────────┤
│  FOOTER  (48px)                                     │
└─────────────────────────────────────────────────────┘
```

- Max content width: `1280px`, centred
- Side padding: `24px`
- Left panel: fixed `320px`
- Gap between panels: `24px`

---

## 5. Components

### 5.1 Navbar
- Height: 56px, `sticky top-0`, `backdrop-blur`
- Left: app icon (blue square) + name + tagline
- Right: three model status badges with pulsing green dot

### 5.2 Model Status Badge
```
[ • Claude ]   border: orange/30, text: orange-300
[ • Gemini ]   border: blue/30,   text: blue-300
[ • Llama  ]   border: purple/30, text: purple-300
```
- Dot pulses green when model is active, red when failed

### 5.3 How It Works Strip
Three step-cards connected by `→` arrows:
```
[⚡ Round 1 — Parallel Draft]  →  [💬 Round 2 — Peer Critique]  →  [✨ Round 3 — Synthesis]
```
Each step-card: `bg-slate-800/60`, rounded-xl, 10px padding, dark border

### 5.4 Input Form
- Background: `bg-slate-900`, border: `border-slate-700/60`, `rounded-2xl`
- Field labels: 11px, `text-slate-400`
- Inputs: `bg-slate-800`, `border-slate-700`, `rounded-lg`, focus ring blue
- CTA button: full-width, `bg-blue-600`, `rounded-xl`, shadow `shadow-blue-900/40`

### 5.5 Debate Progress Tracker
Three round-rows stacked:
- **Done:** emerald circle with ✓, green check per model chip
- **In progress:** numbered circle, blue spinner per chip
- **Pending:** numbered circle (grey), grey chips

### 5.6 Final Paper Card
- Header bar: `bg-slate-800`, dark — holds title, "Synthesised" badge, Download button
- Body: `bg-white`, serif font, school-style formatting
- Section colour coding:
  - MCQ: `border-l-4 border-blue-500`
  - Short Answer: `border-l-4 border-amber-500`
  - Long Answer: `border-l-4 border-emerald-500`

### 5.7 Download Button
- `bg-blue-600`, white text, `⬇ Download Word Document`
- Hover: `bg-blue-500`
- Located both in paper header bar and below the paper

### 5.8 Model Debate Tabs
Four tabs: Claude Draft / Gemini Draft / Llama Draft / Peer Critiques
- Active tab: `border-b-2 border-blue-500 text-blue-400`
- Inactive: `text-slate-500`, hover `text-slate-300`
- Tab body: monospace font, dark bg, scrollable, max-height 176px

---

## 6. Interaction States

| State | Visual |
|---|---|
| Generate button idle | Blue fill, shadow |
| Generate button hover | Lighter blue |
| Generate button loading | Disabled, spinner inside |
| Input field focus | Blue border + soft blue ring |
| Model badge — active | Green pulsing dot |
| Model badge — failed | Red dot, no pulse |
| Round row — done | Emerald background, ✓ icons |
| Round row — running | Blue bg tint, spinning loader |
| Round row — pending | Grey, no animation |

---

## 7. Section-by-Section UX Notes

### Navbar
The model badges serve double duty: they show which models are configured (green dot) and which failed (red dot). This lets the teacher know before generating that something is wrong.

### How It Works Strip
Always visible. Teachers unfamiliar with AI need to understand the 3-round process before trusting the output. This strip explains it without needing a modal or help page.

### Input Panel
Required fields marked with `*`. The form is ordered by specificity: broad (subject) → narrow (topics) → constraints (marks, duration) → optional (special instructions). This mirrors how a teacher thinks.

### Debate Progress Tracker
Appears below the input form after generation starts. Each model chip updates independently as API calls return — giving live feedback even though calls are parallel.

### Final Paper
Rendered in white with serif font — deliberately breaking from the dark UI — because this is a **document**, not an app element. The teacher should immediately recognise it as paper-ready content.

### Model Debate Panel
Collapsed by default into tabs. This is the "show your working" section — useful for curious or sceptical teachers, but not the primary output. Peer Critiques tab is the most interesting: it shows *why* the final paper is better than any individual draft.

---

## 8. Responsive Behaviour
- Below 1024px: Left panel stacks above results (single column)
- Below 768px: How It Works strip becomes vertical
- Mobile is out of scope for v1 — this is a desktop teacher tool

---

## 9. Accessibility
- All interactive elements have `:focus` styles
- Colour is never the only indicator of state (icons accompany colours)
- Contrast ratio on text meets WCAG AA minimum

---

## 10. What NOT to do
- No purple gradients — overused in AI apps
- No hero illustrations or stock photography
- No modal popups for progress — inline progress only
- No skeleton loaders — real progress indicators instead
- No auto-scroll to results — teacher chooses when to look
