---
name: warp-layout-migration
description: Migrate AlphaSquare Vue files that import legacy Modal.vue, ActionSheet.vue, SlideLayout.vue, or explicitly requested slide wrapper layouts such as RightSlideLayout, LeftSlideLayout, and BottomGestureLayout to the repository's GlobalWarps.vue pattern with NewModal.vue, NewActionSheet.vue, or NewSlideLayout.vue, concrete WarpSymbol or typed CustomWarpKey ownership, BEM cleanup for touched SlideLayout templates/styles, and no local WarpLifeCycle, warps.name, or parent-provided name props. Use for targeted files or requested legacy import batches. Excludes FadeLayout, broad codemods, tracking-document updates, and unrelated overlay refactors.
---

# Warp Layout Migration

Use this skill to migrate AlphaSquare feature warps from:

- `Modal.vue` -> `NewModal.vue`
- `ActionSheet.vue` -> `NewActionSheet.vue`
- `SlideLayout.vue` -> `NewSlideLayout.vue`
- Explicitly requested slide wrappers -> `NewSlideLayout.vue`

## Shared Target Architecture

Use the repository's existing pattern:

- `GlobalWarps.vue` registers `{ name: WarpSymbol.X, component: markRaw(defineAsyncComponent(() => import('...'))) }`.
- The feature component renders `<NewModal :name="WarpSymbol.X">`, `<NewActionSheet :name="WarpSymbol.X">`, or `<NewSlideLayout :name="WarpSymbol.X">`.
- Callers open it with `warpApi.show(WarpSymbol.X, args)`.
- Args live on `WarpSymbol.X`; when a warp receives args, define that symbol as `Symbol('X') as CustomWarpKey<...>` and put the exact args contract in the `CustomWarpKey<...>` generic.
- Function callback args are exceptional. Add them only after applying the Callback Args Policy below.
- Do not duplicate domain object shapes inside `warp-symbol.ts`; import existing domain types from `@as/types` or move reusable domain-owned shapes there first.

## Inspect First

Before editing, inspect the current repo pattern instead of relying on memory:

1. Identify whether the target legacy layout is `Modal.vue`, `ActionSheet.vue`, `SlideLayout.vue`, or a slide wrapper.
2. Read the matching new layout implementation: `NewModal.vue`, `NewActionSheet.vue`, or `NewSlideLayout.vue`.
3. Read the owning app's `GlobalWarps.vue`.
4. Read the owning `warp-symbol.ts`.
5. Read at least one successful usage of the matching new layout in the same package; if none exists there, read the closest package's usage before editing.
6. Read every target file and the callers that open the legacy warp.
7. Check pre-existing changes in files you will edit.

## Operating Model

Edit the smallest complete set needed for the GlobalWarps pattern:

- the feature component being migrated;
- the owning `GlobalWarps.vue`;
- the owning `warp-symbol.ts` when a new or typed key is needed;
- callers that use `warpApi.show(...)` or pass data/events into the local warp;
- local parents only when removing a stale local render path.

If the user approved only a subset, ask once for the missing complete file set before editing. Do not implement a local `NewModal` / `NewActionSheet` / `NewSlideLayout` fallback.

When the legacy layout is rendered inline by a parent view, move the warp body into a registered component if needed so `GlobalWarps.vue` owns registration and the parent only calls `warpApi.show(...)`.

## Callback Args Policy

- Do not add function callbacks to `CustomWarpKey` by default.
- Prefer moving side effects into the warp component, the mutation composable, or the domain owner:
  - cache invalidation/refetch belongs in the mutation or cache layer;
  - create/update/delete success behavior belongs with the component that performs the mutation;
  - service creation should happen inside the warp when the warp owns the workflow.
- Use callback args only for narrow UI notification that cannot be owned by the warp itself.
- Treat every function arg as optional unless you have verified the warp cannot be opened by URL, scheme, or untyped global paths.
- Do not pass parent-bound callbacks or props to a global warp unless the opener also closes that warp on unmount.
- Selection callbacks such as `onSelected` should update state only; the ActionSheet/Modal should call the callback and then explicitly hide itself.

## Args Initialization And Local State

- Do not replace `@before-open` with `watch`, `onMounted`, `onBeforeMount`, or `@after-transition` just to copy `warpArgs` into local state.
- `warpApi.show(WarpSymbol.X, args)` patches args before the global warp mounts; initialize local refs directly from `warpArgs` or render from computed values.
- Keep local draft state only when the user can change values before saving/applying.
- Add `@before-close` cleanup only for real draft/discard state or close prevention. Do not preserve legacy close/open lifecycle hooks automatically.
- If a component moved to `GlobalWarps.vue` can now outlive its opener, verify parent-bound args and callbacks cannot become stale. If they can, either remove those args by moving responsibility into the warp/domain owner, or close the warp from the opener's `onBeforeUnmount`.

