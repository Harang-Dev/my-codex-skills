---
name: hw-work-log
description: Select reusable causes, decision criteria, and applicability conditions from the current chat and save them to the personal Notion work retrospective database using a fixed Korean template. Use when the user requests a work retrospective, saved learning notes, end-of-task documentation, or invokes this skill. Supports implementation, research, and design decisions.
---

# HW Work Log

Save reusable knowledge from the current chat: evidence and conditions that help diagnose a similar problem or choose a design later. Avoid task reports and exhaustive conversation summaries.

## Content selection

Apply this question to every item: **Would reading this later change a diagnosis, design, or implementation decision?** Exclude it otherwise.

- Include non-obvious causes and evidence, contracts and ownership boundaries, selection rationale, technical differences between alternatives actually considered, reproduction conditions, solution applicability, and unresolved user-visible behavior.
- Exclude checkout, routine main merges and conflict resolution, commit/push/PR merge status, review replies and thread resolution, commit hash lists, clean working trees, MERGEABLE status, server/tab cleanup, task chronology, and request change history.
- Validation: retain only observations supporting a technical conclusion. Exclude formatting/lint/diff check lists, complete test execution histories, unrelated pre-existing failures, and past passing results for removed tests. Never present unverified claims as facts.
- Cancelled or deferred work: omit who cancelled it and the conversation history. Retain only limitations of the final implementation and their impact.
- Exception: when an unusual merge failure or deployment procedure is itself the learning topic, retain its cause and the solution principle needed to prevent recurrence. Omit the mere fact that the operation was performed.
- Deduplicate: do not repeat the same fact across summaries, actions, results, and reusable principles. Separate independent lessons with short topic labels.
- If there is no meaningful new knowledge, report `재사용할 새 지식 없음` and do not create an unnecessary record. If the user explicitly requests factual logging instead, follow that requested scope.

## Destination and scope

- Database: [작업 이후 정리](https://app.notion.com/p/3f8824902a7c8047b891e1a04da59c96)
- Database ID: `3f882490-2a7c-8047-b891-e1a04da59c96`
- Verified data source: `collection://4a182490-2a7c-8208-af43-87ccedeaeaa2`
- Time zone: `Asia/Seoul`.
- Invoking this skill or an explicit user instruction for automatic recording authorizes creating/updating records at this destination. Do not repeatedly ask for permission. Automatic skill selection alone does not establish authorization to save.
- This skill does not detect completion/archive events or guarantee execution in future chats. Installing global instructions, hooks, or schedules and archiving chats are outside its scope.
- Do not modify Notion schemas, views, or sharing settings, or commit/push repository changes. Do not copy secrets, passwords, personal information, or entire raw logs.

## Record identity and deduplication

Default to **one record per chat**. For multiple tasks, use matching topic labels within each section. Follow-up work and repeated invocations update that record. Split and link records only when the user requests separate task records.

1. Look for the previous saved URL and record key in the current conversation. If a page URL exists, fetch it to verify its destination and key.
2. If the actual chat thread ID is available, use `codex:<thread-id>`. Do not substitute a shared session ID. Never invent IDs or chat URLs, or create a share link solely for recording.
3. Without an ID, use `manual:<initial-record-time-ISO8601>:<short-topic>`. Before creation, search the database for project/topic candidates and fetch them to verify chat identity. Matching titles or branches alone do not justify merging. If a repeated invocation cannot identify its existing record, present candidates and ask for clarification.
4. Use the connected Notion search tool, scoped to this data source. Search by key and topic, then inspect candidate bodies. Search/access failures do not mean no existing record.
5. Report duplicate keys rather than merging/deleting pages arbitrarily. If a create response fails or has an unknown outcome, search by key before retrying. Do not create another page when existence cannot be established.

## Workflow

1. Read the [fixed template](references/template.md). Draft from the current conversation and evidence already available. Identify unavailable historical context. Do not rerun tests or redo work solely to document it.
2. Fetch the database through the connected Notion tool to verify its current data source and exact property names. Before writing content, also fetch `notion://docs/enhanced-markdown-spec`. Never open that URI with a general web tool.
3. After checking for an existing record, create a missing record with **data_source_id** as the parent in `create_pages`. Do not pass the database ID as page_id. Put the title in properties only, not in the body.
4. Fetch the full existing body before updating it. Do not replace existing content when the response is truncated or incomplete. Use `update_content` for changed sections; preserve user notes, review checkmarks, and external links. Update corrected decisions to the currently valid conclusion; retain the reason an earlier decision was wrong only when it offers reusable knowledge. Avoid whole-page replacement and unrelated deletion.
5. Wait for asynchronous operations to finish. After creation or a multi-section edit, fetch the page again to verify the title, key, fixed sections, and properties.
6. Briefly report the saved page link, whether it was created or updated, and the record key. On failure, do not claim success; provide the fixed-template draft in chat. Do not send it to another destination without authorization.

## Database properties

Schema verified on 2026-10-13. Prefer the current fetched schema on every invocation. Preserve the exact Korean property names and option values below.

| Property | Rule |
| --- | --- |
| 작업 이름 | `[YYYY-MM-DD] 프로젝트 · 구체적인 작업 주제`. Keep the initial record date; update only the topic to reflect final scope. For non-code work, use the subject area instead of a project. |
| 설명 | Summarize the key cause or decision criterion as a short Korean noun phrase. Omit task progress status. |
| 복습 여부 | Initialize new records to `시작 전`; preserve existing values on updates. Task completion does not mean `완료`. Change only when the user requests a review-status update. |
| 담당자 | Set only when specified by the user and the actual Notion user ID is verified. |
| 마감일 | Set only an explicitly provided deadline. Do not substitute recording or completion dates. |
| 노력 수준 | Set only a user-specified `작게`, `보통`, or `크게`. Do not infer duration or effort. |

If properties have been removed or changed, retain relevant user-provided values in the body and write only properties supported by the current schema. Do not create properties or select options. Initialize defaults only on creation; preserve unspecified properties on updates.

## Writing rules

- Write saved records in **Korean**, preserving domain terms, function/file names, units, and boundary conditions exactly.
- Use bullets in `항목명: 내용` format, without prose paragraphs. End naturally with nouns or noun phrases such as `발생`, `확인`, `적용`, `제외`, `통과`, or `미검증`. Avoid sentence endings such as `~했습니다`, `~입니다`, and `~한다`. Preserve quotations, code, commands, and proper names verbatim.
- Put one fact or decision in each bullet. Separate multiple pieces of evidence or alternatives. Express conditions and causality explicitly with labels such as `조건`, `원인`, `근거`, and `결과`. Do not omit subjects, negation, quantities, or boundaries to shorten the wording.
- Keep section headings and order fixed. Omit empty subitems instead of filling the page with `해당 없음` or `미실행`. State uncertainty when resolution or verification scope matters to a decision.
- Separate verified causes from hypotheses. Record only selection/exclusion reasons supported by the conversation or evidence. Document explainable decisions and evidence, not private reasoning traces.
- Keep validation evidence only when needed to establish the lesson's confidence or scope. Passing lint does not establish user-visible correctness.
- Include only real PR/code/document links needed to revisit key evidence. Omit unlinked placeholders such as “validation commit” or “review reply.” Format local code paths as code rather than pretending they are portable links.
- Include applicability conditions for reusable knowledge. Do not promote a one-off experience to team policy or automatically edit architecture documents.
- Write 1–3 review exercises as Korean noun phrases, such as `발생 원인과 확인 근거 설명` or `선택한 방식과 대안의 차이 설명`. Do not pad the count with generic procedural questions. Preserve existing user checkmarks.
