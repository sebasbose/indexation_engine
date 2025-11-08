# ✅ Checklist de Verificación del Proyecto

## Pre-Inicio del Sistema

### Requisitos
- [ ] Docker instalado y funcionando
- [ ] Docker Compose instalado
- [ ] Al menos 4GB de RAM disponible
- [ ] Puertos disponibles: 3000, 3001, 3306, 5432, 27017, 9092, 2181

### Verificación de Archivos
- [ ] `docker-compose.yml` existe
- [ ] Carpeta `services/crawler` existe con código
- [ ] Carpeta `services/ingest` existe con código
- [ ] Carpeta `services/api` existe con código
- [ ] Carpeta `services/web` existe con código
- [ ] Archivo `manage.sh` es ejecutable

---

## Inicio del Sistema

### Levantar Servicios
```bash
cd /Users/sebasbose/Desktop/indexation_engine
make start
# o: docker-compose up -d
```

- [ ] Comando ejecutado sin errores
- [ ] Todos los contenedores iniciaron

### Verificar Contenedores
```bash
docker-compose ps
```

Debe mostrar 8 servicios:
- [ ] zookeeper (running)
- [ ] kafka (running)
- [ ] mysql (running)
- [ ] postgres (running)
- [ ] mongodb (running)
- [ ] crawler (running)
- [ ] ingest (running)
- [ ] api (running)
- [ ] web (running)

---

## Verificación de Infraestructura

### Kafka
```bash
docker-compose logs kafka | grep "started"
```
- [ ] Kafka broker started

### MySQL
```bash
docker exec indexation_engine-mysql-1 mysql -u searchuser -psearchpass -e "SELECT 1"
```
- [ ] Conexión exitosa a MySQL

### PostgreSQL
```bash
docker exec indexation_engine-postgres-1 psql -U searchuser -d indexdb -c "SELECT 1"
```
- [ ] Conexión exitosa a PostgreSQL

### MongoDB
```bash
docker exec indexation_engine-mongodb-1 mongosh -u root -p rootpass --quiet --eval "db.version()"
```
- [ ] Conexión exitosa a MongoDB

---

## Verificación de Servicios

### API Gateway
```bash
curl http://localhost:3001/api/health
```
- [ ] Retorna JSON con estado
- [ ] MySQL: connected
- [ ] PostgreSQL: connected
- [ ] MongoDB: connected

### Web Frontend
```bash
curl -I http://localhost:3000
```
- [ ] Retorna HTTP 200 OK

### Crawler
```bash
docker-compose logs crawler | grep "Crawled" | head -5
```
- [ ] Muestra páginas siendo crawleadas

### Ingest Service
```bash
docker-compose logs ingest | grep "connected"
```
- [ ] MySQL connected
- [ ] PostgreSQL connected
- [ ] MongoDB connected

```bash
docker-compose logs ingest | grep "Processing" | head -5
```
- [ ] Muestra mensajes siendo procesados

---

## Verificación de Datos

### Esperar 2-3 minutos para que se indexen páginas

### Verificar Estadísticas
```bash
curl http://localhost:3001/api/stats
```
- [ ] `documents` > 0
- [ ] `tokens` > 0
- [ ] `content_docs` > 0

### Verificar MySQL
```bash
docker exec indexation_engine-mysql-1 mysql -u searchuser -psearchpass -e "SELECT COUNT(*) as total FROM searchdb.documents"
```
- [ ] total > 0

### Verificar PostgreSQL
```bash
docker exec indexation_engine-postgres-1 psql -U searchuser -d indexdb -c "SELECT COUNT(DISTINCT token) as tokens FROM inverted_index"
```
- [ ] tokens > 0

### Verificar MongoDB
```bash
docker exec indexation_engine-mongodb-1 mongosh -u root -p rootpass --quiet --eval "use contentdb; db.documents.countDocuments()"
```
- [ ] count > 0

---

## Verificación de Búsquedas

### Búsqueda Simple
```bash
curl -s "http://localhost:3001/api/search?q=python" | jq '.results | length'
```
- [ ] Retorna resultados (length > 0)

### Búsqueda en UI
1. Abrir http://localhost:3000 en navegador
- [ ] Página carga correctamente
- [ ] Muestra estadísticas del sistema
- [ ] Barra de búsqueda visible

