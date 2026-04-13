param(
    [Parameter(Mandatory = $true)]
    [string]$TargetDir,
    [string]$Title = "Your Paper Title",
    [string]$Author = "Author Name",
    [string]$Affiliation = "School / Department",
    [string]$Email = "author@example.com",
    [switch]$Force
)

$repoRoot = Split-Path $PSScriptRoot -Parent

if ((Test-Path $TargetDir) -and -not $Force) {
    throw "Target directory already exists. Use -Force to overwrite."
}

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}

& (Join-Path $PSScriptRoot "init-vibe-paper.ps1") `
    -ProjectRoot $TargetDir `
    -Title $Title `
    -Author $Author `
    -Affiliation $Affiliation `
    -Email $Email `
    -Force:$Force

Write-Host ("Created a new Vibe Paper project root at: {0}" -f $TargetDir) -ForegroundColor Green
