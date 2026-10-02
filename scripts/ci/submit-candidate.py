#!/usr/bin/env python3
"""Submit the current PR's reviewed source/base pair to ready-for-review CI."""

import argparse
import json
import re
import subprocess
import sys
from urllib.parse import quote


def command(*args):
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def gh_json(*args):
    return json.loads(command("gh", *args))


def current_pr():
    return gh_json("pr", "view", "--json",
                   "number,state,isDraft,headRefOid,baseRefOid,headRefName,baseRefName")


def require_candidate(pr, expected_head, expected_base, branch):
    if pr.get("state") != "OPEN":
        raise RuntimeError("PR must be open")
    if pr.get("headRefName") != branch:
        raise RuntimeError("local branch is not the PR head branch")
    if pr.get("headRefOid") != expected_head or pr.get("baseRefOid") != expected_base:
        raise RuntimeError("PR source/base changed; review the new candidate")


def workflow_has_run(repo, workflow, pr, expected_head, expected_base):
    branch = quote(pr["headRefName"], safe="")
    seen = 0
    for page in range(1, 101):
        data = gh_json("api", f"repos/{repo}/actions/workflows/{workflow}/runs?event=pull_request&branch={branch}&per_page=100&page={page}")
        runs = data["workflow_runs"]
        for run in runs:
            if run.get("event") != "pull_request":
                continue
            linked_numbers = [linked_pr.get("number") for linked_pr in run.get("pull_requests", [])]
            if linked_numbers and pr["number"] not in linked_numbers:
                continue
            immutable_head = run.get("head_sha")
            if not immutable_head:
                raise RuntimeError(f"run {run.get('id', '?')} has unknown head; inspect CI before resubmitting")
            if immutable_head != expected_head:
                continue
            if not linked_numbers:
                raise RuntimeError(f"run {run.get('id', '?')} has unknown PR; inspect CI before resubmitting")
            # GitHub mutates run.pull_requests[].head/base to the PR's current refs.
            # The workflow's run-name captures the source/base pair at event time.
            title = run.get("display_title", "")
            fingerprint = re.fullmatch(r"candidate head=([0-9a-f]{40}) base=([0-9a-f]{40})", title)
            if not fingerprint or fingerprint.group(1) != immutable_head:
                raise RuntimeError(f"run {run.get('id', '?')} has unknown base; inspect CI before resubmitting")
            if fingerprint.group(2) == expected_base:
                return True
        seen += len(runs)
        if seen >= data["total_count"]:
            return False
        if not runs:
            break
    raise RuntimeError("run list is incomplete; inspect CI before resubmitting")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", required=True, help="reviewed PR source commit SHA")
    parser.add_argument("--expected-base", required=True, help="reviewed target branch commit SHA")
    parser.add_argument("--workflow", action="append", required=True,
                        help="heavy CI workflow filename; repeat for each candidate workflow")
    args = parser.parse_args()
    for value in (args.expected_head, args.expected_base):
        if not re.fullmatch(r"[0-9a-f]{40}", value):
            parser.error("expected SHAs must be 40 lowercase hex characters")
    for workflow in args.workflow:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+\.ya?ml", workflow):
            parser.error("workflow must be a filename under .github/workflows")

    if command("git", "status", "--porcelain"):
        raise RuntimeError("working tree is dirty; commit and push before submitting")
    head = command("git", "rev-parse", "HEAD")
    branch = command("git", "branch", "--show-current")
    if not branch or head != args.expected_head:
        raise RuntimeError("local HEAD or branch does not match reviewed PR source")

    pr = current_pr()
    require_candidate(pr, args.expected_head, args.expected_base, branch)
    repo = gh_json("repo", "view", "--json", "nameWithOwner")["nameWithOwner"]
    runs = {workflow: workflow_has_run(repo, workflow, pr, args.expected_head, args.expected_base)
            for workflow in dict.fromkeys(args.workflow)}
    if any(runs.values()) and not all(runs.values()):
        raise RuntimeError("only some candidate workflows have runs; inspect CI before resubmitting")
    if all(runs.values()):
        if pr["isDraft"]:
            raise RuntimeError("candidate run exists but PR is draft; inspect CI before resubmitting")
        print(f"PR #{pr['number']} already has a run for head {head} / base {args.expected_base}; follow its checks")
        return

    # A ready PR needs a new ready_for_review event after a source/base fix.
    if not pr["isDraft"]:
        command("gh", "pr", "ready", str(pr["number"]), "--undo")
    require_candidate(current_pr(), args.expected_head, args.expected_base, branch)
    command("gh", "pr", "ready", str(pr["number"]))
    require_candidate(current_pr(), args.expected_head, args.expected_base, branch)
    print(f"Submitted PR #{pr['number']} head {head} / base {args.expected_base}; CI owner must verify all checks")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"candidate not submitted: {error}", file=sys.stderr)
        sys.exit(1)
