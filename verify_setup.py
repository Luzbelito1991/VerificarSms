"""
🔍 Script de Verificación de Entorno - VerificarSms
Verifica que el entorno esté correctamente configurado antes de ejecutar
"""
import os
import sys
from pathlib import Path

# Colores
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def check(name, condition, required=True):
    """Verifica una condición y muestra el resultado"""
    icon = "✅" if condition else ("❌" if required else "⚠️")
    color = Colors.GREEN if condition else (Colors.RED if required else Colors.YELLOW)
    status = "OK" if condition else ("FALTA" if required else "OPCIONAL")
    
    print(f"{icon} {color}{name:<40} {status}{Colors.END}")
    return condition

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("🔍 VERIFICACIÓN DE ENTORNO - VerificarSms")
    print(f"{'='*60}{Colors.END}\n")
    
    checks_required = []
    checks_optional = []
    
    # Verificaciones requeridas
    print(f"{Colors.BOLD}📋 VERIFICACIONES REQUERIDAS:{Colors.END}\n")
    
    checks_required.append(check(
        "Entorno virtual (python-dotenv/)",
        Path("python-dotenv").exists()
    ))
    
    checks_required.append(check(
        "Archivo .env",
        Path(".env").exists()
    ))
    
    checks_required.append(check(
        "Base de datos (usuarios.db)",
        Path("usuarios.db").exists()
    ))
    
    checks_required.append(check(
        "Carpeta backend/",
        Path("backend").exists()
    ))
    
    checks_required.append(check(
        "requirements.txt",
        Path("requirements.txt").exists()
    ))
    
    # Verificar SECRET_KEY en .env
    secret_key_ok = False
    if Path(".env").exists():
        with open(".env", 'r', encoding='utf-8') as f:
            content = f.read()
            secret_key_ok = "SECRET_KEY=" in content and \
                          "tu-clave-secreta-muy-segura-cambiar-en-produccion" not in content
    
    checks_required.append(check(
        "SECRET_KEY configurada",
        secret_key_ok
    ))
    
    # Verificaciones opcionales
    print(f"\n{Colors.BOLD}📋 VERIFICACIONES OPCIONALES:{Colors.END}\n")
    
    checks_optional.append(check(
        "CSS compilado (static/css/style.css)",
        Path("static/css/style.css").exists(),
        required=False
    ))
    
    checks_optional.append(check(
        "node_modules/ (Tailwind CSS)",
        Path("node_modules").exists(),
        required=False
    ))
    
    checks_optional.append(check(
        "package.json",
        Path("package.json").exists(),
        required=False
    ))
    
    # Verificar SMS_API_KEY en .env
    sms_key_ok = False
    if Path(".env").exists():
        with open(".env", 'r', encoding='utf-8') as f:
            content = f.read()
            sms_key_ok = "SMS_API_KEY=" in content and \
                        "tu-api-key-aqui" not in content
    
    checks_optional.append(check(
        "SMS_API_KEY configurada (envíos reales)",
        sms_key_ok,
        required=False
    ))
    
    # Resumen
    print("\n" + "="*60)
    required_ok = all(checks_required)
    
    if required_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ TODAS LAS VERIFICACIONES REQUERIDAS PASARON{Colors.END}")
        print(f"\n{Colors.BLUE}🚀 Puedes iniciar el servidor con:{Colors.END}")
        
        if sys.platform == "win32":
            print(f"\n   {Colors.BLUE}python-dotenv\\Scripts\\activate{Colors.END}")
            print(f"   {Colors.BLUE}uvicorn backend.main:app --reload{Colors.END}\n")
        else:
            print(f"\n   {Colors.BLUE}source python-dotenv/bin/activate{Colors.END}")
            print(f"   {Colors.BLUE}uvicorn backend.main:app --reload{Colors.END}\n")
        
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ FALTAN CONFIGURACIONES REQUERIDAS{Colors.END}")
        print(f"\n{Colors.YELLOW}💡 Solución:{Colors.END}")
        print(f"   Ejecuta: {Colors.BLUE}python setup.py{Colors.END} para configurar todo automáticamente")
        print(f"   O sigue el README.md para instalación manual\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.END}\n")
        sys.exit(1)
