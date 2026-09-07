# AI Interaction Guidelines — HRMS Intelligence OS

## Core Principle

**AI should feel embedded into normal work, not constantly advertised.**

The interface should communicate intelligence through behavior and information — not through visual decoration.

---

## Language Standards

### ✗ Don't use
- "✨ AI MAGIC ✨"
- "AI-Powered"
- "Intelligent Analysis"
- "Neural inference complete"
- "AI is thinking..."

### ✓ Use instead
- "AI recommendation"
- "Suggested action"
- "Automation available"
- "Analyzing request"
- "Retrieving policy"

---

## AI Recommendation Display

Every AI recommendation must show:

```
AI Recommendation                        [badge: 82% confidence · MEDIUM risk]

Recommendation:
"Schedule retention conversation with Priya Sharma — attrition risk elevated."

Evidence:
• Sentiment score: 2.8/5.0 (declining over 3 months)
• 2 missed 1:1s in Q3
• Compensation gap: ~8% vs P75 market band for role

Sources:
  3 HR records · 1 model · 2 policies

[ Reject ]  [ Modify ]  [ Approve ]
```

**Never hide evidence.** Users must be able to inspect it in one click.

---

## Tool Execution UI

When an agent runs automation steps, show observable stages:

```
✓ Retrieved employee records     08:41:02
✓ Checked leave policy           08:41:04
✓ Calculated entitlement         08:41:06
→ Preparing approval request     08:41:08
```

- `✓` = completed
- `→` = in progress (with spinner)
- `✗` = failed (with error)

**Never** show raw logs to normal users. Advanced trace is expand-on-demand.

---

## HITL Approval Pattern

For every approval:

| Field | Must show |
|---|---|
| Action | Clear description of what will happen |
| Requested by | Agent name + role |
| Risk level | LOW / MEDIUM / HIGH / CRITICAL with icon |
| Evidence | Expandable, not hidden |
| Sources | Record count + type |
| Requested at | Timestamp |
| Expires at | Deadline (urgency) |
| Actions | Approve · Modify · Reject · Delegate |

Risk levels must **never** rely on color alone. Use icon + text + color.

---

## AI Visual Language

### ✓ Allowed
- Small `AI` label in subdued gray or violet
- Subtle `--ai-soft` background on AI-specific panels
- `--ai` (violet) accent for AI-specific badges and borders

### ✗ Prohibited
- Gradient borders on AI cards
- Animated glowing elements
- Sparkle / star icons (`✨`)
- "Powered by AI" in large text
- Purple dominating the interface

Rule: If you remove the word "AI" from the UI, the feature should still function and be understandable.

---

## Streaming Response Display

For AI streaming responses:

1. Show text as it arrives
2. Citations appear below when referenced
3. Tool steps show in a collapsible trace panel
4. Approval blocks appear inline when required
5. Progress indicators for long-running operations

**Do NOT render chain-of-thought.** Only concise execution summaries.

---

## Confidence & Risk Communication

```
Confidence:    82%          (numerical)
Risk:          MEDIUM        (text + badge color)
Evidence:      3 sources    (click to expand)
```

Confidence thresholds:
- ≥ 90% → green confidence indicator
- 70–89% → neutral
- < 70% → amber warning

Never claim 100% confidence for non-deterministic predictions.
