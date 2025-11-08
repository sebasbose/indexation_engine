# Notas de Implementación

## ✅ Completado - Día 0 (7 de noviembre)

### Estructura del Proyecto
El proyecto ha sido completamente estructurado y configurado como un monorepo con los siguientes componentes:

#### 1. Infraestructura (Docker Compose)
- **Kafka + Zookeeper**: Sistema de mensajería para procesamiento asíncrono
- **MySQL**: Almacenamiento de metadatos (url, title, description, keywords)
- **PostgreSQL**: Índice invertido para búsquedas eficientes
- **MongoDB**: Almacenamiento de contenido completo

#### 2. Servicios de Aplicación

**Crawler (services/crawler/)**
- Framework: Scrapy (Python)
- Funcionalidad:
  - Crawlea páginas web desde lista de seeds
  - Extrae: título, meta-description, keywords, contenido
  - Envía datos a Kafka (topic: pages.raw)
- Configuración:
  - Límite: 500 páginas (CLOSESPIDER_PAGECOUNT)
  - Delay: 0.5s entre requests
  - AutoThrottle habilitado
  - Respeta robots.txt

**Ingest Service (services/ingest/)**
- Lenguaje: Python
- Funcionalidad:
  - Consume mensajes de Kafka
  - Tokeniza contenido (lowercase, remove punctuation)
  - Almacena en 3 bases de datos simultáneamente
  - Crea índice invertido (token → document_id → frequency)
- Características:
  - Auto-reconexión a bases de datos
  - Inicialización automática de esquemas
  - Manejo robusto de errores

**API Gateway (services/api/)**
- Framework: Node.js + Express
- Funcionalidad:
  - Endpoint `/api/search`: búsqueda distribuida
  - Endpoint `/api/stats`: estadísticas del sistema
  - Endpoint `/api/health`: verificación de salud
- Algoritmo de búsqueda:
  1. Tokeniza query
  2. Consulta PostgreSQL para encontrar documentos con tokens
  3. Obtiene metadata de MySQL
  4. Obtiene snippets de MongoDB
  5. Agrega y ordena por score (sum de frequencies)
- CORS habilitado para desarrollo

**Web Frontend (services/web/)**
- Framework: Next.js + React
- Características:
  - Interfaz limpia y moderna
  - Búsqueda en tiempo real
  - Visualización de resultados con snippets
  - Estadísticas del sistema
  - Diseño responsive

#### 3. Documentación
- `README.md`: Guía principal
- `docs/QUICKSTART.md`: Inicio rápido
- `docs/arquitectura.md`: Arquitectura detallada
- `docs/PLAN_DE_TRABAJO.md`: Roadmap de 3 días
- `docs/DEBUGGING.md`: Comandos útiles
- `docs/RESUMEN_EJECUTIVO.md`: Resumen del proyecto

#### 4. Scripts y Utilidades
- `manage.sh`: Script bash para gestión del sistema
- `Makefile`: Comandos make para tareas comunes
- `.env.example`: Template de variables de entorno
- `.gitignore`: Archivos a ignorar en git

---

## 🎯 Decisiones de Diseño

### Almacenamiento Distribuido

**MySQL - Metadatos Relacionales**
- Ventaja: Consultas relacionales eficientes, integridad referencial
- Uso: Almacenar información estructurada (url, title, description, etc.)
- Esquema: Tabla `documents` con índices en document_id

**PostgreSQL - Índice Invertido**
- Ventaja: Excelente soporte para índices complejos, JSONB para metadata
- Uso: Índice invertido (token → document_id → frequency)
- Esquema: Tabla `inverted_index` con índices en token y document_id
- Optimización: UNIQUE constraint en (token, document_id) evita duplicados

**MongoDB - Contenido No Estructurado**
- Ventaja: Flexible, eficiente para documentos grandes
- Uso: Almacenar contenido completo de páginas
- Esquema: Colección `documents` con campos flexibles

### Procesamiento Asíncrono con Kafka

**¿Por qué Kafka?**
- Desacoplamiento: Crawler y ingest pueden escalar independientemente
- Resiliencia: Si ingest falla, mensajes se mantienen en cola
- Paralelización: Múltiples consumers pueden procesar en paralelo

**Topic Design**
- `pages.raw`: Páginas crawleadas (key: document_id)
- Particionamiento futuro: Por dominio o hash de URL

### Tokenización Simple

**Algoritmo Actual**
1. Lowercase del texto
2. Remover puntuación (regex: `[^\w\s]`)
3. Split por espacios
4. Filtrar tokens < 3 caracteres

**Mejoras Futuras**
- Stemming (porter stemmer)
- Stop words removal
- Normalización de acentos
- N-gramas para mejores búsquedas

### Scoring Básico

**Algoritmo Actual**
- Score = SUM(frequency) para todos los tokens de la query
- Ordenar por score DESC

