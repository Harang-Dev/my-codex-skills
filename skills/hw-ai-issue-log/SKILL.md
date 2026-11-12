---
name: hw-ai-issue-log
description: Record evidence-backed AI judgment and workflow failures in the user's Notion improvement database after a meaningful user correction or a self-detected failure. Deduplicate by problem and exclude routine product bugs, task logs, and unsupported hypotheses. On request, review accumulated cases against their sources and current instructions to propose improvements.
---

# HW AI Issue Log

Capture concise failure cases for a later agent to improve instructions in batches. The user does not need to review each record. This is separate from `hw-work-log`, which captures reusable technical knowledge per chat.

## Trigger and authority

- Record a demonstrated mismatch with the request, repository conventions, or agreed workflow when it offers a reusable lesson: unsuitable patterns, unnecessary edits or behavior, avoidable complexity, repeated corrections, or misdiagnosed intent. A user correction is evidence of the requested direction; investigate conflicting technical claims before treating them as facts.
- Self-detected issues do not require user feedback if the request, code, or observed result establishes the mismatch. Exclude isolated typos, ordinary product bugs, speculative risks, and preference changes without an AI failure. Do not search all previous chats or manufacture an issue on every turn.
- Use the destination and recording authorization configured by the user. If automatic recording is authorized for that destination, apply it without asking for approval per record. Briefly report a successful save at a natural task boundary.
- Recording does not authorize automatic edits to AGENTS.md, skills, product code, database schema, views, or sharing. Batch instruction improvements require a separate user request. Do not set `반영 완료` merely because the immediate task was corrected.

## Destination and properties

- Use the Notion database and issue template configured by the user. Fetch the database to identify its data source. If the destination or template is missing, prepare the issue body in chat.
- `이름`: one concrete problem statement, not a proposed universal ban.
- `상태`: choose the existing P1–P5 option by impact and recurrence, explaining the reason briefly in `처리 기록`. P1: serious data/security harm or critical task failure; P2: material rework or repeated failure; P3: localized meaningful correction; P4: minor friction; P5: low-impact improvement. These priorities concern AI workflow failures, not PR defect severity. Preserve a user's explicit priority and existing values on updates unless new evidence warrants a documented change.
- `반영 완료`: unchecked for new issues. Preserve existing values; a later instruction-improvement task can mark completion after applying or verifying the relevant change and recording its location and rationale.

## Save workflow

1. Draft from evidence already available. Fetch the data source schema and template to confirm current properties and section headings. Follow the user's live template if it changed. Before writing, fetch `notion://docs/notion-flavored-markdown-spec` using the Notion tool. Use the connected tools' current schemas.
2. Search this data source by the problem's distinctive terms, including related wording. Fetch plausible records and compare the failure mechanism and applicability, not just titles. An empty/failed/truncated search is not proof of absence; narrow or paginate as supported. Do not merge records whose relationship is uncertain.
3. Update an existing unreflected issue with a nonduplicate case and evidence, preserving user notes and processing history. If an already-reflected issue recurs after its recorded improvement, create a new recurrence linked to the earlier record rather than clearing its completion flag. Otherwise create one page per distinct problem with the data source as parent. Never overwrite the database template.
4. Use the body structure below, replacing guidance with actual evidence. Use targeted content updates for existing records; read the complete affected content first. Keep it short, but self-contained enough for a later agent without access to the original chat. Include a short source excerpt and actual thread ID when available; never invent chat URLs, PR links, user quotes, or causes. Do not copy secrets, personal data, entire logs, or private reasoning.
5. Verify the write result. After an ambiguous failure, check for the record before retrying; avoid duplicate creation if success cannot be established. On access/tool failure, report that the issue was not saved and provide a copy-ready body in chat, then continue the main task when possible. Do not change credentials or store a new local backlog automatically.

## Body

Write in Korean using the template's four sections. Separate observations, user decisions, and hypotheses; use `미확인` for an unknown cause. Do not infer an exception-free rule from a single incident.

```markdown
### 상황
- 요청: 원래 작업과 범위
- 문제: 실제로 관찰한 AI 행동과 영향
- 교정: 사용자 피드백 또는 근거에 따른 수정 방향

### 근거
- 핵심 대화 발췌와 필요한 코드·PR 링크
- 출처: 실제 채팅 제목·ID·발생일(확인 가능한 경우)

### 적용 조건
- 교정이 유효한 조건과 유지해야 할 동작
- 개선 가설과 반영 후보(근거가 있을 때만); 원인 미확인 여부

### 처리 기록
- 미반영 · 우선순위 판단 근거
```

## Batch review on request

Run this workflow when the user asks to review accumulated AI issues or improve instructions based on them.

1. Read the unreflected cases in scope and any related reflected cases. Group cases by the decision that led to the failure and its applicability, rather than by similar titles.
2. Check the recorded cause and proposed correction against available original evidence (chat, code, or PR) and the current `AGENTS.md` or relevant skill. When timing affects the diagnosis, check which guidance was in effect when the case occurred. Mark claims you cannot verify as `미확인`. If the evidence contradicts the recorded explanation, state the correction and cite the evidence while preserving the original observation and processing history.
3. Distinguish missing guidance, unclear applicability, and guidance that was available but not consulted at the relevant decision point. Use comparable cases where the approach worked, including relevant `hw-work-log` entries when available, to check applicability and exceptions.
4. For each group, recommend keeping, revising or consolidating, or moving existing guidance, adding a rule, or deferring the decision. Show the supporting cases, rationale, and exact wording and location for any proposed edit. Prefer consolidation over adding overlapping rules.
5. Apply instruction changes only when the user requests them. In `처리 기록`, record the location and rationale of the change or why verified existing guidance already covers the case. Set `반영 완료` after applying or verifying the relevant guidance. Record whether the issue recurs in comparable later work separately when evidence is available.
