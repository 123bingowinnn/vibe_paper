param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [Parameter(Mandatory = $true)]
    [string]$Author,
    [Parameter(Mandatory = $true)]
    [string]$Affiliation,
    [Parameter(Mandatory = $true)]
    [string]$Email,
    [switch]$Force
)

$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) "tools\init-vibe-paper.ps1"
& $scriptPath -ProjectRoot $ProjectRoot -Title $Title -Author $Author -Affiliation $Affiliation -Email $Email -Force:$Force
