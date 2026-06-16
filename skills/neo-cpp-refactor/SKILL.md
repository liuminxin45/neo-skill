---
name: neo-cpp-refactor
description: Refactor C++ .h/.hpp/.cpp/.cc files and C++ project directories with C++11 best practices, Chinese block comments, readability cleanup, defensive safety checks, performance review, file merge/split, directory architecture cleanup, CMake/include/test updates, and scoped verification.
---

# C++ Header/Source Refactor CN

Use this skill for C++ code cleanup and maintainability refactors. Preserve
business behavior unless the user explicitly asks for behavior changes.

## Workflow

1. Inspect the requested `.h/.hpp/.cpp/.cc` files, owning directories, build files, tests, and narrow callers.
2. When a requested header/source has a misleading file name, class name, helper name, or namespace name, evaluate a scoped rename before editing internals.
3. Classify the change size:
   - Small: formatting, comments, local guard checks, private helper cleanup, no public API or behavior change.
   - Medium: internal behavior changes, data-structure cleanup, lock/lifetime changes, local file/class/helper renames, file merge/split inside one module, or meaningful performance changes.
   - Large: public API changes, cross-module contract changes, threading model changes, ownership changes, broad file sets, directory moves, CMake target changes, or include-root changes.
4. For small changes, do not build by default. Run cheap textual checks only when useful.
5. For medium changes, run the narrowest relevant compile/test when behavior, ownership, file names, or public includes change.
6. For large changes, run build and regression tests that match the changed surface. Directory reorganization must prove the project still compiles unless the user explicitly disables verification.
7. Before editing, state the intended edit scope briefly.
8. After editing, report changed files, verification performed or intentionally skipped, and any residual risk.

## Refactor Modes

- Local cleanup: improve one or a few files without moving them.
- Local rename: rename a misleading file, class, helper, namespace, enum, or test name when the better name is obvious and the reference closure is small.
- File consolidation: merge duplicate helpers, split oversized files, remove stale wrappers, or rename files inside the same module.
- Directory reorganization: change folder names, module boundaries, file ownership, include paths, CMake lists, tests, or packaging references.

## Local Rename Rules

- Keep file names, primary class names, include guards, and test names aligned after renaming.
- Prefer concise and accurate names over historical compatibility words.
- Remove misleading terms such as `Base`, `Helper`, `Manager`, `Util`, `Common`, `Defines`, or old vendor/framework prefixes when they do not describe a real design role.
- Keep `Base` only for a true base class, abstract interface, or inherited layer with derived implementations.
- Keep `Helper` only for a small stateless/support object.
- Keep `Manager` only when the type owns lifecycle, registry state, coordination, or policy.
- If a stale-prefix class name is kept for compatibility, record the exact downstream contract and prefer a temporary alias or forwarding layer.
- Keep renames scoped: update includes, build metadata, tests, comments, include guards, and narrow downstream consumers in the same pass.
- Treat public class/function/namespace renames as medium or large changes depending on consumer reach.
- Do not rename just for taste. Rename only when it improves ownership, discoverability, or avoids misleading future edits.
- After any rename, run `rg` for the old file name, old include string, old include guard, old class/type name, and old test name.

## Domain Naming Boundary

- Use domain words consistently. Do not let historical names blur data model, runtime orchestration, protocol DTO, adapter, and UI responsibilities.
- Use concrete nouns for one data item or model node.
- Use capability nouns for module-level workflows such as events, polling, translation, cache, serialization, or service payloads.
- Use bridge names only when a type truly sits between two concepts.
- Before renaming a file, map its responsibility first: data model, serialization, cache management, event dispatch, polling, translation, service payload, adapter, or test.

## Directory Reorganization Rules