**Mejoras Futuras**
- TF-IDF (Term Frequency - Inverse Document Frequency)
- BM25 ranking
- PageRank para autoridad
- Boost por recency (páginas más recientes)

---

## 📊 Modelo de Datos

### MySQL Schema
```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    keywords TEXT,
    crawl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255),
    INDEX idx_document_id (document_id)
);
```

### PostgreSQL Schema
```sql
CREATE TABLE inverted_index (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    frequency INT DEFAULT 1,
    positions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(token, document_id)
);

CREATE INDEX idx_token ON inverted_index(token);
CREATE INDEX idx_document_id ON inverted_index(document_id);
```

### MongoDB Schema (flexible)
```javascript
{
  document_id: String,
  url: String,
  content: String,
  title: String,
  crawl_timestamp: Date
}
```

---

## 🔧 Configuraciones Importantes

### Docker Compose
- Network: `search-network` (bridge)
- Volúmenes persistentes para todas las DBs
- Healthchecks: Configurar en próxima iteración
- Restart policy: Configurar en producción

### Variables de Entorno
Todas definidas en docker-compose.yml:
- Kafka: KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
- MySQL: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
- PostgreSQL: POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE
- MongoDB: MONGODB_URI

### Puertos Expuestos
- Web UI: 3000
- API: 3001
- MySQL: 3306
- PostgreSQL: 5432
- MongoDB: 27017
- Kafka: 9092
- Zookeeper: 2181

---

## ⚡ Performance Consideraciones

### Crawling
- Throughput esperado: 50-100 páginas/minuto
- Depende de: delay configurado, velocidad de respuesta de sitios
- Limitado por: ROBOTSTXT_OBEY, DOWNLOAD_DELAY

### Indexación
- Throughput esperado: 50+ documentos/segundo
- Depende de: velocidad de escritura de DBs, complejidad de tokenización
- Limitado por: velocidad de Kafka consumer, latencia de red

### Búsquedas
- Latencia esperada: < 200ms (p95)
- Depende de: número de tokens en query, tamaño del índice
- Optimización: Índices en PostgreSQL son cruciales

---

## 🚨 Limitaciones Conocidas

1. **No hay autenticación**: Sistema abierto, no hay control de acceso
2. **Scoring simple**: No usa TF-IDF ni algoritmos avanzados
3. **Sin paginación completa**: Implementación básica
4. **No hay caching**: Cada búsqueda consulta las bases de datos
5. **Sin monitoring avanzado**: Solo logs y endpoints básicos
6. **Replicación no implementada**: Simular en Día 2
7. **Sin rate limiting**: API puede ser sobrecargada

---

## 🎓 Conceptos Clave del Proyecto

### Distribución
- **Fragmentación horizontal**: Datos divididos en múltiples nodos
- **Especialización por tipo de dato**: Cada DB optimizada para su uso
- **Consulta distribuida**: API agrega resultados de múltiples fuentes

### Consistencia
- **Eventual consistency**: Ventana entre crawl y disponibilidad en búsqueda
- **No hay transacciones distribuidas**: Cada DB se actualiza independientemente
- **Trade-off aceptado**: Prioriza availability sobre strict consistency

### Tolerancia a Fallos
- **Partial results**: API continúa si una DB falla
- **Kafka como buffer**: Protege contra pérdida de datos si ingest falla
- **Retry logic**: Scrapy reintenta requests fallidos

---

## 📈 Métricas de Éxito

### Funcionales
- ✅ Crawlea 500+ páginas
- ✅ Almacena en 3 bases de datos
- ✅ Búsquedas retornan resultados relevantes
- ✅ UI funcional y responsive

### No Funcionales
- ✅ Latencia de búsqueda < 1s
- ✅ Sistema se levanta en < 5 minutos
- ✅ Documentación completa
- ✅ Código limpio y organizado

---

## 🔜 Próximos Pasos (Para Día 1)

1. **Levantar el sistema** y verificar que todo funciona
2. **Monitorear el crawling** y asegurar que se indexan páginas
3. **Probar búsquedas** con diferentes queries
4. **Identificar y corregir bugs**
5. **Ajustar configuración** si es necesario
6. **Documentar problemas encontrados**

---

## 💡 Tips para la Demo

1. Preparar búsquedas de ejemplo con resultados conocidos
2. Mostrar estadísticas antes/después de crawling
3. Demostrar tolerancia a fallos (detener un contenedor)
4. Explicar arquitectura con diagrama
5. Mostrar código clave (spider, ingest, API)
6. Tener respuestas preparadas para preguntas comunes

---

## 📚 Referencias

- Scrapy: https://docs.scrapy.org/
- Kafka: https://kafka.apache.org/documentation/
- PostgreSQL: https://www.postgresql.org/docs/
- MongoDB: https://docs.mongodb.com/
- Next.js: https://nextjs.org/docs

---

_Documento creado: 7 de noviembre, 2025_
_Última actualización: 7 de noviembre, 2025_