## Layout-Specific Notes

### Modal

- Preserve modal props and behavior supported by `NewModal`: `click-to-close`, style props, `is-wide-content`, `@before-close`, and required close callbacks.
- Convert `@before-open` initialization to typed `warpApi.useArgs(WarpSymbol.X)` and caller-provided `warpApi.show(WarpSymbol.X, args)`. Do not introduce initialization-only `watch`, `onMounted`, `onBeforeMount`, or `@after-transition`.
- Treat `@after-open` or `@after-close` usage as a behavior change risk because `NewModal` exposes `@after-transition`, not the legacy lifecycle pair.

### ActionSheet

- Preserve action sheet props and behavior supported by `NewActionSheet`: `direction`, `allow-mask-click`, `@before-close`, and required close callbacks.
- Convert `@before-open` initialization to typed `warpApi.useArgs(WarpSymbol.X)` and caller-provided `warpApi.show(WarpSymbol.X, args)`. Do not introduce initialization-only `watch`, `onMounted`, `onBeforeMount`, or `@after-transition`.
- Treat `@after-open` or `@after-close` usage as a behavior change risk because `NewActionSheet` exposes `@after-transition`, not the legacy lifecycle pair.

### SlideLayout

- Preserve slide props and behavior supported by `NewSlideLayout`: `direction`, `is-cover-view`, `container-style`, `@before-close`, and required close callbacks.
- Set `direction` explicitly when migrating to `NewSlideLayout`; do not rely on its default if the legacy usage implied a specific slide direction.
- Preserve `is-cover-view` only when the legacy slide was intended to cover the full view.
- For explicitly requested slide wrapper migrations, map wrapper direction to `NewSlideLayout`: `RightSlideLayout` -> `direction="right"`, `LeftSlideLayout` -> `direction="left"`, and `BottomGestureLayout` -> `direction="bottom"`.
- Before replacing a wrapper, inspect its wrapper-specific behavior and preserve only what belongs in the migrated feature: container sizing/style, close behavior, and callback flow. For `BottomGestureLayout`, verify `halfHeight`, `allowHalfStatus`, and status/gesture behavior; if those semantics are required and `NewSlideLayout` cannot represent them, stop and ask instead of silently dropping them.
- Convert `@before-open` initialization to typed `warpApi.useArgs(WarpSymbol.X)` and caller-provided `warpApi.show(WarpSymbol.X, args)`; `NewSlideLayout` does not emit `before-open`. Do not introduce initialization-only `watch`, `onMounted`, `onBeforeMount`, or `@after-transition`.
- Treat `@after-open`, `@after-close`, or `click-outside` usage as a behavior change risk because `NewSlideLayout` does not expose the same legacy events.
- Preserve slot structure deliberately: `NewSlideLayout` has optional `header` and `footer` slots and exposes `scroll-element` from the default slot. Prefer these slots for fixed header/footer regions, and put only the scrollable body in the default slot.
- Because SlideLayout migration usually rewrites the template for `header` / default / `footer` slots, use that edit to convert touched feature-local classes and scoped styles to BEM. Use a component-owned block name derived from the file/component name, elements for structural parts, and modifiers for state, for example `.my-profile-edit__footer`, `.my-profile-edit__save-button`, and `.my-profile-appearance__theme--active`.
- Replace vague feature-local classes such as `.content`, `.body`, `.footer`, `.image`, `.text`, `.title`, `.label`, `.active`, `.button`, and `.wrapper` when they are in the touched SlideLayout template or its scoped style. Keep shared utility classes such as `.clickable-layer` and do not rename classes owned by child components unless the migrated component explicitly passes the class and owns the styling.
- Prefer flat BEM selectors in scoped styles. Avoid introducing new nested generic selectors such as `.footer .button` or `.theme.active`; express state with BEM modifiers instead.
- After splitting header/content/footer, remove local layout CSS that duplicated `NewSlideLayout` ownership: wrapper `$screen-height`, `height: calc(...)`, local `overflow-y: auto`, `hide-scrollbar`, feature-level scrollbar overrides, absolute footer positioning, and desktop width/max-width rules. Keep only feature-owned presentation styles such as image display, text styling, padding, borders, and content-specific spacing.

## Hard Boundaries

