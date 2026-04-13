param(
    [string]$CommitMessage = "Initial commit: Vibe Paper",
    [string]$GitUserName,
    [string]$GitUserEmail
)

$repoRoot = Split-Path $PSScriptRoot -Parent

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    throw "git was not found on PATH. Install Git first."
}

Push-Location $repoRoot
try {
    if ($GitUserName) {
        & $git.Source config user.name $GitUserName
    }

    if ($GitUserEmail) {
        & $git.Source config user.email $GitUserEmail
    }

    if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
        & $git.Source init
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }

    & $git.Source branch -M main
    & $git.Source add .

    $configuredName = (& $git.Source config user.name)
    $configuredEmail = (& $git.Source config user.email)
    if (-not $configuredName -or -not $configuredEmail) {
        Write-Host "Git repository initialized, but no commit was created because git user.name or user.email is not configured." -ForegroundColor Yellow
        Write-Host "Run this script again with -GitUserName and -GitUserEmail, or configure Git globally first." -ForegroundColor Yellow
        exit 0
    }

    & $git.Source commit -m $CommitMessage

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git repository initialized, but commit may have been skipped because there were no new changes." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "Git repository initialized and initial commit created." -ForegroundColor Green
} finally {
    Pop-Location
}
