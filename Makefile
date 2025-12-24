# Makefile para VerificarSms
# Simplifica comandos comunes de Docker

.PHONY: help build up down restart logs logs-app logs-db shell-app shell-db clean test backup

# Colores para output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Muestra esta ayuda
	@echo "$(BLUE)VerificarSms - Comandos Disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ========================================
# 🐋 Docker Compose
# ========================================

build: ## Construir imágenes Docker
	@echo "$(BLUE)🔨 Construyendo imágenes...$(NC)"
	docker-compose build

up: ## Levantar servicios
	@echo "$(BLUE)🚀 Levantando servicios...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Servicios iniciados$(NC)"
	@echo "$(YELLOW)🌐 Accede a: http://localhost:8000$(NC)"

up-dev: ## Levantar servicios en modo desarrollo (con Tailwind)
	@echo "$(BLUE)🚀 Levantando servicios en modo desarrollo...$(NC)"
	docker-compose --profile dev up -d
	@echo "$(GREEN)✅ Servicios de desarrollo iniciados$(NC)"

down: ## Detener servicios
	@echo "$(BLUE)⏹️  Deteniendo servicios...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Servicios detenidos$(NC)"

restart: down up ## Reiniciar servicios

restart-app: ## Reiniciar solo la aplicación
	@echo "$(BLUE)🔄 Reiniciando aplicación...$(NC)"
	docker-compose restart app
	@echo "$(GREEN)✅ Aplicación reiniciada$(NC)"

# ========================================
# 📋 Logs
# ========================================

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-app: ## Ver logs de la aplicación
	docker-compose logs -f app

logs-db: ## Ver logs de PostgreSQL
	docker-compose logs -f postgres

logs-redis: ## Ver logs de Redis
	docker-compose logs -f redis

# ========================================
# 🔧 Shell Access
# ========================================

shell-app: ## Shell en el contenedor de la aplicación
	docker-compose exec app bash

shell-db: ## Shell en PostgreSQL
	docker-compose exec postgres psql -U admin -d verificarsms

shell-redis: ## Shell en Redis
	@echo "$(YELLOW)Usa AUTH con la contraseña de REDIS_PASSWORD$(NC)"
	docker-compose exec redis redis-cli

# ========================================
# 🗄️ Base de Datos
# ========================================

db-backup: ## Crear backup de la base de datos
	@echo "$(BLUE)💾 Creando backup...$(NC)"
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U admin verificarsms > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup creado en backups/$(NC)"

db-restore: ## Restaurar backup (usar: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)⚠️  Uso: make db-restore FILE=backups/backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📥 Restaurando backup $(FILE)...$(NC)"
	docker-compose exec -T postgres psql -U admin -d verificarsms < $(FILE)
	@echo "$(GREEN)✅ Backup restaurado$(NC)"

db-reset: ## Resetear base de datos (⚠️ ELIMINA TODOS LOS DATOS)
	@echo "$(YELLOW)⚠️  ADVERTENCIA: Esto eliminará todos los datos$(NC)"
	@read -p "¿Estás seguro? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)🗑️  Reseteando base de datos...$(NC)"
	docker-compose down -v
	docker-compose up -d
	@echo "$(GREEN)✅ Base de datos reseteada$(NC)"

# ========================================
# 🧪 Testing
# ========================================

test: ## Ejecutar tests
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	docker-compose exec app pytest

test-cov: ## Ejecutar tests con coverage
	@echo "$(BLUE)🧪 Ejecutando tests con coverage...$(NC)"
	docker-compose exec app pytest --cov=backend --cov-report=html
	@echo "$(GREEN)✅ Reporte en htmlcov/index.html$(NC)"

# ========================================
# 🏥 Health & Status
# ========================================

status: ## Ver estado de servicios
	@docker-compose ps

health: ## Verificar health check
	@echo "$(BLUE)🏥 Verificando salud de servicios...$(NC)"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "$(YELLOW)⚠️  Servicio no disponible$(NC)"

# ========================================
# 🧹 Limpieza
# ========================================

clean: ## Limpiar contenedores e imágenes
	@echo "$(BLUE)🧹 Limpiando...$(NC)"
	docker-compose down
	docker image prune -f
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-all: ## Limpieza completa (⚠️ elimina volúmenes)
	@echo "$(YELLOW)⚠️  ADVERTENCIA: Esto eliminará todos los datos$(NC)"
	@read -p "¿Estás seguro? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)🧹 Limpieza completa...$(NC)"
	docker-compose down -v
	docker system prune -a -f
	@echo "$(GREEN)✅ Limpieza completa$(NC)"

# ========================================
# 📊 Monitoring
# ========================================

stats: ## Ver estadísticas de recursos
	docker stats

ps: ## Ver procesos en contenedores
	docker-compose ps

# ========================================
# 🚀 Producción
# ========================================

prod-up: ## Levantar en modo producción
	@echo "$(BLUE)🚀 Levantando en modo producción...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  Archivo .env no encontrado$(NC)"; \
		echo "$(YELLOW)Copia .env.docker a .env y configura los valores$(NC)"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.yml up -d --build
	@echo "$(GREEN)✅ Servicios en producción iniciados$(NC)"

prod-logs: ## Ver logs de producción
	docker-compose -f docker-compose.yml logs -f

# ========================================
# 🔐 Seguridad
# ========================================

generate-secret: ## Generar nueva SECRET_KEY
	@echo "$(BLUE)🔐 Nueva SECRET_KEY:$(NC)"
	@python -c "import secrets; print(secrets.token_urlsafe(32))"

# ========================================
# 📦 Setup Inicial
# ========================================

init: ## Setup inicial completo
	@echo "$(BLUE)📦 Setup inicial...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creando archivo .env...$(NC)"; \
		cp .env.docker .env; \
	fi
	@echo "$(GREEN)✅ Archivo .env creado$(NC)"
	@echo "$(YELLOW)⚠️  IMPORTANTE:$(NC)"
	@echo "  1. Edita .env con tus configuraciones"
	@echo "  2. Genera SECRET_KEY con: make generate-secret"
	@echo "  3. Ejecuta: make up"
	@echo ""
