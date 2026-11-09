---
name: swal-modal-migration
description: Replace SwalAlert helper calls (`swalConfirm`, `swalAlert`, and `swalPrompt`) in the AlphaSquare Vue monorepo with `AConfirmModal.vue`, `AAlertModal.vue`, and `APromptModal.vue` through `useWarpApi` and `WarpSymbol`. Use when migrating supplied Vue files away from `@as/utils/swal`, preserving confirm, cancel, prompt-value, validation, and sequential-action behavior.
---

# Swal Modal Migration

Migrate supplied files individually. Do not use a mechanical global replacement: swalAlert returns a result after dismissal, while Warp modal callbacks have lifecycle phases—`onConfirm`/`onCancel` run before hiding and supported `onAfterClose` callbacks run after the modal has fully closed.

## Read the contract first

Before editing, read these files in the target checkout:

- `packages/modules/src/components/shares/AConfirmModal.vue`
- `packages/modules/src/components/shares/AAlertModal.vue`
- `packages/modules/src/components/shares/APromptModal.vue`
- `packages/modules/src/constants/warp-symbol.ts`
- one nearby existing `warpApi.show(WarpSymbol.A*Modal, ...)` call

Confirm that the target app mounts `GlobalWarps` with `@as/constants/warps`. The shared warp registry already registers these three modal components. If an app does not include it, add the registration before converting calls.

## Keep the migration scope small

- Inspect supplied components' consumers before converting. When the user requests removal of unused components, verify static imports, dynamic loading, registries, and template usage before deleting them instead of migrating them.
- Do not automatically expand helper replacement into parent-popover layering, outside-click handling, transition timing, or repository-wide lint configuration changes. If an observed regression requires such work, explain the cause and separate its scope from the helper conversion; follow any explicit user decision to exclude or revert it and report the remaining behavior gap.
- In particular, do not introduce `refDebounced`, transition-duration imports, or conditional `z-index` classes in `IndicatorSettingPopover.vue` or `PointerSettingPopover.vue` as a standard migration step. These are separate compatibility measures, not requirements of `AConfirmModal`.
- Prefer direct local control flow over extra lifecycle subscriptions, helper functions used only to route an event, or explanatory comments that restate the code. Retain comments only when they explain a non-obvious constraint that still matters.

## Prepare each Vue component

1. Restrict automatic conversion to Vue Composition API contexts. Treat Options API, plain `.ts` files, direct `swal.fire`, and imported `swal.showValidationMessage` as manual-review cases.
2. Remove only the migrated names from `import { ... } from '@as/utils/swal'`. Retain `swal` only when a deliberate direct SwalAlert use remains; never remove its import while expressions such as `swal.isVisible()`, `swal.fire()`, or `swal.showValidationMessage()` still exist.
3. Add missing imports and initialization, preserving the repository import order:

```ts
import { useWarpApi } from '@as/composables/injectable';
import { WarpSymbol } from '@as/constants/warp-symbol';

const warpApi = useWarpApi();
```

When a component only uses shared `A*Modal` keys, import `WarpSymbol` from `@as/constants/warp-symbol`, not an app-local re-export such as `@/constants/warp-symbol`. Reuse an existing app-local `WarpSymbol` when the component also needs app-specific keys; do not add a competing import or rewrite unrelated keys. Reuse an existing `warpApi`; never add a second instance.

## Map options and control flow

| SwalAlert helper | Warp target | Option mapping |
| --- | --- | --- |
| `swalAlert` | `WarpSymbol.AAlertModal` | `confirmButtonText → confirmText` |
| `swalConfirm` | `WarpSymbol.AConfirmModal` | `confirmButtonText → confirmText`, `cancelButtonText → cancelText` |
| `swalPrompt` | `WarpSymbol.APromptModal` | `inputValue → modelValue`, `inputPlaceholder → placeholder`, button texts as above |

Apply the following content mapping to all three helpers; do not map `html` to `body` unconditionally:

