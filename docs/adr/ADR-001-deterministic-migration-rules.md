# ADR-001: Deterministic Migration Rules for LangGraph v1

**Status:** Proposed  
**Date:** 25 November 2026  
**Decision:** Use deterministic, rule-based transformations for the initial LangGraph v1 migration scope.

## 1. Context

LangGraph v1 introduces API changes that require existing Python applications using pre-1.0 LangGraph APIs to be migrated.

The migration agent must identify supported legacy patterns and transform them into their LangGraph v1 equivalents.

The initial implementation will use LibCST to perform deterministic Python source transformations while preserving existing code formatting, comments and structure wherever possible.

The initial scope is deliberately limited to three migration rules derived from the official LangGraph v1 migration guide.

The objective is to establish a reliable deterministic migration foundation before introducing LLM-assisted migration capabilities.

## 2. Decision

We will implement three deterministic migration rules:

- R001: Migrate `create_react_agent` imports.
- R002: Rename supported `create_react_agent()` function calls to `create_agent()`.
- R003: Rename `prompt=` to `system_prompt=` for supported string-literal arguments.

The implementation will use a two-pass analysis and transformation approach:

1. Analyze imports to identify supported migration candidates.
2. Apply deterministic transformations to the identified patterns.

LibCST will be used to preserve source formatting and comments.

## 3. In-Scope Migration Rules

### R001 — Import migration

**Objective:** Migrate supported imports from `langgraph.prebuilt` to `langchain.agents`.

Supported transformation:

Before:

```python
from langgraph.prebuilt import create_react_agent
```

After:

```python
from langchain.agents import create_agent
```

#### Mixed imports

When the import contains additional symbols, only `create_react_agent` will be moved.

Before:

```python
from langgraph.prebuilt import create_react_agent, some_other_function
```

After:

```python
from langchain.agents import create_agent
from langgraph.prebuilt import some_other_function
```

The unrelated imports must remain under their original module.

#### Parenthesized mixed imports

Parenthesized imports are also supported.

Before:

```python
from langgraph.prebuilt import (
    create_react_agent,
    some_other_function,
)
```

After:

```python
from langchain.agents import create_agent
from langgraph.prebuilt import (
    some_other_function,
)
```

#### Formatting and comments

The transformation must preserve relevant formatting and comments.

For example:

Before:

```python
# LangGraph agent import
from langgraph.prebuilt import create_react_agent, some_other_function
```

After:

```python
# LangGraph agent import
from langchain.agents import create_agent
from langgraph.prebuilt import some_other_function
```

### R002 — Function call rename

**Objective:** Rename supported calls to the migrated agent function.

Before:

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=model,
    tools=tools
)
```

After:

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=tools
)
```

The function call is eligible for transformation when the corresponding supported, unaliased import is identified.

### R003 — Prompt argument rename

**Objective:** Rename the `prompt` keyword argument to `system_prompt` on supported migrated agent calls.

Before:

```python
agent = create_react_agent(
    model=model,
    tools=tools,
    prompt="You are a helpful assistant."
)
```

After:

```python
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="You are a helpful assistant."
)
```

Only simple string literals are supported in the initial implementation.

The original string value must remain unchanged.

## 4. Out-of-Scope Migration Patterns

The following scenarios will not be transformed in the initial release.

When an unsupported pattern is encountered, the migration agent must leave the relevant source unchanged. Where appropriate, it should produce a diagnostic for manual review.

### 4.1 Aliased imports

Aliased imports are not supported.

Before:

```python
from langgraph.prebuilt import create_react_agent as cra

agent = cra(model=model, tools=tools)
```

Expected behaviour:

- R001 leaves the import unchanged.
- A diagnostic is generated.
- No alias migration is attempted.
- R002 and R003 do not transform the aliased call.

### 4.2 Dynamic prompt expressions

Dynamic prompt expressions are not supported by R003.

Before:

```python
agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=build_system_prompt(config)
)
```

