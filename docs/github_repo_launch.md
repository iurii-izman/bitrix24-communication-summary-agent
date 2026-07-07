# GitHub Repo Launch Guide

## Goal

Turn the local repository into a strong public GitHub repository with current community-health conventions and clean presentation.

## Already Prepared In This Repository

- `README.md`
- `LICENSE`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `.github/workflows/ci.yml`
- `.github/dependabot.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/CODEOWNERS.example`

## Required Manual GitHub Settings

These cannot be fully applied from the local filesystem alone.

1. Create the GitHub repository with visibility chosen intentionally.
2. Add the repository description from [docs/publication_pack.md](./publication_pack.md).
3. Add repository topics from [docs/publication_pack.md](./publication_pack.md).
4. Upload a social preview image once final screenshots are captured.
5. Enable Issues.
6. Enable Discussions if you want questions outside the issue tracker.
7. Enable Dependabot security updates.
8. Configure branch protection or rulesets for `main`.

## Recommended Ruleset For `main`

- require pull request before merge
- require at least 1 approval
- require status checks to pass
- include the `ci` workflow as a required check
- block force pushes
- block branch deletion

Only enable code-owner review after replacing `.github/CODEOWNERS.example` with a real `.github/CODEOWNERS` file that references actual GitHub users or teams with write access.

## Badge Upgrade After Remote Exists

The README uses safe static badges right now so it renders correctly before the public remote exists.

After the repository is pushed, replace the static CI badge with a live GitHub Actions badge:

```md
![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)
```

Optional GitHub-native badges:

```md
![Last Commit](https://img.shields.io/github/last-commit/<owner>/<repo>)
![Issues](https://img.shields.io/github/issues/<owner>/<repo>)
![Stars](https://img.shields.io/github/stars/<owner>/<repo>?style=social)
```

Use these only after the repository exists publicly; otherwise the README will show broken images.

## CODEOWNERS Activation

1. Copy `.github/CODEOWNERS.example` to `.github/CODEOWNERS`.
2. Replace `@your-github-handle` with the real owner or team.
3. Commit the file to `main`.
4. Then enable code-owner review in branch protection if desired.

## Suggested First Push

```powershell
git remote add origin <repo-url>
git push -u origin main
git push origin v0.1.0
```

## Suggested Post-Push Audit

- confirm the README badges render
- confirm issue forms appear on `New issue`
- confirm the PR template appears on `New pull request`
- confirm the community profile shows green checks for core files
- confirm `ci` runs on the initial push
- confirm Dependabot is active
