#!/bin/bash
# Script para probar la instalación de Docker

echo "🐋 Verificando instalación de Docker..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para checkear comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 está instalado${NC}"
        $1 --version | head -1
        return 0
    else
        echo -e "${RED}❌ $1 NO está instalado${NC}"
        return 1
    fi
}

# Verificar Docker
check_command docker

# Verificar Docker Compose
check_command docker-compose || check_command "docker compose"

echo ""
echo "📋 Verificando archivos necesarios..."

# Verificar archivos
files=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    "docker-entrypoint.sh"
)

all_files_ok=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file existe${NC}"
    else
        echo -e "${RED}❌ $file NO existe${NC}"
        all_files_ok=false
    fi
done

echo ""
if [ "$all_files_ok" = true ]; then
    echo -e "${GREEN}🎉 Todo listo para usar Docker!${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. cp .env.docker .env"
    echo "  2. Edita .env con tus configuraciones"
    echo "  3. docker-compose up -d"
    echo ""
    echo "O usa el Makefile:"
    echo "  make init    # Crear .env"
    echo "  make up      # Levantar servicios"
    echo "  make logs    # Ver logs"
else
    echo -e "${RED}⚠️  Faltan archivos necesarios${NC}"
    exit 1
fi
