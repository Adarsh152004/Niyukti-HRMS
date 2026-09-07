# Design System — HRMS Intelligence OS

## Color System

| Token | Light Mode | Dark Mode | Usage |
|---|---|---|---|
| `--background` | `#F8F9FB` | `#0F1115` | App background |
| `--surface` | `#FFFFFF` | `#171A21` | Cards, panels |
| `--surface-secondary` | `#F3F4F6` | `#1E222B` | Sidebar, table headers |
| `--text-primary` | `#111827` | `#F9FAFB` | Headlines, labels |
| `--text-secondary` | `#4B5563` | `#A1A1AA` | Body text |
| `--text-muted` | `#6B7280` | `#71717A` | Metadata, help text |
| `--border` | `#E5E7EB` | `#272B35` | Default borders |
| `--accent` | `#2563EB` | `#60A5FA` | Primary actions |
| `--success` | `#16A34A` | `#16A34A` | Active, positive |
| `--warning` | `#D97706` | `#D97706` | Pending, caution |
| `--danger` | `#DC2626` | `#DC2626` | Error, destructive |
| `--ai` | `#7C3AED` | `#7C3AED` | AI-specific accents (sparse) |

## Typography Scale

| Name | Size | Weight | Usage |
|---|---|---|---|
| Page Title | 24px | 700 | `<h1>` per page |
| Section Title | 20px | 600 | Section headers |
| Card Title | 14px | 600 | Card/panel titles |
| Body | 14px | 400 | Body copy |
| Dense Table | 13px | 400 | Table rows |
| Metadata | 12px | 400 | Timestamps, codes |
| Label | 11px + uppercase | 600 | Section group labels |

Font: **Inter** with system fallback.

## Spacing Scale

```
4px · 8px · 12px · 16px · 20px · 24px · 32px · 40px · 48px
```

Never use arbitrary spacing values. Stick to the scale.

## Border Radius

```
Button / Input:     6px   (rounded-md)
Card / Panel:       8px   (rounded-lg)
Dialog:            10px   (rounded-xl)
```

## Component Rules

### Buttons
- Primary: solid `--accent` fill, white text
- Secondary: white/neutral with border
- Ghost: transparent, hover shows `--surface-secondary`
- Destructive: red semantic
- AI-assist: `--ai-soft` background, `--ai` text — use sparingly

### Tables
- Sticky thead with `--surface-secondary` background
- Row height: 40px (`h-10`)
- Header height: 36px (`h-9`)
- Row hover: `--surface-secondary/60` tint
- Selected row: `--accent-soft` tint
- Compact text: 13px (`text-sm`)

### AI Components
- AI Recommendation: bordered card with `--ai-soft` header strip
- Never use sparkle icons or gradient borders
- Always show: confidence %, risk level, evidence, sources
- Actions: Approve / Modify / Reject — never just "Accept"

### Approval Cards (HITL)
- Full evidence must be visible or one click away
- Expiration time is always shown
- Risk level uses `RiskBadge` — icon + text + color (never color alone)

## Navigation Groups

```
Overview
  Dashboard

Workforce
  Employees · Departments · Attendance · Leave · Performance · Learning

Talent
  Recruitment · Candidates · Payroll

Operations
  Documents · Policies

AI & Automation
  Command Center · AI Assistant · Agents · Workflows · Approvals

Intelligence
  Analytics · Predictions

Administration
  Governance · Audit · Settings
```

## Dark Mode

- Enabled via `class="dark"` on `<body>` / root element
- Toggle stored in `localStorage` as `hrms-theme`
- System preference respected on first load
- Dark tokens: slightly elevated surfaces, muted accent
- Never invert light mode — use the separate dark token set

## Demo Mode

Controlled by `VITE_APP_MODE=demo`.
- Visible "Demo Mode" badge in Topbar
- All mutations show: "Demo action — no production change was made."
- Fixture data never silently used in production
- `withDataProvider()` is the single abstraction — never bypass it
