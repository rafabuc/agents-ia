# ⚡ Quick Start Commands - English Educator Agent

## 🚀 Comandos Rápidos para Empezar

### 1️⃣ Verificar Ubicación
```bash
cd C:\workspace\python\MLOPS\DataTalksClub\agents-ia\english-educator-agent
dir
```

### 2️⃣ Configurar Variables de Entorno
```bash
# Copiar template
copy .env.example .env

# Editar con tu editor
notepad .env
# O
code .env
```

**Agregar tus API keys:**
```env
OPENAI_API_KEY=sk-tu-key-aqui
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui
```

### 3️⃣ Levantar Docker Services
```bash
cd docker
docker-compose up -d
```

**Verificar servicios:**
```bash
docker-compose ps
```

### 4️⃣ Setup Backend Python
```bash
cd ..\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 5️⃣ Iniciar API Server
```bash
# Asegurar que estás en /backend con venv activado
uvicorn main:app --reload --port 8000
```

### 6️⃣ Probar la API (En otra terminal)
```bash
# Health check
curl http://localhost:8000/health

# Ver documentación
start http://localhost:8000/docs

# Test evaluación
curl -X POST http://localhost:8000/api/v1/evaluate -H "Content-Type: application/json" -d "{\"user_id\": 1}"
```

### 7️⃣ Celery Workers (Opcional)
```bash
# Terminal 1 - Worker
cd backend
venv\Scripts\activate
celery -A tasks worker --loglevel=info --pool=solo

# Terminal 2 - Beat Scheduler
cd backend
venv\Scripts\activate
celery -A tasks beat --loglevel=info
```

---

## 🧪 Comandos de Testing

```bash
# Activar venv
cd backend
venv\Scripts\activate

# Ejecutar todos los tests
pytest tests/ -v

# Solo unit tests
pytest tests/unit/ -v

# Con coverage
pytest --cov=backend tests/

# Test específico
pytest tests/unit/test_evaluator.py -v
```

---

## 🐳 Comandos Docker Útiles

```bash
cd docker

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f postgres

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Ver estado
docker-compose ps

# Entrar a un contenedor
docker exec -it english-tutor-postgres psql -U user -d english_tutor
```

---

## 📊 Acceder a UIs de Monitoring

```bash
# RabbitMQ Management
start http://localhost:15672
# Usuario: admin, Password: admin

# Grafana
start http://localhost:3001
# Usuario: admin, Password: admin

# Prometheus
start http://localhost:9090

# API Docs
start http://localhost:8000/docs

# Qdrant Dashboard
start http://localhost:6333/dashboard
```

---

## 🔍 Comandos de Debugging

```bash
# Ver variables de entorno
type .env

# Verificar Python packages
pip list | findstr langchain

# Verificar puertos en uso
netstat -ano | findstr :8000

# Ver procesos Python
tasklist | findstr python

# Limpiar cache Python
rd /s /q __pycache__
```

---

## 🧹 Comandos de Limpieza

```bash
# Limpiar Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Limpiar Docker
docker system prune -a
docker volume prune

# Limpiar logs
del /s *.log
```

---

## 📦 Comandos de Desarrollo

```bash
# Activar entorno virtual
venv\Scripts\activate

# Instalar nueva dependencia
pip install nombre-paquete
pip freeze > requirements.txt

# Formatear código
black backend/
ruff backend/

# Type checking
mypy backend/

# Generar requirements.txt
pip freeze > requirements.txt
```

---

## 🔄 Comandos Git (Para tu repo)

```bash
# Inicializar repo
git init
git add .
git commit -m "Initial commit: English Educator Agent"

# Crear repo en GitHub y conectar
git remote add origin https://github.com/tu-usuario/english-educator-agent.git
git push -u origin main

# Crear rama de desarrollo
git checkout -b develop

# Commit y push
git add .
git commit -m "Add new feature"
git push
```

---

## 🚨 Solución Rápida de Problemas

### Problema: Puerto 8000 ocupado
```bash
# Encontrar proceso
netstat -ano | findstr :8000

