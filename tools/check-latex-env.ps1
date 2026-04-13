param()

$commands = @("pdflatex", "bibtex", "python")
$found = @{}

Write-Host "Checking Vibe Paper local environment..." -ForegroundColor Cyan
Write-Host ""

foreach ($cmd in $commands) {
    $resolved = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($resolved) {
        $found[$cmd] = $resolved.Source
        Write-Host ("[OK] {0} -> {1}" -f $cmd, $resolved.Source) -ForegroundColor Green
    } else {
            Write-Host ("[Missing] {0}" -f $cmd) -ForegroundColor Yellow
        }
}

if ($found.ContainsKey("python")) {
    try {
        & $found["python"] -c "import flask" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] flask -> Python module import succeeded" -ForegroundColor Green
        } else {
            Write-Host "[Missing] flask Python package" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[Missing] flask Python package" -ForegroundColor Yellow
    }
}

$commonPdflatex = @(
    (Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
    (Join-Path $env:ProgramFiles "MiKTeX\miktex\bin\x64\pdflatex.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "MiKTeX\miktex\bin\x64\pdflatex.exe")
)

if (-not $found.ContainsKey("pdflatex")) {
    foreach ($candidate in $commonPdflatex) {
        if (Test-Path $candidate) {
            Write-Host ""
            Write-Host ("Found pdflatex outside PATH: {0}" -f $candidate) -ForegroundColor Yellow
            break
        }
    }
}

Write-Host ""
Write-Host "Recommended minimum stack:" -ForegroundColor Cyan
Write-Host "- MiKTeX or TeX Live"
Write-Host "- Python 3.10+"
Write-Host "- Flask"
