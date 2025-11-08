# Guía de Inicio Rápido

## Paso 1: Verificar Requisitos

```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar que Docker esté corriendo
docker ps
```

## Paso 2: Levantar el Sistema

```bash
# Desde la raíz del proyecto
cd /Users/sebasbose/Desktop/indexation_engine

# Dar permisos de ejecución al script
chmod +x manage.sh

# Iniciar todos los servicios
./manage.sh start

# O usar docker-compose directamente
docker-compose up -d
```

⏱️ **Tiempo estimado**: 2-3 minutos para descargar imágenes y levantar servicios

## Paso 3: Verificar que Todo Funcione

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver solo logs del crawler
docker-compose logs -f crawler

# Verificar estado de salud
./manage.sh health

# Ver estadísticas
./manage.sh stats
```

## Paso 4: Probar la Búsqueda

1. Abre tu navegador en: **http://localhost:3000**
2. Espera a que el crawler indexe algunas páginas (1-2 minutos)
3. Realiza una búsqueda, por ejemplo: "database"

## Verificación de Componentes

### Web UI
```bash
curl http://localhost:3000
```

### API
```bash
# Health check
curl http://localhost:3001/api/health

# Estadísticas
curl http://localhost:3001/api/stats

# Búsqueda de prueba
curl "http://localhost:3001/api/search?q=python"
```

### Bases de Datos

#### MySQL
```bash
docker exec -it indexation_engine-mysql-1 mysql -u searchuser -psearchpass -e "USE searchdb; SELECT COUNT(*) FROM documents;"
```

#### PostgreSQL
```bash
docker exec -it indexation_engine-postgres-1 psql -U searchuser -d indexdb -c "SELECT COUNT(DISTINCT token) FROM inverted_index;"
```

#### MongoDB
```bash
docker exec -it indexation_engine-mongodb-1 mongosh -u root -p rootpass --eval "use contentdb; db.documents.countDocuments()"
```

## Troubleshooting Común

### Problema: Los contenedores no inician

```bash
# Ver errores
docker-compose logs

# Reiniciar servicios
docker-compose restart

# Si persiste, limpiar y reiniciar
docker-compose down -v
docker-compose up -d
```

### Problema: No se indexan páginas

```bash
# Verificar que Kafka esté funcionando
docker-compose logs kafka

# Verificar que el crawler esté enviando datos
docker-compose logs crawler

# Verificar que ingest esté procesando
docker-compose logs ingest

# Reiniciar el crawler si es necesario
docker-compose restart crawler
```

### Problema: Búsquedas no retornan resultados

```bash
# Verificar cuántos documentos hay indexados
curl http://localhost:3001/api/stats

# Si no hay documentos, reiniciar el crawler
docker-compose restart crawler ingest

# Esperar 2-3 minutos y volver a verificar
```

### Problema: Puerto ya en uso

```bash
# Ver qué está usando el puerto 3000
lsof -i :3000

# Detener el proceso o cambiar el puerto en docker-compose.yml
```

## Comandos Útiles

```bash
# Ver todos los contenedores
docker-compose ps

# Detener todo
./manage.sh stop

# Limpiar todo (incluye datos)
./manage.sh clean

# Reconstruir desde cero
./manage.sh rebuild

# Ver logs en tiempo real de un servicio
docker-compose logs -f api

# Entrar a un contenedor
docker exec -it indexation_engine-api-1 sh
```

## Siguiente Paso: Personalización

### Agregar más URLs para crawlear

Edita: `services/crawler/crawler/spiders/web_spider.py`

```python
start_urls = [
    'https://tu-sitio-1.com',
    'https://tu-sitio-2.com',
    # Agregar más URLs aquí
]
```

Luego reinicia el crawler:
```bash
docker-compose restart crawler
```

### Ajustar límite de páginas

En el mismo archivo:
```python
custom_settings = {
    'CLOSESPIDER_PAGECOUNT': 1000,  # Cambiar a 1000 páginas
}
```

## Checklist de Entrega

- [ ] Sistema levantado con `docker-compose up`
- [ ] Crawler indexando páginas (verificar logs)
- [ ] Datos almacenados en las 3 bases de datos (verificar stats)
- [ ] API respondiendo correctamente (verificar health)
- [ ] Web UI funcionando y mostrando resultados
- [ ] Al menos 500 páginas indexadas
- [ ] Búsquedas funcionando correctamente
- [ ] Documentación actualizada

## Métricas Objetivo

- ✅ Mínimo 500 páginas indexadas
- ✅ Tiempo de respuesta < 1 segundo
- ✅ Sistema funcionando 24/7
- ✅ Tolerancia a fallos básica

## Recursos

- README principal: `README.md`
- Arquitectura detallada: `docs/arquitectura.md`
- Planteamiento original: `docs/planteamiento.md`