- When both `title` and `html` are provided, map `title → title` and `html → body`.
- When only `html` is provided, map `html → title` and omit `body`. Preserve the original HTML content, including tags and line breaks.
- When only `title` is provided, map `title → title` and omit `body`.

Treat an empty `title` with a single message in `html` as a single-message dialog: place the message in `title` and omit `body`. Do not emit `title: ''` plus a populated `body`, or replace an unused `body` with `body: ''`.

For example, `{ html: '삭제하시겠습니까?<br>다시 확인해 주세요.' }` becomes `{ title: '삭제하시겠습니까?<br>다시 확인해 주세요.' }`, while `{ title: '삭제하시겠습니까?', html: '삭제 후에는 복구할 수 없습니다.' }` becomes `{ title: '삭제하시겠습니까?', body: '삭제 후에는 복구할 수 없습니다.' }`.

Omit undefined/default options instead of adding empty fields. The target components sanitize both title and body. Do not carry across SwalAlert-only options (`allowOutsideClick`, `allowEscapeKey`, `delay`, `target`, `input`, `inputAttributes`, `customClass`, or `reverseButtons`) without an explicit product decision.

### Alert

Do not add `onAfterClose` to every `AAlertModal`. Use no callback for a plain acknowledgement alert, or use `onConfirm` when work should begin as soon as the user acknowledges the alert:

```ts
warpApi.show(WarpSymbol.AAlertModal, {
  title: '저장되었습니다.',
});
```

When code follows `await swalAlert(...)`, classify the continuation by its lifecycle dependency:

- Put work that only depends on the user's acknowledgement in `onConfirm`.
- Put work that must wait until the alert is fully closed—such as closing the containing layout, navigating, opening another warp, or performing a close-sensitive focus/state transition—in `onAfterClose`, when the target modal contract provides it.
- Keep work independent of the acknowledgement before `warpApi.show`.

Use `onAfterClose` only for the second case; do not add an empty or redundant `onAfterClose` callback. Do not assume `await warpApi.show` reproduces the SwalAlert result contract.

Before adding a Promise wrapper, inspect the direct caller. If no caller awaits or returns the enclosing operation's completion, put the continuation directly in `onConfirm` or `onAfterClose`. Do not use `await new Promise(resolve => show({ onAfterClose: resolve }))` just to keep the old function's linear shape. For a close-dependent navigation:

```ts
function onNewGameOpened() {
  warpApi.show(WarpSymbol.AAlertModal, {
    title: '새 게임을 하기 위해<br />로그인 페이지로 이동합니다.',
    onAfterClose: () => {
      router.push({ name: 'chartGame', query: { loginReserved: true } });
    },
  });
}
```

If the same continuation is needed both after an alert and without an alert, a nearby domain function may own that shared work. Keep target identity explicit when the continuation acts on an account or another mutable selection. Retain a Promise bridge only when an actual caller consumes its result or completion.

### Confirm

Run the confirmed action directly in `onConfirm`, including closing a parent Warp, opening another Warp, or starting a purchase/login/navigation flow. Prefer an existing function reference when no argument adaptation is needed. Preserve `await` inside the callback so `AConfirmModal` keeps the modal open while the action runs.

Do not introduce a mutable confirmation flag such as `let confirmed = false` or a ref to route work between `onConfirm` and `onAfterClose`. This also applies when the flag only distinguishes cancellation cleanup; do not justify retaining it solely because the confirmed action already runs in `onConfirm`. When a caller awaits completion, preserve that completion contract without inventing a confirmation result; use a result Promise only when the result is actually needed. The old helper's post-dismissal timing alone does not justify deferring the confirmed action to `onAfterClose`.

Use `onCancel` for explicit cancel-button work, but inspect dismissal behavior before moving every false branch there: Escape and outside-click may bypass `onCancel`. Put common dismissal cleanup in supported `onAfterClose` when it must also run for those paths. Preserve a Promise completion contract when a direct consumer actually awaits it; do not replace that contract with a flag used only to route the confirmed action.

