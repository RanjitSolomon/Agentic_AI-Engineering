from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field 
from crewai_tools import SerperDevTool
from .tools.push_tool import PushNotificationTool 
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory 
from crewai.memory.storage.rag_storage import RAGStorage 
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class TrendingCompany(BaseModel): 
    """ A company that is in the news and attracting attention """ 
    name: str = Field(description="Company name") 
    ticker: str = Field(description="Stock ticker symbol") 
    reason: str = Field(description="Reason this company is trending in the news")    

class TrendingCompanyList(BaseModel): 
    """List of multiple trending companies that are in the news""" 
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")    

class TrendingCompanyResearch(BaseModel): 
    """Detailed research on a company""" 
    name: str = Field(description="Company name") 
    market_position: str = Field(description="Current market position and competitive analysis") 
    future_outlook: str = Field(description="Future outlook and growth prospect") 
    investment_potential: str = Field(description="Investment potential and suitability for investment")

class TrendingCompanyResearchList(BaseModel): 
    """A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml' 
    tasks_config = 'config/tasks.yaml'

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            tools=[SerperDevTool()],
            memory=True
        )
    
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'], # type: ignore[index]
            tools=[SerperDevTool()]
        )
    
    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], tools=[PushNotificationTool()], memory=True)

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompanyList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompanyResearchList
        )
    
    @task 
    def pick_best_company(self) -> Task: 
        return Task(
            config=self.tasks_config['pick_best_company']
        )


    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        short_term_memory = ShortTermMemory(
            storage = RAGStorage(
                embedder_config = {
                    "provider": "openai", 
                    "config": {
                        "model": 'text-embedding-3-small'
                    }
                },
                type="short_term",
                path="./memory/"
            )
        )

        long_term_memory = LongTermMemory(
            storage = LTMSQLiteStorage(
                db_path = "./memory/long_term_memory_storage.db"
            )
        )

        entity_memory = EntityMemory(
            storage = RAGStorage(
                embedder_config ={
                    "provider": "openai",
                    "config":{
                        "model": 'text-embedding-3-small'
                    }
                },
                type="short_term",
                path="./memory/"
            )
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical, # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
            verbose=True,
            manager_agent=manager,
            memory=True,
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory,
            entity_memory=entity_memory
        )
