# Git Best Practices Skill

## Description
Use this skill whenever performing git push or git pull operations. It enforces best practices for branch management, commit hygiene, and safe remote operations.

## Git Push Best Practices

When pushing code:

1. **Pre-push checks**:
   - Run `git status` to verify you're on the correct branch
   - Run `git diff --cached` to review staged changes (if any uncommitted work)
   - Ensure the working tree is clean or all intended changes are committed
   - Run `git log --oneline -5` to verify recent commits look correct

2. **Push command**:
   - Always use `git push -u origin <branch-name>` to set upstream tracking
   - Never force push (`--force` or `-f`) without explicit user approval
   - Never push directly to `main` or `master` without explicit permission

3. **Network resilience**:
   - If push fails due to network errors, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
   - If push fails due to rejected updates (non-fast-forward), do NOT force push — pull first, resolve conflicts, then retry

4. **Post-push verification**:
   - Run `git log --oneline origin/<branch-name> -3` to verify the remote has the expected commits

## Git Pull Best Practices

When pulling code:

1. **Pre-pull checks**:
   - Run `git status` to check for uncommitted changes
   - If there are uncommitted changes, stash them first with `git stash` or commit them
   - Verify you're on the correct branch with `git branch --show-current`

2. **Pull command**:
   - Prefer `git pull origin <branch-name>` to be explicit about the source
   - For fetching without merging, use `git fetch origin <branch-name>` first
   - Use `git pull --rebase origin <branch-name>` when appropriate to keep history linear

3. **Network resilience**:
   - If pull/fetch fails due to network errors, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

4. **Post-pull checks**:
   - Run `git log --oneline -5` to review what was pulled
   - If stashed changes exist, apply them with `git stash pop` and resolve any conflicts

## Branch Naming Conventions

- Feature branches: `claude/<feature-name>-<session-id>`
- Always verify the branch name before pushing
- Never create or push to branches outside the designated pattern without permission

## Commit Best Practices

- Write clear, descriptive commit messages
- Use conventional commit format when possible (e.g., `feat:`, `fix:`, `chore:`, `docs:`)
- Keep commits focused — one logical change per commit
- Never use `--no-verify` to skip pre-commit hooks unless explicitly requested

## Safety Rules

- NEVER run `git reset --hard` without user confirmation
- NEVER run `git clean -f` without user confirmation
- NEVER delete remote branches without user confirmation
- NEVER amend commits that have already been pushed
- Always prefer creating new commits over rewriting history
