# ISO 9001 Audit App — UI Refactor Design Spec

**Date:** 2025-06-09  
**Status:** Ready for Implementation  
**Author:** Design Brainstorming Process  

---

## 1. Executive Summary

Refactor the audit app UI from **emoji-heavy, templated dashboard-first structure** to a **professional, workflow-first interface** that matches real audit workflows.

**Key Changes:**
- Remove all emoji navigation (📊 📝 ⚙️ 💾)
- Reverse module order: ENTRADA (data entry) → SEGUIMIENTO (tracking) → ANÁLISIS (reporting)
- Eliminate symmetric card grids; use intentional, harmonious layout
- Introduce semantic color system (green = conforme, red = no-conforme, yellow = mejora)
- Design for 1:30pm live meeting context (speed, clarity, no distractions)

**Target User:** Internal auditors at Casa de la Moneda (CMV)  
**Primary Task:** Register audit findings in real-time during 1:30pm team meeting  
**Feel:** Professional but accessible, confiable pero clara (trustworthy but clear)

---

## 2. User Context

**Who:** Internal auditors (líder auditor + equipo de auditores internos) at CMV  
**When:** Monday-Friday, 7:30am-3:30pm; peak usage at 1:30pm team meeting  
**What:** Register audit findings → Track corrective actions → Share results with team  
**Why:** ISO 9001:2015 internal audit compliance; formal institutional context  

**The 1:30pm Workflow:**
1. Auditors sit in meeting
2. Open app → ENTRADA module
3. Register findings from audits conducted that morning
4. Supervisor reviews on projector
5. After meeting → Dashboard for team communication

**Stress Factor:** Formal institutional setting, real-time data accuracy matters, no time for confusion.

---

## 3. Architecture: Navigation Structure

### 3.1 Top Navigation (Replace Sidebar + Emoji)

```
┌─────────────────────────────────────────────────────┐
│ Logo + "CMV - Auditoría Interna del SGC"            │
│                                                     │
│ ⬛ ENTRADA  ⬜ SEGUIMIENTO  ⬜ ANÁLISIS              │
│ (dark square = active module)                       │
│                                                     │
│ User Menu + Settings (right)                        │
└─────────────────────────────────────────────────────┘
```

**Design Rationale:**
- ✗ Rejects: Sidebar with emoji navigation (📊 Dashboard, 📝 Matriz, ⚙️ SAC, 💾 Exportar)
- ✓ Accepts: Horizontal tabs showing sequential workflow
- Visual indicator (dark square) shows active module without text redundancy

### 3.2 Three Modules (Workflow Order)

| Module | Purpose | Primary Task | When Used |
|--------|---------|--------------|-----------|
| **ENTRADA** | Data Entry | Register new audit findings | 1:30pm in meeting |
| **SEGUIMIENTO** | Action Tracking | Update corrective action status, verify efficacy | Post-meeting, throughout week |
| **ANÁLISIS** | Reporting & Communication | View metrics, generate reports, share with team | After meeting, weekly reviews |

---

## 4. Module 1: ENTRADA (Data Entry)

### 4.1 Structure

**Two Sub-Views:**
1. **Formulario de Hallazgos** — Vertical form for new entry
2. **Lista de Hallazgos del Día** — Expandable cards showing registered findings

### 4.2 Formulario de Hallazgos

**Design Principle:** Vertical layout, validation in real-time, clear error states

**Fields (in order):**

| Field | Type | Validation | Required | Notes |
|-------|------|-----------|----------|-------|
| Proceso Auditado | Dropdown | Must match existing processes | Yes | Auto-complete from list |
| Fecha de Auditoría | Date picker | YYYY-MM-DD format | Yes | |
| Auditor Responsable | Dropdown | Must be team member | Yes | Auto-complete |
| Requisito ISO | Dropdown + Specific field | 4.0-10.3 range | Yes | Shows specific sub-req (7.1.4) |
| Tipo de Hallazgo | Radio button | Conforme / No Conforme / Mejora | Yes | |
| Cumplimiento | Radio button | Conforme / No Conforme | Yes | |
| Evidencia Objetiva | Text area | Min 50 chars if No Conforme | Conditional | Required if No Conforme |
| Observaciones | Text area | Min 0 chars | Optional | |

