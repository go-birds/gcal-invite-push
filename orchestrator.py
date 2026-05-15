import os
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import PurePath

import yaml

REPO_ROOT = os.getcwd()
CHARTER_FILE = "CHARTER.md"


def run(cmd, cwd=None):
    print(f"\n>> {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def output(cmd, cwd=None):
    return subprocess.check_output(cmd, shell=True, cwd=cwd).decode().strip()


def load_config(config_path="agents.yml"):
    with open(config_path) as f:
        return yaml.safe_load(f)


def path_matches(file_path, patterns):
    path = PurePath(file_path)

    for pattern in patterns:
        if file_path == pattern:
            return True

        if pattern.endswith("/") and file_path.startswith(pattern):
            return True

        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            if file_path.startswith(prefix):
                return True

        if path.match(pattern):
            return True

    return False


def check_scope(worktree, allowed_paths):
    changed = output("git diff --name-only", cwd=worktree).splitlines()

    for f in changed:
        if not f:
            continue
        if not path_matches(f, allowed_paths):
            raise Exception(f"Out-of-scope edit: {f}")


def check_protected_files(worktree):
    changed = output("git diff --name-only", cwd=worktree).splitlines()

    for f in changed:
        if f == CHARTER_FILE or f.endswith(f"/{CHARTER_FILE}"):
            raise Exception(
                "Protected file changed: CHARTER.md. "
                "This file may only be changed with explicit user permission."
            )


def build_prompt(agent, allowed_paths):
    paths = "\n".join(f"- {p}" for p in allowed_paths)

    return f"""
You are the {agent['name']} agent.

Task:
{agent['task']}

You may only edit:
{paths}

Rules:
- Before making major changes, respect the project charter.
- Do not edit CHARTER.md.
- Do not edit files outside your allowed paths.
- If the task requires files outside your scope, stop and explain.
- Run or update relevant tests if they are inside your allowed paths.
- Do not commit. The orchestrator will commit after validation.
"""


def prepare_worktree(agent, base_branch):
    name = agent["name"]
    branch = f"agent/{name}"
    worktree = f"../wt-{name}"

    if not os.path.exists(worktree):
        run(f"git worktree add -b {shlex.quote(branch)} {shlex.quote(worktree)} {shlex.quote(base_branch)}")
    else:
        run(f"git checkout {shlex.quote(branch)}", cwd=worktree)

    run(f"git fetch origin {shlex.quote(base_branch)}", cwd=worktree)
    run(f"git rebase {shlex.quote(base_branch)}", cwd=worktree)

    return branch, worktree


def combined_allowed_paths(agent, global_shared_paths):
    paths = []
    paths.extend(agent.get("paths", []))
    paths.extend(agent.get("shared_paths", []))
    paths.extend(global_shared_paths or [])
    return paths


def run_agent(agent, base_branch, default_test_command, global_shared_paths):
    name = agent["name"]
    branch, worktree = prepare_worktree(agent, base_branch)

    allowed_paths = combined_allowed_paths(agent, global_shared_paths)
    test_command = agent.get("test_command") or default_test_command
    setup_command = agent.get("setup_command") or ""

    print(f"\n=== Running agent: {name} ===")

    if setup_command:
        run(setup_command, cwd=worktree)

    prompt = build_prompt(agent, allowed_paths)
    quoted_prompt = shlex.quote(prompt)

    run(f"codex exec {quoted_prompt}", cwd=worktree)

    check_protected_files(worktree)
    check_scope(worktree, allowed_paths)

    if test_command:
        run(test_command, cwd=worktree)

    changed = output("git diff --name-only", cwd=worktree)
    if not changed:
        print(f"No changes from {name}")
        return {
            "name": name,
            "branch": branch,
            "worktree": worktree,
            "changed": False,
            "success": True,
        }

    run("git add .", cwd=worktree)
    run(f"git commit -m {shlex.quote('update from ' + name)}", cwd=worktree)

    return {
        "name": name,
        "branch": branch,
        "worktree": worktree,
        "changed": True,
        "success": True,
    }


def merge_result(result, base_branch, test_command, post_merge_command):
    name = result["name"]
    branch = result["branch"]

    if not result["changed"]:
        print(f"Skipping merge for {name}; no changes.")
        return

    print(f"\n=== Merging {name} ===")

    run(f"git checkout {shlex.quote(base_branch)}", cwd=REPO_ROOT)
    run(f"git merge --no-ff {shlex.quote(branch)}", cwd=REPO_ROOT)

    if test_command:
        run(test_command, cwd=REPO_ROOT)

    if post_merge_command:
        run(post_merge_command, cwd=REPO_ROOT)

    print(f"Accepted {name}")


def main():
    config = load_config()

    base_branch = config.get("base_branch", "main")
    test_command = config.get("test_command", "")
    setup_command = config.get("setup_command", "")
    post_merge_command = config.get("post_merge_command", "")
    global_shared_paths = config.get("shared_paths_global", [])
    agents = sorted(config["agents"], key=lambda a: a.get("priority", 100))

    execution = config.get("execution", {})
    max_parallel = execution.get("max_parallel", len(agents))

    run(f"git checkout {shlex.quote(base_branch)}")
    run("git pull --ff-only")

    if setup_command:
        run(setup_command)

    print(f"\nRunning {len(agents)} agents in parallel...")
    print(f"Max parallel agents: {max_parallel}")

    results = []

    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {
            executor.submit(run_agent, agent, base_branch, test_command, global_shared_paths): agent
            for agent in agents
        }

        for future in as_completed(futures):
            agent = futures[future]
            name = agent["name"]

            try:
                result = future.result()
                results.append(result)
                print(f"\nAgent finished: {name}")
            except Exception as e:
                print(f"\nAgent failed: {name}")
                print(e)

    successful_results = [
        r for r in results
        if r["success"] and r["changed"]
    ]

    print("\nAll agents finished. Merging successful branches one at a time...")

    for result in successful_results:
        try:
            merge_result(result, base_branch, test_command, post_merge_command)
        except Exception as e:
            print(f"\nMerge failed for {result['name']}")
            print(e)
            print("Stopping merges to protect the base branch.")
            break

    print("\nDone.")


if __name__ == "__main__":
    main()
