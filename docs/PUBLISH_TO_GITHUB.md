# Publish to GitHub

## What this guide covers

This guide explains how to turn the local Vibe Paper folder into a Git repository and push it to GitHub.

## 1. Initialize the local Git repository

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\init-git-repo.ps1 `
  -GitUserName "Your Name" `
  -GitUserEmail "you@example.com"
```

This script will:

- initialize a Git repository if one does not already exist
- rename the default branch to `main`
- stage all files
- create an initial commit

## 2. Create the GitHub repository

Create a new empty repository on GitHub, for example:

```text
Vibe-Paper
```

Do not add a README, `.gitignore`, or license on the GitHub website if the local repository already has them.

## 3. Add the remote and push

After you create the GitHub repository, run:

```powershell
git remote add origin https://github.com/<your-username>/Vibe-Paper.git
git push -u origin main
```

If the remote already exists, use:

```powershell
git remote set-url origin https://github.com/<your-username>/Vibe-Paper.git
git push -u origin main
```

## 4. If GitHub asks for authentication

Use one of the normal GitHub authentication methods on your machine:

- Git Credential Manager
- Personal access token
- GitHub Desktop
- SSH keys

## Recommended first release checklist

Before pushing publicly, check:

- the README title and quick start are correct
- no local-only absolute paths remain in committed docs
- example PDFs are acceptable to ship
- no private data, weights, or large datasets are included
- the example workflow still compiles after a clean checkout