# Matar proceso (usa el PID del comando anterior)
taskkill /PID <pid> /F

# O usar otro puerto
uvicorn main:app --reload --port 8001
```

### Problema: Docker no levanta
```bash
# Reiniciar Docker Desktop
# Luego:
cd docker
docker-compose down
docker-compose up -d
```

### Problema: ModuleNotFoundError
```bash
# Verificar que venv está activado
venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Problema: Celery no funciona
```bash
# Verificar RabbitMQ
docker-compose ps rabbitmq

# Reiniciar RabbitMQ
docker-compose restart rabbitmq

# Usar pool solo en Windows
celery -A tasks worker --loglevel=info --pool=solo
```

---

## 📝 Scripts de Utilidad

### Script: Verificar Setup Completo
```bash
@echo off
echo Verificando setup...
echo.

echo [1/5] Verificando Docker...
docker-compose ps
echo.

echo [2/5] Verificando Python...
python --version
echo.

echo [3/5] Verificando dependencias...
pip list | findstr langchain
echo.

echo [4/5] Verificando API...
curl http://localhost:8000/health
echo.

echo [5/5] Verificando servicios...
curl http://localhost:15672
echo.

echo Setup verification complete!
```

### Script: Reiniciar Todo
```bash
@echo off
echo Reiniciando servicios...

cd docker
docker-compose down
timeout /t 3
docker-compose up -d

echo Servicios reiniciados!
docker-compose ps
```

---

## 🎯 Workflow de Desarrollo Típico

### Día a Día
```bash
# 1. Activar entorno
cd backend
venv\Scripts\activate

# 2. Actualizar código
git pull

# 3. Instalar nuevas dependencias (si hay)
pip install -r requirements.txt

# 4. Levantar Docker si no está
cd ..\docker
docker-compose up -d

# 5. Iniciar servidor
cd ..\backend
uvicorn main:app --reload

# 6. Desarrollar y probar
# ...

# 7. Ejecutar tests antes de commit
pytest tests/ -v

# 8. Commit y push
git add .
git commit -m "Your message"
git push
```

---

## 💾 Comandos de Backup

```bash
# Backup de base de datos
docker exec english-tutor-postgres pg_dump -U user english_tutor > backup.sql

# Restaurar backup
docker exec -i english-tutor-postgres psql -U user english_tutor < backup.sql

# Backup de volúmenes Docker
docker-compose down
docker run --rm -v english-educator-agent_postgres_data:/data -v %cd%:/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

---

## 🔐 Variables de Entorno Críticas

```bash
# Verificar que estén configuradas
echo %OPENAI_API_KEY%
echo %ANTHROPIC_API_KEY%

# Si no están en .env, setear temporalmente
set OPENAI_API_KEY=sk-...
set ANTHROPIC_API_KEY=sk-ant-...
```

---

## 📚 Comandos de Documentación

```bash
# Generar documentación API
cd backend
python -c "from main import app; import json; print(json.dumps(app.openapi(), indent=2))" > api_docs.json

# Ver dependencias instaladas
pip list

# Ver árbol de dependencias
pip install pipdeptree
pipdeptree
```

---

## ⚡ One-Liner Commands

```bash
# Setup completo en un comando
git clone <repo> && cd english-educator-agent && copy .env.example .env && cd docker && docker-compose up -d && cd ..\backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# Reinicio rápido
cd docker && docker-compose restart && cd ..\backend && venv\Scripts\activate && uvicorn main:app --reload

# Test rápido
cd backend && venv\Scripts\activate && pytest tests/ -v --tb=short

# Ver todo el estado
docker-compose ps && netstat -ano | findstr ":8000 :5432 :6379 :6333" && pip list | findstr langchain
```

---

## 🎉 ¡Todo Listo!

Ahora tienes todos los comandos necesarios para trabajar con el proyecto.

**Siguiente paso:** Ejecuta los comandos en orden y empieza a desarrollar.

**¿Problemas?** Revisa la sección de troubleshooting o consulta `SETUP_GUIDE.md`
