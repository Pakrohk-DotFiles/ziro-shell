$ErrorActionPreference = "Stop"
# Ziro PowerShell launcher - single source of truth is the Python engine (ziro/).
# Works when run from a file or when piped via iex (no script file).
# Mirrors install.sh behavior on Unix.

$repoUrl = "https://github.com/Pakrohk-DotFiles/ziro-shell.git"

# --- Locate Python 3.11+ (engine needs tomllib) ---
$python = $null
foreach ($c in @("python3", "py", "python")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    $verCheck = & $cmd.Source -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $python = $cmd.Source; break }
}
if (-not $python) {
    Write-Host "error: Python 3.11 or later is required (engine uses tomllib)." -ForegroundColor Red
    Write-Host "  Install from https://www.python.org/downloads/ or: winget install Python.Python.3.12" -ForegroundColor Yellow
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

# Default bare flags to the "install" subcommand (e.g. .\install.ps1 --server),
# but leave explicit subcommands (install/update/doctor/theme) and top-level
# flags untouched so they aren't double-prefixed.
$known = @("install", "update", "doctor", "theme", "--version", "-h", "--help")
$first = if ($args.Count -gt 0) { $args[0] } else { "" }
$engineArgs = @($args)
if ($first -notin $known) { $engineArgs = @("install") + $args }

if ($python -match "py\.exe$") { & $python -3 $engine @engineArgs }
else { & $python $engine @engineArgs }
exit $LASTEXITCODE
