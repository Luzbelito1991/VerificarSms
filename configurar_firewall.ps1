# Script para abrir puerto 8000 en el firewall
# Ejecutar como Administrador: Click derecho -> "Ejecutar con PowerShell como Administrador"

Write-Host "🔥 Configurando Firewall de Windows..." -ForegroundColor Cyan
Write-Host ""

try {
    # Verificar si la regla ya existe
    $existingRule = Get-NetFirewallRule -DisplayName "VerificarSMS Server" -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "⚠️  La regla ya existe. Eliminando regla anterior..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName "VerificarSMS Server"
    }
    
    # Crear nueva regla
    New-NetFirewallRule `
        -DisplayName "VerificarSMS Server" `
        -Description "Permite conexiones entrantes al servidor FastAPI de VerificarSMS" `
        -Direction Inbound `
        -LocalPort 8000 `
        -Protocol TCP `
        -Action Allow `
        -Profile Domain,Private,Public `
        -Enabled True
    
    Write-Host ""
    Write-Host "✅ Firewall configurado correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "📡 Puerto 8000 abierto para conexiones entrantes" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Tu servidor será accesible desde otras PCs en la red" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Error al configurar firewall: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Asegúrate de ejecutar este script como Administrador" -ForegroundColor Yellow
    Write-Host "   Click derecho en el archivo -> 'Ejecutar con PowerShell como Administrador'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Presiona Enter para cerrar..."
Read-Host
