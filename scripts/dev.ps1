$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

Write-Host "Iniciando Tailwind em modo watch..."
$tailwind = Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "watch:css") -NoNewWindow -PassThru

try {
    Write-Host "Iniciando Django em http://127.0.0.1:8000/"
    & ".\.venv\Scripts\python.exe" "manage.py" "runserver" "127.0.0.1:8000"
}
finally {
    if ($tailwind -and -not $tailwind.HasExited) {
        Stop-Process -Id $tailwind.Id
    }
}
