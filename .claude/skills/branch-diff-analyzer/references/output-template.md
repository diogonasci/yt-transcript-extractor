# Output Template: Branch Diff Analysis

Use this exact structure when generating the final document. Sections that don't apply (e.g., no data structure changes) may be omitted per Rule 7/8 (scale to the demand). Remove all `<!-- ... -->` comments from the final output.

---

```markdown
# Análise de Branch: [branch atual] → [branch de comparação]

## 1. Resumo das Alterações

<!-- 2-3 paragraphs in business language: what was done in this branch, what problem it solves or feature it delivers. -->
<!-- This is the executive summary — someone reading only this section should understand the scope. -->

**Arquivos alterados:** X criados, Y modificados, Z removidos

## 2. Visão de Negócio

<!-- Group changes by business context, not by file. -->
<!-- A change spanning 3 files for the same purpose = one item here. -->

### 2.X [Feature/Context Name]

**O que mudou:** <!-- Business-language description -->

**Comportamento anterior:** <!-- How it worked before -->

**Comportamento novo:** <!-- How it works now -->

**Impacto para o usuário:** <!-- What the end user will notice -->

---

## 3. Funções Alteradas

<!-- Complete technical inventory of all affected functions/methods. -->
<!-- Even minor changes (variable rename, formatting) should be listed with a note. -->

### 3.X [File Name]

| Função/Método | Tipo de Alteração | Descrição da Mudança |
|---------------|-------------------|---------------------|
| `FunctionName()` | Criação / Modificação / Remoção | Brief description of what changed |

---

## 4. Estruturas de Dados Alteradas

<!-- Only include if there were changes to tables, models, or schemas. -->

| Estrutura | Tipo de Alteração | Detalhes |
|-----------|-------------------|---------|
| `table_name` | Nova coluna / Nova tabela / Alteração de tipo / Remoção | Change specification |

**DDL/Migrations:**
```sql
-- Structure change scripts
-- Always provide the exact DDL to apply in staging
```

---

## 5. Instruções de Homologação

<!-- Core section for QA/test team. -->
<!-- Each scenario must be independently executable: prep → steps → verify → cleanup. -->

### 5.X [Cenário de Teste: Descriptive name]

**Funcionalidade relacionada:** <!-- Reference to section 2.X -->

**Objetivo:** <!-- What this test validates -->

**Pré-condições:**
<!-- Required state in the environment before testing -->

**Preparação do ambiente:**
```sql
-- Queries to prepare the staging database
-- Insert/update data needed for the scenario
-- ALWAYS include WHERE clauses on UPDATE/DELETE
-- Prefer INSERT with explicit data
```

**Passos para teste:**
<!-- Step-by-step instructions in the application -->
<!-- Be specific: screen names, button labels, field values -->

1. ...
2. ...
3. ...

**Resultado esperado:**
<!-- What should happen if the implementation is correct -->

**Verificação no banco:**
```sql
-- Queries to verify data was changed correctly after test execution
```

**Limpeza (se necessário):**
```sql
-- Queries to revert database state after testing
-- Only include if test data could interfere with other tests
```

---

<!-- Repeat 5.X for each test scenario -->

## 6. Observações

<!-- Any additional relevant information: attention points, known limitations, environment dependencies, deployment order notes -->

## 7. Referência Completa de Arquivos

| Arquivo | Status | Funções Afetadas |
|---------|--------|-----------------|
| `path/to/file` | Criado / Modificado / Removido | List of functions |
```
