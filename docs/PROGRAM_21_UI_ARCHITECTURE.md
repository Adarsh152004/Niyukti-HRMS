# Program 21: UI Architecture, Design System & User Experience

## 1. Enterprise Design System Foundations
- **Typography**: Inter system UI font, clear visual hierarchy, moderate weights.
- **Palette**: Warm slate/gray neutral base with restrained accents (Indigo `#4F46E5`, Emerald `#10B981`, Amber `#F59E0B`, Crimson `#EF4444`).
- **Dark Mode**: Near-black graphite surfaces with low-contrast borders and high-contrast text.
- **Zero AI Slop**: No excessive glowing purple gradients, rainbow dashboards, or glassmorphism.

---

## 2. Reusable Component Primitives
- `<DataTable />`: Paginated, sortable, and filterable table with empty and skeleton loading states.
- `<MetricCard />`: Information-dense metric display with trend indicators and data provenance metadata.
- `<ToolExecution />`: Safe operational progress indicator for automated agent tool execution.
- `<AIRecommendation />`: Decision support card displaying evidence, confidence score, and verifiable policy citations.
- `<StatusBadge />` & `<RiskBadge />`: High-contrast semantic badges for state and risk levels.
- `<CommandPalette />`: Role-aware global navigation (`Ctrl+K`).
