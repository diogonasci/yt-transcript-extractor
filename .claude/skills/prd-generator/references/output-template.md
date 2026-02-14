# Output Template: PRD (Implementation-Ready)

Use this exact structure when generating the final document. Every section must be present unless Rule 8 applies (simple demands may omit inapplicable sections). Remove all `<!-- ... -->` comments from the final output.

---

```markdown
# PRD: [Descriptive title of the demand]

## 1. Objective

<!-- 1-2 paragraphs: what will be implemented and why. Extract from the Executive Summary of the As-Is / To-Be. Be concise — this orients the reader, it doesn't replace the specification. -->

## 2. Technical Context

### 2.1 Relevant Architecture
<!-- High-level view of the affected part of the system: how components relate today. This gives the implementation agent the minimum context to understand where it's working. Use a brief description or a simple diagram (ASCII or mermaid). Don't over-document — just enough to orient. -->

### 2.2 Project Conventions
<!-- Patterns identified in the code that the implementation agent must follow. Examples: -->
<!-- - Naming: functions use camelCase, tables use snake_case -->
<!-- - Error handling: all public functions return a status object -->
<!-- - Logging: use LogError() with error code as first parameter -->
<!-- Only include conventions relevant to the alterations in this PRD. -->

### 2.3 Premises and Decisions
<!-- Inherited from the As-Is / To-Be + any additional decisions made during PRD elaboration. -->
<!-- Each entry should state the decision and its justification. -->

## 3. Specification of Alterations

<!-- This is the core section. Each alteration is an independent, self-contained subsection. -->
<!-- The implementation agent should be able to execute each alteration by reading only its subsection + the dependencies it references. -->

### 3.X [Description of the Alteration]

**Type:** Creation | Modification | Removal

**File:** `full/path/to/file`

**Component:** Function/method/table/structure name

**Context:** <!-- Why this alteration is necessary. Reference to the To-Be behavior. -->

**Current State:**
<!-- For modifications and removals: the relevant excerpt of actual current code. -->
<!-- Use the project's language for syntax highlighting. -->
```language
[current code]
```

**Change Specification:**
<!-- Precise description of what must change. Detailed enough for mechanical execution. -->
<!-- For creations: complete specification of the new component -->
<!-- For modifications: exactly what changes, with pseudocode or expected code when clarity requires it -->
<!-- For removals: what to remove and how to handle existing references -->

**Expected Code:**
<!-- When applicable: the final expected code or detailed pseudocode. -->
<!-- State clearly whether this is FINAL CODE (copy as-is) or PSEUDOCODE (translate to project style). -->
```language
[expected code or pseudocode]
```

**Dependencies:**
<!-- Other alterations in this PRD that must exist for this one to work. -->
<!-- Reference by section number: "Depends on 3.2" -->
<!-- If none: "None" -->

**Impact:**
<!-- Other points in the code affected by this alteration that the agent must verify/adjust. -->
<!-- List specific files and functions. If none: "None" -->

---

<!-- Repeat 3.X for each required alteration -->

## 4. Data Structures

<!-- Only include if the demand involves database or schema changes. -->

### 4.X [Structure Name]

**Type:** New table | Table alteration | New model | Model alteration

**Specification:**

<!-- For tables: complete DDL or ALTER DDL -->
```sql
[DDL or ALTER statement]
```

<!-- For models/schemas: complete field definition -->

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| ... | ... | ... | ... | ... |

**Data Migration:**
<!-- If existing data needs migration/transformation, specify how. -->
<!-- If not applicable: omit this subsection. -->

---

## 5. Interface Contracts

<!-- Only include if the demand involves new or modified APIs, public functions, events, or webhooks. -->

### 5.X [Contract Name]

**Type:** API endpoint | Public function | Event/Webhook | Message

<!-- For APIs: -->
**Method:** GET | POST | PUT | DELETE
**Path:** `/path/to/endpoint`

**Request:**
```json
{
  "field": "type — description"
}
```

**Response (success):**
```json
{
  "field": "type — description"
}
```

**Response (error):**
```json
{
  "field": "type — description"
}
```

<!-- For functions: -->
**Signature:**
```language
FunctionName(param1 AS type, param2 AS type) -> returnType
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ... | ... | ... | ... |

**Return:**
<!-- Detailed description of the return value in each scenario -->

**Errors/Exceptions:**
<!-- Error scenarios and how they must be handled -->

---

## 6. Scenarios and Edge Cases

| # | Scenario | Input/Condition | Expected Behavior | Related Alterations |
|---|----------|-----------------|-------------------|---------------------|
| 1 | ... | ... | ... | 3.X, 3.Y |

## 7. Validations and Business Rules

| # | Rule | Condition | Action | Where to Implement |
|---|------|-----------|--------|-------------------|
| 1 | ... | ... | ... | File/Function |

## 8. Affected Files Summary

<!-- Consolidated table for the implementation agent to have a quick overview. -->

| File | Action | Alterations |
|------|--------|-------------|
| `path/to/file` | Create / Modify / Remove | Brief description |

## 9. References

### 9.1 As-Is / To-Be Document
<!-- Reference to the source document -->

### 9.2 Source Code Files Consulted
<!-- Complete list of files read during PRD elaboration -->
```
