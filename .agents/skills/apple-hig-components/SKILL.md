---
name: apple-hig-components
description: Design, build, and audit UI buttons and action controls following the Apple Human Interface Guidelines (HIG) and modular HIG Components architecture. Use when the user asks to create, style, review, or refactor buttons, action bars, CTAs, or interactive controls with Apple HIG aesthetics, Liquid Glass materials, or Apple component standards across web, iOS, iPadOS, macOS, visionOS, or TedCraft / Edulis interfaces.
---
# Apple HIG Buttons and Modular Component Architecture

Design and implement intuitive, high-craft buttons modeled on the official Apple Human Interface Guidelines (Buttons and Components), combining Apple's spatial ergonomics, hierarchy rules, role semantics, and Liquid Glass materials with web and native implementation standards.

## When to Use

- Designing, coding, or reviewing button components, CTA groups, dialog action bars, toolbars, or inline controls modeled on Apple's Human Interface Guidelines.
- Applying Apple button hierarchy rules (style over size, role semantics, capsule vs. rounded-rectangle geometry, and press/loading states) to web (CSS/Tailwind/React) or native Apple platforms.
- Extending or scaffolding modular HIG component documentation (`.md` specs) mapped to Apple's 8 component categories (`Content`, `Layout and organization`, `Menus and actions`, `Navigation and search`, `Presentation`, `Selection and input`, `Status`, `System experiences`).

## Core Principles (The 3 Button Attributes)

Every button combines three attributes to communicate its function instantaneously:

1. **Style**: Visual hierarchy defined by fill prominence (Prominent, Bordered/Tinted, Borderless/Plain, or Liquid Glass material), shape (Circular, Capsule, or Rounded Rectangle), and standard size scale.
2. **Content**: A crisp verb-led text label, a recognizable symbol/icon, or both.
3. **Role**: Semantic meaning (`Normal`, `Primary`, `Cancel`, `Destructive`) that governs keyboard shortcuts, placement, and color treatment.

## Steps

### 1. Enforce Ergonomic Sizing, Hit Regions, and Spacing

- **Minimum Hit Target**: Guarantee an interactive hit region of at least **`44x44 pt` (`44x44 px` on web)** for all buttons across iOS, iPadOS, macOS, watchOS, and web. For spatial/visionOS targets, enforce at least **`60x60 pt`** with button centers at least `60 pt` apart and `4 pt` outer padding so hover states never collide.
- **Standard Height Scale**: Use standard heights rather than arbitrary vertical resizing:
  - `Mini`: `28 pt` (Circular icon-only; never place in stacks or rows)
  - `Small`: `32 pt` (Compact secondary controls; avoid in primary stacks or rows)
  - `Regular`: `44 pt` (Default across views, dialogs, and toolbars)
  - `Large`: `52 pt` (Prominent hero actions and full-width mobile CTAs)
  - `Extra Large`: `64 pt` (Spatial circular actions)
- **Image/Icon Padding**: Include at least `10 px` (`10 pt`) of internal padding between an icon's visual bounds and the button's outer edges so off-center taps and clicks register reliably.

### 2. Establish Visual Hierarchy Using Style, Never Size

- **Equal Sizing in Action Groups**: When presenting two or more sibling buttons as a coherent set of choices (such as `Cancel` and `Save`, or a horizontal/vertical button group), give every button in the set the **exact same height and size scale**. Never mix a large button and a small button side by side to show importance.
- **Style Prominence**: Differentiate the preferred action using a **prominent filled style** (accent background fill with high-contrast label) and secondary options using **bordered, tinted, or plain styles**.
- **Cap Prominent Buttons**: Limit prominent accent-filled buttons to **1 or 2 per view**. Too many filled accent buttons create visual noise and increase decision latency.
- **Choose Shape by Layout and Content**:
  - **Icon-only button**: Use a **Circular** shape (`border-radius: 9999px`, `1:1` aspect ratio), or a view-attached **Square button** for table/list row manipulation (`+` / `-`).
  - **Standalone button or horizontal row of text buttons**: Prefer a **Capsule** shape (`border-radius: 9999px`).
  - **Vertical stack of text-labeled buttons**: Prefer a **Rounded Rectangle** (`border-radius: 10px` to `12px`) and lock all buttons in the stack to an identical height.

### 3. Assign Semantic Roles and Guard Destructive Actions

Map every button to one of four system roles:

