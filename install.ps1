$ErrorActionPreference = "Stop"
# Ziro PowerShell launcher - single source of truth is the Python engine (ziro/).
# Works when run from a file or when piped via iex (no script file).
# Mirrors install.sh behavior on Unix.

$repoUrl = "https://github.com/Pakrohk-DotFiles/ziro-shell.git"

# --- Locate Python 3 ---
$python = $null
foreach ($c in @("python3", "py", "python")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) {
    Write-Host "error: Python 3 is required. Install python3 and retry." -ForegroundColor Red
    exit 1
}

# --- Locate the engine (ziro/) ---
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$engine = $null

if ($scriptDir -and (Test-Path (Join-Path $scriptDir "ziro"))) {
    $engine = Join-Path $scriptDir "ziro"
} elseif (Test-Path "$HOME\.ziro\ziro") {
    # Piped via iex: engine already installed at ~/.ziro
    $engine = "$HOME\.ziro\ziro"
} elseif (Get-Command git -ErrorAction SilentlyContinue) {
    # Piped and not installed yet: shallow-clone the engine to a temp dir
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("ziro-install-" + [System.Guid]::NewGuid().ToString("N").Substring(0, 8))
    Write-Host "[*] Cloning Ziro to $tmp ..."
    git clone --depth 1 $repoUrl $tmp 2>$null
    if ($LASTEXITCODE -eq 0 -and (Test-Path (Join-Path $tmp "ziro"))) {
        $engine = Join-Path $tmp "ziro"
    } else {
        Write-Host "error: failed to clone $repoUrl" -ForegroundColor Red
        exit 1
    }
}

if (-not $engine) {
    Write-Host "error: Ziro engine (ziro/) not found and git is unavailable to fetch it." -ForegroundColor Red
    Write-Host "  Install git, or clone the repo and run install.ps1 from it." -ForegroundColor Red
    exit 1
}

if ($python -match "py\.exe$") { & $python -3 $engine install @args }
else { & $python $engine install @args }
exit $LASTEXITCODE
