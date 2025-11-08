#!/bin/bash

# Script de utilidades para el motor de búsqueda distribuido

case "$1" in
  start)
    echo "🚀 Iniciando todos los servicios..."
    docker-compose up -d
    echo "✅ Servicios iniciados"
    echo "📊 Web UI: http://localhost:3000"
    echo "🔌 API: http://localhost:3001"
    ;;
    
  stop)
    echo "🛑 Deteniendo servicios..."
    docker-compose down
    echo "✅ Servicios detenidos"
    ;;
    
  restart)
    echo "🔄 Reiniciando servicios..."
    docker-compose restart
    echo "✅ Servicios reiniciados"
    ;;
    
  logs)
    if [ -z "$2" ]; then
      docker-compose logs -f
    else
      docker-compose logs -f "$2"
    fi
    ;;
    
  stats)
    echo "📊 Estadísticas del sistema:"
    curl -s http://localhost:3001/api/stats | python3 -m json.tool
    ;;
    
  health)
    echo "🏥 Estado de salud:"
    curl -s http://localhost:3001/api/health | python3 -m json.tool
    ;;
    
  clean)
    echo "🧹 Limpiando contenedores y volúmenes..."
    docker-compose down -v
    echo "✅ Limpieza completa"
    ;;
    
  rebuild)
    echo "🔨 Reconstruyendo servicios..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Servicios reconstruidos"
    ;;
    
  *)
    echo "Motor de Búsqueda Distribuido - Comandos disponibles:"
    echo ""
    echo "  ./manage.sh start      - Iniciar todos los servicios"
    echo "  ./manage.sh stop       - Detener todos los servicios"
    echo "  ./manage.sh restart    - Reiniciar servicios"
    echo "  ./manage.sh logs [srv] - Ver logs (opcionalmente de un servicio)"
    echo "  ./manage.sh stats      - Ver estadísticas del sistema"
    echo "  ./manage.sh health     - Ver estado de salud"
    echo "  ./manage.sh clean      - Limpiar contenedores y volúmenes"
    echo "  ./manage.sh rebuild    - Reconstruir servicios desde cero"
    echo ""
    echo "Servicios disponibles para logs:"
    echo "  - crawler"
    echo "  - ingest"
    echo "  - api"
    echo "  - web"
    echo "  - kafka"
    echo "  - mysql"
    echo "  - postgres"
    echo "  - mongodb"
    ;;
esac
