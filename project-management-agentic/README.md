# PMP Multi-Agent System

Sistema completo de gestión de proyectos que utiliza agentes de IA especializados en metodologías PMP y SAFe.

## 🚀 Instalación Rápida

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tu API key de OpenAI o Anthropic
```

3. **Inicializar sistema**:
```bash
python main.py init
```

4. **Probar el sistema**:
```bash
python main.py demo
```

## 🔧 Comandos Disponibles

```bash
# Ver estado del sistema
python main.py status

# Crear proyecto
python main.py create-project "Mi Proyecto" --description "Descripción" --methodology PMP

# Listar proyectos
python main.py list-projects

# Ejecutar demo
python main.py demo
```

## 📁 Estructura

```
pmp_multiagent_system/
├── main.py              # Punto de entrada
├── config/              # Configuración
├── agents/              # Agentes de IA
├── models/              # Modelos de BD
├── storage/             # Gestión de archivos/BD
├── utils/               # Utilidades
├── data/                # Datos y proyectos
└── templates/           # Plantillas
```

## 🛠️ Configuración

Edita `.env` con tu clave API:

```bash
OPENAI_API_KEY=tu_clave_aqui
# O
ANTHROPIC_API_KEY=tu_clave_aqui
```

## 🤝 Soporte

Para problemas o preguntas, revisa los logs en `./logs/` o ejecuta `python main.py status`.
