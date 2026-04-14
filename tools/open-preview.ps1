param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [ValidateSet("en", "zh")]
    [string]$Lang = "zh"
)

$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) "scripts\open-preview.ps1"
& $scriptPath -ProjectRoot $ProjectRoot -Lang $Lang
