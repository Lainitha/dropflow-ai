#!/usr/bin/env python3
import os
import sys
import argparse
from crewai import Crew, Process

# Fix Windows console encoding issues
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
from agents.ops_agents import OpsAgents
from tasks.ops_tasks import OpsTasks
from utils.file_utils import ensure_directory_exists
from config import Config

def main():
    parser = argparse.ArgumentParser(description="Shopify Dropshipping Ops Agent")
    parser.add_argument("--catalog", default=Config.CATALOG_PATH, help="Supplier catalog CSV path")
    parser.add_argument("--orders", default=Config.ORDERS_PATH, help="Orders CSV path")
    parser.add_argument("--out", default=Config.OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()
    
    # Ensure output directory exists
    ensure_directory_exists(args.out)
    
    # Initialize agents and tasks
    ops_agents = OpsAgents()
    ops_tasks = OpsTasks()
    
    # Create agents
    manager = ops_agents.create_manager_agent()
    product_sourcing = ops_agents.create_product_sourcing_agent()
    listing = ops_agents.create_listing_agent()
    pricing = ops_agents.create_pricing_agent()
    order_routing = ops_agents.create_order_routing_agent()
    qa = ops_agents.create_qa_agent()
    reporter = ops_agents.create_reporter_agent()
    
    # Create tasks
    task1 = ops_tasks.product_sourcing_task(product_sourcing)
    task2 = ops_tasks.listing_creation_task(listing, [task1])
    task3 = ops_tasks.pricing_task(pricing, [task2])
    task4 = ops_tasks.order_routing_task(order_routing)
    task5 = ops_tasks.qa_task(qa, [task2])
    task6 = ops_tasks.reporting_task(reporter, [task1, task2, task3, task4, task5])
    
    # Create and run crew
    crew = Crew(
        agents=[manager, product_sourcing, listing, pricing, order_routing, qa, reporter],
        tasks=[task1, task2, task3, task4, task5, task6],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    print(f"Operations completed! Results saved to {args.out}")
    return result

if __name__ == "__main__":
    main()