- **`Primary`**: The default, most likely action in a view or sheet. Styled with the primary accent fill and bound to the `Return` / `Enter` key.
- **`Normal`**: Standard secondary or contextual actions with neutral/tinted styling.
- **`Cancel`**: Dismisses the current modal, sheet, or flow without mutating state. Bound to `Escape` and positioned on the leading/left side of confirmation bars.
- **`Destructive`**: Performs irreversible deletion or data loss. Styled with semantic red (`#FF3B30` light / `#FF453A` dark, or tinted red background with red text until hovered/confirmed).
- **Destructive Safety Rule**: **Never assign the `Primary` role (or default `Return` key activation) to a `Destructive` button**, even when deletion is the primary purpose of an alert or confirmation dialog. Always require deliberate selection to prevent accidental data loss.

### 4. Format Labels, Icons, and Asynchronous States

- **Verb-Led Title Case Labels**: Write concise 1 to 3 word labels starting with an active verb in Title Case (for example, `Add to Cart`, `Create Playlist`, `Promote to Main`).
- **Trailing Ellipsis Rule (`...`)**: Append an ellipsis (for example, `Edit...`, `Export Baseline...`) **only** when activating the button opens another window, modal, or view requiring further input before the action executes. Never add an ellipsis to an immediate action.
- **Six Mandatory Interaction States**: Every button implementation must define visual feedback for:
  1. `Idle` (resting surface and border contrast)
  2. `Hover` (subtle luminance lift or surface tint; no custom hover override on visionOS)
  3. `Pressed / Active` (mandatory immediate scale `0.97` to `0.98` or darkening so the control never feels dead)
  4. `Focused` (high-visibility keyboard focus ring with `2 px` offset)
  5. `Selected / Toggled` (reserved high-contrast fill for toggle buttons; never mimic this style on idle buttons)
  6. `Disabled / Unavailable` (reduced opacity `0.4` to `0.5`, pointer events disabled, cursor default)
- **Inline Activity Indicator for Delayed Actions**: When an action takes noticeable time to complete, replace the leading icon with a spinning activity indicator inside the button and update the verb to its progressive participle with an ellipsis (for example, `Checkout` becomes `Checking out...`) while locking out duplicate clicks.

### 5. Apply Material, Contrast, and TedCraft / Edulis Brand Adaptation

- **Liquid Glass and Translucent Surfaces**:
  - Over rich or colorful backgrounds, enclose buttons in a translucent material shape (`backdrop-filter: blur(20px) saturate(180%)`) or monochromatic high-contrast fill so labels never blend into underlying content.
  - On glass windows, use a thin translucent material (`rgba(255, 255, 255, 0.14)`) for inline buttons; for floating spatial bars or corner toolbars, use full Liquid Glass specular borders and backdrop blur.
- **TedCraft / Edulis UI Profile**: When building or auditing **TedCraft / Edulis** interfaces:
  - Use Champagne Gold `#d4a853` (`#0c0c0e` ink) in Dark Obsidian mode and Deep Bronze-Gold `#8c6218` (`#fdfbf7` ink) in Warm Ivory light mode for `Primary` prominent button fills (`>= 4.5:1` WCAG contrast).
  - Use zero emojis anywhere in button labels or UI chrome.
  - Use **Google Fonts Icons (Material Symbols)** on web in place of SF Symbols, scaled proportionally with text and aligned to the optical center.

### 6. Modular Expansion Across Apple HIG Components

When expanding this skill repository with additional component `.md` files emulating Apple's HIG Components catalog, place each component specification under `references/` following the taxonomy in `references/blueprint.md`:

- `references/03-menus-and-actions/buttons.md`: Complete token tables, CSS/React implementation recipes, and platform matrix for Buttons.
- `references/blueprint.md`: Master index and template structure for authoring sibling `.md` specs across all 8 Apple HIG component families.

## Gotchas

- **Never use size to rank sibling options**: Making the "Confirm" button taller or wider than the "Cancel" button beside it breaks visual coherence; keep dimensions identical and vary only the button style (`Prominent` vs. `Bordered`).
- **Never omit a press state on custom buttons**: A button without an immediate `:active` / pressed visual response makes users think the interface froze or ignored their tap.
- **Never place view-only square or help buttons inside window toolbars**: Keep square gradient buttons (`+`/`-`) attached to their target table/view, and place circular `?` help buttons in the lower corner of a dialog or settings pane (maximum one per window).
- **Never let Dynamic Type truncate button labels**: Allow horizontal button pairs to stack vertically at accessibility font sizes rather than clipping text with ellipses.