**Validation Logic:**
- If Cumplimiento = "No Conforme" → Evidencia is REQUIRED
- Real-time validation: Show ⚠️ icon next to unfilled required fields
- On submit: Validate all required fields before allowing save

**Success Feedback:**
```
✓ Hallazgo guardado exitosamente
ID: #2847 | Proceso: EV | Req: 7.1.4
```

### 4.3 Lista de Hallazgos del Día

**Design Principle:** Compact cards, color-coded by status, expandable for details

**Card Structure:**
```
┌──────────────────────────────────────────┐
│ #2847 | EV | Requisito 7.1.4 | NO CONF ✗ │
│ Auditor: Carlos López | 2025-06-09 14:23 │
│ [VER DETALLES ▼]                         │
└──────────────────────────────────────────┘
```

**Color System for Status:**
- ✓ **Green** (Conforme): #10B981
- ✗ **Red** (No Conforme): #EF4444
- ⚠ **Yellow** (Mejora): #F59E0B

**Filtering:**
- Dropdowns: Proceso, Auditor, Estatus
- Real-time filter (no button required)

---

## 5. Module 2: SEGUIMIENTO (Action Tracking)

### 5.1 Structure

**Two Sub-Views:**
1. **Lista de SAC/OM Abiertos** — Active actions grouped by state
2. **Registrar Nueva Acción** — Form to create corrective action

### 5.2 Lista Agrupada por Estado

**Grouping:**
1. ABIERTOS (3) — States: Abierto, En Progreso
2. CERRADOS (5) — State: Cerrado (collapsed by default)

**Card Layout:**
```
┌─────────────────────────────────────────────────┐
│ SAC-2847 | Proceso EV | Req 7.1.4               │
│ Tipo: Acción Correctiva                         │
│ Estado: Abierto | Eficacia: Pendiente verificar │
│ Responsable: Carlos López | Vencimiento: 2025-07│
│ Descripción: Falta documentación...             │
│ [EDITAR ESTATUS ▼]                              │
└─────────────────────────────────────────────────┘
```

**Color System for SAC Status:**
- 🔴 **Red** (Abierto/Crítico): #EF4444
- 🟡 **Yellow** (En Progreso): #F59E0B
- ⚪ **Gray** (Cerrado): #6B7280

### 5.3 Modal: Editar Estatus SAC

**Fields:**

| Field | Type | Logic |
|-------|------|-------|
| Estado del Plan | Radio | Abierto / En Progreso / Cerrado |
| Eficacia | Radio | Pendiente / Eficaz / No Eficaz |
| Comentarios | Text area | Min 20 chars (always required) |
| Fecha Cierre | Date picker | Optional; visible if Cerrado selected |

**Validation Logic:**
- If Estado = "Cerrado" AND Eficacia = "No Eficaz" → Warning: "Acción no resolvió hallazgo. Generar nueva SAC"
- If Estado = "Abierto" → Eficacia locked (cannot select Eficaz)
- Comentarios always required

**Success Feedback:**
```
✓ SAC actualizado exitosamente
Estado: Cerrado | Eficacia: Eficaz
```

### 5.4 Formulario: Nueva Acción

**Fields:**

| Field | Type | Required |
|-------|------|----------|
| Tipo de Acción | Radio | Acción Correctiva / Mejora |
| Proceso Responsable | Dropdown | Yes |
| Auditor Emisor | Dropdown | Yes |
| Requisito ISO | Dropdown | Yes |
| Código SAC/OM | Text | Yes (auto-generated format: SAC-XXXX) |
| Descripción / Plan | Text area | Yes (min 100 chars) |
| Fecha Vencimiento | Date picker | Yes |

---

## 6. Module 3: ANÁLISIS (Reporting)

### 6.1 Structure

**Single View with Multiple Sections (vertically stacked, harmonious grid):**

1. Header: Period selector + filters
2. Row 1: Conformidad Global + Hallazgos Registrados (2 equal cards)
3. Row 2: SAC/OM Status + Conformidad por Proceso (2 equal cards)
4. Row 3: Hallazgos por Requisito ISO (1 full-width card)
5. Row 4: Productividad del Equipo (1 full-width card)
6. Row 5: Tendencia (1 full-width card)
7. Footer: Export options