```ts
// Before: const confirmed = await swalConfirm(options); if (confirmed) await remove();
warpApi.show(WarpSymbol.AConfirmModal, {
  title: '삭제하시겠습니까?',
  confirmText: '삭제',
  cancelText: '취소',
  onConfirm: async () => {
    await remove();
  },
});
```

Do not call the old helper inside a Warp callback and do not move work that previously ran before opening the dialog.

#### Awaited completion versus an actual result

Inspect what the direct consumer needs. An awaited operation does not necessarily need a boolean confirmation result. If the consumer only waits for the dialog and cleanup to finish, preserve a `Promise<void>`. When existing state can drive the same reconciliation after every dismissal, put that work in `onAfterClose` without `confirmed`, `isConfirmed`, or another routing flag/result:

```ts
function resetSort() {
  return new Promise<void>((resolve) => {
    warpApi.show(WarpSymbol.AConfirmModal, {
      title: '정렬을 해제하시겠습니까?',
      confirmText: '정렬 해제',
      onConfirm: () => {
        setCurrentSort({ ...DEFAULT_WATCHLIST_SORT_PREFERENCE });
      },
      onAfterClose: async () => {
        await nextTick();
        sortStocks();
        resolve();
      },
    });
  });
}
```

This example depends on `sortStocks()` rebuilding only the displayed list from the current sort preference: confirmation sets the default preference, while cancellation leaves the existing preference intact. Verify that common cleanup has equivalent effects before using this shape; do not run cancellation-only side effects after confirmation. Do not add an explicit `hide` just to coordinate a result when the modal already closes itself and `onAfterClose` can signal completion.

If the original function returns a confirmation result that callers actually consume, preserve that result contract. Keep the confirmed action in `onConfirm`; a result Promise can resolve success there and cancellation in `onAfterClose` so Escape and outside-click are included. For asynchronous actions, await the action before resolving success. Preserve whether the consumer needs acknowledgement-time completion or a fully closed modal. If an explicit close wait is necessary, first verify that repeated `hide` calls share the pending close operation through `after-remove`, unmount, and cleanup. Never make `onConfirm` await the enclosing Promise whose completion depends on the modal closing.

### Confirm before closing a containing Warp

For an unsaved-changes confirmation, preserve the force/unmodified early return and synchronously call `event.preventDefault()` before any `await`. Keep the parent open when the confirmation is cancelled. Close the parent directly in `onConfirm` with the existing force option; do not add a confirmed flag or a gated `onAfterClose`.

Check `use-warp.ts`, `Warp.vue`, and `plugins/later-call.ts` before choosing the opening sequence. Opening a confirmation immediately inside `before-close` can register it before the parent's cancelled-close Esc entry is restored, making the next Esc target the parent.

Prefer waiting for the pending close attempt locally instead of registering an additional `remove-cancel` listener when both contracts hold:

- A repeated, non-force `warpApi.hide(parentName)` waits for the existing hide attempt rather than starting another attempt.
- `before-close` is delivered through Vue `emit`, whose async listener return value is not awaited by Warp.

Under those contracts, use this shape after the existing early-return checks:

```ts
event.preventDefault();
// 취소된 부모 닫기 처리와 Esc 등록 복원이 끝난 뒤 확인창을 연다.
await warpApi.hide(WarpSymbol.MainChartSettingModal);
warpApi.show(WarpSymbol.AConfirmModal, {
  title: '변경사항을 저장하지 않고 종료하시겠습니까?',
  confirmText: '종료',
  onConfirm: () => {
    warpApi.hide(WarpSymbol.MainChartSettingModal, { force: true });
  },
});
```

The awaited hide completes the cancelled attempt and restores Esc ordering; it does not close the parent. Do not use this pattern inside a directly awaited `warpApi.on('before-remove', async ...)` handler: waiting for the same hide there would deadlock. Do not substitute arbitrary timers or repeated `nextTick()` calls for the lifecycle guarantee. Verify repeated Esc/cancel and confirmed exit using the actual Warp and Esc implementation.

### Prompt

`APromptModal` owns the editable value, so a migrated callback must receive that value. Before converting the first prompt call, update its public contract if it still invokes `onConfirm()` with no argument:

