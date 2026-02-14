# Output Template: As-Is / To-Be Document

Use this exact structure when generating the final document. Every section must be present. If a section has no content, write "N/A — not applicable for this demand" with a brief explanation of why.

Replace all `<!-- ... -->` comments with actual content. Remove the comments from the final output.

---

```markdown
# As-Is / To-Be: [Descriptive title of the demand]

## 1. Executive Summary
<!-- 2-3 paragraphs: what is the demand, why does it exist, and what transformation is expected -->

## 2. Current State (As-Is)

### 2.1 Current Behavior
<!-- Functional description of how the system behaves today in the context of the demand -->

### 2.2 Current Flow
<!-- Step-by-step description of the current execution flow. Use sequential numbering. -->
<!-- Example:
1. User triggers X action
2. System calls function Y in file Z
3. Data is validated against rules A, B
4. Result is persisted in table T
5. Response is returned to the caller
-->

### 2.3 Code Map
<!-- Concrete references in the source code. Every entry must point to a real file/function. -->

| Component | File | Function/Method | Responsibility |
|-----------|------|-----------------|----------------|
| ... | ... | ... | ... |

### 2.4 Data Structures
<!-- Tables, models, schemas involved in the current state -->

| Structure | Type | Relevant Fields | Notes |
|-----------|------|-----------------|-------|
| ... | ... | ... | ... |

### 2.5 Current Integrations
<!-- APIs, services, events participating in the current flow -->

### 2.6 Current Business Rules
<!-- List of business rules identified in the code, with reference to their implementation -->
<!-- Example:
- **Rule 1**: Description of the rule — implemented in `file.ext`, function `func_name`
- **Rule 2**: ...
-->

## 3. Desired State (To-Be)

### 3.1 Expected Behavior
<!-- Functional description of how the system should behave after implementation -->

### 3.2 Proposed Flow
<!-- Step-by-step description of the desired execution flow. Highlight what changes relative to the current flow. -->
<!-- Use markers like [NEW], [CHANGED], [REMOVED] to make differences visible -->
<!-- Example:
1. User triggers X action
2. [CHANGED] System calls function Y2 in file Z (was Y)
3. [NEW] System validates against new rule C
4. Data is validated against rules A, B
5. Result is persisted in table T
6. [NEW] Event is published to notify downstream systems
7. Response is returned to the caller
-->

### 3.3 Required Changes

#### New Components
<!-- Files, functions, tables that need to be created -->
<!-- Example:
- New function `validate_new_rule` in `validators.ext`
- New table `audit_log` to track changes
-->

#### Modified Components
<!-- Existing files, functions, tables that need changes, with description of the change -->
<!-- Example:
- `file.ext` → `func_name`: Add validation step for rule C before persisting
- Table `orders`: Add column `status_reason` (varchar)
-->

#### Removed/Deprecated Components
<!-- Anything that ceases to exist or loses relevance -->

### 3.4 New Business Rules
<!-- Rules that will be added or modified -->
<!-- Example:
- **New Rule C**: Description — must be enforced at step 3 of the proposed flow
- **Modified Rule A**: Previous behavior → New behavior
-->

### 3.5 Integration Impact
<!-- How existing integrations are affected and what new integrations are needed -->

## 4. Gap Analysis

### 4.1 Functional Gaps
<!-- What's missing to go from As-Is to To-Be in terms of functionality -->

### 4.2 Technical Gaps
<!-- Technical limitations, technical debt, or technical prerequisites identified -->

### 4.3 Data Gaps
<!-- Migrations, transformations, or new data needed -->

## 5. Decisions and Premises

### 5.1 Decisions Made
<!-- Ambiguities resolved during analysis, with decision and justification -->

| # | Ambiguity | Decision | Justification |
|---|-----------|----------|---------------|
| 1 | ... | ... | ... |

### 5.2 Premises
<!-- Assumptions made that should be validated -->
<!-- Example:
- P1: We assume the external API supports idempotent retries (not confirmed)
- P2: Current transaction volume won't exceed 1000/day during initial rollout
-->

## 6. Risks and Dependencies

### 6.1 Risks

| Risk | Severity | Suggested Mitigation |
|------|----------|---------------------|
| ... | High/Medium/Low | ... |

### 6.2 Dependencies
<!-- External dependencies, from other teams, or technical -->

## 7. Scenarios and Edge Cases

| # | Scenario | Expected Behavior | Criticality |
|---|----------|-------------------|-------------|
| 1 | ... | ... | High/Medium/Low |

## 8. References

### 8.1 Relevant Files
<!-- Complete list of source code files relevant to the implementation -->

### 8.2 Related Documentation
<!-- Links or references to existing documentation, if any -->
```
