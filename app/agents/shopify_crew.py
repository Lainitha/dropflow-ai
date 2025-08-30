"""CrewAI Agents for Shopify Dropshipping Operations."""
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain.llms import Ollama
from typing import Dict, List, Any
import json
import os
import sys
import pandas as pd
from datetime import datetime
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import calculate_price_with_margin, load_csv, save_json, save_csv

# Deterministic Tools for CrewAI Agents
@tool
def deterministic_product_sourcing_tool(catalog_file: str, output_dir: str) -> str:
    """Select up to 10 supplier_sku values meeting stock>=10 and potential ≥25% margin.
    Writes selection.json as a simple JSON list of supplier_sku strings."""
    catalog = load_csv(catalog_file)
    # Filter by stock threshold
    filtered = [p for p in catalog if int(p.get('stock', 0)) >= 10]
    scored = []
    for p in filtered:
        try:
            cost = float(p.get('cost_price', 0))
            shipping = float(p.get('shipping_cost', 0))
        except ValueError:
            continue
        # Use helper pricing (guarantees ≥25%) to estimate a sell price then compute margin
        price = calculate_price_with_margin(cost, shipping)
        margin = (price - cost - shipping) / price if price else 0
        if margin >= 0.25:
            scored.append((margin, p.get('supplier_sku')))
    # Sort by margin desc and take top 10
    scored.sort(key=lambda x: x[0], reverse=True)
    selected_skus = [sku for _, sku in scored[:10] if sku]
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'selection.json')
    save_json(selected_skus, output_file)
    return f"Selected {len(selected_skus)} SKUs saved to {output_file}: {selected_skus}"

@tool
def deterministic_pricing_tool(cost_price: float, shipping_cost: float, is_australia: bool = True) -> Dict[str, float]:
    """
    Calculate optimal pricing with guaranteed ≥25% margin using deterministic formula.
    
    Formula accounts for:
    - Platform fee: 2.9% * price + $0.30
    - GST: 10% * price (AU customers only)
    - Target margin: ≥25%
    - Rounding: Up to nearest $0.50
    
    Returns dict with calculated_price, actual_margin, fees breakdown.
    """
    base_cost = cost_price + shipping_cost + 0.30  # Fixed platform fee
    
    if is_australia:
        # For AU: base_cost + 0.129*P <= 0.75*P
        # Solving: P >= base_cost / (0.75 - 0.129) = base_cost / 0.621
        min_price = base_cost / 0.621
    else:
        # For non-AU: base_cost + 0.029*P <= 0.75*P
        # Solving: P >= base_cost / (0.75 - 0.029) = base_cost / 0.721
        min_price = base_cost / 0.721
    
    # Round up to nearest $0.50
    final_price = math.ceil(min_price * 2) / 2
    
    # Calculate actual fees and margin
    platform_fee = 0.029 * final_price + 0.30
    gst = 0.10 * final_price if is_australia else 0
    total_fees = platform_fee + gst
    landed_cost = cost_price + shipping_cost + total_fees
    actual_margin = (final_price - landed_cost) / final_price if final_price > 0 else 0
    
    # Ensure margin meets minimum requirement
    while actual_margin < 0.25 and final_price < 1000:
        final_price += 0.50
        platform_fee = 0.029 * final_price + 0.30
        gst = 0.10 * final_price if is_australia else 0
        total_fees = platform_fee + gst
        landed_cost = cost_price + shipping_cost + total_fees
        actual_margin = (final_price - landed_cost) / final_price if final_price > 0 else 0
    
    return {
        'calculated_price': final_price,
        'actual_margin': actual_margin,
        'platform_fee': platform_fee,
        'gst': gst,
        'total_fees': total_fees,
        'landed_cost': landed_cost
    }

