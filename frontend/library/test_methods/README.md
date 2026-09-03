# Page Specification: Library → Test Methods

> **Status:** Active / Finalized Specification  
> **Section:** Library → Test Methods (`frontend/library/test_methods`)  
> **Audience:** Sensory Lab Staff  
> **Traceability:** Implements Decisions D7, D11 from `docs/PROGRAM.md` and Test Methods Decision Records (Q1–Q9).

---

## 1. Overview & Purpose

The **Test Methods** page serves as the central methodology repository and template catalog for sensory testing in the Sensory Lab.

It enables sensory lab staff to:
1. **Catalog & Standardize:** Register standardized sensory testing methods (e.g., Triangle Test, QDA, 9-Point Hedonic) with clear procedures, theoretical assumptions, and operational requirements.
2. **Configure Presets:** Define specific, reusable **Presets** (configuration profiles) under each test method (e.g., *Standard 30-Panelist Difference*, *High-Power 60-Panelist Similarity*).
3. **Instantiate into Lab Workflow:** Directly initialize live sensory tests in the **Lab** execution workflow using a selected preset, automatically populating test setup parameters and preparation checklists.
4. **Bridge to Analytical Pipelines:** Supply structured methodology metadata and expected output metrics to the **Analyze** module (e.g., binomial/Thurstonian $d'$ for discrimination, ANOVA for descriptive profiles).

---

## 2. Domain Entities & Data Schema

### 2.1 Test Method (Parent Entity)

The overarching sensory methodology family.

| Field | Type | Description |
|---|---|---|
| `id` | `UUID / String` | Unique identifier for the test method. |
| `name` | `String` | Human-readable name (e.g., *"Triangle Test"*, *"Quantitative Descriptive Analysis (QDA)"*, *"9-Point Hedonic Acceptance"*). |
| `category` | `Enum` | Primary classification: `discrimination`, `descriptive`, or `hedonic`. |
| `description` | `String` | Overview of the method's purpose and general applicability. |
| `procedure` | `List[String] / Text` | Ordered, sequential steps describing how the evaluation is executed. |
| `assumptions` | `List[String] / Text` | Theoretical and statistical foundations (e.g., guessing probability $p_0=1/3$, attribute independence, consumer sample neutrality). |
| `derived_from_id` | `UUID / String (Optional)` | Lineage reference to the source Test Method if created via duplication. |
| `status` | `Enum` | Lifecycle status: `draft`, `active`, or `archived`. |
| `created_at` / `updated_at` | `Timestamp` | Audit timestamps. |

### 2.2 Preset (Child Entity)

A concrete, runnable configuration profile belonging to a Test Method.

| Field | Type | Description |
|---|---|---|
| `id` | `UUID / String` | Unique identifier for the preset. |
| `test_method_id` | `UUID / String` | Scalar foreign reference to parent Test Method. |
| `name` | `String` | Preset name (e.g., *"Standard 30-Panelist Difference"*, *"Trained Panel 12-Judge Profile"*). |
| `description` | `String (Optional)` | Specific context or use case for this preset. |
| `prerequisites` | `Object / JSON` | Structured operational and design conditions (see Section 2.3). |
| `output_schema` | `Object / JSON` | Expected statistical outputs and metrics produced by this method/preset (see Section 2.4). |
| `is_default` | `Boolean` | Flag indicating the primary default preset for the method. |
| `status` | `Enum` | Lifecycle status: `draft`, `active`, or `archived`. |
| `usage_count` | `Integer` | Number of live Lab test sessions referencing this preset. |

### 2.3 Structured Prerequisites Taxonomy

Prerequisites are categorized into 3 structured groups to facilitate direct handoff into Lab execution:

1. **Input Parameters (Form Prefills for Lab):**
   - Recommended panelist count (e.g., $N = 30$).
   - Sample presentation format (e.g., 3-digit blind code, balanced randomized block).
   - Samples per panelist / replicates per session.
2. **Instructional & Environmental Conditions (Lab Setup Checklist):**
   - Booth lighting / environment (e.g., red masking light, sensory booth temperature $20^\circ\text{C} \pm 2^\circ\text{C}$).
   - Palate cleansing protocol (e.g., filtered water + unsalted cracker, 60-second forced rest).
   - Sample serving volume and container specs (e.g., 30ml in coded odorless cups).
3. **Panelist Eligibility Requirements:**
   - Panel qualification level (e.g., screened for sensory acuity, trained descriptive panelist, naive consumer).
   - Pre-test restrictions (e.g., no eating/caffeine 1 hour prior to session).

### 2.4 Output Metrics & Analysis Schemas

Each method category specifies the statistical results generated in Lab and evaluated in Analyze:

| Category | Typical Method | Result Schema & Analysis Outputs |
|---|---|---|
| **Discrimination** | Triangle, Duo-Trio, 2-AFC | - Number of panelists ($n$), correct responses ($x$), alpha significance level ($\alpha$).<br>- Test decision: Significant Difference = `TRUE` / `FALSE`.<br>- If `TRUE`: p-value, estimated Thurstonian effect size ($d'$).<br>- If `FALSE`: Statistical power, $\beta$-risk, upper bound on proportion of discriminators ($p_d$). |
| **Descriptive** | QDA, Spectrum, Flash Profile | - Attribute scores across samples, panelists, and replicates.<br>- 2-Way / 3-Way ANOVA ($F$-values and $p$-values for Sample, Panelist, Replicate, and Sample $\times$ Panelist interaction).<br>- Mean attribute scores for radar/spider profiles and PCA loadings. |
| **Hedonic** | 9-Point Hedonic, JAR, CATA | - Overall liking distributions, mean liking, standard deviation.<br>- ANOVA / Tukey HSD pairwise sample comparison.<br>- Optional Just-About-Right (JAR) penalty analysis and CATA frequency counts. |

---

## 3. Lifecycle, Immutability & Integrity Rules

```
 ┌─────────────┐       Instantiated in Lab Test       ┌─────────────┐
 │    DRAFT    │ ───────────────────────────────────> │   ACTIVE    │
 │ (Never Used)│                                      │  (In Use)   │
 └──────┬──────┘                                      └──────┬──────┘
        │                                                    │
        │ Delete                                             │ Archive
        ▼                                                    ▼
 ┌─────────────┐                                      ┌─────────────┐
 │   DELETED   │                                      │  ARCHIVED   │
 └─────────────┘                                      └─────────────┘
```

1. **Draft / Unused State:**
   - Methods and Presets with `usage_count == 0` can be freely edited.
   - Hard-deletion is allowed for drafts to cleanly discard mistakes or typos.
2. **Active / In-Use State:**
   - Once a Preset is used in $\ge 1$ Lab test session, that Preset becomes **locked/immutable** to safeguard historical reproducibility.
   - Core parent Method classification (`category`) is locked once any child preset is active.
   - **Adding New Presets:** Sensory staff can add new presets to an existing active Method at any time.
   - **Hard Delete Forbidden:** Active methods and presets cannot be deleted; they can only be **Archived**.
3. **Archival State:**
   - Archived presets/methods are hidden from default Lab creation selection.
   - Existing historical Lab tests referencing archived presets remain fully intact and readable.
   - Can be unarchived or duplicated.
4. **Duplication & Lineage:**
   - Duplicating a Test Method creates a fresh deep-copy in `draft` state with new draft presets.
   - Sets `derived_from_id` to the source method ID for auditability.
   - Parent and child maintain completely decoupled lifecycles (no sync).

---

## 4. Cross-Domain Touchpoints

- **Lab Service:**
  - Queries active Test Methods and Presets to populate the "Create Test / Experiment" dialog.
  - Receives preset parameters to pre-fill test creation forms and generate the technician setup checklist.
  - Validates that a Test Method has at least 1 active preset before allowing instantiation.
- **Analyze Service:**
  - Uses method category and preset output schema to automatically configure compatible statistical pipelines and visualization dashboards (e.g. binomial tables for discrimination, ANOVA models for descriptive).

---

## 5. UI / UX Specifications (`frontend/library/test_methods`)

### 5.1 Catalog View (Main Page)
- **Top Bar:** Search bar, Category filter chips (`All`, `Discrimination`, `Descriptive`, `Hedonic`), Status filter (`Active`, `Archived`, `All`), and **"+ New Test Method"** button.
- **Method Cards / Data Table:**
  - Method Name, Category badge, Preset count, Total Lab usages, Status badge.
  - Quick action menu: *View Details*, *Add Preset*, *Duplicate*, *Archive / Delete*.

### 5.2 Method Detail View
- **Header & Info Pane:**
  - Method Name, Category, Lineage tag (if derived from another method), Status.
  - Detailed Description, Standard Procedure steps, and Theoretical Assumptions.
- **Presets Section:**
  - Tabs or expandable cards for each Preset under this Method.
  - Highlights: Input parameters (sample/panelist defaults), Instructional conditions checklist, Panelist requirements.
  - Usage indicator: "Used in $X$ Lab tests (Locked)" or "Draft (Editable)".
- **Actions Bar:**
  - **"Create Test in Lab"** (primary action button — pre-selects this method and preset in Lab).
  - **"Add Preset"** (opens preset creation form).
  - **"Edit"** (enabled for draft methods/presets).
  - **"Duplicate Method"** (creates an editable draft copy).
  - **"Archive" / "Delete"** (context-aware based on usage status).

### 5.3 Creation & Edit Flow
- **Step 1 — Test Method Definition:** Staff defines method name, category, description, execution procedure, and theoretical assumptions.
- **Step 2 — Presets Management:** Staff can immediately add one or more initial presets or return to add presets later. (UI alerts the user that at least one preset is required before the method can be instantiated in Lab).

---

## 6. Decision Record Summary

| # | Question / Topic | Final Decision | Rationale |
|---|---|---|---|
| **D-TM1** | **Referencing Unit** | Lab tests instantiate a specific **Preset** under a **Test Method**. | Allows standardized methods (e.g. Triangle) to support different standard panel sizes and power levels without redefining the core methodology. |
| **D-TM2** | **Edit vs. Locking** | Used presets and core method classification are locked against edits. | Preserves historical integrity of sensory test records and analysis runs. |
| **D-TM3** | **Preset Expansion** | Users can add new presets to an active method without locking the entire method container. | Provides operational flexibility without breaking historical test runs. |
| **D-TM4** | **Prerequisites Structure** | Classified into Input Requirements, Instructional Conditions, and Panelist Requirements. | Directly feeds Lab form parameters and technician operational checklists. |
| **D-TM5** | **Assumptions Role** | Theoretical documentation of scientific and statistical foundations. | Informs test selection and guides analytical interpretations in Analyze. |
| **D-TM6** | **Output Metrics Mapping** | Presets define structured output schemas aligned with statistical methods (Discrimination, Descriptive, Hedonic). | Connects test execution directly to automated statistical analysis. |
| **D-TM7** | **Duplication Semantics** | Deep copy with `derived_from_id` lineage tracking; completely decoupled lifecycles. | Simple, predictable behavior without complex synchronization rules. |
| **D-TM8** | **Lifecycle & Deletion** | Draft/never-used methods can be hard-deleted; used methods can only be archived. | Clean UX for correcting typos while preventing orphan/corrupted historical tests. |
| **D-TM9** | **Built-in Templates** | Clean slate start; lab staff register custom lab methods. (Standard templates can be seeded later). | Keeps initial implementation lightweight and tailored to lab needs. |
