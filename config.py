import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Providers
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Model Selection
    OPENAI_MODEL = "gpt-3.5-turbo"  # Free tier friendly
    GEMINI_MODEL = "gemini-1.5-flash"
    OLLAMA_LLAMA3_MODEL = "llama3.1"
    OLLAMA_MISTRAL_MODEL = "mistral"
    
    # File Paths
    CATALOG_PATH = "data/supplier_catalog.csv"
    ORDERS_PATH = "data/orders.csv"
    OUTPUT_DIR = "outputs/"
    
    # Business Rules
    MIN_STOCK = 10
    MIN_MARGIN = 0.25
    PLATFORM_FEE_PERCENT = 0.029
    PLATFORM_FEE_FIXED = 0.30
    GST_PERCENT = 0.10  # Australia GST