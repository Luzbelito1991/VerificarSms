#!/bin/bash
# Docker Entrypoint Script para VerificarSms
set -e

echo "🚀 Iniciando VerificarSms..."

# Función para esperar a que PostgreSQL esté listo
wait_for_postgres() {
    echo "⏳ Esperando a que PostgreSQL esté listo..."
    
    # Extraer credenciales de DATABASE_URL
    if [ -n "$DATABASE_URL" ]; then
        # Formato: postgresql://user:pass@host:port/db
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
        DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)$/\1/p')
        
        echo "   Host: $DB_HOST"
        echo "   Port: $DB_PORT"
        echo "   User: $DB_USER"
        echo "   DB: $DB_NAME"
        
        max_attempts=30
        attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; then
                echo "✅ PostgreSQL está listo"
                return 0
            fi
            attempt=$((attempt + 1))
            echo "   Intento $attempt/$max_attempts..."
            sleep 2
        done
        
        echo "❌ PostgreSQL no respondió a tiempo"
        exit 1
    fi
}

# Función para inicializar la base de datos
init_database() {
    echo "📊 Inicializando base de datos..."
    python -m backend.init_db
    
    if [ $? -eq 0 ]; then
        echo "✅ Base de datos inicializada"
    else
        echo "⚠️  La base de datos ya estaba inicializada"
    fi
}

# Función para crear usuario admin por defecto
create_admin_user() {
    echo "👤 Verificando usuario administrador..."
    python -c "
from backend.database import SessionLocal
from backend.models import Usuario
import hashlib

db = SessionLocal()
try:
    admin = db.query(Usuario).filter(Usuario.usuario == 'admin').first()
    if not admin:
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        admin = Usuario(
            usuario='admin',
            password=password_hash,
            rol='admin',
            sucursal='776'
        )
        db.add(admin)
        db.commit()
        print('✅ Usuario admin creado (usuario: admin, contraseña: admin123)')
        print('⚠️  IMPORTANTE: Cambia esta contraseña después del primer login')
    else:
        print('ℹ️  Usuario admin ya existe')
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()
"
}

# Función para mostrar información del entorno
show_environment() {
    echo ""
    echo "🔧 Configuración del entorno:"
    echo "   DEBUG: ${DEBUG:-false}"
    echo "   ENVIRONMENT: ${ENVIRONMENT:-production}"
    echo "   SMS_MODO_SIMULADO: ${SMS_MODO_SIMULADO:-false}"
    echo "   DATABASE: $(echo $DATABASE_URL | sed 's/:.*@/@***@/')"
    if [ -n "$REDIS_URL" ]; then
        echo "   REDIS: Habilitado"
    fi
    echo ""
}

# === Ejecución principal ===

# Si se está usando PostgreSQL, esperar a que esté listo
if [[ "$DATABASE_URL" == postgresql://* ]]; then
    wait_for_postgres
fi

# Inicializar base de datos
init_database

# Crear usuario admin si no existe
create_admin_user

# Mostrar información del entorno
show_environment

echo "🎉 Inicialización completada"
echo "🚀 Ejecutando: $@"
echo ""

# Ejecutar el comando proporcionado (por defecto uvicorn)
exec "$@"
