param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$candidates = @(
    (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe')
)
$pythonExe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $pythonExe) {
    Write-Host 'Python 3.10 ou supérieur est requis. Aucun Python compatible trouvé.'
    Read-Host 'Entrée pour fermer'
    exit 1
}
& $pythonExe (Join-Path $PSScriptRoot 'server.py') --port $Port --open
if ($LASTEXITCODE -ne 0) { Read-Host 'Entrée pour fermer' }
