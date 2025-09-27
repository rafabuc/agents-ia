# Contributing to English Educator Agent

¡Gracias por tu interés en contribuir! 🎉

Este documento proporciona guías sobre cómo contribuir al proyecto.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración de Desarrollo](#configuración-de-desarrollo)
- [Guías de Estilo](#guías-de-estilo)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Features](#sugerir-features)

---

## 📜 Código de Conducta

Este proyecto sigue un Código de Conducta. Al participar, se espera que lo respetes.

**Principios:**
- Ser respetuoso y profesional
- Aceptar críticas constructivas
- Enfocarse en lo mejor para la comunidad
- Mostrar empatía hacia otros miembros

---

## 🤝 Cómo Contribuir

### Tipos de Contribuciones

1. **Código**
   - Nuevas funcionalidades
   - Corrección de bugs
   - Mejoras de performance
   - Tests adicionales

2. **Documentación**
   - Mejoras en README
   - Tutoriales
   - Ejemplos de uso
   - Traducción

3. **Contenido Educativo**
   - Lecciones de gramática
   - Vocabulario
   - Ejercicios
   - Material didáctico

4. **Tests**
   - Unit tests
   - Integration tests
   - E2E tests
   - Performance tests

---

## 🛠️ Configuración de Desarrollo

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/TU-USUARIO/english-educator-agent.git
cd english-educator-agent

# Agrega el repositorio original como upstream
git remote add upstream https://github.com/ORIGINAL/english-educator-agent.git
```

### 2. Crear Rama

```bash
# Actualiza tu main
git checkout main
git pull upstream main

# Crea una rama para tu feature/fix
git checkout -b feature/nombre-descriptivo
# o
git checkout -b fix/descripcion-bug
```

### 3. Setup del Entorno

```bash
# Copia variables de entorno
cp .env.example .env
# Edita .env con tus API keys

# Levanta servicios Docker
cd docker
docker-compose up -d

# Setup backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

### 4. Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Con coverage
pytest --cov=backend tests/

# Tests específicos
pytest tests/unit/test_evaluator_agent.py -v
```

---

## 📝 Guías de Estilo

### Python Code Style

Seguimos **PEP 8** con algunas excepciones:

```python
# ✅ Bueno
def create_lesson(topic: str, level: str) -> dict:
    """Create a personalized lesson.
    
    Args:
        topic: The topic to teach
        level: CEFR level (A1-C2)
        
    Returns:
        Structured lesson dictionary
    """
    # Implementation
    pass

# ❌ Malo
def createLesson(topic,level):
    # Implementation
    pass
```

**Reglas:**
- Nombres de funciones: `snake_case`
- Nombres de clases: `PascalCase`
- Constantes: `UPPER_CASE`
- Docstrings: Google style
- Type hints siempre que sea posible
- Línea máxima: 100 caracteres

### Formateo Automático

Usa `black` y `ruff`:

```bash
# Formatear código
black backend/

# Linter
ruff check backend/

# Fix automático
ruff check --fix backend/
```

### Commits

Formato de commits (Conventional Commits):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, sin cambios en código
- `refactor`: Refactorización
- `test`: Agregar o modificar tests
- `chore`: Mantenimiento

**Ejemplos:**
```bash
git commit -m "feat(agents): add pronunciation checker agent"
git commit -m "fix(api): resolve websocket disconnection issue"
git commit -m "docs: update API examples with new endpoints"
```

---

## 🔄 Proceso de Pull Request

### 1. Antes de Crear PR

- [ ] Código sigue las guías de estilo
- [ ] Tests pasan (`pytest tests/`)
- [ ] Agregaste tests para nueva funcionalidad
- [ ] Actualizaste documentación
- [ ] Commits siguen convenciones
- [ ] Branch está actualizado con main

```bash
# Actualizar tu rama
git fetch upstream
git rebase upstream/main
```

### 2. Crear Pull Request

1. Push tu rama:
```bash
git push origin feature/nombre-descriptivo
```

2. Ve a GitHub y crea el PR

3. Llena la plantilla del PR:

```markdown
## Descripción
Breve descripción de los cambios

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## ¿Cómo se probó?
Describe las pruebas realizadas

## Checklist
- [ ] Tests pasan
- [ ] Documentación actualizada
- [ ] Código formateado
```

### 3. Code Review

- Responde a comentarios constructivamente
- Haz cambios solicitados
- Push cambios adicionales a la misma rama
- Una vez aprobado, será merged

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. Busca si el bug ya fue reportado
2. Asegúrate que es un bug (no un error de configuración)
3. Verifica con la última versión

### Template de Bug Report

```markdown
**Descripción del Bug**
Descripción clara y concisa

**Para Reproducir**
1. Ir a '...'
2. Ejecutar '...'
3. Ver error

**Comportamiento Esperado**
Qué debería pasar

**Screenshots**
Si aplica

**Entorno:**
- OS: [e.g. Windows 11]
- Python: [e.g. 3.11]
- Versión: [e.g. 1.0.0]

**Logs**
```
Pega logs relevantes aquí
```

**Contexto Adicional**
Cualquier otro detalle
```

---

## 💡 Sugerir Features

### Template de Feature Request

```markdown
**¿El feature está relacionado a un problema?**
Descripción clara del problema

**Describe la solución que te gustaría**
Solución propuesta

**Alternativas consideradas**
Otras soluciones que consideraste

**Contexto Adicional**
Screenshots, mockups, ejemplos
```

---

## 🧪 Agregar Tests

### Ubicación de Tests

```
tests/
├── unit/              # Tests unitarios
│   ├── test_agents.py
│   └── test_utils.py
├── integration/       # Tests de integración
│   ├── test_api.py
│   └── test_workflows.py
└── e2e/              # Tests end-to-end
    └── test_user_flows.py
```

### Ejemplo de Test

```python
import pytest
from backend.agents.tutor import TutorAgent

class TestTutorAgent:
    """Test tutor agent functionality."""
    
    @pytest.fixture
    def tutor_agent(self):
        """Create tutor agent instance."""
        return TutorAgent()
    
    def test_create_lesson(self, tutor_agent):
        """Test lesson creation."""
        lesson = tutor_agent.create_lesson(
            topic="Present Perfect",
            level="B1"
        )
        
        assert lesson is not None
        assert "topic" in lesson
        assert lesson["topic"] == "Present Perfect"
    
    @pytest.mark.asyncio
    async def test_async_method(self, tutor_agent):
        """Test async method."""
        result = await tutor_agent.async_method()
        assert result is not None
```

---

## 📚 Agregar Contenido Educativo

### 1. Estructura del Archivo

Ver `data/README.md` para guía completa.

Formato:
```markdown
# Título del Tema - Nivel

## Introducción
...

## Conceptos Principales
...

## Ejemplos
...

## Práctica
...
```

### 2. Naming Convention

```
{topic}_{level}.md
```

Ejemplos:
- `past_simple_a2.md`
- `phrasal_verbs_b2.md`
- `business_vocabulary_c1.md`

### 3. Proceso

```bash
# 1. Crear archivo en carpeta apropiada
vim data/english_content/grammar/past_simple_a2.md

# 2. Seguir estructura y convenciones

# 3. Ejecutar ingesta
python -m rag.ingest

# 4. Verificar en Qdrant
curl http://localhost:6333/collections/english_content
```

---

## 🔍 Code Review Checklist

### Para Reviewers

- [ ] Código es claro y legible
- [ ] Tests adecuados incluidos
- [ ] Documentación actualizada
- [ ] No hay código duplicado
- [ ] Manejo de errores apropiado
- [ ] Performance considerado
- [ ] Security considerado
- [ ] Breaking changes documentados

### Para Contributors

- [ ] PR description clara
- [ ] Commits atómicos y descriptivos
- [ ] Tests pasan
- [ ] Sin conflicts con main
- [ ] Documentación actualizada

---

## 🎯 Áreas que Necesitan Ayuda

Siempre buscamos ayuda en:

### Alto Prioridad
- [ ] Tests adicionales (coverage < 80%)
- [ ] Documentación API (OpenAPI specs)
- [ ] Performance optimization
- [ ] Contenido educativo (lecciones)

### Media Prioridad
- [ ] Frontend web
- [ ] Mobile app
- [ ] Internacionalización (i18n)
- [ ] Accessibility improvements

### Baja Prioridad
- [ ] Refactoring código legacy
- [ ] Mejoras UI/UX
- [ ] Traducción documentación

---

## 📞 Obtener Ayuda

### Canales

- **GitHub Issues**: Para bugs y features
- **Discussions**: Para preguntas y discusiones
- **Discord**: Para chat en tiempo real
- **Email**: contribute@english-tutor-ai.com

### Recursos

- [Setup Guide](SETUP_GUIDE.md)
- [Architecture Doc](PROYECTO_FINAL_ENGLISH_TUTOR.md)
- [API Examples](API_EXAMPLES.md)
- [Navigation Guide](GUIA_NAVEGACION.md)

---

## 🏆 Reconocimientos

### Contributors

Todos los contributors serán:
- Listados en AUTHORS.md
- Reconocidos en release notes
- Mencionados en la documentación

### Top Contributors

Contribuciones excepcionales pueden resultar en:
- Commit access
- Core team membership
- Conference invitations
- Swag y merchandising

---

## 📅 Release Process

### Versioning

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Release Cycle

- **Patch releases**: Cada 2 semanas
- **Minor releases**: Cada 1-2 meses
- **Major releases**: Según necesidad

---

## ✅ Final Checklist

Antes de hacer tu primer PR:

- [ ] Leí CONTRIBUTING.md completo
- [ ] Setup de desarrollo funcionando
- [ ] Tests pasan localmente
- [ ] Código formateado (black/ruff)
- [ ] Commits siguen convención
- [ ] PR description completa
- [ ] Documentación actualizada

---

## 🎉 ¡Gracias por Contribuir!

Tu contribución hace que este proyecto sea mejor para todos.

**Happy Coding!** 🚀

---

*Última actualización: 2024*
*Preguntas? Abre un issue o únete a nuestro Discord*
