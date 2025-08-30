import math
from config import Config

def calculate_price(cost_price: float, shipping_cost: float, country: str = "AU") -> float:
    """
    Calculate minimum price with 25% margin
    Formula: P = (cost_price + shipping_cost + platform_fee + GST) / (1 - margin)
    """
    margin = Config.MIN_MARGIN
    
    # Initial estimate
    estimated_price = (cost_price + shipping_cost + Config.PLATFORM_FEE_FIXED) / (1 - Config.PLATFORM_FEE_PERCENT - margin)
    
    if country == "AU":
        # For AU, include GST
        estimated_price = estimated_price / (1 - Config.GST_PERCENT)
    
    # Round up to nearest $0.50
    rounded_price = math.ceil(estimated_price * 2) / 2
    
    # Verify margin
    landed_cost = calculate_landed_cost(cost_price, shipping_cost, rounded_price, country)
    actual_margin = (rounded_price - landed_cost) / rounded_price
    
    if actual_margin < margin:
        rounded_price += 0.50
    
    return rounded_price

def calculate_landed_cost(cost_price: float, shipping_cost: float, selling_price: float, country: str) -> float:
    platform_fee = (selling_price * Config.PLATFORM_FEE_PERCENT) + Config.PLATFORM_FEE_FIXED
    gst = selling_price * Config.GST_PERCENT if country == "AU" else 0
    return cost_price + shipping_cost + platform_fee + gst