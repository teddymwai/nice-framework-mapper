# Design Tokens & UI Reference Standards

## 1. 4px Grid Rhythm

All spacing must be multiples of 4px:
- `4px`: Hairline padding, tight icon spacing
- `8px`: Standard element gap, pill internal margin
- `12px`: Card padding (compact)
- `16px`: Standard card/modal padding
- `24px`: Section spacing
- `32px`: Main view gutter

## 2. Color Roles

| Token | Hex / Value | Usage |
|---|---|---|
| `--color-bg-base` | `#0d1310` | Main canvas background |
| `--color-bg-surface` | `#151f1a` | Cards, panels, drawers |
| `--color-bg-elevated` | `#1a2620` | Modals, floating popovers |
| `--color-border-subtle` | `rgba(255, 255, 255, 0.08)` | Dividers, card strokes |
| `--color-text-primary` | `#f0f6f2` | Headers, body text |
| `--color-text-muted` | `#9bb1a4` | Metadata, timestamps, captions |
| `--color-accent` | `#1b5e3f` | Primary buttons, active state |
| `--color-accent-hover`| `#22734e` | Hover state |
| `--color-danger` | `#a83232` | Critical alerts, destructive actions |

## 3. Apple HIG Touch Metrics

- Primary Action Button: Height `44px`, Radius `9999px` (Capsule)
- Form Input / Select: Height `44px`, Radius `8px`
- Press Scale: `scale(0.97)` on `:active` with `100ms` cubic-bezier transition
