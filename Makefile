# Makefile para facilitar comandos comunes

.PHONY: help start stop restart logs stats health clean rebuild test

help:
	@echo "Motor de Búsqueda Distribuido - Comandos disponibles:"
	@echo ""
	@echo "  make start     - Iniciar todos los servicios"
	@echo "  make stop      - Detener todos los servicios"
	@echo "  make restart   - Reiniciar servicios"
	@echo "  make logs      - Ver logs de todos los servicios"
	@echo "  make stats     - Ver estadísticas del sistema"
	@echo "  make health    - Ver estado de salud"
	@echo "  make clean     - Limpiar contenedores y volúmenes"
	@echo "  make rebuild   - Reconstruir servicios desde cero"
	@echo "  make test      - Ejecutar pruebas básicas"
	@echo ""

start:
	@echo "🚀 Iniciando servicios..."
	docker-compose up -d
	@echo "✅ Servicios iniciados"
	@echo "📊 Web UI: http://localhost:3000"
	@echo "🔌 API: http://localhost:3001"

stop:
	@echo "🛑 Deteniendo servicios..."
	docker-compose down
	@echo "✅ Servicios detenidos"

restart:
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart
	@echo "✅ Servicios reiniciados"

logs:
	docker-compose logs -f

stats:
	@echo "📊 Estadísticas del sistema:"
	@curl -s http://localhost:3001/api/stats | python3 -m json.tool

health:
	@echo "🏥 Estado de salud:"
	@curl -s http://localhost:3001/api/health | python3 -m json.tool

clean:
	@echo "🧹 Limpiando contenedores y volúmenes..."
	docker-compose down -v
	@echo "✅ Limpieza completa"

rebuild:
	@echo "🔨 Reconstruyendo servicios..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Servicios reconstruidos"

test:
	@echo "🧪 Ejecutando pruebas básicas..."
	@echo "Verificando Web UI..."
	@curl -s -o /dev/null -w "Web UI: %{http_code}\n" http://localhost:3000
	@echo "Verificando API..."
	@curl -s -o /dev/null -w "API: %{http_code}\n" http://localhost:3001/api/health
	@echo "Verificando búsqueda..."
	@curl -s "http://localhost:3001/api/search?q=test" | python3 -m json.tool
