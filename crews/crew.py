# src/latest_ai_development/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class RiskAssessmentCrew():
    """RiskAssessment crew"""

    @agent
    def integrated_risk_detector(self) -> Agent:
        return Agent(
        config=self.agents_config['integrated_risk_detector'],
        verbose=True,
        tools=[SerperDevTool()]
        )

    @agent
    def risk_assessment_expert(self) -> Agent:
        return Agent(
        config=self.agents_config['risk_assessment_expert'],
        verbose=True
        )

    @agent
    def risk_reduction_expert(self) -> Agent:
        return Agent(
        config=self.agents_config['risk_reduction_expert'],
        verbose=True
        )

    @task
    def integrated_risk_detection(self) -> Task:
        return Task(
        config=self.tasks_config['integrated_risk_detection'],
        )

    @task
    def risk_assessment(self) -> Task:
        return Task(
        config=self.tasks_config['risk_assessment'],
        )

    @task
    def risk_reduction(self) -> Task:
        return Task(
        config=self.tasks_config['risk_reduction'],
        )

    @crew
    def crew(self, model) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        return Crew(
        agents=self.agents, # Automatically created by the @agent decorator
        tasks=self.tasks, # Automatically created by the @task decorator
        process=Process.hierarchical,
        manager_llm=model,
        verbose=True,
    ) 


def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI Agents'
    }
    return RiskAssessmentCrew().crew().kickoff(inputs=inputs)