# Project Charter
**Proyecto:** {{ project.name }}
**Fecha:** {{ format_date(now()) }}
**Project Manager:** {{ project.manager | default('TBD') }}

## 1. Propósito del Proyecto
{{ project.description }}

## 2. Objetivos del Proyecto
{% for objective in project.objectives | default(['TBD']) %}
- {{ objective }}
{% endfor %}

## 3. Alcance del Proyecto
### Incluye:
{% for item in project.scope.includes | default(['TBD']) %}
- {{ item }}
{% endfor %}

### No Incluye:
{% for item in project.scope.excludes | default(['TBD']) %}
- {{ item }}
{% endfor %}

## 4. Entregables Principales
{% for deliverable in project.deliverables | default(['TBD']) %}
- {{ deliverable }}
{% endfor %}

## 5. Cronograma de Alto Nivel
- **Inicio:** {{ format_date(project.start_date | default(now())) }}
- **Fin:** {{ format_date(project.end_date | default('TBD')) }}

## 6. Presupuesto Estimado
{{ project.budget | default('TBD') }}

## 7. Riesgos de Alto Nivel
{% for risk in project.high_level_risks | default(['TBD']) %}
- {{ risk }}
{% endfor %}

## 8. Stakeholders Principales
{% for stakeholder in project.stakeholders | default([]) %}
- **{{ stakeholder.name }}:** {{ stakeholder.role }}
{% endfor %}

## 9. Criterios de Éxito
{% for criteria in project.success_criteria | default(['TBD']) %}
- {{ criteria }}
{% endfor %}

## 10. Autorización
**Sponsor:** {{ project.sponsor | default('TBD') }}
**Fecha de Aprobación:** _______________
**Firma:** _______________