**Design Rationale:**
- Grid-based (2+2+1+1+1) creates visual harmony without forced symmetry
- Order reflects importance: metrics first, then analysis, then team data
- Intentional asymmetry through content, not through weird sizing

### 6.2 Key Metrics (Row 1)

**Card 1: Conformidad Global**
```
┌─────────────────────┐
│ CONFORMIDAD GLOBAL  │
│       85.2%         │
│     ↑ +2.1p         │
│  vs. semana ant.    │
│                     │
│  META: 90%          │
│  ██████░░ (85%)     │
└─────────────────────┘
```

**Semantic Styling:**
- Color bar: Green if ≥90%, Yellow if 70-89%, Red if <70%
- Arrow: ↑ (green) if improving, ↓ (red) if declining, → (gray) if flat

**Card 2: Hallazgos Registrados**
```
┌───────────────────────────┐
│ HALLAZGOS REGISTRADOS     │
│                           │
│ Conforme:      28  ✓      │
│ No Conforme:    5  ✗      │
│ Mejora:         9  ⚠      │
│                           │
│ Total: 42 hallazgos       │
└───────────────────────────┘
```

### 6.3 Status & Tracking (Row 2)

**Card 1: SAC/OM Estado**
```
┌──────────────────┐
│ SAC/OM ESTADO    │
│                  │
│ Abiertos: 3  🔴  │
│ Progreso: 5  🟡  │
│ Cerrados: 18 ✓   │
│                  │
│ Eficacia:        │
│ 16/18 (88.9%)    │
└──────────────────┘
```

**Card 2: Conformidad por Proceso**
- Horizontal bar chart
- One bar per process
- Green if ≥90%, Yellow if 70-89%, Red if <70%
- Reference line at 90% (META)

### 6.4 Analysis Section (Rows 3-5)

**Row 3: Hallazgos por Requisito ISO**
- Vertical stacked bar chart
- X-axis: ISO Requirements (5.0, 6.0, 7.0, etc.)
- Segments: Conforme (green), No Conforme (red), Mejora (yellow)
- Highlight highest: "Req 7.0 necesita atención"

**Row 4: Productividad del Equipo**
- Horizontal bars per auditor
- Left: Hallazgos count
- Right: Hours logged
- Show total at bottom

**Row 5: Tendencia**
- Line chart over 4 weeks
- Reference line at META (90%)
- Color: Green if improving, Red if declining
- Label: "Mejorando consistentemente" or "Requiere atención"

### 6.5 Filtering & Export

**Filters (Sticky at top):**
- Period: Date range picker
- Proceso: Multi-select dropdown
- Auditor: Multi-select dropdown
- Estatus: Multi-select (Conforme/No Conforme)

**Export Options:**
- PDF: One-page executive report (for presentation)
- Excel: Raw data for analysis
- Share: Temporary link (shareable URL)

---

## 7. Design System & Tokens

### 7.1 Color Palette

**Semantic Colors (ISO Audit Context):**

| Token | Hex | Usage | Rationale |
|-------|-----|-------|-----------|
| `--success` | #10B981 | Conforme, Eficaz, Cerrado | Green = compliant, safe |
| `--danger` | #EF4444 | No Conforme, Crítico, Abierto | Red = risk, action needed |
| `--warning` | #F59E0B | Mejora, En Progreso, Pendiente | Yellow = attention |
| `--primary` | #1F2937 | Text, headings, primary UI | Dark gray, professional |
| `--secondary` | #6B7280 | Secondary text, metadata | Medium gray |
| `--muted` | #9CA3AF | Disabled, placeholder, tertiary | Light gray |
| `--border` | #E5E7EB | Borders, dividers | Very light gray |
| `--surface` | #FFFFFF | Card backgrounds | White |
| `--surface-alt` | #F9FAFB | Secondary surfaces | Lightest gray |
| `--accent` | #3B82F6 | Links, focus states | Blue (from current design) |

**Color Usage Rules:**
- Never use pure black or white (use --primary, --surface)
- All borders use --border (never solid hex)
- Text hierarchy: --primary (default), --secondary (supporting), --muted (disabled/placeholder)
- Status uses semantic colors ONLY (green/red/yellow/gray)

### 7.2 Typography

**Typefaces:**
- **Display/Headings:** Poppins (via Google Fonts)
- **Body/UI:** Roboto (via Google Fonts)

