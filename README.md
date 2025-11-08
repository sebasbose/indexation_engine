# Motor de Búsqueda Distribuido

Sistema de búsqueda distribuido desarrollado para el curso de Bases de Datos Avanzadas. Este proyecto implementa un motor de búsqueda completo con crawler, procesamiento de mensajes con Kafka, almacenamiento distribuido en múltiples bases de datos y una interfaz web.

## 📚 Documentación

### 🚀 Empieza Aquí
1. **[Resumen Ejecutivo](docs/RESUMEN_EJECUTIVO.md)** ⭐ - Visión general completa
2. **[Inicio Rápido](docs/QUICKSTART.md)** ⭐ - Cómo empezar en 3 pasos
3. **[Checklist](docs/CHECKLIST.md)** ⭐ - Verificación paso a paso

### 📖 Documentación Completa
- **[Índice](docs/INDICE.md)** - Navegación de toda la documentación
- **[Plan de Trabajo](docs/PLAN_DE_TRABAJO.md)** - Roadmap de 3 días
- **[Arquitectura](docs/arquitectura.md)** - Diseño técnico detallado
- **[Diagramas](docs/DIAGRAMAS.md)** - Diagramas visuales del sistema
- **[Debugging](docs/DEBUGGING.md)** - Comandos útiles para troubleshooting
- **[Notas de Implementación](docs/NOTAS_IMPLEMENTACION.md)** - Decisiones de diseño

## Arquitectura

El sistema está compuesto por los siguientes componentes:

### Servicios

1. **Crawler (Scrapy + Python)**
   - Crawlea páginas web y extrae metadatos
   - Envía datos a Kafka para procesamiento asíncrono
   - Ubicación: `services/crawler/`

2. **Ingest (Python)**
   - Consume mensajes de Kafka
   - Almacena datos en 3 bases de datos:
     - **MySQL**: Metadatos (título, URL, descripción)
     - **MongoDB**: Contenido completo de las páginas
     - **PostgreSQL**: Índice invertido para búsquedas
   - Ubicación: `services/ingest/`

3. **API (Node.js + Express)**
   - Gateway que agrega consultas de las 3 bases de datos
   - Endpoint de búsqueda distribuida
   - Ubicación: `services/api/`

4. **Web (Next.js + React)**
   - Interfaz de usuario para búsquedas
   - Muestra resultados y estadísticas
   - Ubicación: `services/web/`

### Infraestructura

- **Kafka + Zookeeper**: Cola de mensajes para procesamiento asíncrono
- **MySQL**: Almacenamiento de metadatos
- **PostgreSQL**: Índice invertido
- **MongoDB**: Almacenamiento de contenido

## Requisitos Previos

- Docker y Docker Compose instalados
- Al menos 4GB de RAM disponible

## Instalación y Ejecución

### 1. Levantar la infraestructura

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f crawler
docker-compose logs -f ingest
docker-compose logs -f api
```

### 2. Inicializar las bases de datos

Los esquemas se inicializan automáticamente cuando el servicio de ingest se conecta por primera vez.

### 3. Acceder a los servicios

- **Web UI**: http://localhost:3000
- **API**: http://localhost:3001
- **MySQL**: localhost:3306
- **PostgreSQL**: localhost:5432
- **MongoDB**: localhost:27017
- **Kafka**: localhost:9092

## Uso

### Realizar búsquedas

1. Abre http://localhost:3000 en tu navegador
2. Ingresa tu consulta en la barra de búsqueda
3. Los resultados se mostrarán con título, URL, snippet y score

### Endpoints de la API

#### Búsqueda
```bash
GET /api/search?q=database&page=1&limit=10
```

#### Estadísticas
```bash
GET /api/stats
```

#### Health Check
```bash
GET /api/health
```

## Desarrollo

### Estructura del Proyecto

```
indexation_engine/
├── docker-compose.yml          # Configuración de Docker
├── services/
│   ├── crawler/               # Spider de Scrapy
│   │   ├── crawler/
│   │   │   ├── spiders/
│   │   │   │   └── web_spider.py
│   │   │   └── pipelines.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── ingest/                # Consumer de Kafka
│   │   ├── consumer.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── api/                   # API Gateway
│   │   ├── index.js
│   │   ├── Dockerfile
│   │   └── package.json
│   └── web/                   # Frontend Next.js
│       ├── pages/
│       ├── styles/
│       ├── Dockerfile
│       └── package.json
├── infra/
│   └── scripts/               # Scripts de inicialización
│       ├── init-mysql.sql
│       └── init-postgres.sql
└── docs/
    └── planteamiento.md       # Especificación del proyecto
```

### Agregar nuevas URLs para crawlear

Edita el archivo `services/crawler/crawler/spiders/web_spider.py` y modifica la lista `start_urls`:

```python
start_urls = [
    'https://example.com',
    'https://another-site.com',
]
```

### Modificar límite de páginas

En el mismo archivo, cambia el valor de `CLOSESPIDER_PAGECOUNT`:

```python
custom_settings = {
    'CLOSESPIDER_PAGECOUNT': 500,  # Cambiar este número
}
```

## Detener el Sistema

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (borra datos)
docker-compose down -v
```

## Troubleshooting

### Los contenedores no inician

```bash
# Ver logs de errores
docker-compose logs

# Reiniciar un servicio específico
docker-compose restart [service-name]
```

### No se están indexando páginas

1. Verifica que Kafka esté funcionando: `docker-compose logs kafka`
2. Verifica que el crawler esté enviando mensajes: `docker-compose logs crawler`
3. Verifica que el ingest esté procesando: `docker-compose logs ingest`

### No aparecen resultados en búsquedas

1. Verifica que hay documentos indexados: http://localhost:3001/api/stats
2. Verifica la conectividad de las bases de datos: http://localhost:3001/api/health
3. Revisa los logs de la API: `docker-compose logs api`

## Características Implementadas

- ✅ Crawler distribuido con Scrapy
- ✅ Cola de mensajes con Kafka
- ✅ Almacenamiento distribuido (MySQL, PostgreSQL, MongoDB)
- ✅ Índice invertido para búsquedas eficientes
- ✅ API Gateway que agrega resultados
- ✅ Interfaz web con Next.js
- ✅ Tokenización y scoring básico
- ✅ Contenerización completa con Docker

## Mejoras Futuras

- [ ] Implementar réplicas de bases de datos
- [ ] Agregar particionamiento de datos
- [ ] Mejorar algoritmo de ranking (TF-IDF)
- [ ] Implementar paginación completa
- [ ] Agregar autenticación
- [ ] Implementar cache de resultados
- [ ] Agregar métricas y monitoreo

## Autores

Proyecto desarrollado para el curso de Bases de Datos Avanzadas - PUCP

## Licencia

MIT
