# Script para iniciar servidor VerificarSMS accesible en la red local
# Ejecutar normalmente (no requiere permisos de administrador)

Write-Host ""
Write-Host "Iniciando servidor VerificarSMS..." -ForegroundColor Cyan
Write-Host "============================================================"
Write-Host ""

# Obtener IP local (priorizar Ethernet sobre interfaces virtuales)
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | 
    Where-Object {
        $_.InterfaceAlias -like "Ethernet*" -and 
        $_.IPAddress -notlike "127.*" -and 
        $_.IPAddress -notlike "169.254.*"
    } | 
    Select-Object -First 1).IPAddress

# Si no encuentra Ethernet, buscar cualquier IP DHCP que no sea virtual
if (-not $localIP) {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | 
        Where-Object {
            $_.PrefixOrigin -eq "Dhcp" -and 
            $_.IPAddress -notlike "127.*" -and 
            $_.IPAddress -notlike "172.*" -and 
            $_.IPAddress -notlike "192.168.137.*"
        } | 
        Select-Object -First 1).IPAddress
}

if ($localIP) {
    Write-Host "Tu IP en la red: $localIP" -ForegroundColor Green
    Write-Host ""
    Write-Host "El servidor estara accesible en:" -ForegroundColor Cyan
    Write-Host "   http://$localIP`:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Tus companeros pueden acceder desde:" -ForegroundColor Cyan
    Write-Host "   http://$localIP`:8000" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "No se pudo detectar IP automaticamente" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "============================================================"
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host ""
Write-Host "============================================================"
Write-Host ""

# Iniciar servidor en todas las interfaces de red (0.0.0.0)
& ".\python-dotenv\Scripts\python.exe" -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
