# PI Planning
**ART:** {{ project.art_name | default('ART Name') }}
**PI:** {{ pi_number | default('X') }}
**Fechas:** {{ format_date(pi_start_date) }} - {{ format_date(pi_end_date) }}

## Objetivos del PI
{% for objective in pi_objectives | default([]) %}
### {{ loop.index }}. {{ objective.title }}
- **Descripción:** {{ objective.description }}
- **Valor de Negocio:** {{ objective.business_value }}
- **Equipos Involucrados:** {{ objective.teams | join(', ') }}
{% endfor %}

## Features Planificadas
| Feature | Epic | Equipo | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 |
|---------|------|--------|----------|----------|----------|----------|----------|
{% for feature in features | default([]) %}
| {{ feature.name }} | {{ feature.epic }} | {{ feature.team }} | {{ feature.sprint1 }} | {{ feature.sprint2 }} | {{ feature.sprint3 }} | {{ feature.sprint4 }} | {{ feature.sprint5 }} |
{% endfor %}

## Dependencies
{% for dependency in dependencies | default([]) %}
- **{{ dependency.from_team }}** → **{{ dependency.to_team }}**: {{ dependency.description }}
{% endfor %}

## Risks and Issues
{% for risk in risks | default([]) %}
### {{ risk.title }}
- **Probabilidad:** {{ risk.probability }}
- **Impacto:** {{ risk.impact }}
- **Mitigación:** {{ risk.mitigation }}
- **Owner:** {{ risk.owner }}
{% endfor %}
