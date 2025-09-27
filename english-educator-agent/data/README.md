# Educational Content Repository

Este directorio contiene todo el contenido educativo que será vectorizado e indexado en el sistema RAG.

## 📁 Estructura

```
english_content/
├── grammar/         # Lecciones de gramática
├── vocabulary/      # Listas y lecciones de vocabulario
├── exercises/       # Ejercicios y práctica
├── reading/         # Textos de lectura
├── writing/         # Guías de escritura
└── pronunciation/   # Guías de pronunciación
```

## 📝 Formato de Archivos

### Convenciones de Nomenclatura

Usa este formato para nombres de archivo:
```
{topic}_{level}.md
```

Ejemplos:
- `present_perfect_b1.md`
- `common_vocabulary_a1.md`
- `business_english_c1.md`

### Niveles CEFR

- **A1** - Principiante
- **A2** - Elemental
- **B1** - Intermedio
- **B2** - Intermedio-Alto
- **C1** - Avanzado
- **C2** - Maestría

### Estructura de Contenido

Cada archivo debe seguir esta estructura:

```markdown
# Título del Tema - Nivel

## Introducción
Breve introducción al tema

## Conceptos Principales
### Concepto 1
Explicación...

### Concepto 2
Explicación...

## Ejemplos
- Ejemplo 1
- Ejemplo 2

## Práctica
Ejercicios o actividades

## Errores Comunes
Qué evitar

## Consejos
Tips útiles

## Recursos Adicionales
Enlaces o referencias
```

## 🎯 Directrices de Contenido

### Para Gramática
- Explicaciones claras y concisas
- Múltiples ejemplos por concepto
- Comparaciones con otros tiempos/estructuras
- Errores comunes señalados
- Ejercicios de práctica

### Para Vocabulario
- Agrupación temática
- Definiciones simples
- Ejemplos en contexto
- Sinónimos y antónimos
- Collocations comunes

### Para Ejercicios
- Variedad de tipos (multiple choice, fill-in-blank, etc.)
- Respuestas incluidas
- Explicaciones de respuestas
- Nivel apropiado claramente indicado

## 🔄 Proceso de Ingesta

1. **Agregar Contenido**: Coloca archivos .md en las carpetas apropiadas

2. **Ejecutar Ingesta**:
```bash
cd backend
python -m rag.ingest
```

3. **Verificar**: Los archivos serán:
   - Divididos en chunks
   - Vectorizados con OpenAI embeddings
   - Almacenados en Qdrant

## 📊 Metadata Automática

El sistema extrae automáticamente:
- **Topic**: Desde el título o nombre de archivo
- **Level**: Desde el nombre de archivo (a1, a2, b1, b2, c1, c2)
- **Type**: Categoría del contenido (grammar, vocabulary, exercise, etc.)

## ✅ Checklist para Nuevo Contenido

Antes de agregar contenido, verifica:

- [ ] Nombre de archivo sigue convención `{topic}_{level}.md`
- [ ] Nivel CEFR es correcto y apropiado
- [ ] Contiene título con nivel
- [ ] Tiene estructura clara con secciones
- [ ] Incluye ejemplos prácticos
- [ ] Sin errores ortográficos o gramaticales
- [ ] Lenguaje apropiado para el nivel indicado
- [ ] Formato Markdown correcto

## 📚 Contenido Actual

### Grammar
- ✅ `present_perfect_b1.md` - Present Perfect Tense
- ✅ `conditionals_b1_b2.md` - Conditionals

### Vocabulary
- ✅ `common_vocabulary_a1.md` - Vocabulario básico A1

### Exercises
- 🔄 Por agregar

### Reading
- 🔄 Por agregar

### Writing
- 🔄 Por agregar

## 🎨 Ejemplos de Contenido

### Ejemplo: Lección de Gramática

```markdown
# Past Simple Tense - A2

## What is Past Simple?

The Past Simple tense is used to describe completed actions in the past.

## Formation

### Regular Verbs
Add -ed to the base form:
- walk → walked
- play → played

### Irregular Verbs
Learn the past form:
- go → went
- eat → ate

## Examples
- I walked to school yesterday.
- She ate breakfast at 8 AM.
- They played soccer last weekend.

## Practice
Complete with the correct past simple form:
1. I _____ (visit) my grandmother last week.
2. He _____ (go) to the movies yesterday.

## Common Mistakes
❌ I goed to the store.
✅ I went to the store.
```

### Ejemplo: Vocabulario Temático

```markdown
# Food and Drinks - A1

## Meals
- **Breakfast** - First meal of the day
- **Lunch** - Midday meal
- **Dinner** - Evening meal

## Common Foods
- **Bread** - Made from flour and water
- **Rice** - Small white or brown grains
- **Eggs** - From chickens

## Practice
Match the food with its category:
1. Apple → a) Vegetable
2. Carrot → b) Fruit
3. Milk → c) Drink
```

## 🚀 Próximos Pasos

Para expandir el contenido:

1. **Priorizar por nivel**: Empezar con A1-B1 (más usuarios)
2. **Cubrir temas esenciales**: Tiempos verbales, vocabulario común
3. **Agregar variedad**: Diferentes tipos de ejercicios
4. **Mantener calidad**: Revisar y actualizar regularmente

## 📧 Contribuciones

Para agregar contenido:
1. Seguir las directrices de este README
2. Usar Markdown correcto
3. Verificar nivel apropiado
4. Ejecutar ingesta después de agregar

---

**Última actualización**: 2024
**Archivos totales**: 3
**Listo para ingesta**: ✅
