$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    py -m venv .venv
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
}
if (-not (Test-Path -LiteralPath 'results\retrieval.json')) {
    & '.\.venv\Scripts\python.exe' -m scripts.evaluate
}
Write-Host 'GearMate: http://127.0.0.1:8000 (Ctrl+C to stop)'
& '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000
