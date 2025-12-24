# PowerShell script para verificar Docker en Windows
# Ejecutar: .\check_docker.ps1

Write-Host "🐋 Verificando instalación de Docker..." -ForegroundColor Blue
Write-Host ""

# Función para verificar comando
function Test-Command {
    param($Command)
    
    try {
        $version = & $Command --version 2>$null
        Write-Host "✅ $Command está instalado" -ForegroundColor Green
        Write-Host "   $version"
        return $true
    }
    catch {
        Write-Host "❌ $Command NO está instalado" -ForegroundColor Red
        return $false
    }
}

# Verificar Docker
$dockerOk = Test-Command "docker"

# Verificar Docker Compose
$composeOk = Test-Command "docker-compose"
if (-not $composeOk) {
    $composeOk = Test-Command "docker compose"
}

Write-Host ""
Write-Host "📋 Verificando archivos necesarios..." -ForegroundColor Blue

# Verificar archivos
$files = @(
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "docker-entrypoint.sh"
)

$allFilesOk = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file existe" -ForegroundColor Green
    }
    else {
        Write-Host "❌ $file NO existe" -ForegroundColor Red
        $allFilesOk = $false
    }
}

Write-Host ""
if ($dockerOk -and $composeOk -and $allFilesOk) {
    Write-Host "🎉 Todo listo para usar Docker!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Copy-Item .env.docker .env"
    Write-Host "  2. Edita .env con tus configuraciones"
    Write-Host "  3. docker-compose up -d"
    Write-Host ""
    Write-Host "O usa comandos directos:" -ForegroundColor Yellow
    Write-Host "  docker-compose ps      # Ver estado"
    Write-Host "  docker-compose logs -f # Ver logs"
    Write-Host "  docker-compose down    # Detener"
}
else {
    Write-Host "⚠️  Hay problemas con la configuración" -ForegroundColor Red
    
    if (-not $dockerOk) {
        Write-Host ""
        Write-Host "Instala Docker Desktop:" -ForegroundColor Yellow
        Write-Host "https://www.docker.com/products/docker-desktop"
    }
    
    if (-not $allFilesOk) {
        Write-Host ""
        Write-Host "Faltan archivos de configuración de Docker" -ForegroundColor Yellow
    }
    
    exit 1
}
