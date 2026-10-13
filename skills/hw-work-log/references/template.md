# Fixed body template v3

Keep the section headings and order below. Write all saved content as short **Korean noun-phrase bullets**. Replace brace-delimited guidance with actual knowledge and omit empty subitems. Format dates, Notion references, and collapsed sections according to the Notion Markdown specification fetched during execution.

Title property: `[initial record date] project · key learning topic`, rendered in Korean. Do not repeat the title in the body. For multiple lessons, use matching short topic labels within sections 1–3. The Korean headings and field labels below are the output contract, not instructions to translate.

```markdown
## 1. 문제와 원인

- 현상: {Recognizable symptom and conditions}
- 원인: {Verified cause or key discovery}
- 근거: {Supporting code contract, documentation, or observation}

## 2. 해결 원리와 판단 기준

- 해결: {Essential change or research conclusion}
- 선택 근거: {Decision criterion reusable in other situations}
- 대안과 차이: {Technical differences actually considered; only if relevant}

## 3. 적용 조건과 주의점

- 적용 조건: {Conditions under which the solution principle holds}
- 경계: {Exceptions, side effects, unresolved behavior, or material unverified scope}
- 재확인 지점: {Code or condition to inspect first for recurrence; only if it adds information}

## 4. 참고 자료

- {Actual link or code path needed to revisit the key evidence}

## 5. 복습 질문

- [ ] {Korean noun-phrase exercise explaining a key cause, decision criterion, or boundary}
```

If references are unavailable, write only `참고 자료 없음` in section 4. Include 1–3 review exercises according to the number and importance of lessons. Do not repeat earlier facts as generic principles in section 3.

At the end, add a collapsed `기록 식별 정보` section containing only `템플릿 버전: 3`, `기록 키`, `프로젝트`, `최초 기록`, and `마지막 갱신`. Include an original chat link only if already available. Omit branches, commit hashes, and task status that are unnecessary for deduplication.

For existing v1/v2 records, apply v3 to new content. Condense existing content only for records the user requests, preserving user notes and review checkmarks. Do not bulk-convert unrelated records.

## Selection examples

From the user's channel studio record, retain these lessons:

- Missing `query.type` validation on direct URL access causing menu-map indexing failure.
- Handling string/null/array query values, validating allowed types, and normalizing invalid values to `channel`.
- Conditions for removing duplicate defaults when the router is the only consumer and guarantees valid input.
- The `beforeEnter` boundary: no execution for query-only navigation on the same route.
- Inner container width/margin restrictions affecting footer alignment.
- Keyboard accessibility limitations remaining after removing a button wrapper from click-only filters.

Exclude:

- Main merges, conflict file counts, commit hashes, pushes, posted replies, and MERGEABLE status.
- Lint/format command lists, server cleanup, and working-tree status.
- Chronology of cancelled menu wiring/404 approaches and past passing counts for removed tests.
- Unrelated pre-existing Stylelint failures and unnecessary lists of checks not run.
