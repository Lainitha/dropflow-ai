# Shopify Dropshipping Operations Agent

Multi-agent system for automated dropshipping operations using CrewAI.

## Clone Repository

**Option 1: GitHub CLI**
```bash
gh repo clone Lainitha/dropflow-ai
cd dropflow-ai
```

**Option 2: Git**
```bash
git clone https://github.com/Lainitha/dropflow-ai.git
cd dropflow-ai
```

**Option 3: Download ZIP**
- Go to https://github.com/Lainitha/dropflow-ai
- Click "Code" → "Download ZIP"
- Extract and navigate to folder

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure LLM Provider (choose one):**

   **Option A: OpenAI**
   - Edit `.env` file
   - Replace `your_valid_openai_api_key_here` with your OpenAI API key

   **Option B: Google Gemini**
   - Edit `.env` file
   - Add `GOOGLE_API_KEY=your_google_api_key`

   **Option C: Ollama (Local)**
   - Install Ollama: https://ollama.ai
   - Pull models:
     ```bash
     ollama pull llama3.1
     ollama pull mistral
     ```
   - Add to `.env`:
     ```
     OLLAMA_BASE_URL=http://localhost:11434
     ```

3. **Update agent configuration:**
   - Edit `agents/ops_agents.py`
   - Change `llm=self.openai_llm` to:
     - `llm=self.gemini_llm` for Gemini
     - `llm=self.ollama_llama3` for Llama3
     - `llm=self.ollama_mistral` for Mistral

4. **Prepare data:**
   - Place supplier catalog in `data/supplier_catalog.csv`
   - Place orders in `data/orders.csv`

## Usage

```bash
python main.py --catalog data/supplier_catalog.csv --orders data/orders.csv --out outputs/
```

## Output Files

- `outputs/selection.json` - Selected products
- `outputs/listings.json` - Product listings
- `outputs/price_update.csv` - Pricing data
- `outputs/order_actions.json` - Order processing
- `outputs/listing_redlines.json` - QA findings
- `outputs/daily_report.md` - Operations report

## Requirements

- Python 3.10+
- One of: OpenAI API key, Google API key, or Ollama installation