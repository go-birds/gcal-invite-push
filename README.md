# Spawn

Spawn is a tiny robot boss for Codex agents.

It lets you say:

> I want three little helpers. One works on this folder. One works on that folder. One works on another folder. Do not let them mess up each other's toys.

Spawn gives each helper its own sandbox, checks its work, runs tests, and only then lets the code go into `main`.

## Like You Are 5

Imagine your repo is a big LEGO table.

You want three kids to build at the same time:

- one kid builds the red house
- one kid builds the blue car
- one kid builds the green tower

But you do not want the red-house kid touching the blue car.

Spawn does this:

1. Gives each kid their own table.
2. Gives each kid a note saying what they may touch.
3. Lets all kids build at the same time.
4. Checks that each kid only touched their own pieces.
5. Checks that the whole LEGO set still works.
6. Adds the good work back to the main table one kid at a time.

## Folder Contents

```text
spawn/
  CHARTER.md              # The laws of Spawn
  README.md               # This file
  agents.template.yml     # Copy this to agents.yml and fill it in
  orchestrator.py         # The script that runs the agents
  .cursor/rules/
    spawn-charter.mdc     # Cursor/Codex rule about checking the charter
```

## Install

From your repo root, copy this folder in:

```bash
cp -R spawn ./spawn
```

Install the Python dependency:

```bash
pip install pyyaml
```

Make sure Codex is installed and works in your terminal:

```bash
codex --help
```

## Step 1: Copy the Template

From your repo root:

```bash
cp spawn/agents.template.yml agents.yml
```

Now edit `agents.yml`.

## Step 2: Fill In Your Agents

Example for an arithmetic repo:

```yaml
base_branch: main
test_command: pytest

execution:
  mode: parallel
  max_parallel: 3

shared_paths_global: []

agents:
  - name: addition
    task: |
      Improve addition logic.
      Keep the public behavior correct.
    paths:
      - src/add.py
      - tests/test_add.py

  - name: subtraction
    task: |
      Improve subtraction logic.
      Keep the public behavior correct.
    paths:
      - src/subtract.py
      - tests/test_subtract.py

  - name: multiplication
    task: |
      Improve multiplication logic.
      Keep the public behavior correct.
    paths:
      - src/multiply.py
      - tests/test_multiply.py
```

## Step 3: Run Spawn

From your repo root:

```bash
python spawn/orchestrator.py
```

## What Happens

Spawn creates folders next to your repo:

```text
../wt-addition
../wt-subtraction
../wt-multiplication
```

Each one is a git worktree.

Each agent gets its own branch:

```text
agent/addition
agent/subtraction
agent/multiplication
```

Then Spawn runs Codex in each worktree.

## Allowed Paths

Each agent can only edit the paths you list.

Exact file:

```yaml
paths:
  - src/add.py
```

Whole folder:

```yaml
paths:
  - src/add/
```

Glob pattern:

```yaml
paths:
  - src/add/**
  - tests/test_*.py
```

## Shared Paths

Shared paths are files that more than one agent may edit.

Use these carefully.

```yaml
shared_paths_global:
  - README.md
```

Or per agent:

```yaml
agents:
  - name: addition
    paths:
      - src/add.py
    shared_paths:
      - pyproject.toml
```

Shared files are where conflicts usually happen.

## Protected File: CHARTER.md

`CHARTER.md` is protected.

Agents are told not to edit it.

The orchestrator also checks the diff and rejects any agent that changes it.

Only the user may approve changes to the charter.

## Cursor / Codex Rule

This folder includes:

```text
.cursor/rules/spawn-charter.mdc
```

That rule says:

- check `CHARTER.md` before major changes
- do not change `CHARTER.md` without user permission
- keep changes consistent with the goal of Spawn

If your repo already has `.cursor/rules`, copy the rule there:

```bash
mkdir -p .cursor/rules
cp spawn/.cursor/rules/spawn-charter.mdc .cursor/rules/spawn-charter.mdc
```

## Why Agents Are Parallel But Merges Are Not

Agents run at the same time:

```text
addition      starts
subtraction   starts
multiplication starts
```

But merges happen one at a time:

```text
merge addition      -> run tests
merge subtraction   -> run tests
merge multiplication -> run tests
```

That protects `main`.

## Stop Conditions

Spawn stops or rejects work when:

- an agent edits a file outside its allowed paths
- an agent edits `CHARTER.md`
- tests fail
- a merge conflict happens
- a merge breaks the full repo test command

## Example Command

```bash
python spawn/orchestrator.py
```

That is the big green button.
