from crewai import Task
from config import Config

class OpsTasks:
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
    
    def product_sourcing_task(self, agent):
        return Task(
            description=f"""Analyze the supplier catalog at {Config.CATALOG_PATH} and select 10 SKUs that meet:
            - Stock level ≥ {Config.MIN_STOCK}
            - Potential margin ≥ {Config.MIN_MARGIN*100}%
            Consider product category, cost, and shipping requirements.""",
            agent=agent,
            expected_output="JSON file with selected SKUs including all relevant product information",
            output_file=f"{self.output_dir}selection.json"
        )
    
    def listing_creation_task(self, agent, context):
        return Task(
            description="""For each selected product, create compelling Shopify listings including:
            - SEO-optimized title
            - Bullet points highlighting key features
            - Detailed description
            - Relevant tags
            - SEO meta description
            Ensure content is persuasive but not misleading.""",
            agent=agent,
            context=context,
            expected_output="JSON file with complete listing content for all selected products",
            output_file=f"{self.output_dir}listings.json"
        )
    
    def pricing_task(self, agent, context):
        return Task(
            description="""Calculate optimal prices for each product ensuring:
            - Minimum 25% margin after all costs
            - Competitive pricing
            - Round to nearest $0.50
            Consider shipping costs and platform fees.""",
            agent=agent,
            context=context,
            expected_output="CSV file with SKU, new price, and margin calculations",
            output_file=f"{self.output_dir}price_update.csv"
        )
    
    def order_routing_task(self, agent):
        return Task(
            description=f"""Process orders from {Config.ORDERS_PATH} and decide:
            - Fulfill immediately if stock available
            - Backorder if stock low but replenishable
            - Substitute with similar product if possible
            Generate appropriate customer emails for each scenario.""",
            agent=agent,
            expected_output="JSON file with order actions and customer email templates",
            output_file=f"{self.output_dir}order_actions.json"
        )
    
    def qa_task(self, agent, context):
        return Task(
            description="""Review product listings for:
            - Over-promising or false claims
            - SEO optimization
            - Compliance with platform policies
            - Grammar and spelling errors
            Provide specific redlines and suggestions.""",
            agent=agent,
            context=context,
            expected_output="JSON file with QA findings and recommendations",
            output_file=f"{self.output_dir}listing_redlines.json"
        )
    
    def reporting_task(self, agent, context):
        return Task(
            description="""Generate a comprehensive daily operations report including:
            - Products selected and reasons
            - Pricing strategy summary
            - Order processing status
            - QA findings and resolutions
            - Recommendations for improvement""",
            agent=agent,
            context=context,
            expected_output="Markdown report summarizing all operations",
            output_file=f"{self.output_dir}daily_report.md"
        )