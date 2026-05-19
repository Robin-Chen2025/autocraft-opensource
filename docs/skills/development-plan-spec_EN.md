# Development Plan Generation Specification

> General development plan generation guidance document, defining the core methodology for how development plans should be generated

**Version:** v2.0  
**Date:** 2026-05-19  
**Change Log:** Removed "plan breakdown" task, work plan lists now clearly define all tasks

---

## 1. Specification Hierarchy and Positioning

### 1.1 Development Plan Document Architecture

AutoCraft development plans use a two-layer document architecture:

| Level | Document Type | Description | Example |
|-------|--------------|-------------|---------|
| **Overview Level** | Project Overview Doc | Batch order, module dependencies, feature overview | Development-Plan-Overview.md |
| **Plan Level** | Work Plan List | Task structure summary for a single work plan | WP-M03-BE-DEV-001.md |

**Document Relationships**:
```
Design Layer (Feature Design Documents)
    ↓ Input
Development Plan Overview (Project Level)
    ↓ Guide
Work Plan List (Plan Level)
    ↓ Direct Execution
Program Code + Test Code (Deliverables)
```

### 1.2 Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Pre-generated List Ensures Integrity** | Unified numbering, consistent naming, clear task count |
| **No Breakdown Task** | Lists clearly define all tasks, execute directly |
| **AI as Intelligent Developer** | Input design document text, not predefined steps |
| **pytest Loop Handles Uncertainty** | Fail→Fix→Retry, iterative fixing is unpredictable |

---

## 2. Task Structure Definition

### 2.1 Task Numbering Rules (No Breakdown Task)

| Plan Type | Task Number Range | Task Structure |
|-----------|------------------|----------------|
| **INFRA** | 001~006 | Skeleton→Environment→Database→Init→Startup→Report |
| **BE-DEV** | 001~N-1 | Feature loop (each feature: test code→program code) → Report |
| **BE-L2** | 001~N-1 | Environment prep → Scenario loop → Report |
| **FE-DEV** | 001~N-1 | Feature loop (each feature: test code→program code) → Report |
| **FE-L2** | 001~N-1 | Environment prep → Scenario loop → Report |
| **L3-E2E** | 001~N-1 | Environment prep → Flow loop (two-layer test) → Report |

### 2.2 Task Structure Examples

**BE-DEV Plan**:
```
001: F-001-Test Code Generation → BUILD
002: F-001-Program Code + pytest → BUILD
003: F-002-Test Code Generation → BUILD
004: F-002-Program Code + pytest → BUILD
...
N-1: BE-DEV Report → DOC
```

**BE-L2 Plan**:
```
001: Test Environment Prep → BUILD
002: Scenario 1 Test → BUILD
003: Scenario 2 Test → BUILD
...
N-1: BE-L2 Report → DOC
```

**INFRA Plan**:
```
001: Project Skeleton Setup → BUILD
002: Development Environment Config → BUILD
003: Database Code Generation → BUILD
004: Database Initialization → EXECUTE
005: Startup Script Creation → BUILD
006: Acceptance Report → DOC
```

---

## 3. Consistency Assurance Mechanism

### 3.1 Numbering Constraint Mechanism

Work plan lists provide numbering constraints that must be followed during execution:

```markdown
## Task Number Constraints

**BE-DEV/FE-DEV Plans**:
| Task Number Range | Task Type | Description |
|-------------------|-----------|-------------|
| 001~N-2 | BUILD | Feature loop (2 tasks per feature) |
| N-1 | DOC | Development report |

**BE-L2/FE-L2 Plans**:
| Task Number Range | Task Type | Description |
|-------------------|-----------|-------------|
| 001 | BUILD | Test environment prep |
| 002~N-2 | BUILD | Scenario loop |
| N-1 | DOC | Test report |

**L3-E2E Plans**:
| Task Number Range | Task Type | Description |
|-------------------|-----------|-------------|
| 001 | BUILD | Test environment prep |
| 002~N-2 | BUILD | Flow loop (two-layer test) |
| N-1 | DOC | E2E report |
```

### 3.2 Version Consistency Check

Work plan lists annotate design document versions, checked at startup:

```markdown
## Design Document Versions

| Document Type | Current Version | Document Path |
|--------------|-----------------|---------------|
| API Design | v1.2 | docs/design/API-Design-v1.2.md |
| Database Design | v1.0 | docs/design/Database-Design-v1.0.md |

**Version Check Rules**:
At startup, read design document version numbers, compare with annotated versions in the list, pause with error if inconsistent.
```

---

## 4. Generation Flow

### 4.1 Planning Phase Generation Flow

```
Development Plan Planning Phase:
    │
    ├─ Batch 1: INFRA + First batch of modules
    │     ├─ Generate development plan overview
    │     ├─ Generate work plan lists
    │     └─ Review → Git commit
    │
    ├─ Batch 2: Second batch of modules
    │     ├─ Generate work plan lists
    │     └─ Review → Git commit
    │
    └─ Complete: All lists
```

### 4.2 Execution Phase Flow

```
Execution Phase:
    │
    ├─ Read work plan list
    ├─ Version consistency check
    │
    ├─ Loop execute tasks (001~N-1)
    │     ├─ Read design document text
    │     ├─ AI autonomous implementation decision
    │     ├─ pytest/vitest loop iteration
    │     └─ Verification sub-agent business validation
    │
    └─ Complete: Update plan status
```

---

## 5. Storage Structure

```
docs/development-plans/
    │
    ├─ Development-Plan-Overview.md
    │
    ├─ M-01/
    │   ├─ WP-M01-BE-DEV-001.md
    │   ├─ WP-M01-BE-L2-001.md
    │   ├─ WP-M01-FE-DEV-001.md
    │   └─ WP-M01-FE-L2-001.md
    │
    └─ L3-E2E/
        ├─ WP-L3-E2E-001.md
        └─ WP-L3-E2E-002.md
```

---

## 6. Version History

| Version | Date | Change Description |
|---------|------|-------------------|
| v2.0 | 2026-05-19 | **Removed "plan breakdown" task**: Lists clearly define all tasks, no breakdown step needed |
| v1.2 | 2026-04-16 | Added integrity review |

---

**Document Version:** v2.0  
**Last Updated:** 2026-05-19