2. Realizar búsqueda: "database"
- [ ] Resultados aparecen
- [ ] Cada resultado muestra: título, URL, snippet, score

3. Probar diferentes búsquedas:
- [ ] "python" retorna resultados
- [ ] "computer" retorna resultados
- [ ] "web" retorna resultados

---

## Verificación de Logs

### Sin Errores Críticos
```bash
docker-compose logs | grep -i "error" | grep -v "404"
```
- [ ] No hay errores críticos (algunos 404 son normales)

### Crawler Activo
```bash
docker-compose logs crawler | tail -20
```
- [ ] Muestra actividad reciente
- [ ] Sin errores de conexión a Kafka

### Ingest Activo
```bash
docker-compose logs ingest | tail -20
```
- [ ] Muestra actividad reciente
- [ ] Procesa mensajes correctamente

---

## Verificación de Performance

### Latencia de Búsqueda
```bash
time curl -s "http://localhost:3001/api/search?q=python" > /dev/null
```
- [ ] Tiempo < 2 segundos

### Throughput de Crawling
```bash
docker-compose logs crawler | grep "Crawled" | wc -l
```
- [ ] Número aumenta con el tiempo

---

## Checklist de Día 1 (Después de 24 horas)

### Volumen de Datos
```bash
curl -s http://localhost:3001/api/stats | jq
```
- [ ] `documents` >= 300
- [ ] `tokens` >= 1000

### Estabilidad
```bash
docker-compose ps
```
- [ ] Todos los contenedores siguen running
- [ ] No hay contenedores en restart loop

---

## Checklist de Día 2 (Antes de entrega)

### Volumen Final
- [ ] `documents` >= 500
- [ ] Búsquedas funcionan correctamente
- [ ] UI responsive y funcional

### Documentación
- [ ] README actualizado
- [ ] Arquitectura documentada
- [ ] Comandos probados

### Demo Preparado
- [ ] Búsquedas de ejemplo preparadas
- [ ] Script de demo escrito
- [ ] Slides preparados

---

## Troubleshooting

### Si algún contenedor no inicia:
```bash
docker-compose logs [service-name]
docker-compose restart [service-name]
```

### Si no hay datos después de 5 minutos:
```bash
docker-compose restart crawler ingest
docker-compose logs -f crawler ingest
```

### Si búsquedas no retornan resultados:
```bash
# Verificar datos
make stats

# Si no hay datos
docker-compose restart crawler ingest

# Esperar 2-3 minutos y reintentar
```

### Si hay errores de puerto en uso:
```bash
# Ver qué usa el puerto
lsof -i :3000

# Detener Docker y reintentar
docker-compose down
docker-compose up -d
```

---

## Checklist Final para Entrega

### Código
- [ ] Repositorio limpio y organizado
- [ ] Sin archivos innecesarios
- [ ] .gitignore configurado
- [ ] Comentarios en código clave

### Documentación
- [ ] README completo
- [ ] QUICKSTART funcional
- [ ] Arquitectura clara
- [ ] Instrucciones de despliegue

### Funcionalidad
- [ ] Sistema levanta con un comando
- [ ] 500+ páginas indexadas
- [ ] Búsquedas funcionan
- [ ] UI completa

### Presentación
- [ ] Demo funcional
- [ ] Slides preparados
- [ ] Respuestas a preguntas preparadas
- [ ] Tiempos ensayados

---

## Última Verificación (Día de Entrega)

### 2 horas antes de presentar:
```bash
# 1. Limpiar y reiniciar todo
make clean
make start

# 2. Esperar 3-5 minutos

# 3. Verificar todo funciona
make health
make stats

# 4. Probar búsquedas en UI
# Abrir http://localhost:3000

# 5. Tomar screenshots si es necesario
```

- [ ] Todo funciona correctamente
- [ ] Screenshots tomados
- [ ] Demo ensayado
- [ ] Listo para presentar

---

## 🎉 ¡Listo para la Demo!

Si todos los checks están ✅, estás listo para:
1. Presentar el proyecto
2. Hacer la demo en vivo
3. Responder preguntas
4. ¡Entregar!

---

_Última actualización: 7 de noviembre, 2025_
