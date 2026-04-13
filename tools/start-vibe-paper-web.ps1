param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8765,
    [switch]$NoBrowser
)

$repoRoot = Split-Path $PSScriptRoot -Parent
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python was not found on PATH. Install Python 3.10+ first."
}

Push-Location $repoRoot
try {
    $argsList = @("-m", "app.server", "--project-root", $ProjectRoot, "--host", $BindHost, "--port", $Port)
    if (-not $NoBrowser) {
        $argsList += "--open-browser"
    }
    & $python.Source @argsList
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
