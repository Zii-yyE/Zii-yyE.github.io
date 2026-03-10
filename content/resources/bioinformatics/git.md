---
title: "Git"
date: 2026-03-10
summary: "A compact Git note: mental model, daily commands, undo patterns, and quick access to the local PDF references."
draft: false
showToc: true
weight: 1
---

<div style="margin: 0 0 1.4rem; padding: 1.1rem 1.1rem 1rem; border: 1px solid var(--border); border-radius: 18px; background: linear-gradient(180deg, var(--entry) 0%, color-mix(in srgb, var(--entry) 80%, var(--theme)) 100%);">
  <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; margin-bottom: 0.7rem;">
    <strong style="font-size: 1.05rem;">Quick references</strong>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.65rem;">
    <a href="/resources/bioinformatics/progit.pdf" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Git Pro PDF</a>
    <a href="/resources/bioinformatics/cheat-sheet.pdf" style="padding: 0.36rem 0.78rem; border: 1px solid var(--border); border-radius: 999px; background: var(--theme); color: var(--primary); text-decoration: none;">Git Cheat Sheet PDF</a>
  </div>
</div>

> Git is easiest when you think in **snapshots**, not files.

# Mental model

The three places that matter:

| Area | What it means | Command to inspect |
| --- | --- | --- |
| Working tree | files you are editing right now | `git status` |
| Index / staging area | what will go into the next commit | `git diff --cached` |
| Commit history | saved snapshots | `git log --oneline --graph --decorate` |

Useful interpretation:

- `git add` means "move this change into the next snapshot".
- `git commit` means "save the staged snapshot".
- `git push` means "publish local commits to the remote".
- `git pull --rebase` means "bring remote commits in, then replay mine on top".

# Daily workflow

The loop I actually use:

```bash
git status
git add -p
git commit -m "meaningful message"
git pull --rebase
git push
```

Why this loop is good:

- `git status` prevents confusion.
- `git add -p` forces clean, reviewable commits.
- `git pull --rebase` usually keeps history linear and easier to read.

# Commands worth memorizing

## Inspect

```bash
git status
git diff
git diff --cached
git log --oneline --graph --decorate --all
git show HEAD
```

## Stage and commit

```bash
git add path/to/file
git add -p
git commit -m "message"
git commit --amend
```

## Branching

```bash
git branch
git switch -c new-branch
git switch main
git merge other-branch
git rebase main
```

## Remote work

```bash
git fetch
git pull --rebase
git push
git push -u origin new-branch
```

# Undo safely

The important distinction is **whether the change is committed** and **whether it has been pushed**.

| Situation | Safer command | What it does |
| --- | --- | --- |
| Throw away unstaged edits in one file | `git restore file` | reset file in working tree |
| Unstage something | `git restore --staged file` | remove it from index |
| Edit the last commit message/content | `git commit --amend` | rewrite most recent local commit |
| Undo a published commit | `git revert <commit>` | create a new inverse commit |
| Move branch pointer backwards locally | `git reset --soft HEAD~1` | keep changes, remove commit |

Short rule:

- If it is already on GitHub, prefer `git revert`.
- If it is still local, `restore`, `amend`, or `reset --soft` are usually cleaner.

# Branches and remotes

## What a branch actually is

A branch is just a movable pointer to a commit.  
Creating a branch is cheap; use them freely.

## A remote is just another repo

Usually:

- `origin` = your GitHub repository
- `main` or `master` = primary branch
- feature branch = temporary branch for one task

Clean pattern:

```bash
git switch main
git pull --rebase
git switch -c fix/readme-links
```

# Handy aliases and config

```bash
git config --global pull.rebase true
git config --global rebase.autoStash true
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.st "status -sb"
```

What these do:

- `pull.rebase true`: `git pull` rebases by default.
- `rebase.autoStash true`: temporarily stashes dirty changes during rebase.
- `git lg`: compact history graph.
- `git st`: shorter status command.

# Practical habits

- Commit small units of thought.
- Write commit messages that describe **why**, not only **what**.
- Use branches for experiments.
- Read `git status` before and after every major command.
- Prefer `git add -p` over `git add .` when the change matters.
- Avoid force push on shared branches unless you are certain.

# When I forget what to do

My fallback sequence:

```bash
git status
git log --oneline --graph --decorate -10
git diff
git diff --cached
```

These four commands usually tell you where you are, what changed, and what Git thinks is about to happen.