- Only migrate `Modal`, `ActionSheet`, `SlideLayout`, and explicitly requested slide wrappers (`RightSlideLayout`, `LeftSlideLayout`, `BottomGestureLayout`); do not migrate `FadeLayout` or other wrapper layouts without explicit approval.
- Do not run broad codemods, repo-wide replacements, repo-wide formatters, or auto-fix commands.
- Do not create or modify tests solely for this migration.
- Do not change shared `NewModal`, `NewActionSheet`, `NewSlideLayout`, `WarpContent`, `WarpsContainer`, or warp API internals without explicit approval.
- Do not put feature emits, alerts, success flows, or business logic in `GlobalWarps.vue`; it should register warps only.
- Do not preserve or introduce feature-level `WarpLifeCycle`, local `warps` arrays, `warps.name`, `props.name`, `props.warpName`, `props.warpSymbol`, or generic name forwarding.

## Migration Steps

1. Replace the legacy layout import with the package's nearby `NewModal`, `NewActionSheet`, or `NewSlideLayout` import alias.
2. Bind the layout to a concrete `WarpSymbol.X`; add or type the symbol as `Symbol('X') as CustomWarpKey<...>` when args or callbacks are needed.
3. Register the component in the owning `GlobalWarps.vue` using the existing `markRaw(defineAsyncComponent(...))` style.
4. Convert `@before-open` data initialization to `const warpArgs = warpApi.useArgs(WarpSymbol.X)` and update callers to pass those values through `warpApi.show(WarpSymbol.X, args)`.
5. Convert local emits that crossed the removed parent boundary into typed callback args only when the Callback Args Policy allows it; otherwise move the behavior into the migrated component, mutation/cache layer, or domain owner.
6. Preserve layout-specific behavior from the matching notes above, including close behavior, mask behavior, direction, cover-view state, wrapper sizing, style props, and required callbacks.
7. For `NewSlideLayout`, split fixed header/footer regions into the `header` and `footer` slots when present, leave the scrollable body in the default slot, convert touched feature-local classes/styles to BEM, and remove local height/scroll/footer-positioning CSS that the layout now owns.
8. Remove stale local render paths, local warp-name props, legacy imports, and unused state.

## Warp Args Safety

- Treat `warpApi.useArgs(WarpSymbol.X)` as live warp state, not a durable request snapshot.
- In async handlers, capture every required arg and callback into local variables before the first `await` or before any code path that may hide/replace the warp.
- Do not read `warpArgs.someValue` again after `warpApi.hide(...)`, alert/modal transitions, cache mutations, or awaited API calls if that value is needed for follow-up UI, toast/alert text, or completion callbacks.
- In selection handlers, keep close ownership inside the warp component: capture the callback, call it for the selection, then explicitly hide the current warp. Parent callbacks should not hide the selecting warp as a side effect.
- Do not pass the entire `warpArgs` object as a child prop. Pass only the explicit fields the child needs so the child prop contract stays clear.
- Prefer:

```ts
async function submit() {
  const { ids, onCompleted } = warpArgs;

  await mutate(ids);
  await swalAlert({ html: `${ids.length}개가 처리되었습니다.` });
  onCompleted?.();
}
```

- Avoid:

```ts
async function submit() {
  await mutate(warpArgs.ids);
  await swalAlert({ html: `${warpArgs.ids.length}개가 처리되었습니다.` });
  warpArgs.onCompleted?.();
}
```

## Validate

Before final response:

- review the scoped diff;
- confirm all edited files were needed for the GlobalWarps pattern;
- search edited paths for `Modal.vue`, `ActionSheet.vue`, `SlideLayout.vue`, `RightSlideLayout`, `LeftSlideLayout`, `BottomGestureLayout`, `@before-open`, `@after-open`, `@after-close`, `click-outside`, `WarpLifeCycle`, `warps.name`, `props.name`, `props.warpName`, and `props.warpSymbol`;
- search edited paths for `watch(`, `onMounted(`, `onBeforeMount(`, and `@after-transition` when they were added during migration; justify or remove initialization-only usage;
- search edited paths for `warpArgs` being passed as a whole prop object; replace with explicit props for only the fields the child needs;
- inspect each `CustomWarpKey<...>` function arg; verify it is necessary, optional-safe, and not a refetch/cache/lifecycle responsibility that belongs elsewhere;
- for every global warp receiving parent-bound callbacks or props, verify the opener closes it on unmount or remove the parent-bound arg;
- search edited paths for async handlers that still read `warpArgs.*` after `await` or after `warpApi.hide(...)`, and capture those args locally when needed;
- for migrated `NewSlideLayout` files, verify header/footer/body split is intentional, verify touched feature-local template/style classes use BEM names, and search for stale local layout ownership such as `$screen-height`, `height: calc(...)`, `overflow-y: auto`, `hide-scrollbar`, feature-level scrollbar overrides, absolute footer positioning, and desktop width/max-width rules that should be owned by `NewSlideLayout`;
- run `git diff --check` and the nearest scoped lint/typecheck when practical;
- state whether runtime UI verification was performed.
