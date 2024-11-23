# crews/crew.py
import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool

# from crews.tools.vision_tool import VisionTool
from crewai_tools import VisionTool


from utils.crews import set_openai_api_key_for_vision_tool


위험성평가_이행점검_매뉴얼 = "src/pdfs/붙임1._2022_위험성평가_이행점검_매뉴얼.pdf"
위험성평가에_관한_지침 = "src/pdfs/사업장 위험성평가에 관한 지침(고용노동부고시)(제2023-19호)(20230522).pdf"
산업안전보건기준에_관한_규칙 = "src/pdfs/산업안전보건기준에 관한 규칙(고용노동부령)(제00417호)(20240628).pdf"
TOOL_MODEL = "gpt-4o"

os.environ["OPENAI_API_KEY"] = set_openai_api_key_for_vision_tool(TOOL_MODEL)



@CrewBase
class RiskAssessmentCrew():
    """
    RiskAssessmentCrew defines the setup for agents and tasks involved in assessing
    and mitigating risks in construction scenarios. The crew integrates tools and 
    configurations for efficient risk analysis, assessment, and reduction.

    Attributes:
        agents_config (dict): Configuration for initializing agents.
        tasks_config (dict): Configuration for initializing tasks.
    """

    @agent
    def integrated_risk_detector(self) -> Agent:
        """
        Initializes an Agent specializing in detecting potential risks from 
        construction site images and task descriptions. Uses a VisionTool for 
        image analysis.

        Agent Role:
            건설 현장 유해·위험 요인 식별 전문가
        Goal:
            제공된 건설 현장 이미지와 작업 설명을 분석하여 잠재적 위험을 식별합니다.
        Backstory:
            30년 이상의 경험을 가진 건설 현장 안전 전문가로, 작업 환경과 수행 작업의 상호작용을 평가해 사고를 예방합니다.

        Returns:
            Agent: An instance configured for integrated risk detection.
        """
        return Agent(
            config=self.agents_config['integrated_risk_detector'],
            tools=[VisionTool()],
            verbose=True
        )

    @agent
    def risk_assessment_expert(self) -> Agent:
        """
        Initializes an Agent specializing in evaluating the severity and frequency 
        of identified risks.

        Agent Role:
            위험성 평가 전문가
        Goal:
            식별된 위험 요소의 심각성 및 빈도를 평가하고 우선순위를 정합니다.
        Backstory:
            건설 산업에서 30년 이상의 경험을 가진 베테랑으로, 심각성과 빈도를 바탕으로 사고를 예방하는 데 기여합니다.

        Returns:
            Agent: An instance configured for risk assessment.
        """
        return Agent(
            config=self.agents_config['risk_assessment_expert'],
            tools=[
                PDFSearchTool(pdf=위험성평가_이행점검_매뉴얼),
                PDFSearchTool(pdf=위험성평가에_관한_지침),
                PDFSearchTool(pdf=산업안전보건기준에_관한_규칙)
            ],
            verbose=True
        )

    @agent
    def risk_reduction_expert(self) -> Agent:
        """
        Initializes an Agent focusing on developing practical and effective risk 
        reduction measures.

        Agent Role:
            위험 저감 대책 전문가
        Goal:
            위험 평가 결과를 기반으로 효과적인 위험 감소 조치를 개발하여 안전성을 향상시킵니다.
        Backstory:
            30년 이상의 경험을 가진 전문가로, 복잡한 평가를 실행 가능한 대책으로 전환합니다.

        Returns:
            Agent: An instance configured for risk reduction.
        """
        return Agent(
            config=self.agents_config['risk_reduction_expert'],
            tools=[
                PDFSearchTool(pdf=위험성평가_이행점검_매뉴얼),
                PDFSearchTool(pdf=위험성평가에_관한_지침),
                PDFSearchTool(pdf=산업안전보건기준에_관한_규칙)
            ],
            verbose=True
        )

    @task
    def integrated_risk_detection(self) -> Task:
        """
        Defines a Task to analyze both site images and task descriptions for 
        identifying potential risks.

        Task Description:
            제공된 건설 현장 이미지와 작업 설명을 동시에 분석하여 잠재적 위험을 식별하고 나열합니다.

        Returns:
            Task: An instance configured for integrated risk detection.
        """
        return Task(
            config=self.tasks_config['integrated_risk_detection'],
            agent=self.integrated_risk_detector()
        )

    @task
    def risk_assessment(self) -> Task:
        """
        Defines a Task to evaluate the severity and frequency of identified risks 
        and assign risk levels.

        Task Description:
            위험 요소를 심각도(S)와 빈도(F)를 기준으로 평가하고 위험 등급을 부여합니다.

        Returns:
            Task: An instance configured for risk assessment.
        """
        return Task(
            config=self.tasks_config['risk_assessment'],
            agent=self.risk_assessment_expert()
        )

    @task
    def risk_reduction(self) -> Task:
        """
        Defines a Task to propose specific risk reduction measures for identified 
        risks with unacceptable levels.

        Task Description:
            위험 평가 결과를 분석하여 실질적인 위험 감소 조치를 제안합니다.

        Returns:
            Task: An instance configured for risk reduction.
        """
        return Task(
            config=self.tasks_config['risk_reduction'],
            agent=self.risk_reduction_expert()
        )

    @crew
    def crew(self, model) -> Crew:
        """
        Creates the RiskAssessment crew, combining agents and tasks for hierarchical 
        risk management.

        Args:
            model (LLM): The large language model used for task management.

        Returns:
            Crew: A configured crew for managing risk assessment workflows.
        """
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.hierarchical,
            manager_llm=model,
            verbose=True,
            planning=True
        )


def run_crew(model, image, tasks):
    """
    Executes the RiskAssessmentCrew by kicking off the process with the provided 
    inputs.

    Args:
        model (LLM): The large language model managing the workflow.
        image (str): Path or identifier of the construction site image.
        tasks (list): List of task descriptions.

    Returns:
        Output from the kickoff process of the RiskAssessmentCrew.
    """
    return RiskAssessmentCrew().crew(model).kickoff(inputs={
        'image': image,
        'tasks': tasks
    })
