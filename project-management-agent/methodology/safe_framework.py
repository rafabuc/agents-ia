from typing import Dict, List
from datetime import datetime

class SAFeFramework:
    """Framework SAFe para desarrollo ágil escalado"""
    
    def __init__(self):
        self.configurations = [
            "Essential SAFe", "Large Solution SAFe", 
            "Portfolio SAFe", "Full SAFe"
        ]
        
        self.core_values = [
            "Alignment", "Built-in Quality", 
            "Transparency", "Program Execution"
        ]
        
        self.lean_agile_principles = [
            "Take an economic view",
            "Apply systems thinking", 
            "Assume variability; preserve options",
            "Build incrementally with fast, integrated learning cycles"
        ]
    
    def get_next_steps(self, current_phase: str) -> List[str]:
        """Obtener próximos pasos según la fase actual SAFe"""
        phase_steps = {
            "assessment": [
                "Realizar SAFe assessment organizacional",
                "Identificar value streams",
                "Definir ARTs (Agile Release Trains)",
                "Seleccionar configuración SAFe apropiada"
            ],
            "preparation": [
                "Entrenar líderes en SAFe",
                "Establecer Lean-Agile Center of Excellence",
                "Identificar Product Owners y Scrum Masters",
                "Definir Definition of Done común"
            ]
        }
        
        return phase_steps.get(current_phase.lower(), [])
    
    def get_guidance(self) -> Dict:
        """Obtener guía del framework SAFe"""
        return {
            "implementation_roadmap": [
                "Reaching the Tipping Point",
                "Train Lean-Agile Change Agents", 
                "Train Executives, Managers, and Leaders",
                "Create a Lean-Agile Center of Excellence"
            ],
            "success_patterns": [
                "Executive leadership and sponsorship",
                "Training and education first",
                "Start with Essential SAFe",
                "Focus on value streams"
            ]
        }
