---
name: hw.architecture-docs
description: Write concise architecture and policy documentation for frontend systems, shared runtime infrastructure, and cross-cutting UI behavior. Use when Codex is asked to document application architecture, runtime layering, component boundaries, ownership rules, system policies, decision records, or exception handling rules that span multiple components or packages. Especially useful for AlphaSquare docs about Warp, overlay/layer policy, service/composable boundaries, and shared UI/runtime contracts.
---

# HW Architecture Docs

## Overview

Inspect the implementation, the real usage sites, and the current operating rules, then write a short architecture document that explains:

- what the system is responsible for
- which boundaries matter
- what rules are intended to be stable
- where exceptions are allowed

This skill is for architecture and policy docs, not component prop documentation.

## Workflow

1. Start from the runtime or system boundary.
   - Read the source-of-truth files first.
   - Prefer entrypoints, shared runtime modules, registries, providers, and common wrappers.
   - For UI architecture, look at the real runtime path before documenting leaf components.

2. Map the system before writing.
   - Identify the main actors.
   - Identify what is global, what is shared, and what is local.
   - Identify where policy is decided versus where policy is merely consumed.
   - If the topic involves multiple packages, note package ownership explicitly.

3. Search for real usage before stating rules.
   - Use `rg` to find representative call sites.
   - Validate whether the rule is broad, default-only, or already full of exceptions.
   - If the codebase contradicts the intended rule, document both:
     - current behavior
     - proposed or target behavior

4. Keep the document decision-oriented.
   - Architecture docs should help readers answer:
     - where should new logic go?
     - what is the default path?
     - what counts as an exception?
     - which layer owns the decision?
   - Avoid turning the doc into a changelog or implementation dump.

5. Prefer policy and boundaries over API duplication.
   - Good content:
     - runtime responsibilities
     - ownership boundaries
     - layer rules
     - default behavior
     - exception paths
     - extension points
     - references to real code and representative usage
   - Avoid:
     - copying full prop tables
     - copying full function signatures unless critical
     - file-by-file summaries with no policy meaning
     - generic “what is Vue” style background

6. Separate default rules from exceptions.
   - Always distinguish:
     - default rule
     - allowed override
     - unresolved question
   - If a system depends on exceptions, document the exception contract explicitly.

7. Match repo conventions.
   - Prefer existing docs locations first.
   - For AlphaSquare, follow the tone and structure already used under `docs/` and package-level docs.
   - Default to concise Korean when the surrounding docs and current task are in Korean.

## Recommended Sections

Use only the sections that materially help the topic. Default target is one short page.

```md
# Topic Name

## Overview
- what this system covers
- what it does not cover

## Current Structure
- main runtime pieces
- ownership boundaries

## Default Rules
- the normal path
- policy that new code should follow

## Exceptions
- what can override the default
- who owns the exception

## Open Questions
- unresolved points that should not be presented as settled

## References
- source-of-truth files
- one or two representative usage files
```

## Heuristics

- If the doc reads like a component README, it is probably the wrong skill.
- If the doc cannot answer “where should new code go?”, it is too shallow.
- If the doc cannot answer “what is the default versus an exception?”, it is too ambiguous.
- If the doc repeats code without explaining responsibility or policy, cut it.
- If multiple packages participate, call out the ownership boundary directly.

## Special Guidance For Runtime Policy Docs

When documenting runtime behavior such as Warp, overlay layering, shared services, or registries:

- document the runtime model first
  - example: queue, stack, registry, provider, plugin
- then document semantic policy
  - example: layer bands, dismiss rules, ownership rules
- then document override points
  - example: per-symbol override, wrapper-level policy, escape hatch
- only after that document representative surfaces

For topics with active debate or ongoing design work:

- do not overstate certainty
- label assumptions clearly
- preserve the distinction between:
  - current implementation
  - agreed direction
  - proposed next step
