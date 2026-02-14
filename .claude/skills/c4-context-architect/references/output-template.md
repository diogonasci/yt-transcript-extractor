# Output Template: C4 Context Diagram Document

Use this exact structure when generating the final document. Every section must be present. If a section has no content, write "N/A — not applicable for this system" with a brief explanation of why.

Replace all `<!-- ... -->` comments with actual content. Remove the comments from the final output.

---

```markdown
# C4 Context: [System Name]

## 1. System Overview

<!-- 2-3 paragraphs: what is the system, what problem does it solve, and who does it serve. This section should be understandable by anyone in the organization, including non-technical stakeholders. -->

## 2. Primary System

<!-- The single system being documented. This is the center of the diagram. -->

| Attribute | Description |
|-----------|-------------|
| **Name** | <!-- Business-friendly name --> |
| **Type** | <!-- Web application, mobile app, backend service, platform, etc. --> |
| **Purpose** | <!-- 1-2 sentences: what it does from the user's perspective --> |
| **Owner** | <!-- Team or department responsible, if known --> |
| **Tech Stack** | <!-- High-level only: main language/framework, if relevant. NOT internal architecture. --> |

## 3. Actors (People)

<!-- Every person or role that interacts directly with the system. -->
<!-- Group by type: internal users, external users, administrators. -->

### 3.X [Actor Name]

| Attribute | Description |
|-----------|-------------|
| **Type** | Internal User / External User / Administrator / External Actor |
| **Description** | <!-- Who is this person/role? What is their relationship to the system? --> |
| **Interaction** | <!-- What do they do with the system? Be specific about the actions. --> |
| **Frequency** | <!-- Daily / Weekly / On-demand / Event-driven --> |

<!-- Repeat 3.X for each actor -->

## 4. External Systems

<!-- Every system outside the boundary of the primary system that interacts with it. -->
<!-- Group by relationship type: dependencies (systems the primary system depends on), dependents (systems that depend on the primary system), peers (bidirectional). -->

### 4.X [External System Name]

| Attribute | Description |
|-----------|-------------|
| **Type** | Dependency / Dependent / Peer |
| **Description** | <!-- What is this system? 1 sentence. --> |
| **Owner** | <!-- Who owns/operates this system? Internal team, third-party vendor, etc. --> |
| **Criticality** | <!-- High / Medium / Low — what happens if this integration fails? --> |

<!-- Repeat 4.X for each external system -->

## 5. Relationships

<!-- Complete inventory of every relationship in the diagram. -->
<!-- Each row = one arrow in the diagram. -->

| From | To | Purpose | Protocol/Mechanism | Direction | Data Exchanged |
|------|----|---------|--------------------|-----------|----------------|
| <!-- Element A --> | <!-- Element B --> | <!-- Why does this relationship exist? --> | <!-- REST API, Webhook, gRPC, Message Queue, Database, File Transfer, SMTP, etc. --> | <!-- → (unidirectional) or ↔ (bidirectional) --> | <!-- What data flows through this relationship? --> |

## 6. System Boundary Notes

### 6.1 What's Inside the Boundary
<!-- Clarify what is considered part of the primary system. This helps prevent boundary confusion. -->
<!-- Example: "The system boundary includes the web application, its backend API, and its dedicated database." -->

### 6.2 What's Outside the Boundary
<!-- Clarify what is explicitly NOT part of the primary system, especially things that might seem internal. -->
<!-- Example: "The identity provider (Keycloak) is operated by the platform team and is treated as an external dependency." -->

### 6.3 Boundary Decisions
<!-- If any boundary decisions were non-obvious, document them here with justification. -->

| Element | Decision | Justification |
|---------|----------|---------------|
| <!-- Element name --> | Inside / Outside | <!-- Why this choice? --> |

## 7. Risks and Observations

### 7.1 Single Points of Failure
<!-- External systems where failure would cause the primary system to be unavailable or degraded. -->

### 7.2 Missing or Unclear Integrations
<!-- Integrations that were implied but not confirmed, or that you suspect exist but couldn't verify. -->

### 7.3 Architectural Observations
<!-- Anything notable about the system's position in its ecosystem: over-coupling, missing redundancy, unusual patterns. Keep it brief — this is context-level, not a full architecture review. -->

## 8. Diagram Specification

<!-- This section provides the exact specification for generating the visual diagram. -->
<!-- It serves as a contract between the document and the diagram. -->

### 8.1 Elements

| ID | Name | Type | Position Hint |
|----|------|------|---------------|
| S1 | <!-- Primary system name --> | System | Center |
| A1 | <!-- Actor name --> | Actor | Left |
| E1 | <!-- External system name --> | External System | Right |
<!-- Continue numbering: A2, A3... for actors, E2, E3... for external systems -->

### 8.2 Connections

| From ID | To ID | Label |
|---------|-------|-------|
| <!-- e.g. A1 --> | <!-- e.g. S1 --> | <!-- e.g. "Manages orders [Web UI]" --> |

## 9. References

### 9.1 Source Material
<!-- What inputs were used to produce this document (codebase, documents, conversations) -->

### 9.2 Related Documentation
<!-- Links or references to existing architecture docs, if any -->
```
