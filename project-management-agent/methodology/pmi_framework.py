from typing import Dict, List
from datetime import datetime

class PMIFramework:
    """Framework PMI para gestión de proyectos"""
    
    def __init__(self):
        self.process_groups = [
            "Initiating", "Planning", "Executing", 
            "Monitoring & Controlling", "Closing"
        ]
        
        self.knowledge_areas = [
            "Integration", "Scope", "Schedule", "Cost", "Quality",
            "Resource", "Communications", "Risk", "Procurement", "Stakeholder"
        ]
    
    def get_next_steps(self, current_phase: str) -> List[str]:
        """Obtener próximos pasos según la fase actual"""
        phase_steps = {
            "initiation": [
                "Desarrollar Project Charter",
                "Identificar stakeholders clave",
                "Realizar análisis inicial de riesgos",
                "Definir criterios de éxito"
            ],
            "planning": [
                "Desarrollar Project Management Plan",
                "Crear Work Breakdown Structure (WBS)",
                "Estimar duración y costos",
                "Identificar y analizar riesgos"
            ]
        }
        
        return phase_steps.get(current_phase.lower(), [])
    
    def get_guidance(self) -> Dict:
        """Obtener guía del framework PMI"""
        return {
            "principles": [
                "Stewardship", "Team", "Stakeholders", "Value",
                "Systems Thinking", "Leadership", "Tailoring", "Quality"
            ],
            "performance_domains": [
                "Stakeholders", "Team", "Development Approach",
                "Planning", "Project Work", "Delivery", "Measurement", "Uncertainty"
            ]
        }
