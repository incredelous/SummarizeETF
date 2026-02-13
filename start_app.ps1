param(
    [switch]$RefreshData,
    [switch]$InstallDeps
)

$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$FrontendDir = Join-Path $Root "frontend"

if (-not (Test-Path (Join-Path $Root "backend"))) {
    throw "backend directory not found: $Root"
}
if (-not (Test-Path $FrontendDir)) {
    throw "frontend directory not found: $FrontendDir"
}

if ($InstallDeps) {
    Write-Host "[1/4] Installing Python dependencies..."
    Set-Location -LiteralPath $Root
    python -m pip install -r requirements.txt

    Write-Host "[2/4] Installing frontend dependencies..."
    Set-Location -LiteralPath $FrontendDir
    npm.cmd install
}

if ($RefreshData) {
    Write-Host "[3/4] Refreshing index data..."
    Set-Location -LiteralPath $Root
    python backend/scripts/refresh_data.py
}

Write-Host "[4/4] Starting backend and frontend..."

$backendCmd = "Set-Location -LiteralPath `"$Root`"; python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000"
$frontendCmd = "Set-Location -LiteralPath `"$FrontendDir`"; npm.cmd run dev"

Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $backendCmd | Out-Null
Start-Sleep -Seconds 1
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $frontendCmd | Out-Null

Write-Host ""
Write-Host "Started:"
Write-Host "- Backend:  http://127.0.0.1:8000/health"
Write-Host "- Frontend: http://127.0.0.1:5173"
Write-Host ""
Write-Host "Tip: close the two opened PowerShell windows to stop the app."
