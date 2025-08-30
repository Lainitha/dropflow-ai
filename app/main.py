"""Main application for Shopify Dropshipping Operations."""
import os
import sys
import argparse
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.shopify_crew import ShopifyDropshippingCrew

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Shopify Dropshipping Operations Agent System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app run --catalog data/supplier_catalog.csv --orders data/orders.csv --out out/
  python -m app run --catalog catalog.csv --orders orders.csv --out results/ --use-crewai
        """
    )
    
    parser.add_argument(
        'command',
        choices=['run'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--catalog',
        required=True,
        help='Path to supplier catalog CSV file'
    )
    
    parser.add_argument(
        '--orders',
        required=True,
        help='Path to orders CSV file'
    )
    
    parser.add_argument(
        '--out',
        required=True,
        help='Output directory for results'
    )
    
    # CrewAI is now the default; deterministic fallback handled internally.
    
    args = parser.parse_args()
    
    # Validate input files exist
    if not os.path.exists(args.catalog):
        print(f"Error: Catalog file not found: {args.catalog}")
        sys.exit(1)
    
    if not os.path.exists(args.orders):
        print(f"Error: Orders file not found: {args.orders}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.out, exist_ok=True)
    
    if args.command == 'run':
        print("Running CrewAI workflow (deterministic artifact fallback enabled)...")
        try:
            crew = ShopifyDropshippingCrew(args.catalog, args.orders, args.out)
            crew.run()
            print(f"\nResults saved to: {args.out}")
        except Exception as e:
            print(f"Fatal error: {e}")
            print("No alternative manual path; please resolve the issue and retry.")

    # Removed manual deterministic execution function; artifact fallback is managed within crew.

if __name__ == '__main__':
    main()
