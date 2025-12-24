"""
🚀 Script de Inicialización - VerificarSms
Configura automáticamente el proyecto en nuevas máquinas
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(message, emoji="🔧"):
    """Imprime un paso del proceso"""
    print(f"\n{emoji} {Colors.BOLD}{message}{Colors.END}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_warning(message):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    """Imprime error"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Imprime información"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def check_python_version():
    """Verifica que la versión de Python sea adecuada"""
    print_step("Verificando versión de Python", "🐍")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8 o superior requerido. Tu versión: {version.major}.{version.minor}")
        sys.exit(1)
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def create_virtualenv():
    """Crea el entorno virtual si no existe"""
    print_step("Configurando entorno virtual", "🔮")
    
    venv_path = Path("python-dotenv")
    
    if venv_path.exists():
        print_warning("El entorno virtual ya existe")
        return True
    
    try:
        print_info("Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", "python-dotenv"], check=True)
        print_success("Entorno virtual creado")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error al crear entorno virtual: {e}")
        return False

def get_pip_command():
    """Obtiene el comando pip correcto según el SO"""
    if sys.platform == "win32":
        return str(Path("python-dotenv") / "Scripts" / "pip.exe")
    else:
        return str(Path("python-dotenv") / "bin" / "pip")

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print_step("Instalando dependencias", "📦")
    
    pip_cmd = get_pip_command()
    
    if not Path(pip_cmd).exists():
        print_error("No se encontró pip en el entorno virtual")
        return False
    
    try:
        print_info("Actualizando pip...")
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True, capture_output=True)
        
        print_info("Instalando requirements.txt...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        print_success("Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error al instalar dependencias: {e}")
        return False

def setup_env_file():
    """Configura el archivo .env"""
    print_step("Configurando variables de entorno", "🔐")
    
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if env_path.exists():
        print_warning(".env ya existe. No se sobrescribirá.")
        return True
    
    if not env_example.exists():
        print_error(".env.example no encontrado")
        return False
    
    try:
        # Copiar y personalizar
        shutil.copy(env_example, env_path)
        
        # Generar SECRET_KEY única
        import secrets
        secret_key = secrets.token_urlsafe(32)
        
        # Leer contenido
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar SECRET_KEY
        content = content.replace(
            'SECRET_KEY=tu-clave-secreta-muy-segura-cambiar-en-produccion',
            f'SECRET_KEY={secret_key}'
        )
        
        # Escribir de vuelta
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success(".env creado con SECRET_KEY única")
        print_warning("⚠️  IMPORTANTE: Configura SMS_API_KEY en .env para enviar SMS reales")
        return True
    except Exception as e:
        print_error(f"Error al crear .env: {e}")
        return False

def init_database():
    """Inicializa la base de datos"""
    print_step("Inicializando base de datos", "🗄️")
    
    db_path = Path("usuarios.db")
    
    if db_path.exists():
        print_warning("usuarios.db ya existe. No se reinicializará.")
        return True
    
    try:
        # Importar aquí para evitar errores si no hay .env
        from backend.init_db import init_db
        init_db()
        print_success("Base de datos inicializada")
        return True
    except Exception as e:
        print_error(f"Error al inicializar base de datos: {e}")
        return False

def create_admin_user():
    """Crea el usuario administrador por defecto"""
    print_step("Creando usuario administrador", "👤")
    
    try:
        from backend.database import SessionLocal
        from backend.models import Usuario
        import hashlib
        
        db = SessionLocal()
        
        # Verificar si ya existe admin
        admin_exists = db.query(Usuario).filter(Usuario.usuario == "admin").first()
        
        if admin_exists:
            print_warning("Usuario 'admin' ya existe")
            db.close()
            return True
        
        # Crear usuario admin
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        admin = Usuario(
            usuario="admin",
            password=password_hash,
            rol="admin",
            sucursal="776"
        )
        
        db.add(admin)
        db.commit()
        db.close()
        
        print_success("Usuario administrador creado")
        print_info("   Usuario: admin")
        print_info("   Contraseña: admin123")
        print_warning("   ⚠️  CAMBIA LA CONTRASEÑA después del primer login!")
        return True
        
    except Exception as e:
        print_error(f"Error al crear usuario admin: {e}")
        return False

def install_npm_dependencies():
    """Instala dependencias de Node.js (Tailwind CSS)"""
    print_step("Configurando Tailwind CSS", "🎨")
    
    package_json = Path("package.json")
    
    if not package_json.exists():
        print_warning("package.json no encontrado. Saltando instalación npm.")
        return True
    
    # Verificar si npm está disponible
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("npm no está instalado. Instálalo para compilar CSS:")
        print_info("   Descarga Node.js desde https://nodejs.org/")
        return True
    
    try:
        print_info("Instalando dependencias npm...")
        subprocess.run(["npm", "install"], check=True)
        print_success("Dependencias npm instaladas")
        
        print_info("Compilando CSS...")
        subprocess.run(["npm", "run", "build"], check=True)
        print_success("CSS compilado")
        return True
        
    except subprocess.CalledProcessError as e:
        print_warning(f"Error con npm: {e}")
        print_info("Puedes instalarlo manualmente con: npm install && npm run build")
        return True  # No es crítico

def verify_setup():
    """Verifica que todo esté configurado correctamente"""
    print_step("Verificando instalación", "🔍")
    
    checks = {
        "Entorno virtual": Path("python-dotenv").exists(),
        "Archivo .env": Path(".env").exists(),
        "Base de datos": Path("usuarios.db").exists(),
        "CSS compilado": Path("static/css/style.css").exists()
    }
    
    all_ok = True
    for check_name, status in checks.items():
        if status:
            print_success(f"{check_name}: OK")
        else:
            print_warning(f"{check_name}: FALTA")
            all_ok = False
    
    return all_ok

def print_next_steps():
    """Imprime los siguientes pasos"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 ¡Instalación completada!{Colors.END}")
    print("="*60)
    
    if sys.platform == "win32":
        activate_cmd = r"python-dotenv\Scripts\activate"
        run_cmd = "uvicorn backend.main:app --reload"
    else:
        activate_cmd = "source python-dotenv/bin/activate"
        run_cmd = "uvicorn backend.main:app --reload"
    
    print(f"\n{Colors.BOLD}📋 Siguientes pasos:{Colors.END}")
    print(f"\n1️⃣  Activar entorno virtual:")
    print(f"   {Colors.BLUE}{activate_cmd}{Colors.END}")
    
    print(f"\n2️⃣  Iniciar el servidor:")
    print(f"   {Colors.BLUE}{run_cmd}{Colors.END}")
    
    print(f"\n3️⃣  Abrir en navegador:")
    print(f"   {Colors.BLUE}http://localhost:8000{Colors.END}")
    
    print(f"\n4️⃣  Login con:")
    print(f"   {Colors.BLUE}Usuario: admin{Colors.END}")
    print(f"   {Colors.BLUE}Contraseña: admin123{Colors.END}")
    
    print(f"\n{Colors.YELLOW}⚠️  IMPORTANTE:{Colors.END}")
    print(f"   • Cambia la contraseña de admin después del primer login")
    print(f"   • Configura SMS_API_KEY en .env para SMS reales")
    print(f"   • SMS_MODO_SIMULADO=true imprime SMS en consola (útil para pruebas)")
    
    print("\n" + "="*60 + "\n")

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("🚀 CONFIGURACIÓN INICIAL - VerificarSms")
    print(f"{'='*60}{Colors.END}\n")
    
    # Verificar que estemos en el directorio correcto
    if not Path("backend").exists() or not Path("requirements.txt").exists():
        print_error("Este script debe ejecutarse desde la raíz del proyecto")
        sys.exit(1)
    
    steps = [
        ("Versión de Python", check_python_version),
        ("Entorno virtual", create_virtualenv),
        ("Dependencias Python", install_dependencies),
        ("Variables de entorno", setup_env_file),
        ("Base de datos", init_database),
        ("Usuario administrador", create_admin_user),
        ("Dependencias npm", install_npm_dependencies)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print_error(f"Error inesperado en {step_name}: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "="*60)
    
    if failed_steps:
        print_warning(f"⚠️  Algunos pasos fallaron: {', '.join(failed_steps)}")
        print_info("Revisa los errores arriba y ejecuta el script nuevamente")
        return 1
    
    verify_setup()
    print_next_steps()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Instalación cancelada por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)
