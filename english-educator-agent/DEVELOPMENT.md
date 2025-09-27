# 🔧 Development Guide - English Educator Agent

Guía completa para desarrolladores que trabajen en el proyecto.

---

## 📁 Estructura del Proyecto

```
english-educator-agent/
├── backend/                    # Backend Python
│   ├── agents/                # Agentes especializados
│   │   ├── evaluator.py      # Evaluación de nivel
│   │   ├── tutor.py          # Creación de lecciones
│   │   ├── grammar.py        # Corrección gramatical
│   │   ├── conversation.py   # Práctica conversacional
│   │   ├── exercise.py       # Generador de ejercicios
│   │   └── progress.py       # Seguimiento de progreso
│   ├── graphs/               # LangGraph workflows
│   │   └── supervisor.py     # Orquestador principal
│   ├── rag/                  # Sistema RAG
│   │   ├── ingest.py        # Ingesta de contenido
│   │   └── retrieval.py     # Retrieval avanzado
│   ├── api/                  # FastAPI endpoints
│   │   ├── routes.py        # REST endpoints
│   │   └── websockets.py    # WebSocket endpoints
│   ├── models/               # SQLAlchemy models
│   ├── tasks/                # Celery tasks
│   ├── utils/                # Utilidades
│   │   └── metrics.py       # Prometheus metrics
│   ├── config.py            # Configuración
│   └── main.py              # Entry point
├── data/                     # Datos y contenido
│   └── english_content/     # Material educativo
│       ├── grammar/
│       ├── vocabulary/
│       └── exercises/
├── docker/                   # Docker configs
│   └── docker-compose.yml   # Servicios
├── monitoring/              # Observabilidad
│   ├── grafana/
│   └── prometheus/
├── tests/                   # Tests
│   ├── unit/
│   └── integration/
├── .env.example            # Template de variables
├── demo.py                 # Script de demostración
└── README.md              # Documentación
```

---

## 🛠️ Herramientas de Desarrollo

### IDEs Recomendados
- **VS Code** con extensiones:
  - Python
  - Pylance
  - Docker
  - REST Client
  - GitLens

- **PyCharm Professional** (alternativa)

### Extensiones VS Code Útiles
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-azuretools.vscode-docker",
    "humao.rest-client",
    "eamodio.gitlens",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

---

## 📝 Convenciones de Código

### Style Guide
- **PEP 8** para Python
- **Type hints** obligatorios
- **Docstrings** para todas las funciones públicas
- **Max line length:** 100 caracteres

### Ejemplo de Función
```python
from typing import List, Dict, Optional

async def process_student_data(
    user_id: int,
    session_data: Dict,
    level: Optional[str] = None
) -> List[Dict]:
    """Process student session data and return insights.
    
    Args:
        user_id: Student's unique identifier
        session_data: Session activity data
        level: Optional CEFR level override
        
    Returns:
        List of insight dictionaries
        
    Raises:
        ValueError: If user_id is invalid
    """
    # Implementation
    pass
```

### Naming Conventions
- **Classes:** `PascalCase` (ej. `EvaluatorAgent`)
- **Functions:** `snake_case` (ej. `check_grammar`)
- **Constants:** `UPPER_SNAKE_CASE` (ej. `MAX_TOKENS`)
- **Private:** `_leading_underscore` (ej. `_internal_method`)

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=backend tests/

# Solo unit tests
pytest tests/unit -v

# Solo integration tests
pytest tests/integration -v

# Test específico
pytest tests/unit/test_evaluator.py -v

# Con logs
pytest -s
```

### Escribir Tests
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_function():
    """Test description."""
    # Arrange
    agent = MyAgent()
    
    # Act
    result = await agent.do_something()
    
    # Assert
    assert result is not None
```

### Coverage Target
- **Mínimo:** 70%
- **Objetivo:** 85%+

---

## 🔍 Debugging

### Local Debugging

**VS Code launch.json:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Usar en código
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### Debug con IPython
```python
# Agregar breakpoint
import ipdb; ipdb.set_trace()

# O usar built-in
breakpoint()
```

---

## 🚀 Workflow de Desarrollo

### 1. Crear Feature Branch
```bash
git checkout -b feature/nombre-feature
```

### 2. Hacer Cambios
```bash
# Editar código
# Agregar tests
# Actualizar documentación
```

