import pandas as pd
import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from crewai_tools import BaseTool
from utils.pricing_utils import calculate_price

class CSVReaderTool(BaseTool):
    name: str = "CSV Reader"
    description: str = "Read data from CSV files"

    def _run(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        return df.to_string()

class CSVWriterTool(BaseTool):
    name: str = "CSV Writer"
    description: str = "Write data to CSV files"

    def _run(self, data: List[Dict], file_path: str) -> str:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return f"Data written to {file_path}"

class JSONWriterTool(BaseTool):
    name: str = "JSON Writer"
    description: str = "Write data to JSON files"

    def _run(self, data: Dict, file_path: str) -> str:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return f"Data written to {file_path}"

class PricingCalculatorTool(BaseTool):
    name: str = "Pricing Calculator"
    description: str = "Calculate optimal pricing with margin requirements"

    def _run(self, cost_price: float, shipping_cost: float, country: str = "AU") -> str:
        price = calculate_price(cost_price, shipping_cost, country)
        return str(price)

class StockValidatorTool(BaseTool):
    name: str = "Stock Validator"
    description: str = "Validate stock levels meet minimum requirements"

    def _run(self, current_stock: int, min_stock: int = 10) -> str:
        result = current_stock >= min_stock
        return str(result)