# Output Template: Sequence Diagram Document

Use this exact structure when generating the final document. Every section must be present. If a section has no content, write "N/A — not applicable for this flow" with a brief explanation of why.

Replace all `<!-- ... -->` comments with actual content. Remove the comments from the final output.

---

```markdown
# Sequence Diagram: [Flow Name]

## 1. Flow Overview

<!-- 2-3 paragraphs: what flow is being documented, what triggers it, and what the expected outcome is. This section should be understandable by anyone in the team, including non-developers who need to understand the behavior. -->

## 2. Trigger and Scope

| Attribute | Description |
|-----------|-------------|
| **Trigger** | <!-- What initiates this flow? (user action, API call, scheduled job, event, webhook) --> |
| **Pre-conditions** | <!-- What must be true before this flow can execute? --> |
| **Success Outcome** | <!-- What is the end state when the flow completes successfully? --> |
| **Failure Outcome** | <!-- What is the end state when the flow fails? How is the caller notified? --> |
| **Scope Start** | <!-- First participant and action in the flow --> |
| **Scope End** | <!-- Last participant and action in the flow --> |

## 3. Participants

<!-- Every participant involved in the flow. Order them left-to-right as they should appear in the diagram: initiator first, then downstream participants in order of first interaction. -->

### 3.X [Participant Name]

| Attribute | Description |
|-----------|-------------|
| **Type** | Actor / Frontend / Backend Service / External System / Database / Message Queue / Worker |
| **Description** | <!-- What is this participant? 1 sentence. --> |
| **Role in Flow** | <!-- What does it do in this specific flow? Initiator, processor, data store, notifier, etc. --> |
| **Aliases** | <!-- Other names for this participant in the codebase or docs, if any. "None" if only one name. --> |

<!-- Repeat 3.X for each participant -->

## 4. Messages — Happy Path

<!-- The main success flow, step by step. Each row is one arrow in the diagram. -->
<!-- Number sequentially. This numbering is the source of truth for message order. -->

| # | From | To | Message | Type | Response | Notes |
|---|------|----|---------|------|----------|-------|
| 1 | <!-- Sender --> | <!-- Receiver --> | <!-- What is being sent/requested. Include method + path for APIs, event name for async. --> | <!-- Sync / Async / Response / Self-call --> | <!-- What comes back? For async: "N/A". For sync: the response payload/status. --> | <!-- Any relevant context: timeout, retry policy, idempotency. --> |

## 5. Alternative Paths

<!-- Error handling, edge cases, conditional branches. Each subsection is one alt/opt block in the diagram. -->

### 5.X [Scenario Name]

**Type:** alt (if/else) / opt (optional) / break (early exit)

**Condition:** <!-- When does this path activate? Be precise. -->

**After Step:** <!-- Which step number from section 4 does this branch from? -->

| # | From | To | Message | Type | Response | Notes |
|---|------|----|---------|------|----------|-------|
| 5.X.1 | <!-- Sender --> | <!-- Receiver --> | <!-- Message --> | <!-- Type --> | <!-- Response --> | <!-- Notes --> |

**Outcome:** <!-- What is the end state of this alternative path? -->

<!-- Repeat 5.X for each alternative path -->

## 6. Loops and Parallel Execution

<!-- Only include if the flow contains loops or parallel blocks. -->

### 6.X [Block Name]

**Type:** loop / par

**Condition:** <!-- For loops: iteration condition. For par: why parallel? -->

**After Step:** <!-- Which step number from section 4 does this start at? -->

| # | From | To | Message | Type | Response | Notes |
|---|------|----|---------|------|----------|-------|
| 6.X.1 | <!-- Sender --> | <!-- Receiver --> | <!-- Message --> | <!-- Type --> | <!-- Response --> | <!-- Notes --> |

<!-- Repeat 6.X for each loop/parallel block -->

## 7. Timing and Constraints

<!-- Only include if timing matters for this flow (timeouts, SLAs, race conditions). -->

| Constraint | Between Steps | Value | Consequence if Violated |
|------------|---------------|-------|------------------------|
| <!-- e.g. Timeout --> | <!-- e.g. Steps 3-4 --> | <!-- e.g. 30 seconds --> | <!-- e.g. Transaction rolled back, error returned to caller --> |

## 8. Observations and Risks

### 8.1 Error Handling Gaps
<!-- Interactions where error handling is not specified or unclear. -->

### 8.2 Potential Failure Points
<!-- Steps where failure is likely or would have cascading effects. -->

### 8.3 Design Observations
<!-- Anything notable: unnecessary round trips, missing retry logic, tight coupling, synchronous calls that could be async. Keep it brief — actionable observations only. -->

## 9. Diagram Specification

<!-- This section provides the exact specification for generating the visual diagram. -->
<!-- It serves as a contract between the document and the diagram. -->

### 9.1 Participants (left to right)

| ID | Name | Type | Mermaid Declaration |
|----|------|------|---------------------|
| P1 | <!-- Participant name --> | <!-- Actor/Participant --> | <!-- e.g. `actor User` or `participant PaymentService` --> |

### 9.2 Messages (top to bottom)

| # | From ID | To ID | Label | Arrow Type |
|---|---------|-------|-------|------------|
| 1 | <!-- e.g. P1 --> | <!-- e.g. P2 --> | <!-- e.g. "POST /payments" --> | <!-- ->> (sync) / -->> (response) / -) (async) --> |

### 9.3 Control Flow Blocks

| Type | Condition | Contains Messages | After Message # |
|------|-----------|-------------------|-----------------|
| <!-- alt/opt/loop/par/break --> | <!-- Condition text --> | <!-- e.g. "5.1.1, 5.1.2" --> | <!-- Step number it branches from --> |

## 10. References

### 10.1 Source Material
<!-- What inputs were used to produce this document (codebase, documents, conversations) -->

### 10.2 Related Documentation
<!-- Links or references to existing docs, API specs, or architecture diagrams -->
```
