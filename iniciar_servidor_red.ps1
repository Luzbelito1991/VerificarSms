# Script para iniciar servidor VerificarSMS accesible en la red local
# Ejecutar normalmente (no requiere permisos de administrador)

Write-Host ""
Write-Host "🚀 Iniciando servidor VerificarSMS..." -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Obtener IP local
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | 
    Where-Object {$_.PrefixOrigin -eq "Dhcp" -or ($_.PrefixOrigin -eq "Manual" -and $_.IPAddress -notlike "127.*")} | 
    Select-Object -First 1).IPAddress

if ($localIP) {
    Write-Host "📡 Tu IP en la red: $localIP" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 El servidor estará accesible en:" -ForegroundColor Cyan
    Write-Host "   http://$localIP:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "👥 Tus compañeros pueden acceder desde:" -ForegroundColor Cyan
    Write-Host "   http://$localIP:8000" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "⚠️  No se pudo detectar IP automáticamente" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "=" * 60
Write-Host ""
Write-Host "🔥 Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host ""
Write-Host "=" * 60
Write-Host ""

# Iniciar servidor en todas las interfaces de red (0.0.0.0)
& ".\python-dotenv\Scripts\python.exe" -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
