# CHARTER.md

## Spawn Charter

This file is the source of truth for the `spawn` agent spawner.

The purpose of `spawn` is to safely run multiple Codex agents against one repo at the same time by giving each agent:

1. Its own git worktree.
2. Its own branch.
3. A clearly scoped task.
4. A clearly scoped set of files or folders it may edit.
5. A validation gate before its code can be accepted.
6. A sequential merge process that protects `main`.

## Laws of Spawn

### Law 1: The Charter Comes First

Before making any major change to `spawn`, check this `CHARTER.md` file.

A major change includes changes to:

- agent scope rules
- orchestration flow
- merge behavior
- test behavior
- protected-file behavior
- retry behavior
- parallel execution behavior
- README instructions
- config structure
- Codex prompts
- Cursor or Codex rules

Any major change must remain consistent with this charter.

### Law 2: Agents Are Workers, Not Deciders

Agents may propose changes.

The orchestrator decides whether those changes are acceptable.

An agent must not decide on its own that it is allowed to edit outside its assigned scope.

### Law 3: Every Agent Gets a Box

Each agent must have:

- a name
- a task
- one or more allowed paths
- its own worktree
- its own branch

Agents should not share working directories.

### Law 4: File Ownership Must Be Enforced

The orchestrator must check the diff after each agent runs.

If an agent changes a file outside its allowed paths, that agent's work must be rejected.

Prompt instructions are not enough. There must be a hard check.

### Law 5: Parallel Work Is Allowed, Parallel Merging Is Not

Agents may run in parallel in separate worktrees.

Merges into the base branch must happen one at a time.

After each merge, the validation command must pass before the next merge is attempted.

### Law 6: Tests Are the Gate

If a test command is configured, it must pass before an agent's code is accepted.

After merging an accepted branch, the test command must pass again on the base branch.

### Law 7: Main Must Be Protected

The base branch, usually `main`, should only receive code that has passed:

1. scope validation
2. agent-level tests
3. merge-level tests

If a merge fails, the orchestrator must stop merging further branches.

### Law 8: Shared Files Are Dangerous

Shared files such as lockfiles, central configs, route registries, barrel exports, and shared test files create conflict risk.

They should be avoided when possible.

If they are allowed, they must be listed explicitly in the agent's allowed paths or shared paths.

### Law 9: CHARTER.md Is Protected

`CHARTER.md` must not be changed by an agent or assistant unless the user explicitly gives permission.

If a requested change conflicts with this charter, stop and ask the user whether they want to amend the charter.

### Law 10: Boring Safety Beats Clever Automation

Prefer simple, visible, debuggable behavior over clever hidden behavior.

The user should be able to understand what happened by reading the terminal output, git branches, commits, and logs.
