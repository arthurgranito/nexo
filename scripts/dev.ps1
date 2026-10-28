param([ValidateSet('up','down','migrate','seed','test','lint')][string]$Task='up')
$ErrorActionPreference='Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
 switch ($Task) {
  up { docker compose up --build -d }
  down { docker compose down }
  migrate { docker compose run --rm migrate }
  seed { docker compose --profile tools run --rm seed }
  test { Push-Location backend; try { python -m pytest -q } finally { Pop-Location } }
  lint { Push-Location backend; try { python -m ruff check . } finally { Pop-Location }; if ($LASTEXITCODE -eq 0) { Push-Location frontend; try { npm run typecheck } finally { Pop-Location } } }
 }
 if ($LASTEXITCODE -ne 0) { throw "Comando falhou: $LASTEXITCODE" }
} finally { Pop-Location }