### 3. Verificar Calidad
```bash
# Format code
black backend/

# Lint
ruff check backend/

# Type check
mypy backend/

# Run tests
pytest
```

### 4. Commit
```bash
git add .
git commit -m "feat: descripción clara del cambio

- Detalle 1
- Detalle 2

Closes #123"
```

### 5. Push y PR
```bash
git push origin feature/nombre-feature
# Crear Pull Request en GitHub
```

---

## 🔧 Troubleshooting Común

### Error: "ModuleNotFoundError"
```bash
# Solución: Verificar venv activado
which python  # Debe mostrar path de venv

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: Database Connection
```bash
# Verificar PostgreSQL
docker-compose ps postgres

# Ver logs
docker-compose logs postgres

# Reiniciar
docker-compose restart postgres
```

### Error: Qdrant Connection
```bash
# Verificar Qdrant
curl http://localhost:6333/healthz

# Ver colecciones
curl http://localhost:6333/collections

# Recrear colección
# En Python:
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
client.delete_collection("english_content")
```

### Error: Celery Tasks Not Running
```bash
# Verificar RabbitMQ
docker-compose ps rabbitmq

# Ver tareas en queue
# Acceder: http://localhost:15672 (admin/admin)

# Reiniciar worker
celery -A tasks worker --loglevel=debug
```

### Error: LangSmith Not Tracing
```bash
# Verificar variables
echo $LANGCHAIN_API_KEY
echo $LANGCHAIN_TRACING_V2

# En código, forzar tracing
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
```

---

## 📊 Monitoring en Desarrollo

### Prometheus Queries Útiles
```promql
# Requests por segundo
rate(api_requests_total[5m])

# Latencia p95
histogram_quantile(0.95, rate(api_latency_seconds_bucket[5m]))

# Errores
rate(api_requests_total{status="error"}[5m])

# Tokens usados
rate(llm_tokens_total[5m])
```

### Grafana Dashboards
1. Importar desde: `monitoring/grafana/dashboards/`
2. O crear custom:
   - Add panel → Query → Prometheus
   - Usar queries arriba

---

## 🔄 Actualizar Dependencias

### Check Updates
```bash
pip list --outdated
```

### Update Package
```bash
pip install --upgrade nombre-paquete
pip freeze > requirements.txt
```

### Update All (con cuidado)
```bash
pip install --upgrade -r requirements.txt
```

---

## 📦 Build & Deploy

### Docker Build Local
```bash
cd docker
docker build -f Dockerfile.backend -t english-tutor-backend:dev ../backend
```

### Test Docker Image
```bash
docker run -p 8000:8000 --env-file ../.env english-tutor-backend:dev
```

### Docker Compose Build
```bash
docker-compose build
docker-compose up -d
```

---

## 🎯 Performance Optimization

### Profiling
```python
import cProfile
import pstats

# Profile función
cProfile.run('my_function()', 'output.prof')

# Analizar
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Memory Profiling
```bash
pip install memory-profiler

# Decorar función
@profile
def my_function():
    pass

# Ejecutar
python -m memory_profiler script.py
```

---

## 📚 Recursos para Desarrolladores

### LangChain/LangGraph
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Templates](https://github.com/langchain-ai/langchain/tree/master/templates)

### FastAPI
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

### Testing
- [Pytest Docs](https://docs.pytest.org/)
- [AsyncIO Testing](https://docs.python.org/3/library/asyncio-dev.html)

### Docker
- [Docker Docs](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🤝 Contributing

### Proceso de Contribución
1. Fork el repositorio
2. Crear feature branch
3. Hacer cambios con tests
4. Pasar todos los checks
5. Crear Pull Request
6. Code review
7. Merge

### Code Review Checklist
- [ ] Código sigue style guide
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] No hay errores de linting
- [ ] Type hints correctos
- [ ] Performance considerado

---

## 🐛 Reportar Bugs

### Template de Issue
```markdown
**Describe el bug**
Descripción clara del problema.

**Para Reproducir**
Pasos:
1. Ir a '...'
2. Ejecutar '...'
3. Ver error

**Comportamiento Esperado**
Qué debería pasar.

**Screenshots/Logs**
Si aplica.

**Entorno:**
- OS: [e.g. Windows 10]
- Python: [e.g. 3.10]
- Versión: [e.g. 1.0.0]
```

---

## 📞 Soporte

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** (configurar email del equipo)

---

**Happy Coding! 💻🚀**
