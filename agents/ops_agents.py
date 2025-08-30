from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.llms import OllamaLLM
from config import Config
from tools.custom_tools import CSVReaderTool, CSVWriterTool, JSONWriterTool, PricingCalculatorTool, StockValidatorTool

class OpsAgents:
    def __init__(self):
        self.openai_llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.1
        )
        
        self.gemini_llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        
        self.ollama_llama3 = OllamaLLM(
            model=Config.OLLAMA_LLAMA3_MODEL,
            base_url=Config.OLLAMA_BASE_URL
        )
        
        self.ollama_mistral = OllamaLLM(
            model=Config.OLLAMA_MISTRAL_MODEL,
            base_url=Config.OLLAMA_BASE_URL
        )
    
    def create_manager_agent(self):
        return Agent(
            role="Operations Manager",
            goal="Orchestrate the entire dropshipping operations workflow",
            backstory="Experienced e-commerce manager specializing in automated dropshipping operations",
            verbose=True,
            llm=self.openai_llm,
            tools=[CSVReaderTool(), JSONWriterTool()]
        )
    
    def create_product_sourcing_agent(self):
        return Agent(
            role="Product Sourcing Specialist",
            goal="Select profitable products with sufficient stock",
            backstory="Expert in identifying high-margin products for dropshipping",
            verbose=True,
            llm=self.openai_llm,
            tools=[CSVReaderTool(), StockValidatorTool()]
        )
    
    def create_listing_agent(self):
        return Agent(
            role="E-commerce Listing Specialist",
            goal="Create compelling product listings with SEO optimization",
            backstory="Professional copywriter with expertise in e-commerce product descriptions",
            verbose=True,
            llm=self.openai_llm
        )
    
    def create_pricing_agent(self):
        return Agent(
            role="Pricing Analyst",
            goal="Calculate optimal prices ensuring minimum 25% margin",
            backstory="Data-driven pricing expert with e-commerce experience",
            verbose=True,
            llm=self.openai_llm,
            tools=[PricingCalculatorTool(), CSVWriterTool()]
        )
    
    def create_order_routing_agent(self):
        return Agent(
            role="Order Routing Specialist",
            goal="Decide order fulfillment strategy and handle customer communication",
            backstory="Operations expert in order management and customer service",
            verbose=True,
            llm=self.openai_llm,
            tools=[CSVReaderTool(), JSONWriterTool()]
        )
    
    def create_qa_agent(self):
        return Agent(
            role="Quality Assurance Specialist",
            goal="Review product listings for accuracy and compliance",
            backstory="Detail-oriented QA professional with e-commerce experience",
            verbose=True,
            llm=self.openai_llm
        )
    
    def create_reporter_agent(self):
        return Agent(
            role="Operations Reporter",
            goal="Generate comprehensive daily operations reports",
            backstory="Analytical reporter skilled in summarizing complex operations data",
            verbose=True,
            llm=self.openai_llm,
            tools=[CSVReaderTool(), JSONWriterTool()]
        )