- First map the current structure with `rg --files`, relevant `CMakeLists.txt`, include paths, tests, exported headers, package scripts, and consumers.
- Identify the intended architecture in terms of ownership: domain model, service/runtime, protocol/DTO, adapter, test, legacy, generated, and build artifact.
- Keep generated output, build folders, local logs, packaged artifacts, and cache files out of source restructuring unless the user explicitly asks.
- Prefer cohesive module directories over type-only buckets.
- Move files with version-control-aware commands such as `git mv` when the directory is a Git repo.
- Update all affected build metadata, include directives, forward declarations, namespace comments, test paths, scripts, and documentation references.
- Run `rg` for old paths, old filenames, old include strings, and stale module names after moves.
- Preserve public include compatibility unless the user accepts a breaking change.
- For broad moves, keep a move map in the working notes and final summary.

## Header Rules

- Put durable migration/refactor history in the file header, not in the body.
- Write durable history entries in Chinese by default and include the date or batch marker when it helps future readers.
- Add Chinese comments for structs, non-trivial types, complex functions, and member variables.
- Prefer comments that explain responsibility, ownership, lifetime, concurrency, valid ranges, or contract constraints.
- Do not comment obvious getters/setters or trivial scalar members unless the surrounding header already does so.
- Keep public signatures stable unless the user explicitly allows API changes.
- Include the headers needed by declarations themselves.
- Separate public API, internal implementation detail, and test-only declarations.

## C++11 Best Practices

- Treat C++11 as the language ceiling unless the repo build files prove a newer standard is enabled.
- Prefer `nullptr`, scoped `enum class`, `override`, `final`, `explicit`, `= default`, and `= delete` where they clarify ownership or intent.
- Prefer RAII and standard containers over manual allocation, raw owning pointers, C arrays, and manual cleanup.
- Use `std::unique_ptr` for exclusive ownership and `std::shared_ptr` only when shared lifetime is real and already matches the local model.
- Do not introduce C++14/17 features unless the target explicitly supports them.
- Use `constexpr` for compile-time constants that are valid in C++11.
- Prefer range-for, `auto` for iterator-heavy or type-obvious code, and explicit types where they improve API readability.
- Avoid accidental platform macro collisions in portable code.
- Keep ABI-facing structs and exported function signatures conservative.

## Source Rules

- Prefer small local helpers when they remove repeated map lookups, validity checks, or lock boilerplate.
- Add defensive checks for null pointers, empty keys, invalid enum/range values, and missing map entries before dereference or mutation.
- Avoid `operator[]` on maps in read/delete paths when it would create unintended empty entries.
- Clean up empty containers after erase when subscription/cache structures would otherwise grow stale buckets.
- Keep hot paths allocation-light and avoid repeated lookups when a saved iterator is clearer and cheaper.
- Use RAII for locks when the local lock API does not already provide it.
- Check ownership, lifetime, nullability, thread affinity, and exception/early-return cleanup before changing structure.
- Prefer structured parsers and existing local abstractions over ad hoc string rewriting.
- Clamp external counts and lengths to local array/container limits before indexing.
- Keep SDK/OS boundary checks close to the boundary.

## Comment Style

- Convert comments in touched files to block comments: `/* ... */`.
- Use Chinese comments by default for new explanatory comments.
- File headers may remain Doxygen block comments.
- Replace namespace and include-guard trailing comments with `/* ... */`.
- Do not churn unrelated untouched files only to change comment style.

## Verification Policy

- Small changes: skip build by default. Useful checks include `rg "//" <touched files>`, `git diff`, or a narrow residue scan.
- Medium changes: prefer a targeted compile/test for the owning module or direct unit test.
- File merge/split: run at least the owning target compile or the narrowest test that includes the changed files.
- Directory reorganization: run source-reference scans and a real build for the affected project or target.
- Large changes: run the relevant build and regression test set.
- If build/test cannot run, explain the risk and the exact skipped command.

## Final Report

- Summarize code cleanup separately from file/directory moves.
- For directory work, include the move map and the old-path residue scan result.
- State exactly which build/test commands ran, or why they were skipped.
- Call out intentionally deferred risks such as public include compatibility, downstream consumers, or unverified optional targets.
