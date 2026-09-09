$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($c in @("python3", "py", "python")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) {
    Write-Host "error: Python 3 is required. Install python3 and retry." -ForegroundColor Red
    exit 1
}
if ($python -match "py\.exe$") { & $python -3 "$scriptDir\ziro\" @args }
else { & $python "$scriptDir\ziro\" @args }
exit $LASTEXITCODE
