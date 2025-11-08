# Comandos Útiles para Debugging y Monitoreo

## Monitoreo de Servicios

### Ver estado de todos los contenedores
```bash
docker-compose ps
```

### Ver uso de recursos
```bash
docker stats
```

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f crawler
docker-compose logs -f ingest
docker-compose logs -f api
docker-compose logs -f web

# Últimas 100 líneas
docker-compose logs --tail=100 crawler
```

## Debugging de Bases de Datos

### MySQL

#### Conectar a MySQL
```bash
docker exec -it indexation_engine-mysql-1 mysql -u searchuser -psearchpass searchdb
```

#### Consultas útiles
```sql
-- Ver cuántos documentos hay
SELECT COUNT(*) FROM documents;

-- Ver últimos 10 documentos indexados
SELECT document_id, url, title, crawl_timestamp 
FROM documents 
ORDER BY crawl_timestamp DESC 
LIMIT 10;

-- Buscar por palabra en título
SELECT url, title 
FROM documents 
WHERE title LIKE '%python%' 
LIMIT 5;

-- Ver dominios más indexados
SELECT source, COUNT(*) as count 
FROM documents 
GROUP BY source 
ORDER BY count DESC 
LIMIT 10;
```

### PostgreSQL

#### Conectar a PostgreSQL
```bash
docker exec -it indexation_engine-postgres-1 psql -U searchuser -d indexdb
```

#### Consultas útiles
```sql
-- Ver cuántos tokens únicos hay
SELECT COUNT(DISTINCT token) FROM inverted_index;

-- Ver tokens más frecuentes
SELECT token, COUNT(*) as doc_count, SUM(frequency) as total_freq
FROM inverted_index
GROUP BY token
ORDER BY doc_count DESC
LIMIT 20;

-- Buscar documentos que contienen un token
SELECT document_id, frequency
FROM inverted_index
WHERE token = 'python'
ORDER BY frequency DESC
LIMIT 10;

-- Ver cuántos documentos están indexados
SELECT COUNT(DISTINCT document_id) FROM inverted_index;

-- Ver tamaño de la tabla
SELECT pg_size_pretty(pg_total_relation_size('inverted_index'));
```

### MongoDB

#### Conectar a MongoDB
```bash
docker exec -it indexation_engine-mongodb-1 mongosh -u root -p rootpass
```

#### Comandos útiles
```javascript
// Usar la base de datos
use contentdb

// Contar documentos
db.documents.countDocuments()

// Ver un documento de ejemplo
db.documents.findOne()

// Buscar por document_id
db.documents.findOne({document_id: "abc123"})

// Ver documentos más recientes
db.documents.find().sort({crawl_timestamp: -1}).limit(5)

// Buscar en contenido
db.documents.find({content: /python/i}).limit(5)

// Ver estadísticas de la colección
db.documents.stats()

// Ver tamaño de la base de datos
db.stats()
```

## Debugging de Kafka

### Ver topics
```bash
docker exec -it indexation_engine-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
```

### Ver mensajes en un topic
```bash
docker exec -it indexation_engine-kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic pages.raw \
  --from-beginning \
  --max-messages 5
```

### Ver consumer groups
```bash
docker exec -it indexation_engine-kafka-1 kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list
```

### Ver lag de un consumer group
```bash
docker exec -it indexation_engine-kafka-1 kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ingest-consumer-group \
  --describe
```

## Testing de API

### Health check
```bash
curl http://localhost:3001/api/health | jq
```

### Estadísticas
```bash
curl http://localhost:3001/api/stats | jq
```

### Búsqueda simple
```bash
curl "http://localhost:3001/api/search?q=python" | jq
```

### Búsqueda con paginación
```bash
curl "http://localhost:3001/api/search?q=database&page=2&limit=5" | jq
```

### Benchmark de búsquedas
```bash
# Medir tiempo de respuesta
time curl -s "http://localhost:3001/api/search?q=python" > /dev/null

# Múltiples búsquedas
for i in {1..10}; do
  time curl -s "http://localhost:3001/api/search?q=test$i" > /dev/null