**Hierarchy:**

| Level | Font | Size | Weight | Usage |
|-------|------|------|--------|-------|
| H1 | Poppins | 2.5rem | 700 | Page titles |
| H2 | Poppins | 1.875rem | 700 | Section headings |
| H3 | Poppins | 1.125rem | 600 | Subsection titles |
| Body | Roboto | 1rem | 400 | Default text |
| Caption | Roboto | 0.875rem | 400 | Metadata, timestamps |
| Mono | Roboto Mono | 0.875rem | 400 | IDs, codes, data |

**No emojis in any text.** Use icons or semantic color only.

### 7.3 Spacing

**Base unit:** 8px

**Spacing Scale:**
- xs: 4px (icon spacing)
- sm: 8px (inner padding)
- md: 16px (component spacing)
- lg: 24px (section spacing)
- xl: 32px (major section spacing)

**Card Padding:** 16px (md) on all sides  
**Grid Gap:** 16px (md) between cards  
**Form Field Spacing:** 16px (md) between fields vertically

### 7.4 Borders & Depth

**Border Approach:** Borders-only (no shadows), clean and technical

**Border Progression:**
- **Standard:** 1px solid rgba(229, 231, 235, 0.5) — soft separation
- **Emphasis:** 1px solid rgba(229, 231, 235, 1) — stronger separation
- **Focus:** 2px solid #3B82F6 — input focus ring

**Card Styling:**
- Border: 1px solid --border
- Border-radius: 8px
- Padding: 16px
- Background: --surface
- No box-shadow

### 7.5 Interactive States

**Buttons:**
- Default: Solid background --accent, white text
- Hover: Slightly darker --accent
- Active: 2px solid --accent (outline style)
- Focus: 2px solid --accent ring
- Disabled: Background --muted, text --secondary, opacity 50%

**Form Inputs:**
- Default: Border --border, background --surface
- Focus: Border --accent 2px, background --surface
- Error: Border --danger 1px, background white
- Disabled: Border --border, background --surface-alt, opacity 50%

**No rounded borders on small elements.** Rounded only on cards (8px) and large surfaces.

---

## 8. Component Library (Brief)

### 8.1 Forms
- Vertical layout (single column)
- Required field indicator: `*`
- Validation messages: Below field in --danger color
- Dropdowns with autocomplete
- Date pickers with visual calendar

### 8.2 Cards
- Border-only styling (no shadow)
- 8px border-radius
- 16px padding
- Consistent --border color

### 8.3 Metrics Cards
- Large number (--primary, bold)
- Label below (--secondary, smaller)
- Optional trend indicator (↑↓→)
- Optional status icon (✓ ✗ ⚠)

### 8.4 Expandable Cards (SAC/OM, Hallazgos)
- Summary line visible by default
- Click to expand inline (no modal)
- Chevron icon indicates expandable state

### 8.5 Data Visualization
- Horizontal bar charts (processes)
- Vertical stacked bar charts (requisites)
- Line charts (trends)
- Color-coded by semantic meaning
- No decorative gradients or effects

---

## 9. Data Flow & Interactions

### 9.1 ENTRADA Workflow

```
User Opens ENTRADA Module
         ↓
Shows Form + List of Today's Findings
         ↓
User Fills Form (vertical, field by field)
         ↓
Real-time Validation (if No Conforme → Evidencia required)
         ↓
User Clicks "GUARDAR EN GOOGLE SHEETS"
         ↓
API Call: Update Google Sheets (ttl=0, always fresh)
         ↓
Success: Show ✓ feedback with ID
         ↓
Add to List (cards refresh, new entry visible)
         ↓
Form Clears (ready for next entry)
```

### 9.2 SEGUIMIENTO Workflow

```
User Opens SEGUIMIENTO Module
         ↓
Shows SAC/OM grouped by state (Abiertos first)
         ↓
User Clicks "EDITAR ESTATUS" on one SAC
         ↓
Inline Expansion (or modal) with edit form
         ↓
User Updates: Estado, Eficacia, Comentarios, Fecha
         ↓
Validation:
  - Cerrado + No Eficaz → Warning
  - Abierto → Eficacia locked
  - Comentarios required
         ↓
User Clicks "GUARDAR CAMBIOS"
         ↓
API Call: Update SAC in Google Sheets
         ↓
Success: List updates, card changes color/state
```

