# Plan de Trabajo - Motor de Búsqueda Distribuido

**Fecha de entrega**: 10 de noviembre, 2025
**Fecha actual**: 7 de noviembre, 2025
**Días disponibles**: 3 días

---

## ✅ Día 0 - Completado (7 de noviembre)

### Infraestructura Base
- [x] Estructura de monorepo creada
- [x] Docker Compose configurado con todos los servicios
- [x] Esquemas de bases de datos definidos

### Servicios Implementados
- [x] **Crawler (Scrapy)**
  - Spider que extrae título, descripción, keywords y contenido
  - Integración con Kafka
  - Pipeline para envío de mensajes
  
- [x] **Ingest Service (Python)**
  - Consumer de Kafka
  - Almacenamiento en MySQL (metadata)
  - Almacenamiento en MongoDB (contenido)
  - Almacenamiento en PostgreSQL (índice invertido)
  - Tokenización básica
  
- [x] **API Gateway (Node.js)**
  - Endpoint de búsqueda distribuida
  - Agregación de resultados de 3 bases de datos
  - Health check y estadísticas
  
- [x] **Frontend (Next.js)**
  - Interfaz de búsqueda
  - Visualización de resultados
  - Estadísticas del sistema

### Documentación
- [x] README principal
- [x] Guía de inicio rápido
- [x] Documentación de arquitectura
- [x] Scripts de gestión

---

## 📋 Día 1 - Pipeline Completo (8 de noviembre)

### Objetivos del Día
- Probar el sistema completo end-to-end
- Indexar al menos 500 páginas
- Optimizar y corregir bugs

### Tareas

#### Mañana (4 horas)
- [ ] Levantar el sistema completo
  - Ejecutar `make start`
  - Verificar que todos los contenedores estén funcionando
  - Revisar logs de cada servicio
  
- [ ] Pruebas iniciales
  - Verificar que el crawler esté funcionando
  - Confirmar que los mensajes llegan a Kafka
  - Validar que ingest procesa correctamente
  
- [ ] Ajustes del crawler
  - Expandir lista de URLs semilla (agregar 20-30 sitios)
  - Ajustar configuración de Scrapy si es necesario
  - Verificar respeto a robots.txt

#### Tarde (4 horas)
- [ ] Optimización de indexación
  - Monitorear velocidad de crawling
  - Verificar que se almacenan datos en las 3 DBs
  - Ajustar delay entre requests si es necesario
  
- [ ] Pruebas de búsqueda
  - Realizar búsquedas de prueba
  - Verificar relevancia de resultados
  - Ajustar algoritmo de scoring si es necesario
  
- [ ] Corrección de bugs
  - Solucionar errores encontrados
  - Mejorar manejo de errores
  - Optimizar consultas SQL/NoSQL

### Métricas Esperadas al Final del Día
- ✅ 300+ páginas indexadas
- ✅ Búsquedas funcionando correctamente
- ✅ Tiempo de respuesta < 1 segundo
- ✅ Sistema estable por al menos 2 horas

---

## 🚀 Día 2 - Robustez y Características Avanzadas (9 de noviembre)

### Objetivos del Día
- Completar 500+ páginas indexadas
- Implementar replicación básica
- Preparar demo y presentación

### Tareas

#### Mañana (4 horas)
- [ ] Completar indexación
  - Asegurar 500+ páginas indexadas
  - Verificar calidad de los datos
  - Limpiar datos duplicados si existen
  
- [ ] Replicación y tolerancia a fallos
  - Configurar réplica de MySQL (opcional, simular con 2 contenedores)
  - Configurar replica set de MongoDB
  - Documentar estrategia de sharding
  
- [ ] Pruebas de tolerancia a fallos
  - Detener contenedor de MySQL y verificar comportamiento
  - Detener contenedor de MongoDB y verificar comportamiento
  - Documentar resultados

#### Tarde (4 horas)
- [ ] Mejoras de UI
  - Agregar paginación
  - Mejorar visualización de resultados
  - Agregar filtros básicos (por fecha, fuente)
  
- [ ] Medición de performance
  - Script de carga con múltiples búsquedas
  - Medir latencias (p50, p95)
  - Documentar métricas
  
- [ ] Preparación de demo
  - Script de demostración
  - Casos de uso de ejemplo
  - Preparar caída de nodo para demo

