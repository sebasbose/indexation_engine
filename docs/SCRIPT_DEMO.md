# 🎬 Script de Demo para Presentación

## Preparación Pre-Demo (30 minutos antes)

```bash
# 1. Asegurarse de que todo esté limpio
cd /Users/sebasbose/Desktop/indexation_engine
make clean

# 2. Levantar sistema desde cero
make start

# 3. Esperar 3-5 minutos para que indexe páginas

# 4. Verificar que hay datos suficientes
make stats
# Debe mostrar: documents >= 100, tokens >= 1000

# 5. Verificar salud del sistema
make health
# Todos los servicios deben estar "connected"

# 6. Abrir pestañas del navegador (NO CERRAR)
# - http://localhost:3000 (Frontend)
# - Terminal con logs listos
```

---

## Demo Script (10-15 minutos)

### 1. Introducción (1 minuto)

**Decir:**
> "Desarrollamos un motor de búsqueda distribuido que indexa páginas web y permite búsquedas eficientes. El sistema usa Kafka para procesamiento asíncrono y almacena datos en 3 bases de datos especializadas."

**Mostrar:** Diapositiva con arquitectura

---

### 2. Arquitectura del Sistema (2 minutos)

**Decir:**
> "El sistema tiene 4 componentes principales: Crawler, Sistema de Mensajería, Almacenamiento Distribuido, y Frontend."

**Mostrar:** Diagrama de arquitectura (docs/DIAGRAMAS.md)

```
Crawler (Scrapy) → Kafka → Ingest Service → 3 Bases de Datos
                                              ↓
                                         API Gateway
                                              ↓
                                          Frontend
```

**Explicar cada capa:**
1. **Crawler**: Scrapy extrae datos de páginas web
2. **Kafka**: Cola de mensajes para procesamiento asíncrono
3. **Almacenamiento**: 
   - MySQL: Metadatos (url, título, descripción)
   - PostgreSQL: Índice invertido (tokens → documentos)
   - MongoDB: Contenido completo
4. **API**: Agrega consultas de las 3 bases de datos
5. **Frontend**: Interfaz Next.js

---

### 3. Demo del Sistema Funcionando (3 minutos)

#### Mostrar Estadísticas

```bash
# Terminal 1
curl -s http://localhost:3001/api/stats | jq
```

**Decir:**
> "Actualmente tenemos [X] documentos indexados con [Y] tokens únicos en nuestro índice invertido."

#### Mostrar la UI

**Ir a:** http://localhost:3000

**Decir:**
> "Esta es nuestra interfaz web donde los usuarios pueden realizar búsquedas."

#### Realizar Búsqueda de Demo

**Búsqueda 1: "python"**

**Decir:**
> "Busquemos 'python'. El sistema tokeniza la query, consulta el índice en PostgreSQL, obtiene metadata de MySQL y snippets de MongoDB, y agrega los resultados ordenados por relevancia."

**Mostrar:** Resultados aparecen con título, URL, snippet y score

**Búsqueda 2: "database systems"**

**Decir:**
> "Con queries de múltiples palabras, el sistema busca documentos que contengan cualquiera de los tokens y suma las frecuencias para calcular el score."

---

### 4. Mostrar el Proceso de Indexación (2 minutos)

#### Ver logs del crawler

```bash
# Terminal 2
docker-compose logs --tail=20 crawler
```

**Decir:**
> "El crawler está constantemente visitando páginas web. Aquí vemos las URLs que está procesando."

#### Ver logs del ingest

```bash
docker-compose logs --tail=20 ingest
```

**Decir:**
> "El servicio de ingest consume mensajes de Kafka y almacena los datos en las 3 bases de datos simultáneamente."

---

### 5. Demostrar Consulta Distribuida (3 minutos)

#### Mostrar consulta a cada base de datos

**Terminal 3 - MySQL (Metadata):**
```bash
docker exec -it indexation_engine-mysql-1 mysql -u searchuser -psearchpass -e \
"SELECT url, title FROM searchdb.documents LIMIT 3;"
```

**Decir:**
> "MySQL almacena los metadatos estructurados de cada documento."

**Terminal 4 - PostgreSQL (Índice):**
```bash
docker exec -it indexation_engine-postgres-1 psql -U searchuser -d indexdb -c \
"SELECT token, COUNT(*) as doc_count FROM inverted_index 
 WHERE token IN ('python', 'database', 'programming') 
 GROUP BY token ORDER BY doc_count DESC;"
```

**Decir:**
> "PostgreSQL mantiene el índice invertido que permite búsquedas rápidas. Aquí vemos cuántos documentos contienen cada token."

**Terminal 5 - MongoDB (Contenido):**
```bash
docker exec -it indexation_engine-mongodb-1 mongosh -u root -p rootpass --quiet --eval \
"use contentdb; db.documents.findOne({}, {url: 1, content: 1, _id: 0})"
```

**Decir:**
> "MongoDB almacena el contenido completo de las páginas para generar snippets."

---

### 6. Tolerancia a Fallos (2-3 minutos)

**IMPORTANTE:** Practica esto antes de la demo

#### Detener MySQL

```bash
docker-compose stop mysql
```

**Decir:**
> "Ahora voy a simular una falla del servidor MySQL para demostrar la tolerancia a fallos del sistema."

#### Verificar health

```bash
curl -s http://localhost:3001/api/health | jq
```

**Mostrar:** MySQL aparece como "disconnected", otros servicios OK

**Decir:**
> "El sistema detecta que MySQL está caído pero los otros servicios siguen funcionando."