@tool
def deterministic_update_pricing_stock_files(selection_file: str, catalog_file: str, output_dir: str) -> str:
    """Create price_update.csv (sku,price,margin) and stock_update.csv (sku,stock) from selection.json + catalog.
    selection.json must be a JSON list of supplier_sku strings."""
    if not os.path.exists(selection_file):
        return f"Selection file missing: {selection_file}"
    try:
        with open(selection_file, 'r', encoding='utf-8') as f:
            selected_skus = json.load(f)
    except Exception as e:
        return f"Failed to read selection: {e}"
    catalog = load_csv(catalog_file)
    cat_index = {p.get('supplier_sku'): p for p in catalog}
    price_rows: List[Dict[str, Any]] = []
    stock_rows: List[Dict[str, Any]] = []
    for sku in selected_skus:
        p = cat_index.get(sku)
        if not p:
            continue
        try:
            cost = float(p.get('cost_price', 0))
            shipping = float(p.get('shipping_cost', 0))
        except ValueError:
            continue
        # Solve for minimum price P such that margin >=25% after fees and GST (AU)
        # Iterate upward in $0.50 increments.
        # Equation: margin = (P - (cost+shipping + (0.029*P + 0.30) + 0.10*P)) / P
        #           = (P - (cost+shipping+0.30) - 0.129P) / P >= 0.25
        base_cost = cost + shipping + 0.30
        min_price = base_cost / (0.75 - 0.129) if (0.75 - 0.129) > 0 else base_cost * 2
        # Round up to nearest 0.50
        import math as _m
        price = _m.ceil(min_price * 2) / 2
        def compute_margin(P: float) -> float:
            fees = 0.029 * P + 0.30 + 0.10 * P  # platform + GST
            landed = cost + shipping + fees
            return (P - landed) / P if P else 0
        while compute_margin(price) < 0.25 and price < 1000:
            price += 0.50
        margin = compute_margin(price)
        price_rows.append({'sku': sku, 'price': f"{price:.2f}", 'margin': f"{margin:.3f}"})
        stock_rows.append({'sku': sku, 'stock': p.get('stock', 0)})
    os.makedirs(output_dir, exist_ok=True)
    price_file = os.path.join(output_dir, 'price_update.csv')
    stock_file = os.path.join(output_dir, 'stock_update.csv')
    save_csv(price_rows, price_file, ['sku','price','margin'])
    save_csv(stock_rows, stock_file, ['sku','stock'])
    return f"Created {price_file} & {stock_file} for {len(price_rows)} SKUs"