```ts
// `warp-symbol.ts`
onConfirm: (modelValue: string) => void;

// `APromptModal.vue`
await warpArgs.onConfirm(warpArgs.modelValue);
```

Then move the confirmed branch into `onConfirm(modelValue)`, and the non-confirmed branch into `onCancel` when needed:

```ts
warpApi.show(WarpSymbol.APromptModal, {
  title: '이름을 입력해 주세요.',
  modelValue: previousName,
  placeholder: '이름',
  onConfirm: async (name) => {
    await rename(name);
  },
});
```

Translate simple `inputAttributes.minlength`/`maxlength` and `preConfirm` checks to the `rules` prop only after confirming the current `ATextField` validation behavior. Replace `swal.showValidationMessage(...)` with a rule that returns its error string. For asynchronous validation or a `preConfirm` that performs side effects, preserve the validation/action sequencing in `onConfirm` and enhance the modal API only when necessary; do not silently lose validation or close the modal on failure.

## Review special cases

- Preserve `swal` imports until no `swal.showValidationMessage` or direct SwalAlert use remains.
- Audit remaining `swal` identifiers in the agreed scope. A guard such as `swal.isVisible()` does not detect Warp dialogs; use applicable Warp state when replacing that guard is in scope, while retaining any guard still needed for remaining legacy dialogs. Do not remove the import while a guard remains or expand into excluded parent-popover changes just to eliminate a legacy reference.
- Do not add `onAfterClose` merely because the migrated call uses `AAlertModal`. Add it only when the continuation must wait for the alert's completed close; use `onConfirm` for acknowledgement-time work and omit both callbacks when no continuation is needed.
- Convert one callback chain at a time. Nested dialogs and post-dismissal navigation often need explicit callback sequencing.
- For confirm dialogs, keep confirmed actions in `onConfirm`. Audit mutable confirmation flags even when they only gate cancellation cleanup. Prefer common state-driven cleanup; use a completion Promise or an actual result contract only as needed by consumers. Navigation or opening another Warp alone does not justify moving confirmed actions to `onAfterClose`.
- Keep `return` behavior: a former `return await swalConfirm(...)` needs a caller-facing contract decision, not a callback-only rewrite.
- Do not convert non-modal feedback to an alert merely because it calls `swalAlert`; preserve the user interaction and timing.

## Validate

1. Run `rg -n '\bswal(?:Confirm|Alert|Prompt)\b' <changed-files>` and confirm every remaining helper hit is intentional.
2. Run `rg -n '\bswal\b' <changed-files>` and inspect every result, including property accesses. If no deliberate direct SwalAlert use remains, this command must have no code hits; comments and strings may remain only when they do not form an executable reference.
3. Check imports for unused `swal`, `swal*`, `useWarpApi`, and `WarpSymbol` names. A retained `swal` import must correspond to an intentional direct use, and a removed import must not leave any `swal` identifier behind.
4. Run package-appropriate lint and focused validation; follow repository restrictions on when typechecks may run. Add or update black-box component tests only when they provide meaningful regression protection and fit the user's requested scope. If the user excludes test code, do not leave new test files in the final diff; distinguish temporary runtime checks, existing tests, and browser verification in the report.
5. Compare each migrated dialog with its original options: `html` alone must become `title` without `body`; `title` and `html` together must become `title` and `body`. Preserve the original content.
6. Exercise each migrated path: confirm, cancel when present, prompt with valid input, prompt with invalid input, and any shortcut or dismissal path previously gated by SwalAlert visibility. For each alert, verify that callbacks are attached only when needed and that close-dependent work uses `onAfterClose` while acknowledgement-time work uses `onConfirm`.
7. Inspect every added Promise bridge against its direct consumers, and check mutable confirmation flags, shared-only Symbol imports, repeated dismissal, cancellation restoration, and caller completion timing. Shared modal tests do not establish that migrated consumers are covered. Record unreproduced consumer paths as unverified; distinguish entry-screen captures from exercising the changed dialog. Respect the user's restrictions on destructive or state-changing validation.
