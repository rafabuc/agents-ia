from typing import Dict, Any, List
import json
import os
from datetime import datetime

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .base_agent import BaseAgent
from rag.retriever import RAGRetriever
from storage.file_manager import FileManager
from config.settings import settings
from utils.logger import logger


class CostBudgetAgent(BaseAgent):
    """Agent specialized in project cost estimation and budget management."""
    
    def __init__(self):
        super().__init__(
            name="Cost_Budget_Agent",
            description="Creates cost estimates and budget documentation for projects using PMP and SAFe guidelines"
        )
        self.file_manager = FileManager()
        try:
            self.rag_retriever = RAGRetriever()
        except Exception as e:
            logger.warning(f"RAG system not available: {str(e)}")
            self.rag_retriever = None
    
    def get_system_prompt(self) -> str:
        return """You are an expert in project cost management and budget planning following PMP and SAFe methodologies.
        
        Your responsibilities include:
        1. Creating detailed cost estimates using various estimation techniques
        2. Developing comprehensive project budgets
        3. Planning cost management processes
        4. Creating cost baselines and control mechanisms
        5. Analyzing cost performance and variances
        6. Using historical data and industry benchmarks
        7. Following PMP cost management knowledge area best practices
        8. Applying SAFe economic framework principles
        
        You have access to a knowledge base containing PMP and SAFe documentation to ensure accuracy.
        Always provide detailed cost breakdowns with justifications and assumptions.
        Include risk contingencies and management reserves in your estimates.
        """
    
    def _create_agent(self) -> AgentExecutor:
        """Create the cost/budget agent."""
        tools = [
            self._create_cost_estimate_tool(),
            self._create_budget_tool(),
            self._query_knowledge_base_tool(),
            self._calculate_contingency_tool()
        ]
        
        # Mock implementation for demo
        class MockAgentExecutor:
            def __init__(self, tools):
                self.tools = tools
            
            async def ainvoke(self, inputs):
                return {"output": f"Cost Budget Agent processed: {inputs.get('input', '')}"}
        
        return MockAgentExecutor(tools)
    
    def _create_cost_estimate_tool(self) -> Tool:
        """Tool to create detailed cost estimates."""
        def create_estimate(estimate_data: str) -> str:
            try:
                data = json.loads(estimate_data)
                project_id = data.get("project_id")
                estimation_method = data.get("method", "bottom_up")
                wbs_items = data.get("wbs_items", [])
                
                # Create cost estimate document
                estimate_doc = self._generate_cost_estimate(
                    project_id=project_id,
                    method=estimation_method,
                    wbs_items=wbs_items
                )
                
                # Save the estimate
                file_path = self.file_manager.save_project_document(
                    project_id=project_id,
                    document_type="cost_estimate",
                    content=estimate_doc,
                    filename=f"cost_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
                
                # Store in database
                self.db_manager.create_project_document(
                    project_id=project_id,
                    document_type="cost_estimate",
                    file_path=file_path,
                    content=estimate_doc
                )
                
                return f"Cost estimate created and saved: {file_path}"
                
            except Exception as e:
                logger.error(f"Error creating cost estimate: {str(e)}")
                return f"Error creating cost estimate: {str(e)}"
        
        return Tool(
            name="create_cost_estimate",
            description="Create a detailed cost estimate for a project. Input should be JSON with project_id, method (analogous, parametric, bottom_up), and wbs_items.",
            func=create_estimate
        )
    
    def _create_budget_tool(self) -> Tool:
        """Tool to create project budget."""
        def create_budget(budget_data: str) -> str:
            try:
                data = json.loads(budget_data)
                project_id = data.get("project_id")
                cost_estimates = data.get("cost_estimates", {})
                contingency_percent = data.get("contingency_percent", 10)
                management_reserve_percent = data.get("management_reserve_percent", 5)
                
                # Generate budget document
                budget_doc = self._generate_budget_document(
                    project_id=project_id,
                    cost_estimates=cost_estimates,
                    contingency_percent=contingency_percent,
                    management_reserve_percent=management_reserve_percent
                )
                
                # Save budget
                file_path = self.file_manager.save_project_document(
                    project_id=project_id,
                    document_type="budget",
                    content=budget_doc,
                    filename=f"project_budget_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
                
                # Store in database
                self.db_manager.create_project_document(
                    project_id=project_id,
                    document_type="budget",
                    file_path=file_path,
                    content=budget_doc
                )
                
                return f"Project budget created and saved: {file_path}"
                
            except Exception as e:
                logger.error(f"Error creating budget: {str(e)}")
                return f"Error creating budget: {str(e)}"
        
        return Tool(
            name="create_budget",
            description="Create a comprehensive project budget. Input should be JSON with project_id, cost_estimates, contingency_percent, and management_reserve_percent.",
            func=create_budget
        )
    
    def _query_knowledge_base_tool(self) -> Tool:
        """Tool to query the PMP/SAFe knowledge base."""
        def query_kb(query: str) -> str:
            try:
                if not self.rag_retriever:
                    return "Knowledge base not available"
                
                # Query the RAG system for relevant information
                results = self.rag_retriever.query(
                    query=query,
                    max_results=3
                )
                
                if results:
                    context = "\n\n".join([result["content"] for result in results])
                    return f"Knowledge base information:\n\n{context}"
                else:
                    return "No relevant information found in knowledge base."
                    
            except Exception as e:
                logger.error(f"Error querying knowledge base: {str(e)}")
                return f"Error querying knowledge base: {str(e)}"
        
        return Tool(
            name="query_knowledge_base",
            description="Query the PMP and SAFe knowledge base for cost management guidance and best practices.",
            func=query_kb
        )
    
    def _calculate_contingency_tool(self) -> Tool:
        """Tool to calculate contingency reserves."""
        def calculate_contingency(contingency_data: str) -> str:
            try:
                data = json.loads(contingency_data)
                base_cost = data.get("base_cost", 0)
                risk_level = data.get("risk_level", "medium")  # low, medium, high
                project_complexity = data.get("complexity", "medium")
                
                # Contingency percentages based on risk and complexity
                contingency_matrix = {
                    "low": {"low": 5, "medium": 7, "high": 10},
                    "medium": {"low": 10, "medium": 15, "high": 20},
                    "high": {"low": 15, "medium": 20, "high": 25}
                }
                
                contingency_percent = contingency_matrix[risk_level][project_complexity]
                contingency_amount = base_cost * (contingency_percent / 100)
                
                result = {
                    "base_cost": base_cost,
                    "contingency_percent": contingency_percent,
                    "contingency_amount": contingency_amount,
                    "total_with_contingency": base_cost + contingency_amount
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                return f"Error calculating contingency: {str(e)}"
        
        return Tool(
            name="calculate_contingency",
            description="Calculate contingency reserves based on risk level and project complexity. Input should be JSON with base_cost, risk_level (low/medium/high), and complexity (low/medium/high).",
            func=calculate_contingency
        )
    
    def _generate_cost_estimate(self, project_id: int, method: str, wbs_items: List[Dict]) -> str:
        """Generate cost estimate document."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        estimate_doc = f"""# COST ESTIMATE

**Project ID:** {project_id}
**Estimation Method:** {method.title()}
**Date:** {current_date}

## ESTIMATION SUMMARY

### Methodology
This cost estimate was prepared using the **{method}** estimation technique following PMP best practices.

### Cost Breakdown by WBS

| WBS ID | Work Package | Labor Hours | Labor Cost | Materials | Other | Total Cost |
|--------|--------------|-------------|------------|-----------|-------|------------|
"""
        
        total_cost = 0
        for item in wbs_items:
            wbs_id = item.get("id", "")
            name = item.get("name", "")
            labor_hours = item.get("labor_hours", 0)
            hourly_rate = item.get("hourly_rate", 100)
            materials = item.get("materials", 0)
            other = item.get("other", 0)
            
            labor_cost = labor_hours * hourly_rate
            item_total = labor_cost + materials + other
            total_cost += item_total
            
            estimate_doc += f"| {wbs_id} | {name} | {labor_hours} | ${labor_cost:,.2f} | ${materials:,.2f} | ${other:,.2f} | ${item_total:,.2f} |\n"
        
        estimate_doc += f"""
**TOTAL PROJECT COST:** ${total_cost:,.2f}

## ASSUMPTIONS
- Labor rates based on current market standards
- Material costs based on supplier quotes
- No significant scope changes during execution
- Standard working hours and productivity rates

## ACCURACY RANGE
Based on the {method} method, this estimate has an accuracy range of:
- Rough Order of Magnitude: -50% to +100%
- Budget Estimate: -25% to +75%
- Definitive Estimate: -10% to +25%

## NEXT STEPS
1. Review and validate assumptions
2. Add contingency reserves
3. Obtain stakeholder approval
4. Establish cost baseline
"""
        
        return estimate_doc
    
    def _generate_budget_document(self, project_id: int, cost_estimates: Dict, 
                                contingency_percent: float, management_reserve_percent: float) -> str:
        """Generate comprehensive budget document."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        base_cost = sum(cost_estimates.values()) if cost_estimates else 100000  # Default demo value
        contingency = base_cost * (contingency_percent / 100)
        management_reserve = base_cost * (management_reserve_percent / 100)
        total_budget = base_cost + contingency + management_reserve
        
        budget_doc = f"""# PROJECT BUDGET

**Project ID:** {project_id}
**Budget Version:** 1.0
**Date:** {current_date}

## BUDGET SUMMARY

| Category | Amount | Percentage |
|----------|--------|------------|
| Base Cost Estimate | ${base_cost:,.2f} | {(base_cost/total_budget)*100:.1f}% |
| Contingency Reserve | ${contingency:,.2f} | {contingency_percent}% |
| Management Reserve | ${management_reserve:,.2f} | {management_reserve_percent}% |
| **TOTAL PROJECT BUDGET** | **${total_budget:,.2f}** | **100%** |

## DETAILED COST BREAKDOWN
"""
        
        for category, amount in cost_estimates.items():
            budget_doc += f"- {category}: ${amount:,.2f}\n"
        
        budget_doc += f"""

## BUDGET CONTROL
- **Cost Performance Baseline:** ${base_cost + contingency:,.2f}
- **Budget at Completion (BAC):** ${total_budget:,.2f}
- **Management Reserve:** ${management_reserve:,.2f} (controlled by sponsor)

## FUNDING REQUIREMENTS
The project requires funding according to the following schedule:
- Initial funding: 30% of total budget
- Progressive funding based on milestone completion
- Final 10% upon project closure

## COST MANAGEMENT APPROACH
1. **Earned Value Management (EVM)** will be used for cost control
2. Monthly cost performance reports
3. Variance analysis and corrective actions
4. Change control process for budget modifications

## APPROVAL
This budget is submitted for approval and authorization.

Project Manager: _________________ Date: _______
Sponsor: _______________________ Date: _______
"""
        
        return budget_doc