Expected behaviour:

The `prompt` argument remains unchanged because its value is not a simple string literal.

This avoids making assumptions about dynamic expressions.

### 4.3 Non-target imports

Imports unrelated to `create_react_agent` are not migrated by R001.

Before:

```python
from langgraph.prebuilt import some_other_function
```

Expected behaviour:

The import remains unchanged.

### 4.4 Wildcard imports

Wildcard imports are outside the initial migration scope.

Before:

```python
from langgraph.prebuilt import *
```

Expected behaviour:

The import remains unchanged.

### 4.5 Other legacy LangChain and LangGraph APIs

The initial implementation is limited to the three documented migration rules in this ADR.

Other API changes, deprecated modules and legacy patterns are not automatically migrated by this release.

They require separate migration rules and corresponding decisions.


### 4.6 Scope-aware name resolution and shadowing

The initial implementation does not perform scope-aware name resolution.

ImportAnalyzer identifies supported imports at the syntax level. R002 and R003 use the collected imported names to identify eligible function calls.

They do not currently determine whether a local variable, function parameter, or another declaration shadows an imported name.

Before:

```python
from langgraph.prebuilt import create_react_agent

def my_function(create_react_agent):
    return create_react_agent(model, tools)
```

In this example, the function parameter shadows the imported
`create_react_agent` name inside `my_function`.

Expected behaviour in a scope-aware implementation:

- The imported function should be migrated.
- The shadowed function parameter and its invocation should remain unchanged.

Current implementation limitation:

R002 may rename the invocation inside `my_function` because it
matches the imported name collected by ImportAnalyzer.

R003 has the same limitation for matching calls.

Scope-aware name resolution and shadowing detection are deferred
to a future enhancement.

This limitation must be documented and considered when evaluating
migration results.

## 5. Explicitly Deferred Backlog Items

These are potential enhancements, not part of the current implementation scope.

| Item | Description | Priority |
|---|---|---|
| Existing target import detection | Detect whether `create_agent` is already imported | Medium |
| Duplicate import prevention | Avoid introducing duplicate `create_agent` imports | Medium |
| Import merging | Merge compatible imports where appropriate | Low |

These enhancements will be considered separately after the initial migration pipeline is established.

## 6. Migration Execution Requirements

The migration implementation must satisfy the following requirements:

1. **Deterministic:** The same source code and migration rules must produce the same output.
2. **Conservative:** Unsupported patterns must remain unchanged.
3. **Formatting preservation:** Existing formatting and comments should be preserved wherever possible.
4. **Traceability:** Each migration rule must be independently identifiable.
5. **Diagnostics:** Unsupported patterns requiring manual review should produce meaningful diagnostics.
6. **Testability:** Each rule must have independent tests covering supported and unsupported patterns.
7. **No silent assumptions:** Dynamic expressions and unsupported patterns must not be rewritten based on guesses.

## 7. Alternatives Considered

### LLM-only migration

Rejected for the initial implementation because transformations should be deterministic and predictable wherever the migration pattern is explicitly known.

### AST-based transformation

LibCST was selected over Python's built-in AST because it preserves comments, whitespace and other formatting details that are important when modifying existing source files.

### Broad migration scope

Rejected for the initial implementation. Additional migration rules will be introduced incrementally with their own documented scope and tests.

## 8. Consequences

### Positive

- Predictable and reproducible transformations.
- Clear separation between supported and unsupported migration patterns.
- Easier testing and debugging.
- Better source-code preservation.
- A foundation for introducing more migration rules incrementally.

### Trade-offs

- Some valid legacy patterns will require manual migration.
- Aliased imports are not automatically supported.
- Dynamic prompt expressions require manual review.
- Import deduplication and merging are deferred.

## 9. References

- Official LangGraph v1 migration guide: https://docs.langchain.com/oss/python/migrate/langgraph-v1
- LibCST documentation: https://libcst.readthedocs.io/

---

**End of ADR-001**