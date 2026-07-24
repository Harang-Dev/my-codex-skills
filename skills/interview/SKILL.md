---
name: interview
description: Structured clarification interview for turning an ambiguous request into an explicit intent brief before planning or implementation. Use when the user explicitly invokes $interview, asks to interview or clarify requirements first, wants one-question-at-a-time discovery, or provides vague goals where intent, outcome, audience, scope, non-goals, constraints, success criteria, decision boundaries, or existing context are not yet explicit.
---

# Interview

Use this skill to clarify a user's real request before proposing a plan or making changes. Ask exactly one focused question at a time, update the working hypothesis after each answer, and stop only when the request can be summarized as an actionable intent brief.

## Opening

Start the interview with exactly:

```markdown
HYPOTHESIS: <one sentence describing what you think the user actually wants>
CONFIDENCE: <0-100%, with a short reason if below 70%>

Q: <one focused question>
GUESS: <your best guess and why you think that>
```

Wait for the user's answer before asking the next question.

## Interview Order

Clarify in this order:

1. Intent: why the user wants this.
2. Outcome: desired end state.
3. User / audience: who benefits or uses it.
4. Scope: how far the work should go.
5. Non-goals: what stays out.
6. Constraints: technical, business, time, cost, UX, compatibility, privacy, security.
7. Success criteria: observable proof it worked.
8. Decision boundaries: what the agent may decide vs. what requires confirmation.
9. Existing context: codebase, product, users, docs, dependencies, and prior decisions.

For coding tasks, ask implementation-detail questions only after intent, outcome, scope, non-goals, and constraints are clear.

Inspect available code, docs, files, and local context instead of asking the user for facts that can be discovered. Ask the user only for judgment, tradeoffs, priorities, business logic, or preferences.

## Question Rules

- Ask exactly one question at a time.
- Every question must include the current guess:

```markdown
Q: <one focused question>
GUESS: <your best guess and why you think that>
```

- After each answer, update `HYPOTHESIS` and `CONFIDENCE`.
- Do not batch questions.
- Do not accept vague words as final answers, including `scalable`, `robust`, `clean`, `modern`, `best practice`, `production-ready`, `intuitive`, and `enterprise-grade`.
- For vague wording, ask what it means concretely in this situation.

## Pressure Test

Ask at least one pressure-test question before ending the interview. Use one of these forms:

- Example: "Can you give a concrete example or counterexample?"
- Assumption: "What assumption would make this wrong?"
- Tradeoff: "If we cannot have both A and B, which one wins?"
- Boundary: "What should we explicitly not do in the first pass?"
- Real want: "If you did not have to justify this to anyone, what would you actually want?"

## Stop Condition

Stop only when all are true:

- You can predict the user's reaction to the next 2 to 3 likely questions.
- Intent, outcome, scope, constraints, success criteria, non-goals, and decision boundaries are explicit.
- At least one pressure-test question has been asked.
- Another question would only polish wording and would not materially change the work.

If confidence is still low after several rounds, say what foundational piece is missing and ask one reframing question.

## Final Brief

When ready, ask for explicit confirmation with:

```markdown
# Confirmed Intent Brief

- Outcome:
- User / audience:
- Why now:
- Success criteria:
- Scope:
- Non-goals:
- Constraints:
- Decision boundaries:
  - You may decide:
  - Ask me before deciding:
- Key assumptions:
- Open questions, if any:

Confirm / refine / reject?
```

Do not treat `whatever you think`, `sounds good`, or `sure` as strong confirmation. If confirmation is vague, ask what the user would refine before moving on.