#### Realizar búsqueda

**Ir a:** http://localhost:3000

**Buscar:** "python"

**Decir:**
> "A pesar de que MySQL está caído, el sistema puede seguir entregando resultados usando PostgreSQL para el índice y MongoDB para el contenido. La API marca el resultado como 'partial' para indicar que falta información."

#### Restaurar MySQL

```bash
docker-compose start mysql
# Esperar 10 segundos
curl -s http://localhost:3001/api/health | jq
```

**Decir:**
> "Una vez que restauramos el servicio, el sistema vuelve a su funcionamiento normal automáticamente."

---

### 7. Métricas y Performance (1 minuto)

```bash
# Medir latencia de una búsqueda
time curl -s "http://localhost:3001/api/search?q=python" > /dev/null
```

**Decir:**
> "El tiempo de respuesta es de aproximadamente [X] milisegundos, lo cual es aceptable para este tipo de sistema."

```bash
# Mostrar estadísticas finales
curl -s http://localhost:3001/api/stats | jq
```

**Decir:**
> "Hemos indexado [X] documentos con [Y] tokens únicos, demostrando la capacidad del sistema para manejar grandes volúmenes de datos."

---

### 8. Conclusiones (1 minuto)

**Decir:**
> "En resumen, hemos implementado:
> 1. Un crawler distribuido que indexa páginas web automáticamente
> 2. Procesamiento asíncrono con Kafka para desacoplar componentes
> 3. Almacenamiento especializado en 3 bases de datos diferentes
> 4. Un índice invertido eficiente para búsquedas rápidas
> 5. Tolerancia a fallos con resultados parciales
> 6. Una interfaz web moderna y funcional
>
> Todo el sistema está contenerizado con Docker y se puede desplegar con un solo comando."

---

## Preguntas Frecuentes (Preparar Respuestas)

### P: ¿Por qué usar 3 bases de datos?

**R:** Cada base de datos está optimizada para un tipo de dato específico:
- MySQL: Excelente para datos relacionales estructurados (metadata)
- PostgreSQL: Superior para índices complejos y búsquedas (índice invertido)
- MongoDB: Eficiente para documentos grandes no estructurados (contenido)

### P: ¿Cómo se calcula el score de relevancia?

**R:** Actualmente usamos un algoritmo simple: sumamos las frecuencias de aparición de cada token de la query en el documento. En producción, implementaríamos TF-IDF o BM25 para mejores resultados.

### P: ¿Cómo se escala el sistema?

**R:** Cada componente puede escalar horizontalmente:
- Crawler: Múltiples instancias procesando diferentes URLs
- Ingest: Consumer group de Kafka para paralelismo
- API: Load balancer con múltiples instancias
- Bases de datos: Sharding y replicación

### P: ¿Qué pasa si Kafka falla?

**R:** Kafka tiene persistencia en disco y replicación. Si el broker falla temporalmente, los mensajes no se pierden. Cuando se recupera, el ingest continúa procesando desde donde quedó.

### P: ¿Cómo se maneja la consistencia?

**R:** Usamos eventual consistency. Hay una pequeña ventana entre que se crawlea una página y está disponible para búsqueda. Esto es aceptable para este tipo de sistema.

### P: ¿Cuántas páginas puede manejar?

**R:** Con la arquitectura actual y configuración básica, podemos manejar fácilmente 10,000-100,000 documentos. Para escalar a millones, necesitaríamos:
- Sharding de las bases de datos
- Múltiples particiones en Kafka
- Cache de resultados
- CDN para el frontend

---

## Checklist Pre-Demo

- [ ] Sistema levantado y estable (30 min antes)
- [ ] Al menos 100 documentos indexados
- [ ] Todas las bases de datos conectadas
- [ ] Pestañas del navegador abiertas
- [ ] Terminales preparadas con comandos
- [ ] Diapositivas listas
- [ ] Practica el flujo completo al menos 2 veces

---

## Comandos de Emergencia

### Si algo falla durante la demo:

```bash
# Reset rápido (2-3 minutos)
docker-compose restart

# Ver qué está fallando
docker-compose ps
docker-compose logs --tail=50

# Reiniciar servicio específico
docker-compose restart [service-name]
```

---

## Tips de Presentación

1. **Habla con confianza**: Conoces tu sistema mejor que nadie
2. **Explica el "por qué"**: No solo el "qué"
3. **Maneja los errores con gracia**: Si algo falla, explica cómo lo solucionarías
4. **Usa términos técnicos correctamente**: Pero explícalos si es necesario
5. **Mantén contacto visual**: No solo leas las diapositivas
6. **Responde preguntas directamente**: Si no sabes algo, di "No lo implementamos pero sería interesante considerarlo"
7. **Termina con tiempo para preguntas**: Deja al menos 5 minutos

---

## Timing Sugerido

- Introducción: 1 min
- Arquitectura: 2 min
- Demo UI: 3 min
- Proceso de indexación: 2 min
- Consulta distribuida: 3 min
- Tolerancia a fallos: 2-3 min
- Métricas: 1 min
- Conclusiones: 1 min
- **Total: 15 minutos**
- Preguntas: 5-10 minutos

---

## Plan B (Si la demo en vivo falla)

1. **Tener screenshots preparados** de cada paso
2. **Tener un video grabado** del sistema funcionando
3. **Explicar con diagramas** cómo funcionaría
4. **Mostrar el código** en lugar de ejecución

---

_¡Éxito en tu presentación!_