done
```

## Debugging del Crawler

### Ver progreso del crawler
```bash
docker-compose logs crawler | grep "Crawled"
```

### Ver errores del crawler
```bash
docker-compose logs crawler | grep -i "error"
```

### Reiniciar el crawler
```bash
docker-compose restart crawler
```

### Entrar al contenedor del crawler
```bash
docker exec -it indexation_engine-crawler-1 sh
```

### Ejecutar crawler manualmente
```bash
docker exec -it indexation_engine-crawler-1 scrapy crawl web_spider
```

## Debugging del Ingest Service

### Ver cuántos mensajes se están procesando
```bash
docker-compose logs ingest | grep "Processing:"
```

### Ver errores de procesamiento
```bash
docker-compose logs ingest | grep -i "error"
```

### Ver conexiones a bases de datos
```bash
docker-compose logs ingest | grep "connected"
```

## Limpieza y Reset

### Limpiar solo los datos (mantener imágenes)
```bash
docker-compose down -v
docker-compose up -d
```

### Limpiar todo y reconstruir
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Limpiar solo una base de datos

#### Limpiar MySQL
```bash
docker exec -it indexation_engine-mysql-1 mysql -u searchuser -psearchpass -e "DROP DATABASE searchdb; CREATE DATABASE searchdb;"
```

#### Limpiar PostgreSQL
```bash
docker exec -it indexation_engine-postgres-1 psql -U searchuser -d indexdb -c "DROP TABLE inverted_index;"
```

#### Limpiar MongoDB
```bash
docker exec -it indexation_engine-mongodb-1 mongosh -u root -p rootpass --eval "use contentdb; db.documents.drop()"
```

## Exportar Datos

### Exportar desde MySQL
```bash
docker exec indexation_engine-mysql-1 mysqldump -u searchuser -psearchpass searchdb > backup_mysql.sql
```

### Exportar desde PostgreSQL
```bash
docker exec indexation_engine-postgres-1 pg_dump -U searchuser indexdb > backup_postgres.sql
```

### Exportar desde MongoDB
```bash
docker exec indexation_engine-mongodb-1 mongodump -u root -p rootpass --db contentdb --out /tmp/backup
docker cp indexation_engine-mongodb-1:/tmp/backup ./backup_mongo
```

## Métricas y Performance

### Ver throughput del crawler
```bash
docker-compose logs crawler | grep "Crawled" | wc -l
```

### Ver throughput del ingest
```bash
docker-compose logs ingest | grep "Successfully processed" | wc -l
```

### Medir latencia de API (10 requests)
```bash
for i in {1..10}; do
  curl -s -o /dev/null -w "Request $i: %{time_total}s\n" "http://localhost:3001/api/search?q=python"
done
```

### Ver uso de CPU y memoria
```bash
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Troubleshooting Común

### Problema: Puerto ya en uso
```bash
# Ver qué proceso está usando el puerto
lsof -i :3000
lsof -i :3001

# Matar el proceso
kill -9 <PID>
```

### Problema: Contenedor en estado unhealthy
```bash
# Ver health check logs
docker inspect --format='{{json .State.Health}}' indexation_engine-api-1 | jq

# Reiniciar contenedor específico
docker-compose restart api
```

### Problema: Disco lleno
```bash
# Ver uso de disco por Docker
docker system df

# Limpiar imágenes no usadas
docker system prune -a

# Limpiar volúmenes no usados
docker volume prune
```

### Problema: Network issues
```bash
# Ver redes de Docker
docker network ls

# Inspeccionar red
docker network inspect indexation_engine_search-network

# Recrear red
docker-compose down
docker network prune
docker-compose up -d
```

## Scripts de Prueba

### Probar todo el pipeline
```bash
#!/bin/bash
echo "1. Verificando servicios..."
docker-compose ps

echo "2. Verificando API..."
curl -s http://localhost:3001/api/health | jq

echo "3. Verificando estadísticas..."
curl -s http://localhost:3001/api/stats | jq

echo "4. Probando búsqueda..."
curl -s "http://localhost:3001/api/search?q=python" | jq '.results | length'

echo "5. Verificando bases de datos..."
docker exec indexation_engine-mysql-1 mysql -u searchuser -psearchpass -e "SELECT COUNT(*) FROM searchdb.documents;"
docker exec indexation_engine-postgres-1 psql -U searchuser -d indexdb -c "SELECT COUNT(DISTINCT token) FROM inverted_index;"
docker exec indexation_engine-mongodb-1 mongosh -u root -p rootpass --quiet --eval "use contentdb; print(db.documents.countDocuments())"
```

## Monitoreo Continuo

### Watch de estadísticas (actualiza cada 5 segundos)
```bash
watch -n 5 'curl -s http://localhost:3001/api/stats | jq'
```

### Tail de logs de múltiples servicios
```bash
docker-compose logs -f crawler ingest api
```

### Ver últimas búsquedas en logs
```bash
docker-compose logs api | grep "Searching for:"
```