### Métricas Esperadas al Final del Día
- ✅ 500+ páginas indexadas
- ✅ Replicación funcionando
- ✅ Pruebas de failover exitosas
- ✅ Demo preparado

---

## 🎯 Día 3 - Documentación y Presentación (10 de noviembre - DÍA DE ENTREGA)

### Objetivos del Día
- Completar documentación
- Preparar presentación
- Ensayar demo
- ENTREGAR

### Tareas

#### Mañana (3 horas)
- [ ] Documentación final
  - Diagrama de arquitectura
  - Diagrama ER de bases de datos
  - Decisiones de diseño
  - Estrategia de fragmentación/replicación
  - Resultados de pruebas de tolerancia a fallos
  
- [ ] Preparación de slides
  - Introducción y motivación
  - Arquitectura del sistema
  - Componentes principales
  - Demo en vivo
  - Resultados y métricas
  - Conclusiones
  
- [ ] Ensayo de presentación
  - Practicar demo
  - Preparar respuestas a preguntas comunes
  - Verificar tiempos

#### Tarde (2 horas antes de entrega)
- [ ] Verificación final
  - Sistema funcionando correctamente
  - Todos los servicios levantados
  - Datos suficientes para demo
  
- [ ] Empaquetado
  - README actualizado
  - Código limpio y comentado
  - Docker Compose funcional
  - Repositorio organizado
  
- [ ] ENTREGA
  - Subir a repositorio
  - Enviar link/archivos
  - Confirmar recepción

---

## 📊 Checklist de Entregables

### Código
- [ ] Monorepo completo y organizado
- [ ] Docker Compose funcional
- [ ] Crawler (Scrapy + Kafka)
- [ ] Ingest service (Python)
- [ ] API Gateway (Node.js)
- [ ] Frontend (Next.js)
- [ ] Scripts de utilidad

### Documentación
- [ ] README con instrucciones claras
- [ ] Arquitectura del sistema
- [ ] Diagramas (topología, ER)
- [ ] Guía de despliegue
- [ ] Resultados de pruebas

### Funcionalidad
- [ ] 500+ páginas indexadas
- [ ] Búsqueda distribuida funcionando
- [ ] Datos en 3 bases de datos
- [ ] UI funcional
- [ ] Tolerancia a fallos básica

### Presentación
- [ ] Slides preparados
- [ ] Demo funcional
- [ ] Script de presentación
- [ ] Respuestas a preguntas preparadas

---

## 🎯 Prioridades

### Alta Prioridad (MUST HAVE)
1. Sistema funcionando end-to-end
2. 500+ páginas indexadas
3. Búsqueda funcionando correctamente
4. Docker Compose completo
5. Documentación básica

### Media Prioridad (SHOULD HAVE)
1. Replicación simulada
2. Pruebas de tolerancia a fallos
3. Métricas de performance
4. UI mejorada
5. Documentación detallada

### Baja Prioridad (NICE TO HAVE)
1. Ranking TF-IDF avanzado
2. Paginación completa
3. Autenticación
4. Monitoreo avanzado
5. Tests unitarios

---

## 🚨 Riesgos y Mitigaciones

### Riesgo 1: No alcanza el tiempo
**Mitigación**: Priorizar funcionalidad core, cortar features no esenciales

### Riesgo 2: Problemas de conectividad entre contenedores
**Mitigación**: Usar healthchecks, depends_on, verificar networking

### Riesgo 3: Crawler bloqueado por sitios
**Mitigación**: Ampliar lista de URLs, reducir velocidad, respetar robots.txt

### Riesgo 4: Bajo rendimiento de búsquedas
**Mitigación**: Optimizar consultas, agregar índices, limitar resultados

---

## 📝 Notas Importantes

- Mantener commits frecuentes en Git
- Probar cada componente individualmente antes de integrar
- Documentar decisiones importantes
- Mantener logs limpios y útiles
- Preparar plan B para la demo (grabación de respaldo)

---

## ✅ Checklist Diario

### Cada mañana:
- [ ] Levantar sistema
- [ ] Verificar logs
- [ ] Revisar métricas
- [ ] Planificar tareas del día

### Cada tarde:
- [ ] Commit de cambios
- [ ] Actualizar documentación
- [ ] Revisar progreso
- [ ] Planificar siguiente día

### Cada noche:
- [ ] Backup del código
- [ ] Detener servicios (opcional)
- [ ] Anotar problemas pendientes
- [ ] Preparar tareas para mañana
