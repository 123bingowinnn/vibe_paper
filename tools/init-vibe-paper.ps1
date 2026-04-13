param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [string]$Title,
    [string]$Author = "Author Name",
    [string]$Affiliation = "School / Department",
    [string]$Email = "author@example.com",
    [switch]$Force
)

$repoRoot = Split-Path $PSScriptRoot -Parent
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python was not found on PATH. Install Python 3.10+ first."
}

Push-Location $repoRoot
try {
    $argsList = @("-m", "core.cli", "init", "--project-root", $ProjectRoot, "--author", $Author, "--affiliation", $Affiliation, "--email", $Email)
    if ($Title) {
        $argsList += @("--title", $Title)
    }
    if ($Force) {
        $argsList += "--force"
    }
    & $python.Source @argsList
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

