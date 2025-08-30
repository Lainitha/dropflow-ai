"""Utility functions for the Shopify Dropshipping system."""
import json
import csv
import math
from typing import Dict, List, Any

def calculate_price_with_margin(cost_price: float, shipping_cost: float, 
                                is_australia: bool = False, margin: float = 0.25) -> float:
    """
    Calculate the minimum price to achieve the target margin.
    
    Formula:
    - Platform fee = 2.9% * P + $0.30
    - GST = 10% * P (AU only)
    - Landed cost = cost_price + shipping_cost + fee + GST
    - Margin >= 25%
    - Round up to nearest $0.50
    
    Solving for P:
    Margin = (P - landed_cost) / P >= 0.25
    0.25 * P <= P - landed_cost
    landed_cost <= 0.75 * P
    
    landed_cost = cost_price + shipping_cost + 0.029*P + 0.30 + (0.10*P if AU else 0)
    
    For AU: landed_cost = cost_price + shipping_cost + 0.129*P + 0.30
    For non-AU: landed_cost = cost_price + shipping_cost + 0.029*P + 0.30
    """
    base_cost = cost_price + shipping_cost + 0.30
    
    if is_australia:
        # For AU: base_cost + 0.129*P <= 0.75*P
        # base_cost <= (0.75 - 0.129)*P
        # base_cost <= 0.621*P
        # P >= base_cost / 0.621
        min_price = base_cost / 0.621
    else:
        # For non-AU: base_cost + 0.029*P <= 0.75*P
        # base_cost <= (0.75 - 0.029)*P
        # base_cost <= 0.721*P
        # P >= base_cost / 0.721
        min_price = base_cost / 0.721
    
    # Round up to nearest $0.50
    final_price = math.ceil(min_price * 2) / 2
    
    # Verify the margin
    platform_fee = 0.029 * final_price + 0.30
    gst = 0.10 * final_price if is_australia else 0
    landed_cost = cost_price + shipping_cost + platform_fee + gst
    actual_margin = (final_price - landed_cost) / final_price if final_price > 0 else 0
    
    # If margin is still below target due to rounding, increase price
    while actual_margin < margin and final_price < 1000:
        final_price += 0.50
        platform_fee = 0.029 * final_price + 0.30
        gst = 0.10 * final_price if is_australia else 0
        landed_cost = cost_price + shipping_cost + platform_fee + gst
        actual_margin = (final_price - landed_cost) / final_price if final_price > 0 else 0
    
    return final_price

def load_csv(filepath: str) -> List[Dict[str, Any]]:
    """Load CSV file and return as list of dictionaries."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for key in ['cost_price', 'stock', 'weight_kg', 'shipping_cost', 'supplier_lead_days', 'quantity']:
                if key in row and row[key]:
                    try:
                        if key in ['cost_price', 'weight_kg', 'shipping_cost']:
                            row[key] = float(row[key])
                        else:
                            row[key] = int(row[key])
                    except ValueError:
                        pass
            data.append(row)
    return data

def save_json(data: Any, filepath: str):
    """Save data as JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_csv(data: List[Dict[str, Any]], filepath: str, fieldnames: List[str]):
    """Save data as CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
