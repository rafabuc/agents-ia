# 🚀 Project Management Agent

Agente avanzado de gestión de proyectos con soporte completo para metodologías PMI y SAFe, potenciado por Claude AI.

## ✨ Características

- ✅ **Planes de trabajo** basados en PMI y SAFe
- ✅ **Documentación automática** con plantillas
- ✅ **Chat contextual** con Claude AI
- ✅ **Interfaz CLI elegante** con Rich
- ✅ **Sistema de proyectos** persistente

## 🚀 Instalación Rápida

### Requisitos
- Python 3.9+
- Clave API de Anthropic (Claude)

### Pasos
```bash
# 1. Clonar/descargar código
# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
cp .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY

# 5. Configuración inicial
python main.py setup

# 6. ¡Usar el agente!
python main.py start
```

## 🎮 Uso

### Modo Interactivo
```bash
python main.py start
```

### Comandos CLI
```bash
python main.py setup     # Configuración inicial
python main.py test      # Probar instalación
python main.py --help    # Ver ayuda
```

## 📖 Comandos Disponibles

- `crear proyecto` - Crear nuevo proyecto
- `proyectos` - Listar proyectos
- `generar plan` - Crear plan de trabajo
- `help` - Mostrar ayuda
- `quit` - Salir

## 🔑 Obtener API Key

1. Ve a https://console.anthropic.com/
2. Crea cuenta y agrega tarjeta
3. Crear API Key
4. Copiar clave completa
5. Agregar a .env: `ANTHROPIC_API_KEY=tu_clave_aqui`

## 💰 Costos

- **Créditos iniciales**: $5 USD gratuitos
- **Uso típico**: $0.01-0.05 por consulta
- **Uso diario**: $0.25-1.00 USD

## 🎯 Ejemplos de Uso

```
PM-Agent> crear proyecto
# Guía interactiva para crear proyecto

PM-Agent> ¿Qué es un Project Charter en PMI?
# Explicación detallada con contexto

PM-Agent> generar plan
# Plan de trabajo completo basado en metodología
```

## 🛠️ Estructura del Proyecto

- `core/` - Motor del agente y Claude client
- `methodology/` - Frameworks PMI y SAFe  
- `templates/` - Plantillas de documentos
- `knowledge_base/` - Base de conocimiento
- `utils/` - Utilidades y helpers

## 🐛 Troubleshooting

### Error: API key not found
```bash
# Verificar .env
cat .env | grep ANTHROPIC_API_KEY
```

### Error: Import modules
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt
```

## 📝 Licencia

MIT License - ver LICENSE para detalles.

## 🤝 Contribuir

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agregar funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

---

**⭐ Si te ayuda, considera darle una estrella!**