class ShopifyDropshippingCrew:
    """Main crew for Shopify dropshipping operations."""
    
    def __init__(self, catalog_file: str, orders_file: str, output_dir: str):
        self.catalog_file = catalog_file
        self.orders_file = orders_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Initialize LLMs - using Ollama with local models
        self.llama3 = Ollama(model="llama3", temperature=0.7)
        self.mistral = Ollama(model="mistral", temperature=0.7)

        # Initialize agents
        self._create_agents()
        
    def _create_agents(self):
        """Create all agents for the crew."""
        
        # 1. Manager Agent - Orchestrates workflow
        self.manager_agent = Agent(
            role="Operations Manager",
            goal="Orchestrate the entire dropshipping workflow and ensure all tasks are completed successfully",
            backstory="You are an experienced operations manager who coordinates all aspects of the dropshipping business",
            verbose=True,
            allow_delegation=True,
            llm=self.llama3
        )
        
        # 2. Product Sourcing Agent - Selects products
        self.sourcing_agent = Agent(
            role="Product Sourcing Specialist",
            goal="Select profitable products with adequate stock from supplier catalog using deterministic analysis",
            backstory="You are an expert at analyzing product catalogs and selecting items with guaranteed high profit potential using mathematical models",
            verbose=True,
            allow_delegation=False,
            llm=self.llama3,
            tools=[deterministic_product_sourcing_tool]
        )
        
        # 3. Listing Agent - Generates product content
        self.listing_agent = Agent(
            role="Product Listing Creator",
            goal="Create compelling product listings with SEO-optimized content",
            backstory="You are a skilled copywriter who creates engaging product descriptions and marketing content",
            verbose=True,
            allow_delegation=False,
            llm=self.mistral
        )
        
        # 4. Pricing & Stock Agent - Calculates prices
        self.pricing_agent = Agent(
            role="Pricing Strategist",
            goal="Produce compliant price_update.csv & stock_update.csv with ≥25% margin guarantee",
            backstory="You deterministically compute profitable selling prices considering fees & GST, ensuring data files are written",
            verbose=True,
            allow_delegation=False,
            llm=self.llama3,
            tools=[deterministic_update_pricing_stock_files]
        )
        
        # 5. Order Routing Agent - Processes orders
        self.order_agent = Agent(
            role="Order Fulfillment Specialist",
            goal="Process orders and determine fulfillment actions",
            backstory="You manage order processing and customer communications efficiently",
            verbose=True,
            allow_delegation=False,
            llm=self.mistral
        )
        
        # 6. QA Agent - Reviews listings
        self.qa_agent = Agent(
            role="Quality Assurance Reviewer",
            goal="Review product listings for accuracy and compliance",
            backstory="You ensure all product claims are accurate and marketing content is appropriate",
            verbose=True,
            allow_delegation=False,
            llm=self.llama3
        )
        
        # 7. Reporter Agent - Creates reports
        self.reporter_agent = Agent(
            role="Business Reporter",
            goal="Generate comprehensive daily operations reports",
            backstory="You compile and summarize all business activities into clear reports",
            verbose=True,
            allow_delegation=False,
            llm=self.mistral
        )
    
    def run(self):
        """Execute the complete workflow."""
        print("Starting Shopify Dropshipping Operations...")
        
        # Create tasks for each agent
        tasks = self._create_tasks()
        
        # Create the crew
        crew = Crew(
            agents=[
                self.manager_agent,
                self.sourcing_agent,
                self.listing_agent,
                self.pricing_agent,
                self.order_agent,
                self.qa_agent,
                self.reporter_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        print("\nOperations completed successfully!")
        return result
    
    def _create_tasks(self) -> List[Task]:
        """Create tasks for the crew."""
        tasks: List[Task] = []

        # Task 1: Product Selection (deterministic tool)
        product_selection_task = Task(
            description=(
                f"Use deterministic_product_sourcing_tool on {self.catalog_file} to select up to 10 profitable SKUs "
                f"(stock >=10 and achievable margin >=25%). Tool saves selection.json (list of supplier_sku strings) "
                f"in {self.output_dir}. Always invoke the tool."
            ),
            agent=self.sourcing_agent,
            expected_output="selection.json containing list of selected supplier_sku strings",
            tools=[deterministic_product_sourcing_tool]
        )
        tasks.append(product_selection_task)

        # Task 2: Pricing & Stock (deterministic tool)
        pricing_task = Task(
            description=(
                "Generate price_update.csv & stock_update.csv by calling deterministic_update_pricing_stock_files "
                f"with selection_file={self.output_dir}/selection.json, catalog_file={self.catalog_file}, output_dir={self.output_dir}. "
                "Ensure each price yields >=25% margin after 2.9% + $0.30 fees and 10% GST, rounded to nearest $0.50."
            ),
            agent=self.pricing_agent,
            expected_output="price_update.csv (sku,price,margin) and stock_update.csv (sku,stock) created",
            tools=[deterministic_update_pricing_stock_files]
        )
        tasks.append(pricing_task)

        # Task 3: Listing Generation (LLM)
        listing_generation_task = Task(
            description=(
                f"For each SKU in selection.json, load source fields from {self.catalog_file} & price from price_update.csv. "
                f"Create listings.json (array) with objects: sku, title (<=80 chars), bullets (5-7, first bullet 'Price: $X.XX'), "
                "description (160-220 words), tags, seo_title, meta_description, price (string matching price_update.csv). "
                f"Write listings.json to {self.output_dir}."
            ),
            agent=self.listing_agent,
            expected_output="listings.json with marketing content for each SKU"
        )
        tasks.append(listing_generation_task)

        # Task 4: Order Routing (LLM deterministic logic description)
        order_processing_task = Task(
            description=(
                f"Read orders.csv at {self.orders_file} and supplier stock in {self.catalog_file}. For each order decide action: "
                "Fulfill if quantity <= stock else Backorder. Produce order_actions.json (array) with fields: order_id, sku, quantity, "
                f"action, customer_email; save to {self.output_dir}. Keep customer_email concise (confirmation or backorder notice)."
            ),
            agent=self.order_agent,
            expected_output="order_actions.json created with actions"
        )
        tasks.append(order_processing_task)

        # Task 5: QA
        qa_review_task = Task(
            description=(
                f"Review listings.json for factual accuracy, over-claims, awkward phrasing. Output listing_redlines.json (array) with "
                "objects: sku, issues (list), suggestions (list). Provide concise actionable feedback; save file to output dir."
            ),
            agent=self.qa_agent,
            expected_output="listing_redlines.json with issues & suggestions"
        )
        tasks.append(qa_review_task)

        # Task 6: Reporter
        reporting_task = Task(
            description=(
                f"Summarize daily operations into daily_report.md in {self.output_dir}: count selected SKUs, pricing stats (min/avg/max), "
                "order actions counts (Fulfill vs Backorder), and SKUs with QA issues. Format markdown with sections."
            ),
            agent=self.reporter_agent,
            expected_output="daily_report.md summarizing operations"
        )
        tasks.append(reporting_task)

        return tasks