### 9.3 ANÁLISIS Workflow

```
User Opens ANÁLISIS Module
         ↓
Shows: Metrics + Filters
         ↓
User Selects Period, Process, Auditor
         ↓
All Charts Update (real-time, no button click needed)
         ↓
User Reviews Metrics + Gráficos
         ↓
User Clicks "DESCARGAR PDF" or "COMPARTIR"
         ↓
PDF Generated (executive summary)
         ↓
Or: Shareable link created (24h expiry)
```

---

## 10. Loading & Error States

### 10.1 Loading States

**Form Submission:**
- Button shows spinner while saving: "GUARDANDO..."
- Field focus disabled until complete
- Timeout after 5s: Show error message

**Data Visualization:**
- Skeleton screens while fetching (card-shaped placeholders)
- Minimal animation (no bounce/spring)

### 10.2 Empty States

**No hallazgos today:**
```
Sin hallazgos registrados
Comienza a completar el formulario arriba
```

**No SAC/OM abiertos:**
```
No hay acciones abiertas
Todas las SAC/OM están cerradas ✓
```

### 10.3 Error States

**Validation Error:**
```
⚠️ Campo requerido: Evidencia Objetiva
(Requerido para No Conforme)
```

**Network Error:**
```
Error al guardar: Verifica tu conexión a internet
[REINTENTAR]
```

**Google Sheets Error:**
```
Error al sincronizar con Google Sheets
Contacta al administrador si persiste
```

---

## 11. Accessibility & Responsive

### 11.1 Keyboard Navigation
- Tab order follows visual flow
- Enter to submit forms
- Escape to close expandables
- All buttons and interactive elements focusable

### 11.2 Mobile / Responsive
- Stack cards vertically on mobile
- Forms remain single-column
- Dropdowns full-width on mobile
- Charts adapt (horizontal bars compress, line charts still readable)
- Not mobile-first; desktop is primary (used on projector in meetings)

### 11.3 Dark Mode (Future)
- Token adjustments: darker backgrounds, lighter text
- Shadows become more visible (borders-only approach still holds)
- Semantic colors slightly desaturated on dark backgrounds

---

## 12. Future Features (Backlog)

### 12.1 Control de Horas de Auditoría del Equipo

**Purpose:** Track audit hours by auditor role (líder auditor, auditor interno, etc.)

**Scope (To be designed):**
- Time logging widget (hours per auditor per day)
- Weekly/monthly summary
- Role-based hour distribution
- Export for payroll/reporting

**Notes:** This feature requires separate design spec (not included in this refactor)

### 12.2 Other Future Enhancements
- Real-time collaboration (multiple auditors entering data simultaneously)
- Export to PDF report (executive summary for board)
- Mobile app (iOS/Android)
- AI-powered hallazgo categorization

---

## 13. Implementation Notes

### 13.1 No Breaking Changes
- Keep Google Sheets backend unchanged
- Keep validation logic unchanged
- Only UI layer refactoring

### 13.2 Gradual Rollout (Optional)
1. Deploy ENTRADA first (most used)
2. Test with auditors at 1:30pm meeting
3. Deploy SEGUIMIENTO
4. Deploy ANÁLISIS last

### 13.3 Testing Checklist
- [ ] Form validation works for all fields
- [ ] Google Sheets sync completes in <2s
- [ ] Colors display correctly (no color blindness issues)
- [ ] Charts render with sample data
- [ ] Filters update in real-time
- [ ] PDF export produces readable document
- [ ] Responsive on mobile (secondary use case)

---

## 14. Design Principles Applied

✓ **No AI-generated patterns** — No emojis, no generic colors, no symmetry-for-symmetry  
✓ **Professional + Accessible** — Formal but clear for new auditors  
✓ **Workflow-first** — Entrada → Seguimiento → Análisis matches real tasks  
✓ **Semantic color** — Green/red/yellow means something in ISO audit context  
✓ **Harmonious not chaotic** — Grid-based layout, intentional (not weird) asymmetry  
✓ **Data-centric** — Charts communicate, not decorate  
✓ **Real-time feedback** — Every action shows immediate response  
✓ **No distractions** — Meeting-ready (1:30pm context matters)

---

**End of Spec**

